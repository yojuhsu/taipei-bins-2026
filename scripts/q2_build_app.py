#!/usr/bin/env python3
"""把 data.json 內嵌進單檔網頁 _草稿/作品_垃圾桶/index.html。Leaflet 走 cdnjs，底圖走 OSM tile。"""
import json, os
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_草稿", "作品_垃圾桶")
data = json.load(open(os.path.join(OUT, "data.json"), encoding="utf-8"))
S = data["summary"]
def pct(a, b): return f"{a / b * 100:.0f}%"
kpi = {r: dict(none=S[f"stop_{r}"]["none"], cvs=S[f"stop_{r}"]["cvs"], pub=S[f"stop_{r}"]["pub"], n=S[f"stop_{r}"]["n"],
               mrt_none=S[f"mrt_{r}"]["none"], mrt_n=S[f"mrt_{r}"]["n"]) for r in (50, 100, 200)}
html = r"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>2026 debug松：找回消失的垃圾桶</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<style>
:root{--paper:#f5f2ea;--ink:#1c1b19;--mute:#6a665c;--rule:#d9d3c4;--none:#a63d24;--cvs:#c9961a;--pub:#2f6b3a;--mrt:#1f4e79;--bin:#1c1b19}
*{box-sizing:border-box}html{height:100%}
body{margin:0;min-height:100%;background:var(--paper);color:var(--ink);font:15px/1.6 "PingFang TC","Noto Sans TC",system-ui,sans-serif;display:flex;flex-direction:column}
header{padding:12px 16px 8px;border-bottom:2px solid var(--ink);display:flex;flex-wrap:wrap;gap:6px 24px;align-items:baseline}
header h1{font-size:1.25rem;margin:0;letter-spacing:.01em}
header .claim{color:var(--mute);font-size:.92rem;margin:0}.opener{border:1px solid var(--line);background:#fff;padding:8px 14px;margin:10px 0 6px;font-size:.95rem}.opener p{margin:5px 0}
.kpis{display:flex;gap:18px;flex-wrap:wrap;padding:8px 16px;border-bottom:1px solid var(--rule);font-size:.9rem}
.kpi b{font-size:1.35rem;font-variant-numeric:tabular-nums;margin-right:4px}
.kpi.none b{color:var(--none)}.kpi.cvs b{color:var(--cvs)}.kpi.pub b{color:var(--pub)}
main{flex:1;display:flex;min-height:0;height:calc(100vh - 150px)}
#map{flex:1;min-height:360px;background:#e9e4d8}
aside{width:380px;max-width:100%;min-height:0;border-left:1px solid var(--rule);display:flex;flex-direction:column;background:#faf8f2}
.ctl{padding:10px 14px;border-bottom:1px solid var(--rule);display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;font-size:.9rem}
.ctl label{display:inline-flex;gap:4px;align-items:center}
.seg button{border:1.5px solid var(--ink);background:transparent;padding:3px 10px;font:inherit;cursor:pointer}
.seg button.on{background:var(--ink);color:var(--paper)}
.seg button+button{border-left:0}
select{font:inherit;padding:2px 6px;border:1.5px solid var(--ink);background:#fff}
.tabs{display:flex;border-bottom:1px solid var(--rule)}
.tabs button{flex:1;border:0;background:transparent;padding:8px 4px;font:inherit;font-weight:600;cursor:pointer;color:var(--mute);border-bottom:3px solid transparent}
.tabs button.on{color:var(--ink);border-bottom-color:var(--ink)}
.pane{display:none;padding:12px 14px;overflow:auto;min-height:0;flex:1;font-size:.92rem}.pane.on{display:block}
.pane h3{font-size:.98rem;margin:14px 0 4px}.pane h3:first-child{margin-top:0}
.pane p{margin:.4rem 0}.pane ul{padding-left:1.1rem;margin:.3rem 0}.pane li{margin:.2rem 0}
.pane table{border-collapse:collapse;width:100%;font-size:.86rem;margin:.4rem 0}
.pane th,.pane td{text-align:left;padding:4px 6px;border-bottom:1px solid var(--rule);vertical-align:top}
.pane th{border-bottom:2px solid var(--ink)}
.pane td:first-child,.pane th:first-child{white-space:nowrap}
.lg{display:flex;gap:12px;flex-wrap:wrap;font-size:.85rem;margin:.3rem 0}
.sw{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:4px;vertical-align:-1px}
code{background:#ebe6d8;padding:0 .3em;font-size:.88em}
.warn{border-left:3px solid var(--none);padding:6px 10px;background:#f3dfd7;margin:.5rem 0}
footer{padding:6px 16px;border-top:1px solid var(--rule);color:var(--mute);font-size:.8rem}
.leaflet-popup-content{font:13px/1.5 "PingFang TC","Noto Sans TC",sans-serif}
@media (max-width:760px){main{display:block;height:auto}#map{height:56vh;min-height:300px}aside{width:100%;border-left:0;border-top:1px solid var(--rule);display:block}.pane{overflow:visible}}
</style>
</head>
<body>
<header>
  <h1>2026 debug松：找回消失的垃圾桶</h1>
  <p class="claim">官方題目背景：行人專用垃圾桶從約 3,000 組降到約 800 組，今年從 1,682 組撤到 806 組。這頁先回答一個小問題：公車站牌 100 公尺內有沒有垃圾桶。</p>
<div class="opener"><p><b>題目在問什麼</b>：行人專用垃圾桶從約 3,000 組減到約 800 組，題目要的是用 IoT 感測器把桶放回最需要的地方。</p><p><b>我們認為重點是什麼</b>：桶是市府撤的，不是壞了沒補；環保局長說是經里長要求或里長同意後撤的，沒有逐桶的紀錄可以查，只能當說法。衝突集中在捷運站、公車站、公園這幾類地方，而「撤了之後路面變髒了嗎、家戶垃圾少了嗎」兩邊都沒有數字。感測器要最佳化的「滿不滿」根本沒有資料。</p><p><b>解方的方向</b>：先把數字收齊再談放桶，桶上貼 QR 讓路人回報、陳情與開單加地點、固定幾十個點定期拍。這一頁先量出一件事：每個公車站牌 50 到 200 公尺內，有沒有公共垃圾桶或超商。</p></div>
</header>
<div class="kpis" id="kpis"></div>
<main>
  <div id="map"></div>
  <aside>
    <div class="ctl">
      <span>半徑</span><span class="seg" id="rseg"><button data-r="50">50 m</button><button data-r="100" class="on">100 m</button><button data-r="200">200 m</button></span>
      <select id="dsel"><option value="">全市 12 區</option></select>
      <label><input type="checkbox" id="onlynone"> 只看什麼都沒有的站牌</label>
      <label><input type="checkbox" id="showcvs"> 顯示超商</label>
      <label><input type="checkbox" id="showbins" checked> 顯示公共桶</label>
    </div>
    <div class="tabs"><button class="on" data-t="read">怎麼讀</button><button data-t="plan">100 天怎麼做</button><button data-t="src">資料與限制</button></div>
    <div class="pane on" id="p-read">
      <div class="lg"><span><i class="sw" style="background:var(--none)"></i>半徑內沒有公共桶也沒有超商</span><span><i class="sw" style="background:var(--cvs)"></i>只有超商（收不收路人垃圾未驗）</span><span><i class="sw" style="background:var(--pub)"></i>有公共桶</span><span><i class="sw" style="background:var(--bin)"></i>公共桶（點位表 681）</span><span><i class="sw" style="background:var(--spot);border:2px solid var(--bin)"></i>景點商圈桶（130 點，圈越大處數越多）</span><span><i class="sw" style="background:var(--mrt);border-radius:2px"></i>捷運站</span></div>
      <p>點任何一個站牌，看它最近的公共桶、景點桶、超商各在幾公尺外。底圖是臺北市 456 個里的界線，沒有街道，因為這個頁面不能載入外部地圖磁磚。</p>
      <h3>這頁回答的問題</h3>
      <p>「找回消失的垃圾桶」這個題目，先要知道消失在哪裡。里層的統計會被面積與戶籍人口帶著走，所以這頁直接看<b>人經過的點</b>：3,460 個公車站牌與 87 個捷運站。</p>
      <h3>口徑</h3>
      <div class="tw"><table><tr><th>名稱</th><th>單位</th><th>來源</th></tr>
      <tr><td>681</td><td>點（位置）</td><td>環保局點位表，2026-09-30 更新</td></tr>
      <tr><td>130 點、940 處</td><td>地點與處數</td><td>環保局景點商圈表，2026-08-18 更新</td></tr>
      <tr><td>806 組、1,612 座</td><td>組、座（一組兩座）</td><td>環保局，自由時報 2026-08-10</td></tr>
      <tr><td>3,460 個站牌</td><td>實體站位，一個地點一個，不分路線（公運處另有「路線站牌」28,826 筆，一根桿子每條路線算一筆）</td><td>公運處站位檔，2026-10-20；2020 年 data.taipei SHP 是 3,407</td></tr>
      <tr><td>1,682 組</td><td>組</td><td>114 年底，中央社 2026-05-11 引環保局</td></tr></table></div>
      <p>點、組、座三者的換算市府沒有公布，這頁不混用：「有公共桶」只看距離，不數個數。</p>
      <h3>它不回答的</h3>
      <p>撤桶對不對。環保局拿不出數字證明撤桶之後家戶垃圾變少，要桶的人也拿不出數字證明撤桶之後路面變髒或抱怨變多；雙方都在用照片和里長的感受說話。所以下一步是先把數字收齊，見「100 天怎麼做」。</p>
    </div>
    <div class="pane" id="p-plan">
      <h3>問題有兩層</h3>
      <p><b>第一層，現有的桶撐不撐得住。</b>每個桶多快滿、清運來不來得及。環保局說非市中心一天收約 4 次、市中心最多 10 次，但沒有公布任何一個桶的滿度。</p>
      <p><b>第二層，桶增減之後的後果。</b>多放桶，誰來清、人力從哪裡來。少了桶，家戶垃圾丟包的開單變多還是變少、病媒與老鼠有沒有變多、路面有沒有變髒、抱怨有沒有變多。現在手上有的數字：丟包開單 109 年 5,598 件、110 年 4,916、111 年 3,669、115 年上半年 1,339（撤桶前就在降，112 到 114 年缺）；環保局每年有滅鼠餌劑標案，2026 年 5 月起十二區滅鼠；陳情「路面清潔」115 年 5 月 1,220 件是高峰，其中 342 件派給水質病媒管制科。沒有的：鼠患通報的地點、路面髒亂的指標。</p>
      <h3>要收的三種數字</h3>
      <div class="tw"><table><tr><th>數字</th><th>怎麼收</th><th>負責</th><th>成本</th></tr>
      <tr><td>1 桶的狀態</td><td><b>QR 通報</b>：每個桶貼一張 QR（LINE 官方帳號或台北通），路人經過看到滿了、溢了、有家戶垃圾、有老鼠，拍照上傳。桶的編號寫在 QR 裡，不用定位、不用打字。清潔隊不記任何東西。撤掉的桶原地也貼一張「這裡原本有桶」，少了桶之後的狀況就有人回報。<b>限制</b>：有人經過又願意拍才有資料，夜間與冷門桶偏少，報的是「有人覺得有問題」，不是滿度本身，照片要有人分類。所以它是第一階段：三個月的通報挑出值得裝感測器或攝影辨識的 50 個點。</td><td>資訊局（帳號與表單）、環保局（貼紙與審照片）</td><td>貼紙 1,612 座加撤桶點，LINE 官方帳號與表單一次開發，審照片的人力</td></tr>
      <tr><td>2 地點</td><td>陳情與丟包開單加座標。QR 通報天生帶地點，但它只收得到桶旁邊的事，撤桶之後的抱怨沒有桶可以貼，而且不是人人會掃。現在撤桶靠里長說哪裡髒，放桶靠議員說哪裡缺，兩邊的證據都沒有地點：陳情只到「某區清潔隊」，開單只有新聞提到的熱點。加了座標，同一個站牌旁邊開了幾張單、收到幾件抱怨，才能逐點決定留或撤。目的是讓撤的理由和放的理由在同一個地點被比較；現在只有撤的那一邊有聲音。</td><td>研考會（1999）、環保局</td><td>欄位改版，無硬體</td></tr>
      <tr><td>3 路面</td><td>固定 60 個點（今年撤桶的 30 個、保留的 30 個），每兩週拍一次 50 公尺路段，分四級。這是「少了桶路面有沒有變髒」唯一的直接證據。誰拍：委外或區公所志工，不加在清潔隊身上。</td><td>環保局發包或區公所</td><td>約一人日跑 30 點（推估）</td></tr></table></div>
      <h3>第四件事：清潔隊的人力對得上桶嗎</h3>
      <p>清潔隊按區編制。各區的人數、清運路線、班次都沒有開放，只有全市約 6,000 人（SEGIS，112 年）。紅燈最多的北投、南港、文山，意思是站牌 100 公尺內沒有公共桶，不代表沒人掃街；但要在那裡放桶，先要知道該區清潔隊一天能多跑幾趟。所需資料：各區清潔隊人數、清運路線與班次。</p>
      <h3>放回去的規則（有了數字之後）</h3>
      <p>比照上海 2023 年導則：公車站原則每站一處、捷運出入口 50 公尺內一處。用這頁的「什麼都沒有」清單當起點；這是量測，不是該放桶的結論，上海導則是可以借的規則，不是依據。每多放一座，成本不是鐵箱（2015、2016 年決標每組 10,800 到 11,340 元），是每天 4 到 10 次清運。</p>
      <h3>所需資料（向市府要的）</h3>
      <ul><li>撤桶紀錄：日期、地點、原因、申請人（里長或評估）</li><li>每個桶的清運排程；滿度由 QR 通報與第二階段感測器補</li><li>陳情與丟包開單的座標</li><li>各區清潔隊人數、清運路線與班次</li><li>捷運站、公園、市場、夜市各機關自設桶的位置（現在沒有開放）</li></ul>
      <h3>成本三列</h3>
      <div class="tw"><table><tr><th>項目</th><th>量級</th><th>依據</th></tr>
      <tr><td>採購</td><td>每組 10,800 到 11,340 元（2015、2016 年決標）</td><td>政府電子採購網，經歐噴採購 API</td></tr>
      <tr><td>清運</td><td>每座每天 4 到 10 次，人時待局處提供</td><td>聯合報 2026-07-21 引環保局</td></tr>
      <tr><td>收數字</td><td>QR 貼紙與帳號一次開發、審照片人力；路面調查每輪數個人日（推估）；感測器或攝影辨識每點硬體與維運，待估</td><td></td></tr></table></div>
    </div>
    </div>
    <div class="pane" id="p-src">
      <h3>資料（全部真實，沒有模擬）</h3>
      <ul>
      <li>公共桶：data.taipei「臺北市行人專用清潔箱」兩個檔，點位表 681 點（2026-09-30）、景點商圈周邊 130 點含處數（2026-08-18）。環保局。</li>
      <li>公車站牌（實體站位，一個地點一個，不分路線）：公運處開放資料容器的站位檔 GetStopLocation，2026-10-20 抓，臺北市里界內 3,460 個。跟 data.taipei 2020 年的站牌 SHP（3,407）比，50 公尺內互相對得到 93%；用 2020 版算，100 公尺內什麼都沒有的是 50%，用 2026 版是 53%。</li>
      <li>捷運站：TDX 捷運車站 API，臺北市 87 站。交通部。</li>
      <li>超商：OpenStreetMap 的 7-Eleven、全家、萊爾富、OK，臺北市 1,566 點。<b>只畫到稅籍登記 2,663 家的約六成</b>，所以「只有超商」偏少、「什麼都沒有」偏多，是上限。© OpenStreetMap contributors，ODbL。</li>
      <li>里界：內政部國土測繪中心村里界 115/08，這頁用簡化版畫底圖。</li>
      <li>撤桶數字：中央社 2026-05-11、聯合報 2026-07-21、自由時報 2026-08-10，皆引環保局。</li></ul>
      <h3>限制</h3>
      <ul>
      <li>距離是直線，不是步行路徑；公園、市場、捷運站內各機關自設的桶不在資料裡。</li>
      <li>景點商圈表只有地點中心座標，一處可能涵蓋好幾個桶。</li>
      <li>超商門口有沒有桶、收不收路人垃圾，沒有資料集，這頁不假設它收。</li>
      <li>站牌是 2026 年 10 月的站位檔；公運處另有「路線站牌」28,826 筆（同一根桿子每條路線算一筆），這頁不用那一層。</li>
      <li>沒有用 YouBike 與任何個資。</li></ul>
      <h3>使用注意</h3>
      <ul>
      <li>結論隨半徑變：50 公尺內什麼都沒有的站牌 73%，100 公尺 50%，200 公尺 29%。引用時一定要寫半徑。</li>
      <li>「什麼都沒有」偏多：直線距離、超商只抓到六成、公園與捷運站內的桶不在資料裡，這三個都讓紅點變多；景點表一個座標代表好幾處，會讓少數站牌被標成有桶，方向相反，影響一兩個百分點。拿去要求某個站牌放桶之前，先去現場看。</li>
      <li>點位表的「點」和景點表的「處」不能相加成桶數，這頁只算距離。</li>
            <li>超商層來自 OpenStreetMap（ODbL）：再發布含超商層的衍生資料要標 © OpenStreetMap contributors 並沿用 ODbL。政府資料依政府資料開放授權條款第 1 版，要標來源。</li>
      <li>這頁只告訴你哪裡沒有桶，不是撤桶對不對的證據。</li>
      <li>沒有個資。不要把這頁的點跟任何含個人資料的檔案合併。</li></ul>
      <h3>怎麼做的</h3>
      <p>Python 標準函式庫算距離（北緯 25.05 度平面近似），Leaflet 1.9.4 畫圖。程式與資料整理用 Claude Code，方法論由 Codex 與另一個 Claude 審過一輪。程式 MIT，資料依各來源授權。</p>
      <p><b>程式、資料與重跑方式：</b><a href="https://github.com/yojuhsu/taipei-bins-2026" target="_blank" rel="noopener">github.com/yojuhsu/taipei-bins-2026</a>（data.json、456 里整合表、計算腳本、README）。</p>
    </div>
  </aside>
</main>
<footer>資料截至 2026-10-20。這是研究示意，不是市府的決策。超商資料 © OpenStreetMap contributors。本作品使用臺北市政府環境保護局、交通局、公共運輸處與內政部國土測繪中心提供之開放資料，依「政府資料開放授權條款－第 1 版」利用；衍生之資料表與程式以 CC BY 4.0 與 MIT 授權釋出。程式與資料：<a href="https://github.com/yojuhsu/taipei-bins-2026" target="_blank" rel="noopener">GitHub</a>。</footer>
<script id="data" type="application/json">__DATA__</script>
<script>
const D=JSON.parse(document.getElementById('data').textContent);
const C={none:'#a63d24',cvs:'#c9961a',pub:'#2f6b3a'};
let R=100, DIST='', ONLY=false;
const map=L.map('map',{preferCanvas:true,zoomSnap:0.25});
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© OpenStreetMap contributors'}).addTo(map);
const status=p=>{const pub=(p.d_bin!=null&&p.d_bin<=R)||(p.d_spot!=null&&p.d_spot<=R);const cv=p.d_cvs!=null&&p.d_cvs<=R;return pub?'pub':(cv?'cvs':'none')};
const fmt=d=>d==null?'無':(d+' 公尺');
const stopLayer=L.layerGroup().addTo(map), binLayer=L.layerGroup().addTo(map), spotLayer=L.layerGroup().addTo(map), cvsLayer=L.layerGroup(), mrtLayer=L.layerGroup().addTo(map);
const markers=[];
D.nodes.forEach(p=>{
  const m=L.circleMarker([p.lat,p.lon],{radius:p.kind==='mrt'?6:4,weight:p.kind==='mrt'?2:0.5,color:p.kind==='mrt'?'#1f4e79':'#fff',fillOpacity:0.9});
  m.bindPopup(()=>`<b>${p.kind==='mrt'?'捷運 ':''}${p.name||'（無名）'}</b><br>${p.dist_name}${p.li}<br>最近公共桶（點位表）：${fmt(p.d_bin)}<br>最近景點桶：${fmt(p.d_spot)}${p.spot_name?'（'+p.spot_name+'，'+p.spot_n+' 處）':''}<br>最近超商（OSM）：${fmt(p.d_cvs)}`);
  markers.push([p,m]);
});
D.bins.forEach(b=>binLayer.addLayer(L.circleMarker([b.lat,b.lon],{radius:3,color:'#1c1b19',fillColor:'#1c1b19',fillOpacity:1,weight:0}).bindPopup('公共桶（點位表）<br>'+b.addr)));
D.spots.forEach(s=>spotLayer.addLayer(L.circleMarker([s.lat,s.lon],{radius:Math.min(3+Math.sqrt(s.n)*1.2,10),color:'#1c1b19',fillColor:'#fff',fillOpacity:0.6,weight:2}).bindPopup('景點商圈桶：'+s.name+'，'+s.n+' 處')));
D.cvs.forEach(c=>cvsLayer.addLayer(L.circleMarker([c.lat,c.lon],{radius:2.5,color:'#8a8578',fillColor:'#8a8578',fillOpacity:0.8,weight:0}).bindPopup('超商（OSM）'+c.brand)));
function render(){
  stopLayer.clearLayers(); const cnt={none:0,cvs:0,pub:0,n:0,mn:0,mnone:0};
  markers.forEach(([p,m])=>{
    if(DIST&&p.dist_name!==DIST) return;
    const s=status(p);
    if(p.kind==='stop'){cnt[s]++;cnt.n++;} else {cnt.mn++; if(s==='none') cnt.mnone++;}
    if(ONLY&&s!=='none') return;
    m.setStyle({fillColor:C[s], color:p.kind==='mrt'?'#1f4e79':'#fff'}); stopLayer.addLayer(m);
  });
  const pc=x=>cnt.n?Math.round(x/cnt.n*100)+'%':'-';
  document.getElementById('kpis').innerHTML=
   `<span class="kpi none"><b>${cnt.none.toLocaleString()}</b>站牌 ${R} m 內什麼都沒有（${pc(cnt.none)}）</span>`+
   `<span class="kpi cvs"><b>${cnt.cvs.toLocaleString()}</b>只有超商（${pc(cnt.cvs)}）</span>`+
   `<span class="kpi pub"><b>${cnt.pub.toLocaleString()}</b>有公共桶（${pc(cnt.pub)}）</span>`+
   `<span class="kpi"><b>${cnt.mnone}</b>／${cnt.mn} 個捷運站什麼都沒有</span>`+
   `<span class="kpi" style="color:var(--mute)">共 ${cnt.n.toLocaleString()} 個站牌${DIST?'（'+DIST+'）':''}</span>`;
}
document.querySelectorAll('#rseg button').forEach(b=>b.onclick=()=>{document.querySelectorAll('#rseg button').forEach(x=>x.classList.remove('on'));b.classList.add('on');R=+b.dataset.r;render();});
const dsel=document.getElementById('dsel'); [...new Set(D.nodes.map(p=>p.dist_name).filter(Boolean))].sort().forEach(d=>{const o=document.createElement('option');o.value=d;o.textContent=d;dsel.appendChild(o)});
dsel.onchange=()=>{DIST=dsel.value;render(); if(DIST){const pts=D.nodes.filter(p=>p.dist_name===DIST);map.fitBounds(pts.map(p=>[p.lat,p.lon]),{padding:[20,20]});}};
document.getElementById('onlynone').onchange=e=>{ONLY=e.target.checked;render();};
document.getElementById('showcvs').onchange=e=>{e.target.checked?cvsLayer.addTo(map):map.removeLayer(cvsLayer);};
document.getElementById('showbins').onchange=e=>{if(e.target.checked){binLayer.addTo(map);spotLayer.addTo(map);}else{map.removeLayer(binLayer);map.removeLayer(spotLayer);}};
document.querySelectorAll('.tabs button').forEach(b=>b.onclick=()=>{document.querySelectorAll('.tabs button').forEach(x=>x.classList.remove('on'));document.querySelectorAll('.pane').forEach(x=>x.classList.remove('on'));b.classList.add('on');document.getElementById('p-'+b.dataset.t).classList.add('on');});
render();
map.fitBounds(D.nodes.map(p=>[p.lat,p.lon]),{padding:[10,10]});
</script>
</body>
</html>
"""
html = html.replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(html)
print("wrote", os.path.join(OUT, "index.html"), len(html))
