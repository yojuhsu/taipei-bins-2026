#!/usr/bin/env python3
"""題 2 作品的點層資料（第二版，站牌改用 2026 年公運處站位檔）：每個公車站牌與捷運站，最近的公共桶（681 點表）、景點表桶（130 點，N 處）、超商（OSM 四大）距離。
輸出 _草稿/作品_垃圾桶/data.json（給網頁內嵌）與 points_summary.json。距離用北緯 25.05 度平面近似，公尺。"""
import csv, io, json, math, os, re, sys, struct, zipfile, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from li_geo import POLYS, locate
DATA = os.environ.get("CIVIC_DATA", os.path.expanduser("~/Projects/civic-debug-data"))
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(OUT, exist_ok=True)
KX = 111320 * math.cos(math.radians(25.05)); KY = 110574
def rd(fn):
    b = open(fn, "rb").read()
    for enc in ("utf-8-sig", "big5"):
        try: return list(csv.DictReader(io.StringIO(b.decode(enc))))
        except UnicodeDecodeError: pass
def num(s):
    try: return float(re.sub(r"[^\d.\-]", "", str(s)))
    except Exception: return None
# --- 圖層 ---
bins = []
for r in rd(os.path.join(DATA, "trashbin_csv.raw")):
    lon, lat = num(r["經度"]), num(r["緯度"])
    if lon and lat: bins.append(dict(lon=lon, lat=lat, dist=r["行政區"], addr=r["地址"]))
spots = []
for r in rd(os.path.join(DATA, "trashbin_130.raw")):
    lon, lat = num(r["經度"]), num(r["緯度"]); m = re.search(r"(\d+)", r["備註"] or "")
    if lon and lat: spots.append(dict(lon=lon, lat=lat, dist=r["行政區"], name=r["地址"], n=int(m.group(1)) if m else 1))
cvs = []
for e in json.load(open(os.path.join(DATA, "q2", "osm_convenience.json"), encoding="utf-8"))["elements"]:
    t = e.get("tags", {}); b = t.get("brand") or t.get("name") or ""
    if not any(b.startswith(x) for x in ("7-Eleven", "全家便利商店", "萊爾富", "OK超商")): continue
    lon = e.get("lon") or e.get("center", {}).get("lon"); lat = e.get("lat") or e.get("center", {}).get("lat")
    if locate(lon, lat): cvs.append(dict(lon=lon, lat=lat, brand=b[:6]))
mrt = []
for s in json.load(open(os.path.join(DATA, "q2", "tdx_trtc_stations.json"), encoding="utf-8")):
    if s.get("LocationCity") != "臺北市": continue
    mrt.append(dict(lon=s["StationPosition"]["PositionLon"], lat=s["StationPosition"]["PositionLat"], name=s["StationName"]["Zh_tw"], town=s.get("LocationTown")))
# 站牌（實體站位）：公運處 blob GetStopLocation，2026-10-20 21:43 抓（題 5 串），複製到 q2/；2020 年 SHP 版留在 _舊版 對照
import gzip
_J = json.loads(gzip.open(os.path.join(DATA, "q2", "GetStopLocation_20261020.gz"), "rb").read().decode("utf-8-sig", errors="replace"))
_recs = _J["BusInfo"] if isinstance(_J, dict) else _J
stops = []
for _r in _recs:
    try: _lon, _lat = float(_r["lon"]), float(_r["lat"])
    except Exception: continue
    stops.append(dict(lon=_lon, lat=_lat, name=(_r.get("name") or "").replace("\ufffd", ""), id=str(_r.get("nid") or _r.get("id") or "")))
# --- 最近距離（格網索引）---
def grid(pts, cell=0.003):
    g = collections.defaultdict(list)
    for p in pts: g[(int(p["lon"] / cell), int(p["lat"] / cell))].append(p)
    return g, cell
def nearest(p, g, cell, maxr=3):
    best = None; bd = 1e12
    gx, gy = int(p["lon"] / cell), int(p["lat"] / cell)
    for dx in range(-maxr, maxr + 1):
        for dy in range(-maxr, maxr + 1):
            for q in g.get((gx + dx, gy + dy), ()):
                d = math.hypot((q["lon"] - p["lon"]) * KX, (q["lat"] - p["lat"]) * KY)
                if d < bd: bd, best = d, q
    return bd if best else None, best
G = {k: grid(v) for k, v in (("bin", bins), ("spot", spots), ("cvs", cvs))}
def enrich(p, kind):
    c = locate(p["lon"], p["lat"]); li = POLYS.get(c)
    p["kind"] = kind; p["dist_name"] = li["dist"] if li else ""; p["li"] = li["name"] if li else ""
    for k in ("bin", "spot", "cvs"):
        d, q = nearest(p, *G[k]); p["d_" + k] = round(d) if d is not None else None
        if k == "spot" and q: p["spot_n"] = q["n"]; p["spot_name"] = q["name"]
    return p
nodes = [enrich(dict(s), "stop") for s in stops if locate(s["lon"], s["lat"])] + [enrich(dict(m), "mrt") for m in mrt]
# --- 摘要 ---
def status(p, r):
    pub = (p["d_bin"] is not None and p["d_bin"] <= r) or (p["d_spot"] is not None and p["d_spot"] <= r)
    priv = p["d_cvs"] is not None and p["d_cvs"] <= r
    return "pub" if pub else ("cvs" if priv else "none")
summary = {}
for r in (50, 100, 200):
    for kind in ("stop", "mrt"):
        ns = [p for p in nodes if p["kind"] == kind]; c = collections.Counter(status(p, r) for p in ns)
        summary[f"{kind}_{r}"] = dict(n=len(ns), pub=c["pub"], cvs=c["cvs"], none=c["none"], pub681=sum(1 for p in ns if p["d_bin"] is not None and p["d_bin"] <= r))
by_dist = collections.defaultdict(lambda: collections.Counter())
for p in nodes:
    if p["kind"] == "stop": by_dist[p["dist_name"]][status(p, 100)] += 1; by_dist[p["dist_name"]]["n"] += 1
summary["stop_100_by_district"] = {d: dict(c) for d, c in by_dist.items()}
json.dump(dict(nodes=nodes, bins=bins, spots=spots, cvs=cvs, mrt=mrt, summary=summary,
               meta=dict(bins_src="data.taipei 行人專用清潔箱 點位表 681（2026-09-30 更新）", spots_src="同資料集 景點商圈周邊 130 點（2026-08-18 更新，備註 N 處）",
                         stops_src="公運處 blob 站位檔 GetStopLocation（2026-10-20），臺北市里界內 3,460；2020 年 SHP 3,407 的對照見 README", mrt_src="TDX 捷運車站 87（臺北市）", cvs_src="OpenStreetMap 四大超商 1,566（ODbL，覆蓋約六成）",
                         li_src="內政部國土測繪中心 村里界 115/08", built="2026-10-20")),
          open(os.path.join(OUT, "data.json"), "w", encoding="utf-8"), ensure_ascii=False)
json.dump(summary, open(os.path.join(OUT, "points_summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("nodes", len(nodes), "bins", len(bins), "spots", len(spots), "cvs", len(cvs), "mrt", len(mrt))
for k, v in summary.items():
    if k != "stop_100_by_district": print(k, v)
print("stop 100m by district:", {d: f"{c['none']}/{c['n']}" for d, c in sorted(by_dist.items(), key=lambda x: -x[1]['none'] / x[1]['n'])})
