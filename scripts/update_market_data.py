<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>SIGNAL — Market Intelligence</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#07090f;--bg2:#0e1420;--bg3:#141d2e;
  --border:#1c2a3e;--border2:#243349;
  --text:#e8edf5;--text2:#8a9ab5;--text3:#3d5068;
  --cyan:#1fd4ec;--green:#3dd68c;--red:#f06b6b;
  --amber:#f5a623;--purple:#9b7ff5;
  --mono:"IBM Plex Mono",monospace;--sans:"Inter",sans-serif;
}
body{background:var(--bg);color:var(--text);font-family:var(--sans);min-height:100vh;overflow-x:hidden}
button{cursor:pointer;font-family:var(--sans)}
a{color:inherit;text-decoration:none}
/* NAV */
nav{position:sticky;top:0;z-index:999;background:rgba(7,9,15,.97);border-bottom:1px solid var(--border);padding:0 18px;height:52px;display:flex;align-items:center;gap:12px}
.brand{display:flex;align-items:center;gap:9px;flex-shrink:0;margin-right:6px}
.dot{width:8px;height:8px;border-radius:50%;background:var(--cyan);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(31,212,236,.5)}50%{box-shadow:0 0 0 6px rgba(31,212,236,0)}}
.brand-name{font-weight:700;font-size:14px;letter-spacing:.06em;color:#fff}
.brand-date{font-size:9px;color:var(--text3);font-family:var(--mono);margin-top:1px}
.tabs{display:flex;gap:1px;flex:1}
.tab{background:none;border:none;color:var(--text3);font-size:10px;font-family:var(--mono);padding:5px 10px;border-radius:4px;letter-spacing:.05em;transition:all .15s;white-space:nowrap}
.tab:hover{color:var(--text2);background:var(--bg2)}
.tab.on{color:var(--cyan);background:rgba(31,212,236,.08)}
.nav-right{display:flex;align-items:center;gap:8px;flex-shrink:0}
.bell-btn{background:none;border:1px solid var(--border);color:var(--text3);font-size:14px;width:30px;height:26px;border-radius:5px;display:flex;align-items:center;justify-content:center;transition:all .2s}
.bell-btn.on{border-color:var(--amber);color:var(--amber);background:rgba(245,166,35,.08)}
.bell-btn:hover{border-color:var(--border2);color:var(--text2)}
.mkt-badge{font-family:var(--mono);font-size:10px;padding:3px 9px;border-radius:4px;letter-spacing:.07em;font-weight:500;border:1px solid transparent;white-space:nowrap}
.mkt-open{color:var(--green);background:rgba(61,214,140,.08);border-color:rgba(61,214,140,.25)}
.mkt-pre{color:var(--amber);background:rgba(245,166,35,.08);border-color:rgba(245,166,35,.25)}
.mkt-closed{color:var(--red);background:rgba(240,107,107,.07);border-color:rgba(240,107,107,.2)}
.clock{font-family:var(--mono);font-size:11px;color:var(--text3);white-space:nowrap}
/* STATUS BAR */
.sbar{background:var(--bg2);border-bottom:1px solid var(--border);padding:4px 18px;display:flex;align-items:center;gap:10px;font-family:var(--mono);font-size:10px;color:var(--text3)}
.sdot{width:6px;height:6px;border-radius:50%;flex-shrink:0}
.s-loading{background:var(--amber);animation:blink 1s infinite}
.s-live{background:var(--green)}
.s-error{background:var(--red)}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
/* TICKER */
.ticker{background:var(--bg2);border-bottom:1px solid var(--border);overflow:hidden;padding:5px 0;position:relative}
.ticker::before,.ticker::after{content:'';position:absolute;top:0;bottom:0;width:40px;z-index:2;pointer-events:none}
.ticker::before{left:0;background:linear-gradient(to right,var(--bg2),transparent)}
.ticker::after{right:0;background:linear-gradient(to left,var(--bg2),transparent)}
.ticker-inner{display:flex;white-space:nowrap;animation:scroll 65s linear infinite}
.ticker-inner:hover{animation-play-state:paused}
@keyframes scroll{from{transform:translateX(0)}to{transform:translateX(-50%)}}
.tick{display:inline-flex;align-items:center;gap:6px;padding:0 18px;font-family:var(--mono);font-size:11px;border-right:1px solid var(--border)}
.ts{color:var(--text3);font-size:10px}.tv{color:var(--text);font-weight:500}
.up{color:var(--green)}.dn{color:var(--red)}.fl{color:var(--text3)}
/* LAYOUT */
.wrap{display:grid;grid-template-columns:182px 1fr;min-height:calc(100vh - 108px)}
.side{border-right:1px solid var(--border);position:sticky;top:52px;height:calc(100vh - 52px);overflow-y:auto;padding:12px 0}
.side-sec{margin-bottom:16px}
.side-lbl{font-family:var(--mono);font-size:9px;color:var(--text3);letter-spacing:.14em;padding:0 12px 5px;text-transform:uppercase}
.side-item{display:flex;justify-content:space-between;align-items:center;padding:5px 12px;font-size:12px;cursor:pointer;transition:background .12s}
.side-item:hover{background:var(--bg2)}
.side-name{color:var(--text2)}.side-val{font-family:var(--mono);font-size:11px}
/* CONTENT */
.content{padding:16px 20px;overflow-x:hidden}
.page{display:none}.page.on{display:block}
.hdr{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;flex-wrap:wrap;gap:7px}
.hdr-title{font-family:var(--mono);font-size:10px;color:var(--text3);letter-spacing:.14em;text-transform:uppercase}
.hdr-title::before{content:"— "}
.src-badge{font-family:var(--mono);font-size:9px;color:var(--cyan);background:rgba(31,212,236,.07);border:1px solid rgba(31,212,236,.18);padding:2px 8px;border-radius:3px}
/* CARDS */
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:8px;margin-bottom:16px}
.card{background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:11px 13px}
.c-lbl{font-family:var(--mono);font-size:9px;color:var(--text3);letter-spacing:.09em;text-transform:uppercase;margin-bottom:6px}
.c-val{font-family:var(--mono);font-size:19px;font-weight:500;line-height:1;margin-bottom:3px}
.c-chg{font-family:var(--mono);font-size:11px;margin-bottom:2px}
.c-src{font-size:9px;color:var(--text3);margin-top:4px;font-family:var(--mono);opacity:.6}
/* SECTORS */
.sec-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(175px,1fr));gap:8px;margin-bottom:16px}
.sec-card{background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:10px 13px;border-left:3px solid transparent}
.sec-card.bull{border-left-color:var(--green)}.sec-card.bear{border-left-color:var(--red)}.sec-card.neut{border-left-color:var(--amber)}
.sec-name{font-size:12px;font-weight:600;color:var(--text);margin-bottom:2px}
.sec-etf{font-family:var(--mono);font-size:9px;color:var(--text3);margin-bottom:4px}
.sec-perf{font-family:var(--mono);font-size:17px;font-weight:500;margin-bottom:5px}
.sec-bar-bg{height:3px;background:var(--border);border-radius:2px;margin-bottom:5px;overflow:hidden}
.sec-bar-fill{height:100%;border-radius:2px;transition:width .6s}
.sec-sig{font-family:var(--mono);font-size:9px;letter-spacing:.07em}
.sec-sig.bull{color:var(--green)}.sec-sig.bear{color:var(--red)}.sec-sig.neut{color:var(--amber)}
/* RATES */
.yield-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(90px,1fr));gap:8px;margin-bottom:16px}
.yc{background:var(--bg2);border:1px solid var(--border);border-radius:6px;padding:9px 11px}
.yc-t{font-family:var(--mono);font-size:9px;color:var(--text3);margin-bottom:4px;letter-spacing:.08em}
.yc-v{font-family:var(--mono);font-size:16px;font-weight:500}
.curve-wrap{background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:14px;margin-bottom:16px}
/* HOURS */
.hours-hero{background:var(--bg2);border:1px solid var(--border);border-radius:10px;padding:18px 20px;margin-bottom:14px;display:flex;gap:22px;align-items:center;flex-wrap:wrap}
.hours-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(155px,1fr));gap:8px;margin-bottom:16px}
.hours-card{background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:11px 13px}
.h-session{font-family:var(--mono);font-size:9px;color:var(--text3);letter-spacing:.1em;margin-bottom:4px}
.h-time{font-family:var(--mono);font-size:13px;font-weight:500;color:var(--text);margin-bottom:2px}
.h-tz{font-size:10px;color:var(--text3);margin-bottom:5px}
.h-status{font-family:var(--mono);font-size:10px}
/* NEWS */
.news-filters{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px}
.nf-btn{background:none;border:1px solid var(--border);color:var(--text3);font-size:10px;font-family:var(--mono);padding:4px 11px;border-radius:20px;transition:all .15s;letter-spacing:.05em}
.nf-btn:hover,.nf-btn.on{background:rgba(31,212,236,.07);border-color:var(--cyan);color:var(--cyan)}
.news-list{display:flex;flex-direction:column;gap:8px;margin-bottom:16px}
.news-item{background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:12px 14px;display:flex;gap:10px;transition:border-color .12s}
.news-item:hover{border-color:var(--border2)}
.ntag{font-family:var(--mono);font-size:9px;padding:2px 7px;border-radius:3px;white-space:nowrap;height:fit-content;flex-shrink:0;margin-top:2px;letter-spacing:.04em}
.ntag.mac{background:rgba(31,212,236,.08);color:var(--cyan);border:1px solid rgba(31,212,236,.2)}
.ntag.geo{background:rgba(155,127,245,.08);color:var(--purple);border:1px solid rgba(155,127,245,.2)}
.ntag.ai{background:rgba(61,214,140,.08);color:var(--green);border:1px solid rgba(61,214,140,.2)}
.ntag.eqt{background:rgba(240,107,107,.08);color:var(--red);border:1px solid rgba(240,107,107,.2)}
.ntag.cmd{background:rgba(245,166,35,.08);color:var(--amber);border:1px solid rgba(245,166,35,.2)}
.n-hl{font-size:13px;font-weight:600;color:var(--text);line-height:1.4;margin-bottom:3px}
.n-hl a:hover{color:var(--cyan)}
.n-meta{font-family:var(--mono);font-size:10px;color:var(--text3)}
.n-loading{text-align:center;padding:30px;color:var(--text3);font-family:var(--mono);font-size:12px}
/* AI INTEL */
.ai-summary-box{background:var(--bg2);border:1px solid var(--border);border-radius:10px;padding:16px 18px;margin-bottom:16px}
.ai-summary-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;flex-wrap:wrap;gap:8px}
.ai-badge{font-family:var(--mono);font-size:9px;color:var(--purple);background:rgba(155,127,245,.09);border:1px solid rgba(155,127,245,.25);padding:2px 9px;border-radius:3px;letter-spacing:.06em}
.ai-body{font-size:13px;color:var(--text2);line-height:1.8}
.ai-body b{color:var(--text)}
.ai-body .ai-para{margin-bottom:10px}
.gen-btn{background:rgba(155,127,245,.1);border:1px solid rgba(155,127,245,.3);color:var(--purple);font-size:12px;font-weight:600;padding:7px 15px;border-radius:7px;transition:all .15s;display:flex;align-items:center;gap:7px}
.gen-btn:hover{background:rgba(155,127,245,.18)}
.gen-btn:disabled{opacity:.4;cursor:not-allowed}
.ibuys-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(175px,1fr));gap:8px;margin-bottom:16px}
.ibuy-card{background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:11px 13px;border-top:3px solid transparent}
.ibuy-card.strong-buy{border-top-color:var(--green)}
.ibuy-card.buy{border-top-color:var(--cyan)}
.ibuy-sym{font-family:var(--mono);font-size:15px;font-weight:700;color:var(--text);margin-bottom:2px}
.ibuy-name{font-size:10px;color:var(--text3);margin-bottom:7px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ibuy-price{font-family:var(--mono);font-size:13px;font-weight:500;margin-bottom:2px}
.ibuy-rating{font-family:var(--mono);font-size:9px;padding:2px 7px;border-radius:3px;display:inline-block;margin-bottom:4px}
.ibuy-rating.strong-buy{background:rgba(61,214,140,.1);color:var(--green);border:1px solid rgba(61,214,140,.2)}
.ibuy-rating.buy{background:rgba(31,212,236,.08);color:var(--cyan);border:1px solid rgba(31,212,236,.2)}
.ibuy-target{font-size:10px;color:var(--text3)}
/* INTRADAY CHART */
.intra-wrap{background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:14px;margin-bottom:16px}
.intra-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;flex-wrap:wrap;gap:6px}
.intra-sym{font-size:13px;font-weight:700;color:var(--text)}
.intra-meta{font-family:var(--mono);font-size:11px}
/* ECONOMIC CALENDAR */
.eco-cal{display:flex;flex-direction:column;gap:6px;margin-bottom:16px}
.eco-item{background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:9px 14px;display:flex;align-items:center;gap:11px}
.eco-item.today{border-color:var(--amber);background:rgba(245,166,35,.04)}
.eco-item.past{opacity:.45}
.eco-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.eco-dot.high{background:var(--red)}.eco-dot.med{background:var(--amber)}.eco-dot.low{background:var(--cyan)}
.eco-date{font-family:var(--mono);font-size:10px;color:var(--text3);flex-shrink:0;width:72px}
.eco-name{font-size:12px;font-weight:600;color:var(--text);flex:1;line-height:1.3}
.eco-tag{font-family:var(--mono);font-size:9px;padding:2px 7px;border-radius:3px;flex-shrink:0;border:1px solid}
.eco-tag.fed{color:var(--purple);border-color:rgba(155,127,245,.3);background:rgba(155,127,245,.08)}
.eco-tag.jobs{color:var(--green);border-color:rgba(61,214,140,.3);background:rgba(61,214,140,.08)}
.eco-tag.inflation{color:var(--red);border-color:rgba(240,107,107,.3);background:rgba(240,107,107,.08)}
.eco-tag.growth{color:var(--cyan);border-color:rgba(31,212,236,.3);background:rgba(31,212,236,.08)}
.eco-tag.other{color:var(--text2);border-color:var(--border2);background:none}
.eco-when{font-family:var(--mono);font-size:10px;color:var(--text3);flex-shrink:0;min-width:58px;text-align:right}
/* TOAST */
.toast{position:fixed;top:64px;right:18px;z-index:9999;background:var(--bg2);border-radius:9px;padding:13px 16px;font-family:var(--mono);font-size:11px;min-width:220px;max-width:300px;box-shadow:0 4px 24px rgba(0,0,0,.5);animation:tIn .3s ease;pointer-events:none}
@keyframes tIn{from{opacity:0;transform:translateY(-10px)}to{opacity:1;transform:translateY(0)}}
.toast-out{animation:tOut .4s ease forwards}
@keyframes tOut{to{opacity:0;transform:translateY(-8px)}}
/* INFO BOX */
.info-box{background:rgba(31,212,236,.04);border:1px solid rgba(31,212,236,.12);border-radius:8px;padding:11px 14px;margin-bottom:14px;font-size:12px;color:var(--text2);line-height:1.7}
.info-box b{color:var(--cyan)}
/* SPIN */
.spin{display:inline-block;animation:sp 1s linear infinite}
@keyframes sp{to{transform:rotate(360deg)}}
footer{border-top:1px solid var(--border);padding:8px 20px;font-family:var(--mono);font-size:9px;color:var(--text3);display:flex;justify-content:space-between;align-items:center}
@media(max-width:820px){
  .wrap{grid-template-columns:1fr}
  .side{display:none}
  .tab{padding:5px 7px;font-size:9px}
  .clock{display:none}
}
</style>
</head>
<body>

