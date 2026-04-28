#!/usr/bin/env python3
"""Generate V3 TCM Persona Demo HTML"""

html = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>中医节气签到地图 x AI千人千面 Demo V3</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Helvetica Neue",Arial,sans-serif;background:#F5F0EB;color:#333;display:flex;justify-content:center;padding:20px 0;min-height:100vh}
.mc{width:1260px;max-width:98vw}
.pt{display:flex;justify-content:center;gap:12px;margin-bottom:20px;flex-wrap:wrap}
.ptab{padding:10px 24px;border-radius:24px;border:2px solid #ddd;background:#fff;cursor:pointer;font-size:14px;font-weight:600;transition:all .3s;user-select:none}
.ptab:hover{border-color:#FFC107}
.ptab.active{color:#fff;border-color:transparent;transform:scale(1.05)}
.ptab[data-p=wj].active{background:linear-gradient(135deg,#1a3a0a,#2D5016)}
.ptab[data-p=xl].active{background:linear-gradient(135deg,#7CB342,#AED581);color:#2E5B1A}
.ptab[data-p=lz].active{background:linear-gradient(135deg,#D4A017,#c0392b);color:#fff}
.ca{display:flex;justify-content:center;gap:28px;align-items:flex-start}
.pf{width:390px;min-width:390px;height:844px;border-radius:44px;background:#000;padding:12px;box-shadow:0 20px 60px rgba(0,0,0,.25),inset 0 0 0 2px #333;position:relative;flex-shrink:0}
.pn{width:120px;height:28px;background:#000;border-radius:0 0 16px 16px;position:absolute;top:0;left:50%;transform:translateX(-50%);z-index:100}
.ps{width:100%;height:100%;border-radius:34px;overflow:hidden;position:relative;transition:background .5s}
.psc{width:100%;height:100%;overflow-y:auto;overflow-x:hidden;padding-bottom:120px;scroll-behavior:smooth}
.psc::-webkit-scrollbar{width:3px}
.psc::-webkit-scrollbar-thumb{background:rgba(0,0,0,.15);border-radius:3px}
/* V3: Banner */
.ba{padding:36px 16px 12px;text-align:center;border-radius:0 0 20px 20px;transition:background .5s}
.bti{font-size:22px;font-weight:800;margin-bottom:4px;text-shadow:1px 1px 2px rgba(0,0,0,.15);letter-spacing:1px}
.bsu{font-size:12px;opacity:.85;margin-bottom:6px}
/* V3: Banner badge */
.bbdg{display:inline-block;padding:3px 12px;border-radius:12px;font-size:11px;font-weight:700;margin-top:4px}
.ccrd{background:rgba(255,255,255,.92);border-radius:12px;padding:10px 14px;display:inline-block;box-shadow:0 2px 8px rgba(0,0,0,.08);backdrop-filter:blur(4px);margin-top:8px}
.ccrd .stn{font-size:16px;font-weight:700;color:#5A3A00}
.ccrd .dtd{font-size:11px;color:#888;margin-top:2px}
/* V3: Progress bar */
.pgbar{margin:10px 16px 0;background:rgba(255,255,255,.85);border-radius:10px;padding:8px 12px}
.pgbar-track{height:10px;background:#e0e0e0;border-radius:5px;overflow:visible;position:relative}
.pgbar-fill{height:100%;border-radius:5px;transition:width .6s}
.pgbar-txt{font-size:11px;margin-top:4px;font-weight:600;text-align:center}
.pgbar-break{position:absolute;top:-3px;width:16px;height:16px;background:#e74c3c;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:8px;z-index:2;color:#fff;font-weight:700;border:2px solid #fff}
/* Button */
.ce{margin:10px 16px;background:#fff;border-radius:14px;padding:14px;box-shadow:0 2px 10px rgba(0,0,0,.06)}
.cbtn{width:100%;padding:14px;border:none;border-radius:12px;font-size:16px;font-weight:700;color:#fff;cursor:pointer;transition:all .3s;position:relative;overflow:hidden}
.cbtn:hover{transform:scale(1.02)}
.chnt{font-size:11px;color:#999;text-align:center;margin-top:6px}
/* V3: Button animations */
@keyframes shimmer{0%{left:-100%}100%{left:200%}}
.cbtn-shimmer::after{content:'';position:absolute;top:0;left:-100%;width:50%;height:100%;background:linear-gradient(90deg,transparent,rgba(255,255,255,.35),transparent);animation:shimmer 2.5s infinite}
@keyframes bounce-btn{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}
.cbtn-bounce{animation:bounce-btn 1.5s ease-in-out infinite}
@keyframes red-glow{0%,100%{box-shadow:0 0 8px rgba(231,76,60,.4)}50%{box-shadow:0 0 24px rgba(231,76,60,.8)}}
.cbtn-redglow{animation:red-glow 1.2s ease-in-out infinite}
/* Coupons */
.cr{display:flex;gap:6px;margin:8px 16px 0;align-items:stretch}
.ci{flex:1;border-radius:8px;padding:8px 4px;text-align:center;font-size:10px;font-weight:600;position:relative;overflow:hidden}
.ci .cv{font-size:16px;font-weight:800;display:block}
.ci .ctag{font-size:8px;padding:2px 6px;border-radius:6px;display:inline-block;margin-top:2px}
.ci-big{flex:2}
.ci-big .cv{font-size:28px;line-height:1.3}
.ci-timer{position:absolute;top:0;left:0;right:0;background:rgba(231,76,60,.8);color:#fff;font-size:9px;font-weight:700;padding:2px 0;text-align:center}
/* Map */
.ma{position:relative;width:100%;min-height:960px;padding:20px 0;transition:background 1s}
.msvg{position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:1}
.mdeco{position:absolute;font-size:18px;z-index:0;opacity:.6;pointer-events:none}
.sw{position:absolute;z-index:10}
.pol{padding:6px 6px 20px 6px;border-radius:3px;width:130px;position:relative;transition:all .3s}
.pol:hover{z-index:20}
.pp{width:100%;height:78px;border-radius:2px;display:flex;flex-direction:column;align-items:center;justify-content:center;position:relative;overflow:hidden}
.prab{font-size:22px;position:absolute;bottom:2px;right:4px;opacity:.7}
.pitm{font-size:9px;font-weight:700;position:absolute;bottom:2px;left:4px;opacity:.85;color:#5A3A00}
.ptxt{font-size:10px;font-weight:600;color:#5A3A00;text-align:center;margin-top:3px;line-height:1.3;padding:0 2px}
.psts{font-size:9px;margin-top:1px;text-align:center}
.stag{padding:3px 8px;border-radius:2px;font-size:10px;font-weight:700;box-shadow:1px 1px 3px rgba(0,0,0,.1);white-space:nowrap;position:absolute;z-index:15}
.pini{font-size:16px;position:absolute;z-index:15}
.sbdg{position:absolute;top:-6px;right:-6px;font-size:14px;z-index:20}
/* V3: Card overlays & animations */
.pol-overlay{position:absolute;top:6px;left:6px;right:6px;bottom:20px;background:rgba(255,255,255,.6);display:flex;align-items:center;justify-content:center;font-size:28px;border-radius:2px;z-index:5}
@keyframes breathe{0%,100%{box-shadow:0 0 6px rgba(76,175,80,.3)}50%{box-shadow:0 0 22px rgba(76,175,80,.9)}}
.pol-breathe{animation:breathe 2s ease-in-out infinite;border:2px solid #4CAF50}
@keyframes red-flash{0%,100%{border-color:#e74c3c;box-shadow:0 0 6px rgba(231,76,60,.3)}50%{border-color:#ff6b6b;box-shadow:0 0 16px rgba(231,76,60,.7)}}
.pol-redflash{animation:red-flash 1s ease-in-out infinite;border:2px solid #e74c3c}
.pol-label{position:absolute;bottom:-16px;left:50%;transform:translateX(-50%);padding:2px 8px;border-radius:10px;font-size:9px;font-weight:700;white-space:nowrap;z-index:25}
@keyframes gold-glow{0%,100%{box-shadow:2px 3px 10px rgba(0,0,0,.12)}50%{box-shadow:0 0 16px rgba(201,168,50,.55)}}
.pol-goldglow{animation:gold-glow 2s ease-in-out infinite}
/* Rewards */
.ra{display:flex;justify-content:space-around;padding:14px 12px;background:rgba(255,255,255,.7);margin:8px 12px;border-radius:12px}
.ri{text-align:center;font-size:10px;color:#666;position:relative}
.ric{font-size:22px;display:block}
.ris{font-size:10px;margin-top:2px;font-weight:600}
.ri-bd{width:44px;height:44px;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 4px;border:2px solid #ddd;font-size:20px}
.ri-guide{border:2px dashed #7CB342!important;position:relative}
.ri-guide::after{content:'从这里开始';position:absolute;top:46px;left:50%;transform:translateX(-50%);font-size:8px;color:#7CB342;white-space:nowrap;font-weight:600}
/* V3: Bottom special card */
.bsc{margin:10px 12px;padding:14px 16px;border-radius:12px;font-size:14px;font-weight:700;cursor:pointer;transition:all .3s;text-align:center}
.bsc:hover{transform:scale(1.02)}
/* Push */
.pfl{position:absolute;bottom:54px;left:8px;right:8px;padding:10px 14px;border-radius:12px;font-size:12px;z-index:50;backdrop-filter:blur(6px);box-shadow:0 4px 12px rgba(0,0,0,.3);line-height:1.5}
@keyframes push-pulse{0%,100%{box-shadow:0 4px 12px rgba(0,0,0,.3),0 0 0 0 rgba(231,76,60,0)}50%{box-shadow:0 4px 12px rgba(0,0,0,.3),0 0 0 5px rgba(231,76,60,.5)}}
.pfl-pulse{animation:push-pulse 1.5s ease-in-out infinite}
/* Bottom tabs */
.btabs{position:absolute;bottom:0;left:0;right:0;height:50px;background:#fff;display:flex;border-top:1px solid #eee;z-index:60;border-radius:0 0 34px 34px}
.btab{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:10px;color:#999;gap:2px}
.btab.act{color:#FFC107;font-weight:700}
.btic{font-size:18px}
/* Side panel */
.sp{width:380px;background:#fff;border-radius:16px;padding:20px;box-shadow:0 4px 20px rgba(0,0,0,.06);position:sticky;top:20px;max-height:844px;overflow-y:auto}
.sp::-webkit-scrollbar{width:3px}
.sp::-webkit-scrollbar-thumb{background:rgba(0,0,0,.1);border-radius:3px}
.spn{font-size:18px;font-weight:800;margin-bottom:4px}
.spd{font-size:12px;color:#888;margin-bottom:14px;line-height:1.5}
/* V3: CSS Radar chart */
.radar-wrap{width:200px;height:200px;margin:0 auto 16px;position:relative}
.radar-label{position:absolute;font-size:9px;font-weight:600;color:#666;text-align:center;white-space:nowrap}
.dl{list-style:none}
.dit{padding:8px 0;border-bottom:1px solid #f0f0f0}
.dit:last-child{border-bottom:none}
.dih{display:flex;align-items:center;gap:6px;margin-bottom:3px}
.dib{width:20px;height:20px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:800;color:#fff;flex-shrink:0}
.cdot{width:8px;height:8px;border-radius:50%;display:inline-block;flex-shrink:0;margin-left:auto}
.din{font-size:12px;font-weight:700;color:#555}
.div-v{font-size:13px;font-weight:600;color:#222;margin-left:26px}
.dif{font-size:10px;color:#999;margin-left:26px;margin-top:2px;line-height:1.4}
.sum-card{margin-top:14px;padding:12px;border-radius:10px;font-size:13px;font-weight:700;text-align:center;line-height:1.6}
.pgti{text-align:center;margin-bottom:16px}
.pgti h1{font-size:22px;font-weight:800;color:#333}
.pgti p{font-size:13px;color:#888;margin-top:4px}
.fi{animation:fadeIn .4s ease-out}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.s1{background:linear-gradient(135deg,#E8F5E9,#C8E6C9)}
.s2{background:linear-gradient(135deg,#DCEDC8,#AED581)}
.s3{background:linear-gradient(135deg,#C8E6C9,#81C784)}
.s4{background:linear-gradient(135deg,#A5D6A7,#66BB6A)}
.s5{background:linear-gradient(135deg,#FFF9C4,#FFE082)}
.s6{background:linear-gradient(135deg,#FFE0B2,#FFCC80)}
.s7{background:linear-gradient(135deg,#FFCC80,#FFB74D)}
.s8{background:linear-gradient(135deg,#D7CCC8,#BCAAA4)}
.s9{background:linear-gradient(135deg,#BCAAA4,#A1887F)}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
.blink{animation:blink 1.2s ease-in-out infinite}
@keyframes flash-tag{0%,100%{opacity:1;transform:translateX(-50%) scale(1)}50%{opacity:.7;transform:translateX(-50%) scale(1.05)}}
</style>
</head>
<body>
<div class="mc">
  <div class="pgti"><h1>🏥 中医节气签到地图 × AI千人千面</h1><p>同一个签到活动，三种用户看到完全不同的内容 · V3 视觉差异版</p></div>
  <div class="pt">
    <div class="ptab active" data-p="wj" onclick="sw('wj')">🧘 养生达人·王姐</div>
    <div class="ptab" data-p="xl" onclick="sw('xl')">🌱 尝鲜小白·小林</div>
    <div class="ptab" data-p="lz" onclick="sw('lz')">😴 沉睡用户·老张</div>
  </div>
  <div class="ca">
    <div class="pf"><div class="pn"></div>
      <div class="ps" id="ps">
        <div class="psc" id="psc">
          <div class="ba" id="ba">
            <div class="bti" id="bti"></div>
            <div class="bsu" id="bsu"></div>
            <div class="bbdg" id="bbdg"></div>
            <br>
            <div class="ccrd"><div class="stn">谷雨 · 四月二十日</div><div class="dtd">农历三月初四 · 2026年</div></div>
          </div>
          <div class="pgbar" id="pgbar"></div>
          <div class="ce"><button class="cbtn" id="cbtn"></button><div class="chnt" id="chnt"></div></div>
          <div class="cr" id="cpr"></div>
          <div class="ma" id="ma">
            <svg class="msvg" id="msvg" viewBox="0 0 358 960" preserveAspectRatio="xMidYMid meet"></svg>
            <div class="mdeco" style="top:60px;left:20px">🌸</div><div class="mdeco" style="top:180px;right:25px">🌸</div>
            <div class="mdeco" style="top:340px;left:15px">🌿</div><div class="mdeco" style="top:500px;right:20px">☀️</div>
            <div class="mdeco" style="top:620px;left:25px">🍂</div><div class="mdeco" style="top:740px;right:18px">🌰</div>
            <div class="mdeco" style="top:850px;left:30px">❄️</div>
            <div id="sc"></div>
          </div>
          <div class="ra" id="ra"></div>
          <div id="bscArea"></div>
        </div>
        <div class="pfl" id="pfl"></div>
        <div class="btabs">
          <div class="btab act"><span class="btic">📅</span>谷雨签到</div>
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
var P=[
  {x:210,y:30,r:-3,s:'s1'},{x:70,y:130,r:5,s:'s2'},{x:210,y:230,r:-4,s:'s3'},
  {x:70,y:330,r:6,s:'s4'},{x:210,y:430,r:-5,s:'s5'},{x:70,y:530,r:4,s:'s6'},
  {x:210,y:630,r:-6,s:'s7'},{x:70,y:730,r:5,s:'s8'},{x:210,y:830,r:-3,s:'s9'}
];
var T=[
  {n:'春分',d:'3.20-4.3'},{n:'谷雨',d:'4.13-4.27'},{n:'小满',d:'5.20-6.4'},
  {n:'夏至',d:'6.21-7.5'},{n:'三伏',d:'7.15-8.24'},{n:'秋分',d:'9.22-10.7'},
  {n:'霜降',d:'10.23-11.6'},{n:'小雪',d:'11.22-12.6'},{n:'冬至',d:'12.21-1.5'}
];

/* ===== V3 PERSONA DATA ===== */
var D={
wj:{
  nm:'\u{1f9d8} 养生达人·王姐',ds:'35岁 | 高消费复购 | 月均¥800+ | 已签5天',
  pageBg:'#FDF6EC',mapBg:'linear-gradient(180deg,#f5f0e0 0%,#ede5d0 50%,#e8ddc4 100%)',
  bg:'linear-gradient(135deg,#1a3a0a,#2D5016)',fc:'#f5e6b8',
  cardBorder:'2px solid #c9a832',cardBg:'#fffef8',tagBg:'#FFF3B0',tagColor:'#6B4F00',
  ti:'累计签到 领大奖',su:'专属养生定制方案',
  badge:'🏆 VIP养生家',badgeBg:'linear-gradient(135deg,#c9a832,#e6c84a)',badgeColor:'#3a2600',
  bb:'linear-gradient(135deg,#c9a832,#e6c84a)',bx:'继续打卡',bc:'#3a2600',btnClass:'cbtn-shimmer',
  ht:'再签2天解锁神秘大礼🎁',htHtml:false,
  pgPct:71,pgFill:'linear-gradient(90deg,#c9a832,#e6c84a)',pgText:'5/7 即将达成终极奖励！',pgBreakPct:-1,pgBlink:false,
  cp:[{a:'¥40',c:'满420减',tag:'VIP专享',big:0},{a:'¥27',c:'满287减',tag:'VIP专享',big:0},{a:'¥18',c:'满188减',tag:'VIP专享',big:0}],
  cpBd:'2px solid #c9a832',cpBg:'linear-gradient(135deg,#FFFDE7,#FFF8E1)',cpCo:'#8B6914',cpTm:0,
  st:[
    {t:'推拿精选¥388',s:'✅已领',u:1,it:'🐰推拿'},{t:'艾灸月卡¥1280',s:'✅已领',u:1,it:'🐰艾灸'},
    {t:'体质调理¥568',s:'✅已领',u:1,it:'🐰调理'},{t:'药膳食补¥428',s:'✅已领',u:1,it:'🐰药膳'},
    {t:'三伏贴¥328',s:'✅已领',u:1,it:'🐰三伏'},{t:'秋季润肺¥298',s:'即将解锁',u:0},
    {t:'膏方进补¥488',s:'即将解锁',u:0},{t:'温泉养生¥668',s:'即将解锁',u:0},
    {t:'冬令进补¥888',s:'即将解锁',u:0}
  ],
  rc:'#c9a832',rw2:3.5,rd:'',ro:.85,brk:-1,
  pu:'🧘 王姐，明天小满节气开启，VIP养生方案已备好',
  puBg:'rgba(0,0,0,.88)',puCo:'#f5e6b8',puBd:'1px solid #c9a832',puPl:0,
  rw:[{i:'💰',l:'三次签到礼',s:'✅',c:'#4CAF50',bd:'#c9a832'},{i:'🧧',l:'五次签到礼',s:'✅',c:'#4CAF50',bd:'#c9a832'},{i:'🎫',l:'七次签到礼',s:'🔜即将达成',c:'#FF9800',bd:'#FF9800'},{i:'🎁',l:'神秘大礼',s:'🔜即将达成',c:'#FF9800',bd:'#FF9800'}],
  rwG:-1,
  bsc:'📊 您的年度养生报告 →',bscBg:'#fffef8',bscBd:'2px solid #c9a832',bscCo:'#5A3A00',bscTm:0,
  sum:'高价值用户 → 高门槛高回报，VIP留存',sumBg:'linear-gradient(135deg,#1a3a0a,#2D5016)',sumCo:'#f5e6b8',
  rad:[95,85,71,80,90],radCo:'#2D5016',radFi:'rgba(45,80,22,.25)',
  dm:[
    {id:'❶',n:'用户分层',v:'高价值复购用户',d:'小林：新客探索期 / 老张：沉睡召回期',co:'#2D5016',dt:'#1a3a0a'},
    {id:'❷',n:'消费能力',v:'月均¥800+，客单价¥400+',d:'小林：预算敏感¥30内 / 老张：中等¥100',co:'#2D5016',dt:'#1a3a0a'},
    {id:'❸',n:'签到进度',v:'5/7天（即将达成终极奖励）',d:'小林：0/7 / 老张：2/7断签',co:'#2D5016',dt:'#1a3a0a'},
    {id:'❹',n:'券面额策略',v:'¥40/¥27/¥18 高门槛高面额',d:'小林：¥5/¥3/免单 / 老张：¥15/¥25/¥10',co:'#2D5016',dt:'#1a3a0a'},
    {id:'❺',n:'商品推荐',v:'高端养生套餐 ¥328~¥888',d:'小林：入门¥9.9~69.9 / 老张：中端¥39~299',co:'#2D5016',dt:'#1a3a0a'},
    {id:'❻',n:'话术调性',v:'VIP尊享、专属定制',d:'小林：新手友好 / 老张：限时回归',co:'#2D5016',dt:'#1a3a0a'},
    {id:'❼',n:'紧迫感策略',v:'进度激励（再签2天）',d:'小林：首签翻倍 / 老张：48h倒计时',co:'#2D5016',dt:'#1a3a0a'},
    {id:'❽',n:'Push策略',v:'VIP方案预告',d:'小林：体验券 / 老张：过期提醒',co:'#2D5016',dt:'#1a3a0a'}
  ]
},
xl:{
  nm:'🌱 尝鲜小白·小林',ds:'22岁 | 首次参与 | 低频新客',
  pageBg:'#f0faf0',mapBg:'linear-gradient(180deg,#eef9ee 0%,#e5f5e5 50%,#ddf0dd 100%)',
  bg:'linear-gradient(135deg,#81C784,#b2fab4)',fc:'#1b4d1b',
  cardBorder:'2px solid #f8bbd0',cardBg:'#fff8fc