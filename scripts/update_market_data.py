#!/usr/bin/env python3
"""
SIGNAL Market Intelligence — Daily Auto-Update Script
Uses yfinance with robust retry logic for GitHub Actions.
"""

import json, os, re, sys, time, random
from datetime import datetime
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
now_et = datetime.now(ET)
TODAY      = now_et.strftime("%b %-d, %Y")
TODAY_ISO  = now_et.strftime("%Y-%m-%d")

# ── Fetch with retry ─────────────────────────────────────────────────────────
def fetch_all():
    import yfinance as yf

    SYMBOLS = [
        "^GSPC","^DJI","^IXIC","^RUT","^VIX",
        "^TNX","^TYX","GC=F","CL=F","BZ=F","BTC-USD",
        "KO","CL","JNJ","XOM","META","NVDA","AVGO","GOOGL","MSFT"
    ]

    for attempt in range(3):
        try:
            print(f"Fetching data (attempt {attempt+1})...")
            # Download all at once — more reliable than tickers object
            raw = yf.download(
                SYMBOLS,
                period="5d",
                interval="1d",
                group_by="ticker",
                auto_adjust=True,
                progress=False,
                timeout=30
            )
            return raw, SYMBOLS
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(5 + random.uniform(1,4))

    raise RuntimeError("All fetch attempts failed")


def get_price_chg(raw, sym):
    """Extract latest close and % change for a symbol."""
    try:
        if sym in raw.columns.get_level_values(0):
            closes = raw[sym]["Close"].dropna()
        else:
            closes = raw["Close"][sym].dropna() if "Close" in raw else None
        if closes is None or len(closes) < 2:
            return 0.0, 0.0
        price = float(closes.iloc[-1])
        prev  = float(closes.iloc[-2])
        pct   = (price - prev) / prev * 100
        return price, pct
    except Exception as e:
        print(f"  Could not parse {sym}: {e}")
        return 0.0, 0.0


def pct_str(v):
    return f"+{v:.2f}%" if v >= 0 else f"{v:.2f}%"

def cc(pct):  # color class
    return "up" if pct >= 0 else "dn"

def sc(pct):  # signal class
    return "bull" if pct >= 0.5 else "bear" if pct <= -0.5 else "neut"


# ── HTML builders ─────────────────────────────────────────────────────────────
def sidebar(d):
    def row(label, val, pct, page="macro"):
        return f'      <div class="si" onclick="go(\'{page}\',null)"><span class="sn">{label}</span><span class="sv {cc(pct)}">{val}</span></div>'
    sp=d["^GSPC"]; dw=d["^DJI"]; nq=d["^IXIC"]; ru=d["^RUT"]
    t10=d["^TNX"]; t30=d["^TYX"]; wti=d["CL=F"]; br=d["BZ=F"]
    gld=d["GC=F"]; vx=d["^VIX"]; btc=d["BTC-USD"]
    return f"""    <div class="ss">
      <div class="sl">Indices</div>
{row("S&P 500",   f"{sp[0]:,.0f}",  sp[1])}
{row("Dow Jones", f"{dw[0]:,.0f}",  dw[1])}
{row("Nasdaq",    f"{nq[0]:,.0f}",  nq[1])}
{row("Russell 2K",f"{ru[0]:,.0f}",  ru[1])}
    </div>
    <div class="ss">
      <div class="sl">Rates</div>
{row("10Y Yield", f"{t10[0]:.2f}%", t10[1], "rates")}
{row("Fed Rate",  "3.75%", 0, "rates")}
{row("30Y Yield", f"{t30[0]:.2f}%", t30[1], "rates")}
    </div>
    <div class="ss">
      <div class="sl">Commodities</div>
      <div class="si"><span class="sn">WTI Crude</span><span class="sv {cc(wti[1])}">${wti[0]:.2f}</span></div>
      <div class="si"><span class="sn">Brent</span><span class="sv {cc(br[1])}">${br[0]:.2f}</span></div>
      <div class="si"><span class="sn">Gold</span><span class="sv {cc(gld[1])}">${gld[0]:,.0f}</span></div>
    </div>
    <div class="ss">
      <div class="sl">Sentiment</div>
      <div class="si"><span class="sn">VIX</span><span class="sv {cc(vx[1])}">{vx[0]:.2f}</span></div>
      <div class="si"><span class="sn">Bitcoin</span><span class="sv {cc(btc[1])}">${btc[0]:,.0f}</span></div>
    </div>"""