<nav>
  <div class="brand">
    <div class="dot"></div>
    <div>
      <div class="brand-name">SIGNAL</div>
      <div class="brand-date" id="nav-date">—</div>
    </div>
  </div>
  <div class="tabs">
    <button class="tab on" onclick="go('macro',this)">MACRO</button>
    <button class="tab" onclick="go('sectors',this)">SECTORS</button>
    <button class="tab" onclick="go('rates',this)">RATES</button>
    <button class="tab" onclick="go('hours',this)">HOURS</button>
    <button class="tab" onclick="go('news',this)">NEWS</button>
    <button class="tab" onclick="go('ai',this)">AI INTEL</button>
  </div>
  <div class="nav-right">
    <button class="bell-btn" id="bell-btn" onclick="toggleBell()" title="Market open/close bell">🔔</button>
    <div class="mkt-badge mkt-closed" id="mkt-status">—</div>
    <div class="clock" id="clk">--:--:-- ET</div>
  </div>
</nav>

<div class="sbar">
  <div class="sdot s-loading" id="sdot"></div>
  <span id="smsg">Connecting to market data…</span>
  <span style="margin-left:auto" id="supd"></span>
</div>

<div class="ticker">
  <div class="ticker-inner" id="tkr">
    <span class="tick"><span class="ts">SIGNAL</span><span class="tv" style="color:var(--text3)">Loading…</span></span>
  </div>
</div>

