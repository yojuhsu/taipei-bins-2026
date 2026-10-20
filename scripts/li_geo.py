"""臺北市 456 里的多邊形與點對多邊形定位（從 join_li.py 抽出來的共用模組）。
用法：from li_geo import POLYS, locate；locate(lon, lat) 回傳 villcode 或 None。"""
import collections, math, os, struct, zipfile

DATA = os.environ.get("CIVIC_DATA", os.path.expanduser("~/Projects/civic-debug-data"))
_z = zipfile.ZipFile(os.path.join(DATA, "peripheral", "tgos_li.zip"))
_dbf = _z.read("VILLAGE_NLSC_1150817.dbf"); _shp = _z.read("VILLAGE_NLSC_1150817.shp")
_N = struct.unpack("<I", _dbf[4:8])[0]; _hl, _rl = struct.unpack("<HH", _dbf[8:12]); _fl = []; _i = 32
while _dbf[_i] != 0x0D:
    _fl.append((_dbf[_i:_i + 11].split(b"\0")[0].decode("latin1"), _dbf[_i + 16])); _i += 32
_attrs = []
for _k in range(_N):
    _rec = _dbf[_hl + _k * _rl: _hl + (_k + 1) * _rl]; _off = 1; _v = {}
    for _nm, _ln in _fl:
        _v[_nm] = _rec[_off:_off + _ln].decode("utf-8", "replace").strip(); _off += _ln
    _attrs.append(_v)
POLYS = {}
_pos = 100; _idx = 0
while _pos < len(_shp):
    _clen = struct.unpack(">i", _shp[_pos + 4:_pos + 8])[0] * 2
    _body = _shp[_pos + 8: _pos + 8 + _clen]; _pos += 8 + _clen
    _a = _attrs[_idx]; _idx += 1
    if _a["COUNTYNAME"] != "臺北市": continue
    if struct.unpack("<i", _body[:4])[0] not in (5, 15): continue
    _minx, _miny, _maxx, _maxy = struct.unpack("<4d", _body[4:36])
    _npart, _npts = struct.unpack("<ii", _body[36:44])
    _parts = list(struct.unpack(f"<{_npart}i", _body[44:44 + 4 * _npart])) + [_npts]
    _po = 44 + 4 * _npart
    _pts = struct.unpack(f"<{2 * _npts}d", _body[_po:_po + 16 * _npts])
    _rings = [[(_pts[2 * j], _pts[2 * j + 1]) for j in range(_parts[r], _parts[r + 1])] for r in range(_npart)]
    POLYS[_a["VILLCODE"]] = dict(code=_a["VILLCODE"], dist=_a["TOWNNAME"], name=_a["VILLNAME"], towncode=_a["TOWNCODE"],
                                  bbox=(_minx, _miny, _maxx, _maxy), rings=_rings)
assert len(POLYS) == 456, len(POLYS)

CELL = 0.01
_grid = collections.defaultdict(list)
for _p in POLYS.values():
    _x0, _y0, _x1, _y1 = _p["bbox"]
    for _gx in range(int(_x0 / CELL), int(_x1 / CELL) + 1):
        for _gy in range(int(_y0 / CELL), int(_y1 / CELL) + 1):
            _grid[(_gx, _gy)].append(_p)

def inside(x, y, rings):
    c = False
    for r in rings:
        n = len(r); j = n - 1
        for k in range(n):
            xi, yi = r[k]; xj, yj = r[j]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi: c = not c
            j = k
    return c

_cache = {}
def locate(lon, lat):
    if lon is None or lat is None: return None
    key = (round(lon, 6), round(lat, 6))
    if key in _cache: return _cache[key]
    res = None
    for p in _grid.get((int(lon / CELL), int(lat / CELL)), ()):
        x0, y0, x1, y1 = p["bbox"]
        if x0 <= lon <= x1 and y0 <= lat <= y1 and inside(lon, lat, p["rings"]):
            res = p["code"]; break
    _cache[key] = res
    return res