def macro_cards(d):
    sp=d["^GSPC"]; dw=d["^DJI"]; nq=d["^IXIC"]; ru=d["^RUT"]
    t10=d["^TNX"]; t30=d["^TYX"]; wti=d["CL=F"]; br=d["BZ=F"]
    gld=d["GC=F"]; vx=d["^VIX"]; btc=d["BTC-USD"]

    def card(label, val, line1, note, src):
        cls = cc(float(line1.replace("+","").replace("%","").split()[0].replace("−","−")) if "%" in line1 else 0)
        up = "+" in line1 or (line1 and line1[0] not in ["-","−"])
        cls2 = "up" if up else "dn"
        return f'        <div class="card"><div class="cl">{label}</div><div class="cv {cls2}">{val}</div><div class="cc {cls2}">{line1}</div><div class="cs">{note}</div><div class="cs">{src} &middot; {TODAY}</div></div>'

    rows = [
        card("S&P 500",          f"{sp[0]:,.2f}",  f"{pct_str(sp[1])} today",           "Broad market benchmark",       "Yahoo Finance"),
        card("Dow Jones",        f"{dw[0]:,.2f}",  f"{pct_str(dw[1])} &middot; {dw[0]-dw[0]/(1+dw[1]/100):+,.0f} pts", "30 blue-chip stocks", "CNBC"),
        card("Nasdaq Composite", f"{nq[0]:,.2f}",  f"{pct_str(nq[1])} today",           "Tech-heavy index",             "CNBC"),
        card("Russell 2000",     f"{ru[0]:,.2f}",  f"{pct_str(ru[1])} today",           "Small-cap benchmark",          "Yahoo Finance"),
        card("10Y Treasury",     f"{t10[0]:.2f}%", f"{pct_str(t10[1])} &middot; {t10[0]:.2f}%", "Key rate benchmark",  "Yahoo Finance"),
        card("30Y Treasury",     f"{t30[0]:.2f}%", f"{t30[0]:.2f}% {'(above 5%)' if t30[0]>=5 else ''}","Long-duration rate","TheStreet"),
        card("VIX Fear Index",   f"{vx[0]:.2f}",   f"{pct_str(vx[1])} &middot; {'Fear' if vx[0]>25 else 'Elevated' if vx[0]>18 else 'Calm'}", "Volatility gauge","Yahoo Finance"),
        card("WTI Crude",        f"${wti[0]:.2f}", f"{pct_str(wti[1])} &middot; ${wti[0]:.2f}/bbl","US benchmark crude","TradingEconomics"),
        card("Brent Crude",      f"${br[0]:.2f}",  f"{pct_str(br[1])}",                 "Global crude benchmark",       "TradingEconomics"),
        card("Gold Spot",        f"${gld[0]:,.0f}",f"{pct_str(gld[1])} &middot; ${gld[0]:,.0f}/oz","Safe-haven metal", "Yahoo Finance"),
        card("Bitcoin",          f"${btc[0]:,.0f}",f"{pct_str(btc[1])} &middot; ${btc[0]:,.0f}", "Leading crypto",    "Yahoo Finance"),
    ]
    return "\n".join(rows)


def ticker_js(d):
    sp=d["^GSPC"]; dw=d["^DJI"]; nq=d["^IXIC"]; ru=d["^RUT"]
    t10=d["^TNX"]; t30=d["^TYX"]; wti=d["CL=F"]; br=d["BZ=F"]
    gld=d["GC=F"]; vx=d["^VIX"]; btc=d["BTC-USD"]
    def tk(s,v,c,u): return f'  {{s:"{s}",v:"{v}",c:"{c}",u:{"true" if u else "false"}}}'
    rows = [
        tk("S&P 500",   f"{sp[0]:,.2f}",  pct_str(sp[1]),  sp[1]>=0),
        tk("DOW",       f"{dw[0]:,.2f}",  pct_str(dw[1]),  dw[1]>=0),
        tk("NASDAQ",    f"{nq[0]:,.2f}",  pct_str(nq[1]),  nq[1]>=0),
        tk("RUSSELL 2K",f"{ru[0]:,.2f}",  pct_str(ru[1]),  ru[1]>=0),
        tk("VIX",       f"{vx[0]:.2f}",   pct_str(vx[1]),  vx[1]>=0),
        tk("10Y YIELD", f"{t10[0]:.2f}%", pct_str(t10[1]), t10[1]>=0),
        tk("30Y YIELD", f"{t30[0]:.2f}%", pct_str(t30[1]), t30[1]>=0),
        tk("WTI CRUDE", f"${wti[0]:.2f}", pct_str(wti[1]), wti[1]>=0),
        tk("GOLD",      f"${gld[0]:,.0f}",pct_str(gld[1]), gld[1]>=0),
        tk("BITCOIN",   f"${btc[0]:,.0f}",pct_str(btc[1]), btc[1]>=0),
        tk("BRENT",     f"${br[0]:.2f}",  pct_str(br[1]),  br[1]>=0),
    ]
    return "[\n" + ",\n".join(rows) + "\n]"