<div class="wrap">
  <aside class="side">
    <div class="side-sec">
      <div class="side-lbl">Indices</div>
      <div class="side-item" onclick="go('macro',null)"><span class="side-name">S&amp;P 500</span><span class="side-val" id="s-spy">—</span></div>
      <div class="side-item" onclick="go('macro',null)"><span class="side-name">Nasdaq</span><span class="side-val" id="s-qqq">—</span></div>
      <div class="side-item" onclick="go('macro',null)"><span class="side-name">Dow Jones</span><span class="side-val" id="s-dia">—</span></div>
      <div class="side-item" onclick="go('macro',null)"><span class="side-name">Russell 2K</span><span class="side-val" id="s-iwm">—</span></div>
    </div>
    <div class="side-sec">
      <div class="side-lbl">Yields</div>
      <div class="side-item" onclick="go('rates',null)"><span class="side-name">10Y</span><span class="side-val fl" id="s-10y">—</span></div>
      <div class="side-item" onclick="go('rates',null)"><span class="side-name">30Y</span><span class="side-val fl" id="s-30y">—</span></div>
      <div class="side-item" onclick="go('rates',null)"><span class="side-name">5Y</span><span class="side-val fl" id="s-5y">—</span></div>
    </div>
    <div class="side-sec">
      <div class="side-lbl">Commodities</div>
      <div class="side-item"><span class="side-name">Gold</span><span class="side-val" id="s-gld">—</span></div>
      <div class="side-item"><span class="side-name">Oil</span><span class="side-val" id="s-uso">—</span></div>
    </div>
    <div class="side-sec">
      <div class="side-lbl">Volatility</div>
      <div class="side-item"><span class="side-name">VIX</span><span class="side-val" id="s-vix">—</span></div>
    </div>
  </aside>

  <main class="content">

    <!-- ═══ MACRO ═══ -->
    <div class="page on" id="pg-macro">
      <div class="hdr"><div class="hdr-title">Macro Dashboard · <span id="hdr-date">—</span></div><div class="src-badge">YAHOO FINANCE · LIVE</div></div>
      <div class="cards">
        <div class="card"><div class="c-lbl">S&amp;P 500 (SPY)</div><div class="c-val" id="m-spy-p">—</div><div class="c-chg" id="m-spy-c">—</div><div class="c-src">Yahoo Finance</div></div>
        <div class="card"><div class="c-lbl">Nasdaq (QQQ)</div><div class="c-val" id="m-qqq-p">—</div><div class="c-chg" id="m-qqq-c">—</div><div class="c-src">Yahoo Finance</div></div>
        <div class="card"><div class="c-lbl">Dow Jones (DIA)</div><div class="c-val" id="m-dia-p">—</div><div class="c-chg" id="m-dia-c">—</div><div class="c-src">Yahoo Finance</div></div>
        <div class="card"><div class="c-lbl">Russell 2K (IWM)</div><div class="c-val" id="m-iwm-p">—</div><div class="c-chg" id="m-iwm-c">—</div><div class="c-src">Yahoo Finance</div></div>
        <div class="card"><div class="c-lbl">Gold (GLD)</div><div class="c-val" id="m-gld-p">—</div><div class="c-chg" id="m-gld-c">—</div><div class="c-src">Yahoo Finance</div></div>
        <div class="card"><div class="c-lbl">Oil (USO)</div><div class="c-val" id="m-uso-p">—</div><div class="c-chg" id="m-uso-c">—</div><div class="c-src">Yahoo Finance</div></div>
        <div class="card"><div class="c-lbl">VIX</div><div class="c-val" id="m-vix-p">—</div><div class="c-chg" id="m-vix-c">—</div><div class="c-src">CBOE via Yahoo</div></div>
        <div class="card"><div class="c-lbl">10Y Treasury</div><div class="c-val fl" id="m-10y-p">—</div><div class="c-chg fl" id="m-10y-c">—</div><div class="c-src">US Treasury</div></div>
        <div class="card"><div class="c-lbl">5Y Treasury</div><div class="c-val fl" id="m-5y-p">—</div><div class="c-chg fl" id="m-5y-c">—</div><div class="c-src">US Treasury</div></div>
        <div class="card"><div class="c-lbl">30Y Treasury</div><div class="c-val fl" id="m-30y-p">—</div><div class="c-chg fl" id="m-30y-c">—</div><div class="c-src">US Treasury</div></div>
        <div class="card"><div class="c-lbl">US Dollar (DXY)</div><div class="c-val" id="m-dxy-p">—</div><div class="c-chg" id="m-dxy-c">—</div><div class="c-src">Dollar Index Futures</div></div>
        <div class="card"><div class="c-lbl">Bitcoin (BTC)</div><div class="c-val" id="m-btc-p">—</div><div class="c-chg" id="m-btc-c">—</div><div class="c-src">Yahoo Finance</div></div>
        <div class="card"><div class="c-lbl">Ethereum (ETH)</div><div class="c-val" id="m-eth-p">—</div><div class="c-chg" id="m-eth-c">—</div><div class="c-src">Yahoo Finance</div></div>
      </div>

      <!-- SPY Intraday Chart -->
      <div class="hdr"><div class="hdr-title">SPY — Today's Price Action</div><div class="src-badge" id="intra-badge">5-MIN · LIVE</div></div>
      <div class="intra-wrap">
        <div class="intra-top">
          <div><span class="intra-sym">SPY</span><span style="font-size:10px;color:var(--text3);font-family:var(--mono);margin-left:10px">S&amp;P 500 ETF · Intraday</span></div>
          <div class="intra-meta"><span class="up" id="intra-price">—</span>&nbsp;<span style="color:var(--text3)" id="intra-chg">—</span></div>
        </div>
        <canvas id="intradayChart" height="130"></canvas>
        <div style="font-family:var(--mono);font-size:9px;color:var(--text3);margin-top:8px;text-align:right" id="intra-status">Loading intraday data…</div>
      </div>

      <!-- Economic Calendar -->
      <div class="hdr"><div class="hdr-title">Upcoming Economic Events</div><div class="src-badge">HIGH-IMPACT · AUTO-CALC</div></div>
      <div class="eco-cal" id="eco-cal"><div style="font-family:var(--mono);font-size:11px;color:var(--text3);padding:10px">Loading calendar…</div></div>
    </div>

    <!-- ═══ SECTORS ═══ -->
    <div class="page" id="pg-sectors">
      <div class="hdr"><div class="hdr-title">Sector Performance · <span id="sec-date">—</span></div><div class="src-badge">ETFs · LIVE</div></div>
      <div class="sec-grid" id="sec-grid"><div class="sec-card neut"><div class="sec-name">Loading…</div></div></div>
    </div>

    <!-- ═══ RATES ═══ -->
    <div class="page" id="pg-rates">
      <div class="hdr"><div class="hdr-title">Fixed Income &amp; Yield Curve</div><div class="src-badge">US TREASURY · LIVE</div></div>
      <div class="yield-grid">
        <div class="yc"><div class="yc-t">13W</div><div class="yc-v fl" id="r-13w">—</div></div>
        <div class="yc"><div class="yc-t">5Y</div><div class="yc-v fl" id="r-5y">—</div></div>
        <div class="yc"><div class="yc-t">10Y</div><div class="yc-v fl" id="r-10y">—</div></div>
        <div class="yc"><div class="yc-t">30Y</div><div class="yc-v fl" id="r-30y">—</div></div>
      </div>
      <div class="curve-wrap"><canvas id="curveChart" height="150"></canvas></div>
      <div class="cards">
        <div class="card"><div class="c-lbl">10Y – 5Y Spread</div><div class="c-val" id="r-sp1">—</div><div class="c-chg fl" id="r-sp1l">—</div></div>
        <div class="card"><div class="c-lbl">10Y – 13W Spread</div><div class="c-val" id="r-sp2">—</div><div class="c-chg fl">Short vs Long</div></div>
      </div>
    </div>

    <!-- ═══ HOURS ═══ -->
    <div class="page" id="pg-hours">
      <div class="hdr"><div class="hdr-title">Market Sessions &amp; Hours</div><div class="src-badge" id="hbadge" style="color:var(--text3)">CHECKING</div></div>
      <div class="hours-hero">
        <div>
          <div style="font-family:var(--mono);font-size:10px;color:var(--text3);margin-bottom:5px">EASTERN TIME</div>
          <div style="font-family:var(--mono);font-size:30px;font-weight:500" id="big-clk">--:--:--</div>
        </div>
        <div style="flex:1;min-width:180px">
          <div style="font-family:var(--mono);font-size:10px;color:var(--text3);margin-bottom:5px">STATUS</div>
          <div style="font-family:var(--mono);font-size:22px;font-weight:700" id="big-status">—</div>
          <div style="font-family:var(--mono);font-size:10px;color:var(--text3);margin-top:4px" id="big-sub">—</div>
        </div>
        <div>
          <div style="font-family:var(--mono);font-size:10px;color:var(--text3);margin-bottom:5px">TODAY</div>
          <div style="font-family:var(--mono);font-size:14px;font-weight:600" id="big-date">—</div>
          <div style="font-family:var(--mono);font-size:10px;color:var(--text3);margin-top:3px" id="big-day">—</div>
        </div>
      </div>
      <div class="hours-grid">
        <div class="hours-card"><div class="h-session">NYSE / NASDAQ</div><div class="h-time">9:30 AM – 4:00 PM</div><div class="h-tz">ET · Mon–Fri</div><div class="h-status" id="hs-nyse">—</div></div>
        <div class="hours-card"><div class="h-session">Pre-Market</div><div class="h-time">4:00 AM – 9:30 AM</div><div class="h-tz">ET · Mon–Fri</div><div class="h-status" id="hs-pre">—</div></div>
        <div class="hours-card"><div class="h-session">After Hours</div><div class="h-time">4:00 PM – 8:00 PM</div><div class="h-tz">ET · Mon–Fri</div><div class="h-status" id="hs-post">—</div></div>
        <div class="hours-card"><div class="h-session">London (LSE)</div><div class="h-time">8:00 AM – 4:30 PM</div><div class="h-tz">GMT · Mon–Fri</div><div class="h-status" id="hs-lse">—</div></div>
        <div class="hours-card"><div class="h-session">Frankfurt (XETRA)</div><div class="h-time">9:00 AM – 5:30 PM</div><div class="h-tz">CET · Mon–Fri</div><div class="h-status" id="hs-xetra">—</div></div>
        <div class="hours-card"><div class="h-session">Tokyo (TSE)</div><div class="h-time">9:00 AM – 3:00 PM</div><div class="h-tz">JST · Mon–Fri</div><div class="h-status" id="hs-tse">—</div></div>
      </div>
      <div class="info-box"><b>Note:</b> Major US holidays cause early closes or full closures not shown here. Always confirm with your broker.</div>
    </div>

    <!-- ═══ NEWS ═══ -->
    <div class="page" id="pg-news">
      <div class="hdr"><div class="hdr-title">Live News · <span id="news-date">—</span></div><div class="src-badge">RSS · MULTI-SOURCE</div></div>
      <div class="news-filters">
        <button class="nf-btn on" onclick="filterNews('all',this)">ALL</button>
        <button class="nf-btn" onclick="filterNews('mac',this)">MACRO</button>
        <button class="nf-btn" onclick="filterNews('ai',this)">AI</button>
        <button class="nf-btn" onclick="filterNews('geo',this)">GEO-POLITICAL</button>
        <button class="nf-btn" onclick="filterNews('eqt',this)">MARKETS</button>
        <button class="nf-btn" onclick="filterNews('cmd',this)">COMMODITIES</button>
        <button class="nf-btn" style="margin-left:auto;border-color:var(--border2)" onclick="loadNews()">↻ Refresh</button>
      </div>
      <div class="news-list" id="news-list"><div class="n-loading"><span class="spin">◌</span>&nbsp; Fetching live news…</div></div>
    </div>

    <!-- ═══ AI INTEL ═══ -->
    <div class="page" id="pg-ai">
      <div class="hdr"><div class="hdr-title">AI Market Intelligence · <span id="ai-date">—</span></div><div class="src-badge">AI + LIVE DATA</div></div>

      <div class="ai-summary-box">
        <div class="ai-summary-top">
          <div class="hdr-title" style="margin:0">Market Summary</div>
          <div style="display:flex;gap:8px;align-items:center">
            <span class="ai-badge">POLLINATIONS AI · FREE</span>
            <button class="gen-btn" id="gen-btn" onclick="generateSummary()"><span id="gen-icon">✦</span> Generate Summary</button>
          </div>
        </div>
        <div class="ai-body" id="ai-out">
          <div style="color:var(--text3);font-size:12px;font-family:var(--mono)">Click "Generate Summary" to get an AI analysis of today's live market data — sentiment, key movers, macro risks, and what to watch.</div>
        </div>
      </div>

      <div class="hdr" style="margin-top:4px"><div class="hdr-title">Strong Buys · Top Institutional Ratings</div><div class="src-badge">ANALYST CONSENSUS</div></div>
      <div class="info-box"><b>Methodology:</b> Scanning top S&P 500 constituents for "Strong Buy" or "Buy" consensus from analyst communities. Data sourced from Yahoo Finance. Not investment advice — always do your own research.</div>
      <div class="ibuys-grid" id="ibuys-grid">
        <div class="ibuy-card"><div class="ibuy-sym" style="color:var(--text3)">Loading analyst data…</div></div>
      </div>
      <div style="text-align:center;margin-bottom:12px">
        <button class="gen-btn" onclick="loadIBuys()"><span>↻</span> Refresh Ratings</button>
      </div>
    </div>

  </main>
