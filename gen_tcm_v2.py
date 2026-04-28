#!/usr/bin/env python3
"""Generate TCM Solar Term Check-in Map × AI Persona Demo V2"""

html = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>中医节气签到地图 × AI千人千面 Demo V2</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Helvetica Neue',Arial,sans-serif;background:#F5F0EB;color:#333;display:flex;justify-content:center;padding:20px 0;min-height:100vh}
.mc{width:1200px;max-width:98vw}
.pt{display:flex;justify-content:center;gap:12px;margin-bottom:20px;flex-wrap:wrap}
.ptab{padding:10px 24px;border-radius:24px;border:2px solid #ddd;background:#fff;cursor:pointer;font-size:14px;font-weight:600;transition:all .3s;user-select:none}
.ptab:hover{border-color:#FFC107}
.ptab.active{color:#fff;border-color:transparent;transform:scale(1.05)}
.ptab[data-p="wj"].active{background:linear-gradient(135deg,#2D5016,#4A7C2E)}
.ptab[data-p="xl"].active{background:linear-gradient(135deg,#7CB342,#AED581);color:#2E5B1A}
.ptab[data-p="lz"].active{background:linear-gradient(135deg,#D4A017,#F0C040);color:#5A3A00}
.ca{display:flex;justify-content:center;gap:28px;align-items:flex-start}
.pf{width:390px;min-width:390px;height:844px;border-radius:44px;background:#000;padding:12px;box-shadow:0 20px 60px rgba(0,0,0,.25),inset 0 0 0 2px #333;position:relative;flex-shrink:0}
.pn{width:120px;height:28px;background:#000;border-radius:0 0 16px 16px;position:absolute;top:0;left:50%;transform:translateX(-50%);z-index:100}
.ps{width:100%;height:100%;border-radius:34px;overflow:hidden;position:relative;background:#FDF6EC}
.psc{width:100%;height:100%;overflow-y:auto;overflow-x:hidden;padding-bottom:120px;scroll-behavior:smooth}
.psc::-webkit-scrollbar{width:3px}
.psc::-webkit-scrollbar-thumb{background:rgba(0,0,0,.15);border-radius:3px}
.ba{padding:36px 16px 12px;text-align:center;border-radius:0 0 20px 20px;transition:background .5s}
.bt{font-size:22px;font-weight:800;margin-bottom:4px;text-shadow:1px 1px 2px rgba(0,0,0,.1);letter-spacing:1px}
.bs{font-size:12px;opacity:.85;margin-bottom:10px}
.cc{background:rgba(255,255,255,.92);border-radius:12px;padding:10px 14px;display:inline-block;box-shadow:0 2px 8px rgba(0,0,0,.08);backdrop-filter:blur(4px)}
.cc .st{font-size:16px;font-weight:700;color:#5A3A00}
.cc .dd{font-size:11px;color:#888;margin-top:2px}
.ce{margin:12px 16px;background:#fff;border-radius:14px;padding:14px;box-shadow:0 2px 10px rgba(0,0,0,.06)}
.cb{width:100%;padding:12px;border:none;border-radius:10px;font-size:16px;font-weight:700;color:#fff;cursor:pointer;transition:all .3s}
.cb:hover{transform:scale(1.02)}
.cb:active{transform:scale(.98)}
.ch{font-size:11px;color:#999;text-align:center;margin-top:6px}
.cr{display:flex;gap:6px;margin:8px 16px 0;overflow-x:auto}
.ci{flex:1;min-width:0;background:linear-gradient(135deg,#FFF8E1,#FFF3C4);border:1px dashed #E6C200;border-radius:8px;padding:8px 4px;text-align:center;font-size:10px;color:#8B6914;font-weight:600}
.ci .cv{font-size:16px;color:#D4A017;font-weight:800}
.ma{position:relative;width:100%;min-height:960px;padding:20px 0;background:linear-gradient(180deg,#FDF8EE 0%,#FBF4E4 30%,#F8EFDA 60%,#F5E8CE 100%)}
.msvg{position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:1}
.md{position:absolute;font-size:18px;z-index:0;opacity:.6;pointer-events:none}
.sw{position:absolute;z-index:10}
.pol{background:#fff;padding:6px 6px 20px 6px;box-shadow:2px 3px 10px rgba(0,0,0,.14);border-radius:3px;width:130px;position:relative;transition:transform .3s,box-shadow .3s}
.pol:hover{box-shadow:3px 5px 16px rgba(0,0,0,.22);z-index:20}
.pp{width:100%;height:78px;border-radius:2px;display:flex;flex-direction:column;align-items:center;justify-content:center;position:relative;overflow:hidden}
.pr{font-size:26px;position:absolute;bottom:1px;right:2px;opacity:.7}
.ptx{font-size:10px;font-weight:600;color:#5A3A00;text-align:center;margin-top:3px;line-height:1.3;padding:0 2px}
.pst{font-size:9px;margin-top:1px;text-align:center}
.stag{background:#FFF3B0;padding:3px 8px;border-radius:2px;font-size:10px;font-weight:700;color:#6B4F00;box-shadow:1px 1px 3px rgba(0,0,0,.1);white-space:nowrap;position:absolute;z-index:15}
.pin{font-size:16px;position:absolute;z-index:15;filter:drop-shadow(0 1px 2px rgba(0,0,0,.2))}
.sbdg{position:absolute;top:-6px;right:-6px;font-size:14px;z-index:20}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
.blink{animation:blink 1.2s ease-in-out infinite}
@keyframes glow{0%,100%{box-shadow:2px 3px 10px rgba(0,0,0,.14)}50%{box-shadow:2px 3px 16px rgba(255,140,0,.5)}}
.glowc{animation:glow 1.5s ease-in-out infinite}
.ra{display:flex;justify-content:space-around;padding:14px 12px;background:rgba(255,255,255,.7);margin:8px 12px;border-radius:12px}
.ri{text-align:center;font-size:10px;color:#666}
.ric{font-size:24px;display:block;margin-bottom:2px}
.ris{font-size:11px;margin-top:2px;font-weight:600}
.pfl{position:absolute;bottom:54px;left:8px;right:8px;background:rgba(0,0,0,.82);color:#fff;padding:10px 14px;border-radius:12px;font-size:12px;z-index:50;backdrop-filter:blur(6px);box-shadow:0 4px 12px rgba(0,0,0,.3);line-height:1.5}
.btabs{position:absolute;bottom:0;left:0;right:0;height:50px;background:#fff;display:flex;border-top:1px solid #eee;z-index:60;border-radius:0 0 34px 34px}
.btab{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:10px;color:#999;gap:2px}
.btab.active{color:#FFC107;font-weight:700}
.btic{font-size:18px}
.sp{width:340px;background:#fff;border-radius:16px;padding:20px;box-shadow:0 4px 20px rgba(0,0,0,.06);position:sticky;top:20px;max-height:844px;overflow-y:auto;transition:opacity .4s}
.sp::-webkit-scrollbar{width:3px}
.sp::-webkit-scrollbar-thumb{background:rgba(0,0,0,.1);border-radius:3px}
.spn{font-size:18px;font-weight:800;margin-bottom:4px}
.spd{font-size:12px;color:#888;margin-bottom:14px;line-height:1.5}
.dl{list-style:none}
.di{padding:10px 0;border-bottom:1px solid #f0f0f0}
.di:last-child{border-bottom:none}
.dh{display:flex;align-items:center;gap:6px;margin-bottom:4px}
.db{width:20px;height:20px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:800;color:#fff;flex-shrink:0}
.dn{font-size:12px;font-weight:700;color:#555}
.dv{font-size:13px;font-weight:600;color:#222;margin-left:26px}
.df{font-size:10px;color:#999;margin-left:26px;margin-top:2px;line-height:1.4}
.pgt{text-align:center;margin-bottom:16px}
.pgt h1{font-size:22px;font-weight:800;color:#333}
.pgt p{font-size:13px;color:#888;margin-top:4px}
.fi{animation:fadeIn .4s ease-out}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.ss1{background:linear-gradient(135deg,#E8F5E9,#C8E6C9)}
.ss2{background:linear-gradient(135deg,#DCEDC8,#AED581)}
.ss3{background:linear-gradient(135deg,#C8E6C9,#81C784)}
.ss4{background:linear-gradient(135deg,#A5D6A7,#66BB6A)}
.ss5{background:linear-gradient(135deg,#FFF9C4,#FFE082)}
.ss6{background:linear-gradient(135deg,#FFE0B2,#FFCC80)}
.ss7{background:linear-gradient(135deg,#FFCC80,#FFB74D)}
.ss8{background:linear-gradient(135deg,#D7CCC8,#BCAAA4)}
.ss9{background:linear-gradient(135deg,#BCAAA4,#A1887F)}
.pol.lk .pp{filter:grayscale(.6) brightness(.92)}
.pol.lk{opacity:.7}
</style>
</head>
<body>
<div class="mc">
  <div class="pgt"><h1>🏥 中医节气签到地图 × AI千人千面</h1><p>同一个签到活动，三种用户看到完全不同的内容</p></div>
  <div class="pt">
    <div class="ptab active" data-p="wj" onclick="sw('wj')">🧘 养生达人·王姐</div>
    <div class="ptab" data-p="xl" onclick="sw('xl')">🌱 尝鲜小白·小林</div>
    <div class="ptab" data-p="lz" onclick="sw('lz')">😴 沉睡用户·老张</div>
  </div>
  <div class="ca">
    <div class="pf"><div class="pn"></div>
      <div class="ps">
        <div class="psc" id="psc">
          <div class="ba" id="ba"><div class="bt" id="bti"></div><div class="bs" id="bsu"></div><div class="cc"><div class="st">谷雨 · 四月二十日</div><div class="dd">农历三月初四 · 2026年</div></div></div>
          <div class="ce"><button class="cb" id="cbtn"></button><div class="ch" id="chnt"></div></div>
          <div class="cr" id="cpr"></div>
          <div class="ma" id="ma">
            <svg class="msvg" id="msvg" viewBox="0 0 358 960" preserveAspectRatio="xMidYMid meet"><path id="rp" fill="none" stroke="#8B6914" stroke-width="2.5" stroke-dasharray="8 6" opacity="0.45"/></svg>
            <div class="md" style="top:60px;left:20px">🌸</div><div class="md" style="top:180px;right:25px">🌸</div>
            <div class="md" style="top:340px;left:15px">🌿</div><div class="md" style="top:500px;right:20px">☀️</div>
            <div class="md" style="top:620px;left:25px">🍂</div><div class="md" style="top:740px;right:18px">🌰</div>
            <div class="md" style="top:850px;left:30px">❄️</div><div class="md" style="top:260px;right:40px;font-size:14px">🌸</div>
            <div class="md" style="top:440px;left:40px;font-size:14px">🌰</div>
            <div id="sc"></div>
          </div>
          <div class="ra" id="ra"></div>
        </div>
        <div class="pfl" id="pfl"></div>
        <div class="btabs">
          <div class="btab active"><span class="btic">📅</span>谷雨签到</div>
          <div class="btab"><span class="btic">🏠</span>主会场</div>
          <div class="btab"><span class="btic">🌿</span>中医方剂</div>
          <div class="btab"><span class="btic">✨</span>祛痘</div>
        </div>
      </div>
    </div>
    <div class="sp" id="sp"></div>
  </div>
</div>
<script>
// Station positions (S-shape snake)
var P=[{x:210,y:30,r:-3,tp:'l',s:'ss1'},{x:70,y:130,r:5,tp:'r',s:'ss2'},{x:210,y:230,r:-4,tp:'l',s:'ss3'},{x:70,y:330,r:6,tp:'r',s:'ss4'},{x:210,y:430,r:-5,tp:'l',s:'ss5'},{x:70,y:530,r:4,tp:'r',s:'ss6'},{x:210,y:630,r:-6,tp:'l',s:'ss7'},{x:70,y:730,r:5,tp:'r',s:'ss8'},{x:210,y:830,r:-3,tp:'l',s:'ss9'}];
// Solar terms
var T=[{n:'春分',d:'3.20-4.3'},{n:'谷雨',d:'4.13-4.27'},{n:'小满',d:'5.20-6.4'},{n:'夏至',d:'6.21-7.5'},{n:'三伏',d:'7.15-8.24'},{n:'秋分',d:'9.22-10.7'},{n:'霜降',d:'10.23-11.6'},{n:'小雪',d:'11.22-12.6'},{n:'冬至',d:'12.21-1.5'}];

// Data
var D={
wj:{
  nm:'🧘 养生达人·王姐',ds:'35岁 | 高消费复购 | 月均¥800+ | 已签5天',
  bg:'linear-gradient(135deg,#2D5016,#4A7C2E)',fc:'#fff',
  ti:'累计签到 领大奖',su:'专属养生定制方案',
  bb:'linear-gradient(135deg,#2D5016,#4A7C2E)',bx:'继续打卡',bc:'#fff',
  ht:'再签2天解锁神秘大礼🎁',
  cp:[{a:'¥40',c:'满420减'},{a:'¥27',c:'满287减'},{a:'¥18',c:'满188减'}],
  st:[{t:'推拿精选¥388',s:'✅已领',u:1},{t:'艾灸月卡¥1280',s:'✅已领',u:1},{t:'体质调理¥568',s:'✅已领',u:1},{t:'药膳食补¥428',s:'✅已领',u:1},{t:'三伏贴套餐¥328',s:'✅已领',u:1},{t:'秋季润肺方¥298',s:'🔒待解锁',u:0},{t:'膏方进补¥488',s:'🔒待解锁',u:0},{t:'温泉养生¥668',s:'🔒待解锁',u:0},{t:'冬令进补¥888',s:'🔒待解锁',u:0}],
  pu:'🧘 王姐，明天小满节气开启，VIP养生方案已备好',
  rw:[{i:'💰',l:'三次签到礼',s:'✅',c:'#4CAF50'},{i:'🧧',l:'五次签到礼',s:'✅',c:'#4CAF50'},{i:'🎫',l:'七次签到礼',s:'🔜',c:'#FF9800'},{i:'🎁',l:'神秘大礼',s:'🔜',c:'#FF9800'}],
  sp:{},
  dm:[
    {id:'❶',n:'用户分层',v:'高价值复购用户',d:'小林：新客探索期 / 老张：沉睡召回期',co:'#2D5016'},
    {id:'❷',n:'消费能力',v:'月均¥800+，客单价¥400+',d:'小林：预算敏感¥30内 / 老张：中等¥100左右',co:'#2D5016'},
    {id:'❸',n:'签到进度',v:'5/7天（即将达成终极奖励）',d:'小林：0/7未开始 / 老张：2/7断签',co:'#2D5016'},
    {id:'❹',n:'券面额策略',v:'¥40/¥27/¥18（高门槛高面额）',d:'小林：¥5/¥3/免单 / 老张：¥15/¥25/¥10回归',co:'#2D5016'},
    {id:'❺',n:'商品推荐',v:'高端养生套餐（¥328~¥888）',d:'小林：入门体验¥9.9~¥69.9 / 老张：中端¥39~¥299',co:'#2D5016'},
    {id:'❻',n:'话术调性',v:'VIP尊享、专属定制',d:'小林：首次体验、新手友好 / 老张：好久不见、限时回归',co:'#2D5016'},
    {id:'❼',n:'紧迫感策略',v:'进度激励（再签2天）',d:'小林：首签翻倍 / 老张：48h倒计时',co:'#2D5016'},
    {id:'❽',n:'Push策略',v:'VIP方案预告',d:'小林：体验券利益点 / 老张：过期提醒+限时优惠',co:'#2D5016'}
  ]
},
xl:{
  nm:'🌱 尝鲜小白·小林',ds:'22岁 | 首次参与 | 低频新客',
  bg:'linear-gradient(135deg,#7CB342,#AED581)',fc:'#2E5B1A',
  ti:'累计签到 领大奖',su:'你的第一次节气养生之旅✨',
  bb:'linear-gradient(135deg,#7CB342,#AED581)',bx:'立即签到',bc:'#2E5B1A',
  ht:'首签奖励翻倍✨',
  cp:[{a:'¥5',c:'满29减'},{a:'¥3',c:'满19减'},{a:'免单',c:'体验券'}],
  st:[{t:'肩颈放松¥29.9',s:'💡推荐首选',u:0},{t:'足浴体验¥19.9',s:'🔒',u:0},{t:'养生茶饮¥9.9',s:'🔒',u:0},{t:'刮痧体验¥39.9',s:'🔒',u:0},{t:'艾灸入门¥49.9',s:'🔒',u:0},{t:'拔罐体验¥29.9',s:'🔒',u:0},{t:'泡脚套餐¥25.9',s:'🔒',u:0},{t:'暖宫调理¥59.9',s:'🔒',u:0},{t:'冬季暖身套餐¥69.9',s:'🔒',u:0}],
  pu:'🌿 小林，完成首次签到即得体验券，29.9元享肩颈放松~',
  rw:[{i:'💰',l:'三次签到礼',s:'🔒',c:'#999'},{i:'🧧',l:'五次签到礼',s:'🔒',c:'#999'},{i:'🎫',l:'七次签到礼',s:'🔒',c:'#999'},{i:'🎁',l:'神秘大礼',s:'🔒',c:'#999'}],
  sp:{0:{lb:'从这里开始！',bk:1}},
  dm:[
    {id:'❶',n:'用户分层',v:'新客探索期',d:'王姐：高价值复购 / 老张：沉睡召回期',co:'#7CB342'},
    {id:'❷',n:'消费能力',v:'预算敏感，¥30以内',d:'王姐：月均¥800+ / 老张：中等¥100左右',co:'#7CB342'},
    {id:'❸',n:'签到进度',v:'0/7天（全新开始）',d:'王姐：5/7天 / 老张：2/7断签',co:'#7CB342'},
    {id:'❹',n:'券面额策略',v:'¥5/¥3/免单（低门槛引流）',d:'王姐：¥40/¥27/¥18 / 老张：¥15/¥25/¥10',co:'#7CB342'},
    {id:'❺',n:'商品推荐',v:'入门体验（¥9.9~¥69.9）',d:'王姐：高端¥328~¥888 / 老张：中端¥39~¥299',co:'#7CB342'},
    {id:'❻',n:'话术调性',v:'首次体验、新手友好、轻松尝鲜',d:'王姐：VIP尊享 / 老张：好久不见、限时',co:'#7CB342'},
    {id:'❼',n:'紧迫感策略',v:'首签翻倍奖励',d:'王姐：再签2天 / 老张：48h倒计时',co:'#7CB342'},
    {id:'❽',n:'Push策略',v:'体验券+低价利益点',d:'王姐：VIP方案预告 / 老张：过期+限时优惠',co:'#7CB342'}
  ]
},
lz:{
  nm:'😴 沉睡用户·老张',ds:'40岁 | 去年参与今年断签 | 30天未回访',
  bg:'linear-gradient(135deg,#D4A017,#F0C040)',fc:'#5A3A00',
  ti:'累计签到 领大奖',su:'好久不见，专属回归礼等你💪',
  bb:'linear-gradient(135deg,#D4A017,#F0C040)',bx:'回归签到',bc:'#5A3A00',
  ht:'断签不清零，继续累计！限时48h',
  cp:[{a:'¥15',c:'满99回归专享'},{a:'¥25',c:'满199限时48h'},{a:'¥10',c:'无门槛回归礼'}],
  st:[{t:'推拿5折¥99',s:'✅已领',u:1},{t:'足浴回归价¥39',s:'✅已领',u:1},{t:'回归补签¥1',s:'⚠️断签！',u:0,w:1},{t:'中药泡脚¥59',s:'🔒',u:0},{t:'刮痧套餐¥79',s:'🔒',u:0},{t:'推拿月卡¥199',s:'🔒',u:0},{t:'秋冬进补¥129',s:'🔒',u:0},{t:'药膳套餐¥149',s:'🔒',u:0},{t:'年度回归大礼包¥299',s:'🔒',u:0}],
  pu:'⏰ 老张，您的回归礼即将过期！48h内签到领¥25专享券',
  rw:[{i:'💰',l:'三次签到礼',s:'🔜差1次',c:'#FF9800'},{i:'🧧',l:'五次签到礼',s:'🔒',c:'#999'},{i:'🎫',l:'七次签到礼',s:'🔒',c:'#999'},{i:'🎁',l:'神秘大礼',s:'🔒',c:'#999'}],
  sp:{2:{lb:'⚠️ 断签！补签¥1',gw:1}},
  dm:[
    {id:'❶',n:'用户分层',v:'沉睡召回期（30天未回访）',d:'王姐：高价值复购 / 小林：新客探索期',co:'#D4A017'},
    {id:'❷',n:'消费能力',v:'中等消费，客单价¥100左右',d:'王姐：月均¥800+ / 小林：¥30以内',co:'#D4A017'},
    {id:'❸',n:'签到进度',v:'2/7天（去年遗留+断签）',d:'王姐：5/7天 / 小林：0/7天',co:'#D4A017'},
    {id:'❹',n:'券面额策略',v:'¥15/¥25/¥10（回归专享+限时）',d:'王姐：¥40/¥27/¥18 / 小林：¥5/¥3/免单',co:'#D4A017'},
    {id:'❺',n:'商品推荐',v:'中端回归价（¥39~¥299）',d:'王姐：高端¥328~¥888 / 小林：入门¥9.9~¥69.9',co:'#D4A017'},
    {id:'❻',n:'话术调性',v:'好久不见、专属回归、限时48h',d:'王姐：VIP尊享 / 小林：首次体验、新手友好',co:'#D4A017'},
    {id:'❼',n:'紧迫感策略',v:'48h倒计时+断签不清零',d:'王姐：再签2天 / 小林：首签翻倍',co:'#D4A017'},
    {id:'❽',n:'Push策略',v:'过期提醒+限时优惠逼单',d:'王