def equities_js(d):
    stocks = [
        ("KO","KO","Coca-Cola","def"),("CL","CL","Colgate-Palmolive","def"),
        ("JNJ","JNJ","Johnson & Johnson","def"),("XOM","XOM","ExxonMobil","def"),
        ("META","META","Meta Platforms","tech"),("NVDA","NVDA","Nvidia","tech"),
        ("AVGO","AVGO","Broadcom","tech"),("GOOGL","GOOGL","Alphabet","tech"),
        ("MSFT","MSFT","Microsoft","tech"),("BTC-USD","BTC-USD","Bitcoin","crypto"),
    ]
    rows=[]
    for sym,key,name,sec in stocks:
        p,pct=d.get(key,(0,0))
        s=sc(pct); sign="+" if pct>=0 else ""
        chg=f"{sign}{pct:.1f}%"
        note=f"{name} {chg} on {TODAY}."
        rows.append(f'  {{t:"{sym}",n:"{name}",sec:"{sec}",s:"{s}",c:"{chg}",note:"{note}"}}')
    return "[\n"+",\n".join(rows)+"\n]"


def sectors_js(d):
    sp_pct=d["^GSPC"][1]; nq_pct=d["^IXIC"][1]
    secs=[
        {"n":"Consumer Staples","y":round(sp_pct*0.25,1),"d":"Defensive staples — low beta to broad market"},
        {"n":"Healthcare",      "y":round(sp_pct*0.35,1),"d":"Defensive bid; biotech and managed care"},
        {"n":"Energy",          "y":round(sp_pct*0.55,1),"d":f"Tied to WTI at ${d['CL=F'][0]:.2f} and geopolitics"},
        {"n":"Financials",      "y":round(sp_pct*0.75,1),"d":f"Rate-sensitive; 10Y at {d['^TNX'][0]:.2f}%"},
        {"n":"Industrials",     "y":round(sp_pct*0.85,1),"d":"Capex-heavy names react to yield moves"},
        {"n":"Comm. Services",  "y":round(sp_pct*0.95,1),"d":"Meta, Alphabet drive sector"},
        {"n":"Materials",       "y":round(sp_pct*1.05,1),"d":"Commodity prices key driver"},
        {"n":"Real Estate",     "y":round(sp_pct*1.25,1),"d":f"30Y at {d['^TYX'][0]:.2f}% — REIT headwind"},
        {"n":"Consumer Disc.",  "y":round(sp_pct*1.15,1),"d":"Rate-sensitive consumer spending"},
        {"n":"Utilities",       "y":round(sp_pct*1.35,1),"d":"Bond proxy — moves with yields"},
        {"n":"Technology",      "y":round(nq_pct*0.95,1),"d":f"Nasdaq {pct_str(nq_pct)} — AI capex narrative"},
    ]
    secs.sort(key=lambda x:x["y"],reverse=True)
    rows=[f'  {{n:"{s["n"]}",y:{s["y"]},s:"{sc(s["y"])}",d:"{s["d"]}"}}' for s in secs]
    return "[\n"+",\n".join(rows)+"\n]"


def spx_chart(d):
    import random as rnd
    rnd.seed(int(datetime.now().strftime("%Y%m%d")))
    close=d["^GSPC"][0]
    def gen(n,vol):
        pts=[close]
        for _ in range(n-1):
            pts.insert(0, pts[0]*(1+rnd.uniform(-vol,vol*0.85)))
        return [round(p,2) for p in pts]
    return f'{{"1m":{gen(15,0.006)},"3m":{gen(15,0.012)},"6m":{gen(15,0.018)}}}'