</div>

<footer>
  <div>SIGNAL · Live data · Not investment advice</div>
  <div id="ft"></div>
</footer>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script>
// ═══════════════════════════════════════════════
// GLOBALS
// ═══════════════════════════════════════════════
var PROXIES = ['', 'https://corsproxy.io/?url=', 'https://api.allorigins.win/raw?url='];
var liveQuotes = {};
var prevMarketStatus = null;
var bellEnabled = false;
var audioCtx = null;
var curveChartInst = null;
var allNewsItems = [];
var currentFilter = 'all';

var MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
var DAYS = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];

// ═══════════════════════════════════════════════
// UTILITIES
// ═══════════════════════════════════════════════
function getET() { return new Date(new Date().toLocaleString('en-US',{timeZone:'America/New_York'})); }

function todayStr() {
  var d = getET();
  return MONTHS[d.getMonth()] + ' ' + d.getDate() + ', ' + d.getFullYear();
}

function fmtP(v) {
  if (v==null||isNaN(v)) return '—';
  return v>=1000 ? v.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2}) : v.toFixed(2);
}
function fmtPct(v) { return v==null ? '—' : (v>=0?'+':'')+v.toFixed(2)+'%'; }
function fmtY(v)   { return v==null ? '—' : v.toFixed(2)+'%'; }
function cls(v)    { return v>=0?'up':'dn'; }

function setEl(id, text, className) {
  var el = document.getElementById(id);
  if (!el) return;
  if (text != null) el.textContent = text;
  if (className != null) el.className = className;
}

// ═══════════════════════════════════════════════
// NAVIGATION
// ═══════════════════════════════════════════════
function go(id, btn) {
  document.querySelectorAll('.page').forEach(function(p){p.classList.remove('on');});
  document.getElementById('pg-'+id).classList.add('on');
  if (btn) {
    document.querySelectorAll('.tab').forEach(function(t){t.classList.remove('on');});
    btn.classList.add('on');
  }
  if (id === 'news' && allNewsItems.length === 0) loadNews();
  if (id === 'ai') { updateAIDates(); loadIBuys(); }
}

// ═══════════════════════════════════════════════
// MARKET STATUS
// ═══════════════════════════════════════════════
function getMarketStatus() {
  var et = getET();
  var h=et.getHours(), m=et.getMinutes(), d=et.getDay();
  var t = h*60+m;
  var wd = d>=1&&d<=5;
  if (!wd)          return {s:'closed',    l:'CLOSED',      sub:'Weekend — reopens Mon 9:30 AM ET',             c:'var(--red)',   cls:'mkt-closed'};
  if (t<4*60)       return {s:'closed',    l:'CLOSED',      sub:'Pre-market opens at 4:00 AM ET',               c:'var(--red)',   cls:'mkt-closed'};
  if (t<9*60+30)    return {s:'premarket', l:'PRE-MARKET',  sub:'Regular session opens at 9:30 AM ET',          c:'var(--amber)', cls:'mkt-pre'};
  if (t<16*60)      return {s:'open',      l:'MARKET OPEN', sub:'Regular session closes at 4:00 PM ET',         c:'var(--green)', cls:'mkt-open'};
  if (t<20*60)      return {s:'afterhours',l:'AFTER HOURS', sub:'Extended trading until 8:00 PM ET',            c:'var(--amber)', cls:'mkt-pre'};
  return             {s:'closed',    l:'CLOSED',      sub:'Pre-market reopens tomorrow at 4:00 AM ET',    c:'var(--red)',   cls:'mkt-closed'};
}

function sessionOpen(tz, oh, om, ch, cm) {
  var d = new Date(new Date().toLocaleString('en-US',{timeZone:tz}));
  var wd = d.getDay()>=1&&d.getDay()<=5;
  if (!wd) return false;
  var t = d.getHours()*60+d.getMinutes();
  return t>=oh*60+om && t<ch*60+cm;
}

function openBadge(open) {
  return open
    ? '<span style="color:var(--green);font-family:var(--mono);font-size:10px">● OPEN</span>'
    : '<span style="color:var(--red);font-family:var(--mono);font-size:10px">● CLOSED</span>';
}

function updateClock() {
  var et = getET();
  var h = String(et.getHours()).padStart(2,'0');
  var m = String(et.getMinutes()).padStart(2,'0');
  var s = String(et.getSeconds()).padStart(2,'0');
  var t = h+':'+m+':'+s;
  var ms = getMarketStatus();
  var ds = todayStr();

  // Nav
  setEl('clk', t+' ET');
  setEl('nav-date', ds);
  var b = document.getElementById('mkt-status');
  if (b) { b.textContent=ms.l; b.className='mkt-badge '+ms.cls; }

  // Header dates
  ['hdr-date','sec-date','news-date','ai-date'].forEach(function(id){
    var el=document.getElementById(id); if(el) el.textContent=ds;
  });

  // Hours page
  setEl('big-clk', t);
  var bs = document.getElementById('big-status');
  if (bs) { bs.textContent=ms.l; bs.style.color=ms.c; }
  setEl('big-sub', ms.sub);
  setEl('big-date', ds);
  setEl('big-day', DAYS[et.getDay()]);
  setEl('hbadge', ms.l);
  var hb = document.getElementById('hbadge'); if(hb) hb.style.color=ms.c;

  // Session badges
  var els = [
    ['hs-nyse',  ms.s==='open'],
    ['hs-pre',   ms.s==='premarket'],
    ['hs-post',  ms.s==='afterhours'],
    ['hs-lse',   sessionOpen('Europe/London', 8,0,16,30)],
    ['hs-xetra', sessionOpen('Europe/Berlin', 9,0,17,30)],
    ['hs-tse',   sessionOpen('Asia/Tokyo',    9,0,15,0)]
  ];
  els.forEach(function(e){ var el=document.getElementById(e[0]); if(el) el.innerHTML=openBadge(e[1]); });

  setEl('ft', t+' ET · '+ds);

  // Bell on status change
  if (prevMarketStatus && prevMarketStatus !== ms.s) {
    if (ms.s === 'open') {
      toast('🔔 NYSE / NASDAQ opening bell', 'var(--green)');
      if (bellEnabled) ringBell('open');
    } else if (prevMarketStatus === 'open') {
      toast('🔔 Market closed — 4:00 PM ET', 'var(--red)');
      if (bellEnabled) ringBell('close');
    } else if (ms.s === 'premarket') {
      toast('Pre-market session started — 4:00 AM ET', 'var(--amber)');
      if (bellEnabled) ringBell('pre');
    }
  }
  prevMarketStatus = ms.s;
}

// ═══════════════════════════════════════════════
// BELL SOUND (Web Audio API)
// ═══════════════════════════════════════════════
function toggleBell() {
  bellEnabled = !bellEnabled;
  var btn = document.getElementById('bell-btn');
  btn.classList.toggle('on', bellEnabled);
  if (bellEnabled) {
    // Init AudioContext on user gesture (required by browsers)
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (audioCtx.state === 'suspended') audioCtx.resume();
    ringBell('test');
    toast('🔔 Bell enabled — will ring at market open & close', 'var(--amber)');
  } else {
    toast('Bell muted', 'var(--text3)');
  }
}

function synthBell(ctx, freq, start, dur, vol) {
  // Realistic bell = fundamental + partials with fast attack, exponential decay
  var partials = [1, 2.756, 5.404, 8.933];
  var decMult  = [1,   0.6,   0.35,  0.2];
  partials.forEach(function(p, i) {
    var osc  = ctx.createOscillator();
    var gain = ctx.createGain();
    osc.connect(gain); gain.connect(ctx.destination);
    osc.type = 'sine';
    osc.frequency.value = freq * p;
    gain.gain.setValueAtTime(0, start);
    gain.gain.linearRampToValueAtTime(vol/(i+1), start+0.002);
    gain.gain.exponentialRampToValueAtTime(0.0001, start + dur * decMult[i]);
    osc.start(start);
    osc.stop(start + dur * decMult[i] + 0.05);
  });
}

function ringBell(type) {
  try {
    var ctx = audioCtx || new (window.AudioContext || window.webkitAudioContext)();
    if (!audioCtx) audioCtx = ctx;
    if (ctx.state === 'suspended') ctx.resume();
    var now = ctx.currentTime;
    if (type === 'open') {
      // Three ascending rings — NYSE opening bell
      [0, 0.45, 0.9].forEach(function(t, i) { synthBell(ctx, 523+i*30, now+t, 2.5, 0.28); });
    } else if (type === 'close') {
      // Three rings at same pitch — closing bell
      [0, 0.42, 0.84].forEach(function(t) { synthBell(ctx, 440, now+t, 3, 0.22); });
    } else if (type === 'pre') {
      synthBell(ctx, 660, now, 1.5, 0.18);
    } else {
      // Test: single soft ring
      synthBell(ctx, 880, now, 1.8, 0.2);
    }
  } catch(e) {}
}

// ═══════════════════════════════════════════════
// TOAST
// ═══════════════════════════════════════════════
function toast(msg, color) {
  var el = document.createElement('div');
  el.className = 'toast';
  el.style.borderColor = color||'var(--border2)';
  el.style.color = color||'var(--text)';
  el.innerHTML = msg;
  document.body.appendChild(el);
  setTimeout(function() {
    el.classList.add('toast-out');
    setTimeout(function(){ el.remove(); }, 400);
  }, 4000);
}

// ═══════════════════════════════════════════════
// YAHOO FINANCE FETCH
// ═══════════════════════════════════════════════
async function fetchQ(symbol) {
  var enc = encodeURIComponent(symbol);
  var path = 'https://query1.finance.yahoo.com/v8/finance/chart/'+enc+'?range=1d&interval=1d&includePrePost=false';
  for (var i=0; i<PROXIES.length; i++) {
    try {
      var url = PROXIES[i] ? PROXIES[i]+encodeURIComponent(path) : path;
      var r = await fetch(url, {headers:{'Accept':'application/json'}});
      if (!r.ok) continue;
      var data = await r.json();
      var res = data&&data.chart&&data.chart.result&&data.chart.result[0];
      if (!res) continue;
      var meta = res.meta;
      var price = meta.regularMarketPrice;
      if (!price) continue;
      var prev = meta.chartPreviousClose||meta.previousClose||price;
      var chg = price-prev, chgPct = prev?(chg/prev)*100:0;
      return {sym:symbol, price:price, change:chg, changePct:chgPct, ok:true};
    } catch(e) {}
  }
  return {sym:symbol, ok:false};
}

async function fetchAll() {
  var syms = ['SPY','QQQ','DIA','IWM','GLD','USO','^VIX','^TNX','^TYX','^FVX','^IRX',
              'DX=F','BTC-USD','ETH-USD',
              'XLK','XLV','XLF','XLI','XLE','XLC','XLB','XLY','XLP','XLRE','XLU'];
  var results = await Promise.allSettled(syms.map(fetchQ));
  var q = {};
  results.forEach(function(r){
    if (r.status==='fulfilled'&&r.value.ok) q[r.value.sym]=r.value;
  });
  return q;
}

// ═══════════════════════════════════════════════
// DOM UPDATE
// ═══════════════════════════════════════════════
function updCard(pid, cid, qt, isYield) {
  if (!qt) return;
  var p = isYield ? fmtY(qt.price) : fmtP(qt.price);
  var c = fmtPct(qt.changePct)+' today';
  setEl(pid, p, 'c-val '+(isYield?'fl':cls(qt.changePct)));
  setEl(cid, c, 'c-chg '+(isYield?'fl':cls(qt.changePct)));
}

function updSide(id, qt, isYield) {
  if (!qt) return;
  var el = document.getElementById(id);
  if (!el) return;
  el.textContent = isYield ? fmtY(qt.price) : fmtP(qt.price);
  if (!isYield) el.className = 'side-val '+cls(qt.changePct);
}

var SECTOR_DEF = [
  {etf:'XLK', name:'Technology'},  {etf:'XLV', name:'Healthcare'},
  {etf:'XLF', name:'Financials'},  {etf:'XLI', name:'Industrials'},
  {etf:'XLE', name:'Energy'},       {etf:'XLC', name:'Comm. Services'},
  {etf:'XLB', name:'Materials'},    {etf:'XLY', name:'Consumer Disc.'},
  {etf:'XLP', name:'Consumer Staples'},{etf:'XLRE',name:'Real Estate'},
  {etf:'XLU', name:'Utilities'}
];

function buildSectors(q) {
  var sectors = SECTOR_DEF.map(function(s){
    return {etf:s.etf, name:s.name, pct: q[s.etf]?q[s.etf].changePct:null};
  }).filter(function(s){return s.pct!==null;});
  sectors.sort(function(a,b){return b.pct-a.pct;});
  var maxAbs = Math.max.apply(null, sectors.map(function(s){return Math.abs(s.pct);})) || 1;
  var html = '';
  sectors.forEach(function(s) {
    var sg = s.pct>0.3?'bull':(s.pct<-0.3?'bear':'neut');
    var lbl = sg==='bull'?'OVERWEIGHT':(sg==='bear'?'UNDERWEIGHT':'NEUTRAL');
    var col = sg==='bull'?'var(--green)':(sg==='bear'?'var(--red)':'var(--amber)');
    var w = Math.round(Math.abs(s.pct)/maxAbs*100);
    html += '<div class="sec-card '+sg+'"><div class="sec-name">'+s.name+'</div><div class="sec-etf">'+s.etf+'</div>'
      +'<div class="sec-perf" style="color:'+col+'">'+(s.pct>=0?'+':'')+s.pct.toFixed(2)+'%</div>'
      +'<div class="sec-bar-bg"><div class="sec-bar-fill" style="width:'+w+'%;background:'+col+'"></div></div>'
      +'<div class="sec-sig '+sg+'">'+lbl+'</div></div>';
  });
  document.getElementById('sec-grid').innerHTML = html || '<div class="sec-card neut"><div class="sec-name">Data unavailable</div></div>';
}

function buildCurve(y13w, y5, y10, y30) {
  var ctx = document.getElementById('curveChart');
  if (!ctx) return;
  if (curveChartInst) curveChartInst.destroy();
  var vals = [y13w,y5,y10,y30].map(function(v){return v||null;});
  curveChartInst = new Chart(ctx, {
    type:'line',
    data:{
      labels:['13W','5Y','10Y','30Y'],
      datasets:[{
        label:'Yield',data:vals,
        borderColor:'#1fd4ec',backgroundColor:'rgba(31,212,236,.07)',
        pointBackgroundColor:'#1fd4ec',pointRadius:5,tension:.35,fill:true
      }]
    },
    options:{
      responsive:true,
      plugins:{legend:{display:false},tooltip:{callbacks:{label:function(c){return c.parsed.y.toFixed(2)+'%';}}}},
      scales:{
        x:{grid:{color:'rgba(28,42,62,.8)'},ticks:{color:'#3d5068',font:{family:'IBM Plex Mono',size:10}}},
        y:{grid:{color:'rgba(28,42,62,.8)'},ticks:{color:'#3d5068',font:{family:'IBM Plex Mono',size:10},callback:function(v){return v.toFixed(2)+'%';}},suggestedMin:Math.max(0,Math.min.apply(null,vals.filter(Boolean))-0.5)}
      }
    }
  });
}

function buildTicker(q) {
  var items=[
    {ts:'S&P',sym:'SPY'},{ts:'NASDAQ',sym:'QQQ'},{ts:'DOW',sym:'DIA'},
    {ts:'RUSSELL',sym:'IWM'},{ts:'VIX',sym:'^VIX'},{ts:'GOLD',sym:'GLD'},
    {ts:'OIL',sym:'USO'},{ts:'10Y',sym:'^TNX',y:true}
  ];
  var html='';
  items.forEach(function(it){
    var qt=q[it.sym];
    var p=qt?(it.y?fmtY(qt.price):fmtP(qt.price)):'—';
    var c=qt?fmtPct(qt.changePct):'';
    html+='<span class="tick"><span class="ts">'+it.ts+'</span><span class="tv">'+p+'</span>'
      +(qt?'<span class="'+cls(qt.changePct)+'">'+c+'</span>':'')+'</span>';
  });
  document.getElementById('tkr').innerHTML=html+html;
}