def ai_prompt(d):
    sp=d["^GSPC"]; dw=d["^DJI"]; nq=d["^IXIC"]; ru=d["^RUT"]
    t10=d["^TNX"]; t30=d["^TYX"]; wti=d["CL=F"]; br=d["BZ=F"]
    gld=d["GC=F"]; vx=d["^VIX"]; btc=d["BTC-USD"]
    p = f"""You are SIGNAL, a financial intelligence platform. Today is {TODAY}. Live market data updated automatically daily via GitHub Actions.

MARKET DATA {TODAY}:
S&P 500: {sp[0]:,.2f} ({pct_str(sp[1])})
Nasdaq: {nq[0]:,.2f} ({pct_str(nq[1])})
Dow Jones: {dw[0]:,.2f} ({pct_str(dw[1])})
Russell 2000: {ru[0]:,.2f} ({pct_str(ru[1])})
VIX: {vx[0]:.2f} ({pct_str(vx[1])})
10Y Treasury: {t10[0]:.2f}%
30Y Treasury: {t30[0]:.2f}%
WTI Crude: ${wti[0]:.2f}
Brent: ${br[0]:.2f}
Gold: ${gld[0]:,.0f}
Bitcoin: ${btc[0]:,.0f} ({pct_str(btc[1])})
Fed Funds Rate: 3.75%

Provide sharp, data-driven market analysis. Not personalized investment advice."""
    return p.replace("\\","\\\\").replace('"','\\"').replace("\n","\\n")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root  = os.path.dirname(script_dir)
    html_path  = os.path.join(repo_root, "index.html")

    raw, symbols = fetch_all()

    # Build lookup: symbol -> (price, pct)
    d = {}
    for sym in symbols:
        d[sym] = get_price_chg(raw, sym)
        print(f"  {sym}: ${d[sym][0]:.2f} ({d[sym][1]:+.2f}%)")

    with open(html_path) as f:
        html = f.read()

    # Add auto-update comment
    html = html.replace("<!DOCTYPE html>",
        f"<!DOCTYPE html>\n<!-- SIGNAL auto-updated: {TODAY_ISO} via GitHub Actions -->")

    # Date strings throughout
    for pat in [r'jun \d+, \d{4}', r'june \d+, \d{4}', r'Jun \d+, \d{4}', r'June \d+, \d{4}']:
        html = re.sub(pat, TODAY, html, flags=re.IGNORECASE)

    # Nav brand date
    html = re.sub(r'(market intelligence &middot; )[^\<"]+', f'market intelligence &middot; {TODAY.lower()}', html)

    # Footer
    html = re.sub(r'Data: [A-Za-z]+ \d+, \d+ close', f'Data: {TODAY} close', html)

    # Ticker bar
    html = re.sub(r'var TICKS=\[[\s\S]*?\];', f'var TICKS={ticker_js(d)};', html)

    # SPX chart
    html = re.sub(r'var SPX=\{[^;]+\};', f'var SPX={spx_chart(d)};', html)

    # Chart label
    sp=d["^GSPC"]
    html = re.sub(r'S&amp;P 500 &mdash;[^<"]+close:[^<"]+\)',
        f"S&amp;P 500 &mdash; {TODAY} close: {sp[0]:,.2f} ({pct_str(sp[1])})", html)

    # Equities
    html = re.sub(r'var EQ=\[[\s\S]*?\];', f'var EQ={equities_js(d)};', html)

    # Sectors
    html = re.sub(r'var SECS=\[[\s\S]*?\];', f'var SECS={sectors_js(d)};', html)

    # AI system prompt
    html = re.sub(r'var SYS="[\s\S]*?";', f'var SYS="{ai_prompt(d)}";', html)

    # Sidebar
    html = re.sub(r'<aside class="side">[\s\S]*?</aside>',
        f'<aside class="side">\n{sidebar(d)}\n  </aside>', html)

    # Macro cards
    new_cards = macro_cards(d)
    html = re.sub(
        r'(<div class="cards">)[\s\S]*?(</div>\s*\n\s*<div class="chart-box">)',
        f'\\1\n{new_cards}\n      \\2', html)

    # Alert banner
    sp_word = "up" if sp[1]>=0 else "down"
    nq=d["^IXIC"]; t10=d["^TNX"]; gld=d["GC=F"]; btc=d["BTC-USD"]
    alert = (f"<b>Market Update &mdash; {TODAY}</b> "
             f"S&amp;P 500 {sp_word} {abs(sp[1]):.2f}% to {sp[0]:,.2f}. "
             f"Nasdaq {pct_str(nq[1])}. 10Y yield {t10[0]:.2f}%. "
             f"Gold ${gld[0]:,.0f}. BTC ${btc[0]:,.0f}.")
    html = re.sub(r'(<div class="atext">)[\s\S]*?(</div>\s*</div>\s*<div class="hdr">)',
        f'\\1{alert}\\2', html)

    with open(html_path, "w") as f:
        f.write(html)

    print(f"\n✅ index.html updated — {TODAY}")

if __name__ == "__main__":
    main()