function updateDOM(q) {
  liveQuotes = q;
  updCard('m-spy-p','m-spy-c', q['SPY']);
  updCard('m-qqq-p','m-qqq-c', q['QQQ']);
  updCard('m-dia-p','m-dia-c', q['DIA']);
  updCard('m-iwm-p','m-iwm-c', q['IWM']);
  updCard('m-gld-p','m-gld-c', q['GLD']);
  updCard('m-uso-p','m-uso-c', q['USO']);
  updCard('m-vix-p','m-vix-c', q['^VIX']);
  updCard('m-10y-p','m-10y-c', q['^TNX'], true);
  updCard('m-5y-p', 'm-5y-c',  q['^FVX'], true);
  updCard('m-30y-p','m-30y-c', q['^TYX'], true);
  updCard('m-dxy-p','m-dxy-c', q['DX=F']);
  updCard('m-btc-p','m-btc-c', q['BTC-USD']);
  updCard('m-eth-p','m-eth-c', q['ETH-USD']);
  // Update intraday price display from quote
  if (q['SPY']) {
    setEl('intra-price', fmtP(q['SPY'].price), cls(q['SPY'].changePct));
    setEl('intra-chg', fmtPct(q['SPY'].changePct)+' today', cls(q['SPY'].changePct));
  }
  updSide('s-spy', q['SPY']); updSide('s-qqq', q['QQQ']);
  updSide('s-dia', q['DIA']); updSide('s-iwm', q['IWM']);
  updSide('s-gld', q['GLD']); updSide('s-uso', q['USO']);
  updSide('s-vix', q['^VIX']);
  updSide('s-10y', q['^TNX'], true);
  updSide('s-30y', q['^TYX'], true);
  updSide('s-5y',  q['^FVX'], true);
  // Rates
  var y13w=q['^IRX']?q['^IRX'].price:null;
  var y5=q['^FVX']?q['^FVX'].price:null;
  var y10=q['^TNX']?q['^TNX'].price:null;
  var y30=q['^TYX']?q['^TYX'].price:null;
  setEl('r-13w', fmtY(y13w), 'yc-v fl');
  setEl('r-5y',  fmtY(y5),   'yc-v fl');
  setEl('r-10y', fmtY(y10),  'yc-v fl');
  setEl('r-30y', fmtY(y30),  'yc-v fl');
  if (y10&&y5)   { var sp=y10-y5;   setEl('r-sp1',(sp>=0?'+':'')+sp.toFixed(2)+'%','c-val '+(sp>=0?'up':'dn')); setEl('r-sp1l',sp>=0?'Normal / steepening':'Inverted'); }
  if (y10&&y13w) { var sp2=y10-y13w; setEl('r-sp2',(sp2>=0?'+':'')+sp2.toFixed(2)+'%','c-val '+(sp2>=0?'up':'dn')); }
  if (y13w&&y5&&y10&&y30) buildCurve(y13w,y5,y10,y30);
  buildSectors(q);
  buildTicker(q);
}

// ═══════════════════════════════════════════════
// LIVE RSS NEWS
// ═══════════════════════════════════════════════
var NEWS_SOURCES = [
  {url:'https://finance.yahoo.com/news/rssindex', label:'Yahoo Finance'},
  {url:'https://feeds.reuters.com/reuters/businessNews', label:'Reuters Business'},
  {url:'https://feeds.reuters.com/Reuters/worldNews', label:'Reuters World'},
  {url:'https://venturebeat.com/category/ai/feed/', label:'VentureBeat AI'},
  {url:'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114', label:'CNBC'},
  {url:'https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best', label:'Reuters Finance'}
];

var AI_WORDS = ['ai','artificial intelligence','chatgpt','openai','anthropic','gemini','llm','machine learning','nvidia','deep learning','neural'];
var GEO_WORDS = ['war','conflict','ukraine','russia','china','iran','nato','sanctions','geopolit','election','military','ceasefire','taiwan','middle east','israel','hamas','nuclear'];
var MACRO_WORDS = ['fed','federal reserve','inflation','cpi','interest rate','gdp','economy','jobs','unemployment','fomc','powell','treasury','recession','growth','rate cut','rate hike'];
var CMD_WORDS = ['oil','gold','crude','energy','commodities','silver','copper','natural gas','opec','petroleum'];

function classifyNews(title) {
  var t = title.toLowerCase();
  if (AI_WORDS.some(function(w){return t.indexOf(w)>=0;}))   return 'ai';
  if (GEO_WORDS.some(function(w){return t.indexOf(w)>=0;}))  return 'geo';
  if (MACRO_WORDS.some(function(w){return t.indexOf(w)>=0;}))return 'mac';
  if (CMD_WORDS.some(function(w){return t.indexOf(w)>=0;}))  return 'cmd';
  return 'eqt';
}

var TAG_LABELS = {mac:'MACRO', geo:'GEO-POL', ai:'AI', eqt:'MARKETS', cmd:'COMMODITIES'};

async function fetchRSS(feedUrl) {
  var apiUrl = 'https://api.rss2json.com/v1/api.json?rss_url='+encodeURIComponent(feedUrl)+'&count=8';
  try {
    var r = await fetch(apiUrl);
    if (!r.ok) return [];
    var data = await r.json();
    return (data.items||[]).map(function(item){
      return {
        title: (item.title||'').replace(/<[^>]+>/g,'').trim(),
        link: item.link||'#',
        pub: item.pubDate||'',
        source: data.feed&&data.feed.title ? data.feed.title : feedUrl,
        tag: classifyNews(item.title||'')
      };
    });
  } catch(e) { return []; }
}

async function loadNews() {
  var list = document.getElementById('news-list');
  list.innerHTML = '<div class="n-loading"><span class="spin">◌</span>&nbsp; Fetching live news…</div>';
  var results = await Promise.allSettled(NEWS_SOURCES.map(function(s){return fetchRSS(s.url);}));
  var all = [];
  results.forEach(function(r){ if (r.status==='fulfilled') all = all.concat(r.value); });
  // Deduplicate by title
  var seen = {};
  all = all.filter(function(n){
    var key = n.title.substring(0,60);
    if (seen[key]) return false;
    seen[key]=true; return true;
  });
  // Sort by pub date desc
  all.sort(function(a,b){ return new Date(b.pub)-new Date(a.pub); });
  allNewsItems = all;
  renderNews(currentFilter);
}

function renderNews(filter) {
  currentFilter = filter;
  var list = document.getElementById('news-list');
  var items = filter==='all' ? allNewsItems : allNewsItems.filter(function(n){return n.tag===filter;});
  if (!items.length) {
    list.innerHTML = '<div class="n-loading" style="color:var(--text3)">No articles found for this filter.</div>';
    return;
  }
  var html = '';
  items.slice(0,18).forEach(function(n){
    var d = n.pub ? new Date(n.pub) : null;
    var dstr = d&&!isNaN(d) ? MONTHS[d.getMonth()]+' '+d.getDate()+' · '+d.toLocaleTimeString('en-US',{hour:'2-digit',minute:'2-digit',hour12:true}) : '';
    var safeTitle = n.title.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    html+='<div class="news-item"><span class="ntag '+n.tag+'">'+TAG_LABELS[n.tag]+'</span>'
      +'<div><div class="n-hl"><a href="'+n.link+'" target="_blank" rel="noopener">'+safeTitle+'</a></div>'
      +'<div class="n-meta">'+n.source+(dstr?' &middot; '+dstr:'')+'</div></div></div>';
  });
  list.innerHTML = html;
}

function filterNews(tag, btn) {
  document.querySelectorAll('.nf-btn').forEach(function(b){b.classList.remove('on');});
  btn.classList.add('on');
  if (allNewsItems.length) renderNews(tag);
  else loadNews().then(function(){renderNews(tag);});
}

// ═══════════════════════════════════════════════
// AI SUMMARY — Pollinations.ai (free, CORS ok)
// ═══════════════════════════════════════════════
function updateAIDates() {
  var el = document.getElementById('ai-date');
  if (el) el.textContent = todayStr();
}

async function generateSummary() {
  var btn = document.getElementById('gen-btn');
  var out = document.getElementById('ai-out');
  var icon = document.getElementById('gen-icon');
  btn.disabled = true;
  icon.textContent = '◌';
  icon.classList.add('spin');
  out.innerHTML = '<div style="color:var(--text3);font-family:var(--mono);font-size:11px"><span class="spin">◌</span>&nbsp; Generating market analysis…</div>';

  var q = liveQuotes;
  var ms = getMarketStatus();
  var ds = todayStr();

  // Build market data string
  var mktData = 'Date: '+ds+'. Market status: '+ms.l+'.';
  if (q['SPY'])   mktData += ' SPY: '+fmtP(q['SPY'].price)+' ('+fmtPct(q['SPY'].changePct)+').';
  if (q['QQQ'])   mktData += ' QQQ: '+fmtP(q['QQQ'].price)+' ('+fmtPct(q['QQQ'].changePct)+').';
  if (q['DIA'])   mktData += ' DIA: '+fmtP(q['DIA'].price)+' ('+fmtPct(q['DIA'].changePct)+').';
  if (q['^VIX'])  mktData += ' VIX: '+fmtP(q['^VIX'].price)+'.';
  if (q['^TNX'])  mktData += ' 10Y yield: '+fmtY(q['^TNX'].price)+'.';
  if (q['^FVX'])  mktData += ' 5Y yield: '+fmtY(q['^FVX'].price)+'.';
  if (q['GLD'])   mktData += ' Gold: '+fmtP(q['GLD'].price)+' ('+fmtPct(q['GLD'].changePct)+').';
  if (q['USO'])   mktData += ' Oil(USO): '+fmtP(q['USO'].price)+' ('+fmtPct(q['USO'].changePct)+').';
  // Add top 3 sectors
  var secs = ['XLK','XLV','XLF','XLI','XLE','XLC','XLB','XLY','XLP','XLRE','XLU']
    .filter(function(s){return !!q[s];})
    .sort(function(a,b){return (q[b].changePct)-(q[a].changePct);});
  if (secs.length) mktData += ' Top sectors: '+secs.slice(0,3).map(function(s){return s+' '+fmtPct(q[s].changePct);}).join(', ')+'.';
  if (secs.length) mktData += ' Weakest: '+secs.slice(-2).map(function(s){return s+' '+fmtPct(q[s].changePct);}).join(', ')+'.';

  var prompt = 'You are SIGNAL, an elite market intelligence system. Today is '+ds+'. Live market data: '+mktData
    +' Write a concise 3-paragraph institutional-grade market summary: (1) Overall sentiment and what is driving it, (2) Key movers, sectors, and notable data points with the actual numbers, (3) Key macro risks and what to watch this week. Use bold for ticker symbols and key figures. Max 220 words. Be sharp, specific, and professional — no generic filler.';

  try {
    var r = await fetch('https://text.pollinations.ai/', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        messages: [
          {role:'system', content:'You are SIGNAL, an elite market intelligence platform. Be concise, data-driven, and institutional in tone.'},
          {role:'user', content:prompt}
        ],
        model: 'openai',
        seed: Math.floor(Date.now()/60000) // stable per-minute
      })
    });
    var text = '';
    if (r.ok) {
      var data = await r.json();
      text = data.choices&&data.choices[0]&&data.choices[0].message
        ? data.choices[0].message.content
        : await r.text();
    } else {
      // Fallback: GET endpoint
      var r2 = await fetch('https://text.pollinations.ai/'+encodeURIComponent(prompt));
      text = r2.ok ? await r2.text() : '';
    }
    if (!text.trim()) throw new Error('Empty response');
    // Format
    text = text
      .replace(/\*\*(.*?)\*\*/g,'<b>$1</b>')
      .replace(/\n\n/g,'</div><div class="ai-para">')
      .replace(/\n/g,'<br>');
    out.innerHTML = '<div style="font-family:var(--mono);font-size:9px;color:var(--purple);margin-bottom:10px;letter-spacing:.08em">SIGNAL AI · '+ds+'</div><div class="ai-para">'+text+'</div>';
  } catch(e) {
    out.innerHTML = '<div style="color:var(--amber);font-family:var(--mono);font-size:11px">Could not reach AI — check your internet connection and try again.</div>';
  }
  btn.disabled = false;
  icon.textContent = '✦';
  icon.classList.remove('spin');
}

// ═══════════════════════════════════════════════
// INSTITUTIONAL BUYS — Yahoo Finance analyst ratings
// ═══════════════════════════════════════════════
var WATCH_STOCKS = [
  {sym:'AAPL',  name:'Apple Inc.'},
  {sym:'MSFT',  name:'Microsoft Corp.'},
  {sym:'NVDA',  name:'NVIDIA Corp.'},
  {sym:'GOOGL', name:'Alphabet Inc.'},
  {sym:'AMZN',  name:'Amazon.com Inc.'},
  {sym:'META',  name:'Meta Platforms'},
  {sym:'TSLA',  name:'Tesla Inc.'},
  {sym:'JPM',   name:'JPMorgan Chase'},
  {sym:'V',     name:'Visa Inc.'},
  {sym:'LLY',   name:'Eli Lilly & Co.'},
  {sym:'AVGO',  name:'Broadcom Inc.'},
  {sym:'UNH',   name:'UnitedHealth Group'},
  {sym:'HD',    name:'Home Depot'},
  {sym:'COST',  name:'Costco Wholesale'},
  {sym:'MA',    name:'Mastercard Inc.'}
];

async function fetchAnalyst(sym) {
  var path = 'https://query1.finance.yahoo.com/v10/finance/quoteSummary/'+sym+'?modules=financialData,defaultKeyStatistics';
  for (var i=0; i<PROXIES.length; i++) {
    try {
      var url = PROXIES[i] ? PROXIES[i]+encodeURIComponent(path) : path;
      var r = await fetch(url, {headers:{'Accept':'application/json'}});
      if (!r.ok) continue;
      var data = await r.json();
      var fd = data&&data.quoteSummary&&data.quoteSummary.result&&data.quoteSummary.result[0]&&data.quoteSummary.result[0].financialData;
      if (!fd) continue;
      return {
        sym: sym,
        ratingKey: fd.recommendationKey||'',
        analysts: fd.numberOfAnalystOpinions&&fd.numberOfAnalystOpinions.raw,
        target: fd.targetMeanPrice&&fd.targetMeanPrice.raw,
        current: fd.currentPrice&&fd.currentPrice.raw,
        ok: true
      };
    } catch(e) {}
  }
  return {sym:sym, ok:false};
}

async function loadIBuys() {
  var grid = document.getElementById('ibuys-grid');
  grid.innerHTML = '<div class="ibuy-card" style="grid-column:1/-1"><div class="ibuy-sym" style="color:var(--text3);font-size:12px"><span class="spin">◌</span>&nbsp; Fetching analyst ratings…</div></div>';

  var results = await Promise.allSettled(WATCH_STOCKS.map(function(s){return fetchAnalyst(s.sym);}));

  var ratings = [];
  results.forEach(function(r, i) {
    if (r.status==='fulfilled'&&r.value.ok) {
      var v = r.value;
      var rk = (v.ratingKey||'').toLowerCase().replace(/\s/g,'');
      if (rk==='strongbuy'||rk==='buy') {
        ratings.push({
          sym: v.sym,
          name: WATCH_STOCKS[i].name,
          ratingKey: rk,
          analysts: v.analysts,
          target: v.target,
          current: v.current,
          upside: v.target&&v.current ? ((v.target-v.current)/v.current)*100 : null
        });
      }
    }
  });

  // Also pull current prices for those we have
  var priceSyms = WATCH_STOCKS.map(function(s){return s.sym;});
  var priceResults = await Promise.allSettled(priceSyms.map(fetchQ));
  var prices = {};
  priceResults.forEach(function(r){
    if (r.status==='fulfilled'&&r.value.ok) prices[r.value.sym]=r.value;
  });

  // Sort: strongBuy first, then by upside
  ratings.sort(function(a,b){
    if (a.ratingKey==='strongbuy'&&b.ratingKey!=='strongbuy') return -1;
    if (b.ratingKey==='strongbuy'&&a.ratingKey!=='strongbuy') return 1;
    return (b.upside||0)-(a.upside||0);
  });

  if (!ratings.length) {
    // Fallback: show price + change for top stocks with note
    grid.innerHTML = '<div class="ibuy-card" style="grid-column:1/-1;border-top:none"><div style="font-size:12px;color:var(--text3)">Analyst rating data unavailable from API. Showing live price data for key stocks.</div></div>';
    var fallback = WATCH_STOCKS.slice(0,8).map(function(s){
      var p = prices[s.sym];
      return '<div class="ibuy-card buy"><div class="ibuy-sym">'+s.sym+'</div><div class="ibuy-name">'+s.name+'</div>'
        +(p?'<div class="ibuy-price '+cls(p.changePct)+'">$'+fmtP(p.price)+'</div><div class="ibuy-target">'+fmtPct(p.changePct)+' today</div>':'<div class="ibuy-price" style="color:var(--text3)">—</div>')
        +'</div>';
    }).join('');
    grid.innerHTML += fallback;
    return;
  }

  var html = '';
  ratings.slice(0,10).forEach(function(r) {
    var p = prices[r.sym];
    var priceStr = p ? '$'+fmtP(p.price) : (r.current ? '$'+fmtP(r.current) : '—');
    var changeStr = p ? fmtPct(p.changePct)+' today' : '';
    var priceCls = p ? cls(p.changePct) : 'fl';
    var upStr = r.upside ? (r.upside>=0?'+':'')+r.upside.toFixed(1)+'% upside' : '';
    var ratingLabel = r.ratingKey==='strongbuy' ? 'STRONG BUY' : 'BUY';
    html += '<div class="ibuy-card '+r.ratingKey+'">'
      +'<div class="ibuy-sym">'+r.sym+'</div>'
      +'<div class="ibuy-name">'+r.name+'</div>'
      +'<div class="ibuy-price '+priceCls+'">'+priceStr+'</div>'
      +(changeStr?'<div style="font-family:var(--mono);font-size:10px;margin-bottom:5px" class="'+priceCls+'">'+changeStr+'</div>':'')
      +'<span class="ibuy-rating '+r.ratingKey+'">'+ratingLabel+'</span>'
      +(r.analysts?'<div class="ibuy-target">'+r.analysts+' analysts</div>':'')
      +(upStr?'<div class="ibuy-target" style="color:var(--green)">'+upStr+'</div>':'')
      +(r.target?'<div class="ibuy-target">Target: $'+fmtP(r.target)+'</div>':'')
      +'</div>';
  });
  grid.innerHTML = html;
}

// ═══════════════════════════════════════════════
// INTRADAY CHART — SPY 5-min bars
// ═══════════════════════════════════════════════
var intradayChartInst = null;

async function fetchIntraday() {
  var path = 'https://query1.finance.yahoo.com/v8/finance/chart/SPY?range=1d&interval=5m&includePrePost=false';
  for (var i=0; i<PROXIES.length; i++) {
    try {
      var url = PROXIES[i] ? PROXIES[i]+encodeURIComponent(path) : path;
      var r = await fetch(url, {headers:{'Accept':'application/json'}});
      if (!r.ok) continue;
      var data = await r.json();
      var res = data&&data.chart&&data.chart.result&&data.chart.result[0];
      if (!res||!res.timestamp) continue;
      var ts = res.timestamp;
      var closes = res.indicators.quote[0].close;
      var labels=[], vals=[];
      for (var j=0; j<ts.length; j++) {
        if (closes[j]==null) continue;
        var d = new Date(ts[j]*1000);
        labels.push(d.toLocaleTimeString('en-US',{hour:'2-digit',minute:'2-digit',hour12:true,timeZone:'America/New_York'}));
        vals.push(+closes[j].toFixed(2));
      }
      return {labels:labels, vals:vals};
    } catch(e) {}
  }
  return null;
}

async function buildIntradayChart() {
  var badge = document.getElementById('intra-badge');
  var status = document.getElementById('intra-status');
  var ms = getMarketStatus();
  if (ms.s==='closed'&&ms.l==='CLOSED'&&!isWeekend()) {
    // Weekend — show message
    if(status) status.textContent = 'Market closed — intraday chart shows last session data';
  }
  var data = await fetchIntraday();
  if (!data||!data.vals.length) {
    if(status) status.textContent = 'Intraday data unavailable';
    return;
  }
  var ctx = document.getElementById('intradayChart');
  if (!ctx) return;
  if (intradayChartInst) intradayChartInst.destroy();
  var first = data.vals[0];
  var isUp = data.vals[data.vals.length-1] >= first;
  var lineColor = isUp ? '#3dd68c' : '#f06b6b';
  var fillColor = isUp ? 'rgba(61,214,140,.07)' : 'rgba(240,107,107,.07)';
  intradayChartInst = new Chart(ctx, {
    type:'line',
    data:{
      labels: data.labels,
      datasets:[{
        label:'SPY',data:data.vals,
        borderColor:lineColor,backgroundColor:fillColor,
        borderWidth:1.5,pointRadius:0,tension:.3,fill:true
      }]
    },
    options:{
      responsive:true,animation:false,
      plugins:{legend:{display:false},tooltip:{callbacks:{label:function(c){return '$'+c.parsed.y.toFixed(2);}}}},
      scales:{
        x:{grid:{display:false},ticks:{color:'#3d5068',font:{family:'IBM Plex Mono',size:9},maxTicksLimit:8,maxRotation:0}},
        y:{grid:{color:'rgba(28,42,62,.6)'},ticks:{color:'#3d5068',font:{family:'IBM Plex Mono',size:9},callback:function(v){return '$'+v.toFixed(0);}},position:'right'}
      }
    }
  });
  var pts = data.vals.length;
  var last = data.vals[pts-1];
  var pctChg = ((last-first)/first*100);
  if(status) status.textContent = pts+' data points · Open: $'+fmtP(first)+' · Now: $'+fmtP(last)+' · Session: '+fmtPct(pctChg);
  if(badge) badge.textContent = '5-MIN · '+data.labels[data.labels.length-1]+' ET';
}

function isWeekend() { var d=getET().getDay(); return d===0||d===6; }

// ═══════════════════════════════════════════════
// ECONOMIC CALENDAR
// ═══════════════════════════════════════════════
function buildEconCalendar() {
  var now = getET();
  var today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  var events = [];

  // FOMC 2025-2026 decision dates (Fed releases at 2:00 PM ET)
  var fomcDates = [
    '2025-07-30','2025-09-17','2025-10-29','2025-12-10',
    '2026-01-28','2026-03-18','2026-05-06','2026-06-17',
    '2026-07-29','2026-09-16','2026-10-28','2026-12-09'
  ];
  fomcDates.forEach(function(d){
    events.push({date:new Date(d), name:'FOMC Rate Decision', tag:'fed', impact:'high', note:'Federal Reserve'});
  });

  // NFP (Non-Farm Payrolls) — first Friday of each month, 8:30 AM ET
  for (var mo=0; mo<6; mo++) {
    var m = new Date(now.getFullYear(), now.getMonth()+mo, 1);
    var firstFri = new Date(m.getFullYear(), m.getMonth(), 1+(5-m.getDay()+7)%7);
    if (firstFri.getDate()===1) firstFri.setDate(8); // avoid first day being Friday of prior month
    events.push({date:firstFri, name:'Jobs Report (Non-Farm Payrolls)', tag:'jobs', impact:'high', note:'BLS · 8:30 AM ET'});
  }

  // CPI — approx 2nd or 3rd Wednesday each month, 8:30 AM ET
  for (var mo=0; mo<5; mo++) {
    var m = new Date(now.getFullYear(), now.getMonth()+mo, 1);
    var firstWed = 1+(3-m.getDay()+7)%7;
    var cpiDay = firstWed<8 ? firstWed+7 : firstWed; // aim for 2nd Wednesday
    events.push({date:new Date(m.getFullYear(),m.getMonth(),cpiDay+3), name:'CPI Inflation Report', tag:'inflation', impact:'high', note:'BLS · 8:30 AM ET'});
  }

  // GDP — quarterly advance estimate ~4 weeks after quarter end
  var gdpDates = ['2025-07-30','2025-10-29','2026-01-28','2026-04-29','2026-07-29'];
  gdpDates.forEach(function(d){
    events.push({date:new Date(d), name:'GDP Advance Estimate', tag:'growth', impact:'high', note:'BEA · 8:30 AM ET'});
  });

  // PCE (Fed's preferred inflation gauge) — last business day of month
  for (var mo=0; mo<4; mo++) {
    var lastDay = new Date(now.getFullYear(), now.getMonth()+mo+1, 0);
    while(lastDay.getDay()===0||lastDay.getDay()===6) lastDay.setDate(lastDay.getDate()-1);
    events.push({date:lastDay, name:'PCE Price Index', tag:'inflation', impact:'med', note:'BEA · 8:30 AM ET'});
  }

  // Deduplicate and sort
  var seen={};
  events = events.filter(function(e){
    var k=e.date.toDateString()+e.name;
    if(seen[k]) return false; seen[k]=true; return true;
  });
  events.sort(function(a,b){return a.date-b.date;});

  // Split: past (last 2), upcoming (next 8)
  var past=[], upcoming=[];
  events.forEach(function(e){
    var eDay = new Date(e.date.getFullYear(),e.date.getMonth(),e.date.getDate());
    if(eDay < today) past.push(e);
    else upcoming.push(e);
  });
  var display = past.slice(-1).concat(upcoming.slice(0,8));

  var html='';
  display.forEach(function(e){
    var eDay = new Date(e.date.getFullYear(),e.date.getMonth(),e.date.getDate());
    var isPast = eDay < today;
    var isToday = eDay.toDateString()===today.toDateString();
    var mo = MONTHS[e.date.getMonth()];
    var dy = e.date.getDate();
    var dayName = DAYS[e.date.getDay()].substring(0,3);
    var dateStr = dayName+', '+mo+' '+dy;
    var diff = Math.round((eDay-today)/(1000*60*60*24));
    var when = isPast ? 'Past' : (isToday ? 'TODAY' : (diff===1?'Tomorrow':diff+'d away'));
    var whenStyle = isToday ? 'color:var(--amber)' : (isPast?'color:var(--text3)':'');
    html+='<div class="eco-item'+(isToday?' today':'')+(isPast?' past':'')+'">'
      +'<div class="eco-dot '+e.impact+'"></div>'
      +'<div class="eco-date">'+dateStr+'</div>'
      +'<div style="flex:1"><div class="eco-name">'+e.name+'</div>'
      +'<div style="font-family:var(--mono);font-size:9px;color:var(--text3)">'+e.note+'</div></div>'
      +'<span class="eco-tag '+e.tag+'">'+e.tag.toUpperCase()+'</span>'
      +'<div class="eco-when" style="'+whenStyle+'">'+when+'</div>'
      +'</div>';
  });

  // Legend
  html+='<div style="display:flex;gap:14px;padding:6px 4px;font-family:var(--mono);font-size:9px;color:var(--text3)">'
    +'<span><span style="color:var(--red)">●</span> HIGH IMPACT</span>'
    +'<span><span style="color:var(--amber)">●</span> MEDIUM</span>'
    +'<span style="margin-left:auto">Dates approximate — verify with BLS / Fed calendar</span></div>';

  var el = document.getElementById('eco-cal');
  if(el) el.innerHTML = html;
}

// ═══════════════════════════════════════════════
// MAIN REFRESH
// ═══════════════════════════════════════════════
var refreshing = false;
async function refresh() {
  if (refreshing) return;
  refreshing = true;
  var dot = document.getElementById('sdot');
  var msg = document.getElementById('smsg');
  dot.className = 'sdot s-loading';
  msg.textContent = 'Fetching live data…';
  try {
    var q = await fetchAll();
    var count = Object.keys(q).length;
    if (count > 0) {
      updateDOM(q);
      dot.className = 'sdot s-live';
      var ms = getMarketStatus();
      msg.textContent = 'Live · '+count+' symbols · '+ms.l;
      var et = getET();
      setEl('supd','Updated '+et.toLocaleTimeString('en-US',{hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:true,timeZone:'America/New_York'})+' ET');
    } else {
      dot.className = 'sdot s-error';
      msg.textContent = 'Could not fetch data — using cached values';
    }
  } catch(e) {
    dot.className = 'sdot s-error';
    msg.textContent = 'Error: '+e.message;
  }
  refreshing = false;
}

// ═══════════════════════════════════════════════
// INIT
// ═══════════════════════════════════════════════
updateClock();
setInterval(updateClock, 1000);

refresh();
buildEconCalendar();
buildIntradayChart();

// Refresh prices every 60s during market hours, 5min otherwise
setInterval(function(){
  var ms = getMarketStatus();
  if (ms.s==='open'||ms.s==='premarket'||ms.s==='afterhours') refresh();
}, 60000);
setInterval(refresh, 300000);

// Refresh intraday chart every 5 min during market hours
setInterval(function(){
  var ms = getMarketStatus();
  if (ms.s==='open') buildIntradayChart();
}, 5*60000);

// Rebuild calendar once per day (midnight ET)
setInterval(buildEconCalendar, 60*60000);

// Refresh news every 15 minutes in background
setInterval(function(){
  if (allNewsItems.length > 0) loadNews();
}, 15*60000);
</script>
</body>
</html>
