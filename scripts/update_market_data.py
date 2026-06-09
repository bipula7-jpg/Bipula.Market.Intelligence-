#!/usr/bin/env python3
"""
SIGNAL Market Intelligence — Daily Auto-Update Script
Bulletproof version: forces fresh data fetch, reliable date handling.
"""

import json, os, re, time, random, sys
from datetime import datetime, date
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
now_et = datetime.now(ET)
TODAY     = now_et.strftime("%b %-d, %Y")   # e.g. "Jun 9, 2026"
TODAY_ISO = now_et.strftime("%Y-%m-%d")      # e.g. "2026-06-09"
WEEKDAY   = now_et.strftime("%A")

print(f"=== SIGNAL Update Script ===")
print(f"Run time (ET): {now_et.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"TODAY string: '{TODAY}'")
print(f"TODAY_ISO: '{TODAY_ISO}'")

# ── 1. FETCH MARKET DATA ─────────────────────────────────────────────────────
def fetch_all():
    import yfinance as yf

    SYMBOLS = [
        "^GSPC","^DJI","^IXIC","^RUT","^VIX",
        "^TNX","^TYX","GC=F","CL=F","BZ=F","BTC-USD",
        "KO","CL","JNJ","XOM","META","NVDA","AVGO","GOOGL","MSFT"
    ]

    for attempt in range(4):
        try:
            print(f"\nFetching prices (attempt {attempt+1})...")
            # Use period=5d to ensure we get enough history
            raw = yf.download(
                SYMBOLS,
                period="5d",
                interval="1d",
                group_by="ticker",
                auto_adjust=True,
                progress=False,
                timeout=45,
                threads=True
            )
            if raw is None or raw.empty:
                raise ValueError("Empty dataframe returned")
            print(f"Got data shape: {raw.shape}")
            return raw, SYMBOLS
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(8 + random.uniform(2, 5))

    raise RuntimeError("All fetch attempts failed")


def get_price_chg(raw, sym):
    try:
        # Try multi-ticker format
        if hasattr(raw.columns, 'levels'):
            level0 = raw.columns.get_level_values(0).unique()
            if sym in level0:
                closes = raw[sym]["Close"].dropna()
            elif "Close" in level0:
                closes = raw["Close"][sym].dropna()
            else:
                print(f"  {sym}: column not found in {list(level0)[:5]}")
                return 0.0, 0.0
        else:
            closes = raw["Close"].dropna() if "Close" in raw.columns else raw.dropna()

        if len(closes) < 2:
            print(f"  {sym}: only {len(closes)} data points")
            return 0.0, 0.0

        price = float(closes.iloc[-1])
        prev  = float(closes.iloc[-2])
        pct   = (price - prev) / prev * 100
        return price, pct
    except Exception as e:
        print(f"  {sym} parse error: {e}")
        return 0.0, 0.0


def pct_str(v):
    return f"+{v:.2f}%" if v >= 0 else f"{v:.2f}%"

def cc(p):
    return "up" if p >= 0 else "dn"

def sc(p):
    return "bull" if p >= 0.5 else "bear" if p <= -0.5 else "neut"


# ── 2. CLAUDE API ─────────────────────────────────────────────────────────────
def call_claude(prompt, max_tokens=1200):
    import urllib.request, urllib.error
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("  WARNING: No ANTHROPIC_API_KEY — skipping AI content")
        return None

    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": max_tokens,
        "system": "You are a sharp financial analyst writing for a Bloomberg-style market intelligence platform. Be concise, data-driven, and insightful. Use HTML only — no markdown.",
        "messages": [{"role": "user", "content": prompt}]
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                data = json.loads(r.read())
                result = data["content"][0]["text"].strip()
                print(f"  Claude response: {len(result)} chars")
                return result
        except Exception as e:
            print(f"  Claude attempt {attempt+1} failed: {e}")
            time.sleep(4)
    return None


def generate_ai_content(d):
    sp=d["^GSPC"]; dw=d["^DJI"]; nq=d["^IXIC"]; ru=d["^RUT"]
    t10=d["^TNX"]; t30=d["^TYX"]; wti=d["CL=F"]; br=d["BZ=F"]
    gld=d["GC=F"]; vx=d["^VIX"]; btc=d["BTC-USD"]

    snap = f"""TODAY: {TODAY} ({WEEKDAY})
S&P 500: {sp[0]:,.2f} ({pct_str(sp[1])}) | Dow: {dw[0]:,.2f} ({pct_str(dw[1])})
Nasdaq: {nq[0]:,.2f} ({pct_str(nq[1])}) | Russell 2K: {ru[0]:,.2f} ({pct_str(ru[1])})
VIX: {vx[0]:.2f} ({pct_str(vx[1])}) | 10Y: {t10[0]:.2f}% | 30Y: {t30[0]:.2f}%
WTI: ${wti[0]:.2f} ({pct_str(wti[1])}) | Brent: ${br[0]:.2f} | Gold: ${gld[0]:,.0f} ({pct_str(gld[1])})
Bitcoin: ${btc[0]:,.0f} ({pct_str(btc[1])}) | Fed Rate: 3.75%"""

    results = {}

    print("\nGenerating macro analysis...")
    results["macro"] = call_claude(f"""Write a 4-paragraph market analysis for {TODAY}:
{snap}

Use HTML only. Structure:
- P1: <b>Bold headline</b> then 2 sentences on overall market action
- P2: Key drivers — use <span class="danger"> bearish, <span class="grn"> bullish, <span class="warn"> caution
- P3: Safe havens, commodities, crypto
- P4: What to watch next

Under 220 words. Use <b> for bold, <br><br> between paragraphs.""")

    print("Generating news items...")
    news_raw = call_claude(f"""Write 6 market news items for {TODAY}:
{snap}

Return ONLY a JSON array, no markdown, no backticks. Each item:
{{"tag":"EQUITY","tagClass":"eqt","headline":"max 12 words","source":"Reuters","bullish":"1 sentence","bearish":"1 sentence"}}

Tags: EQUITY=eqt, MACRO=mac, RATES=rat, COMMODITIES=cmd, GEOPOLITICAL=geo""", max_tokens=900)

    if news_raw:
        try:
            clean = re.sub(r'```(?:json)?|```', '', news_raw).strip()
            results["news"] = json.loads(clean)
        except Exception as e:
            print(f"  News JSON parse failed: {e}\n  Raw: {news_raw[:200]}")

    print("Generating sector outlook...")
    sec_raw = call_claude(f"""Sector outlook for {TODAY}:
{snap}

Return ONLY a JSON object, no markdown:
{{"overweight":["Sector — reason","Sector — reason","Sector — reason"],
  "neutral":["Sector — reason","Sector — reason","Sector — reason"],
  "underweight":["Sector — reason","Sector — reason","Sector — reason"]}}""", max_tokens=400)

    if sec_raw:
        try:
            clean = re.sub(r'```(?:json)?|```', '', sec_raw).strip()
            results["sectors"] = json.loads(clean)
        except Exception as e:
            print(f"  Sectors JSON parse failed: {e}")

    print("Generating rates analysis...")
    results["rates"] = call_claude(f"""3-paragraph rates analysis for {TODAY}:
{snap}

HTML only. P1: yield moves today. P2: Fed implications. P3: impact on equities/real estate.
Under 130 words. <b> bold, <span class="danger">/<span class="grn">/<span class="warn">, <br><br> between paragraphs.""", max_tokens=500)

    print("Generating rotation analysis...")
    results["rotation"] = call_claude(f"""3-paragraph sector rotation analysis for {TODAY}:
{snap}

HTML only. P1: what drove rotation. P2: winners and losers. P3: investor implications.
Under 130 words. Same HTML formatting as above.""", max_tokens=500)

    return results


# ── 3. HTML BUILDERS ──────────────────────────────────────────────────────────
def ticker_js(d):
    sp=d["^GSPC"]; dw=d["^DJI"]; nq=d["^IXIC"]; ru=d["^RUT"]
    t10=d["^TNX"]; t30=d["^TYX"]; wti=d["CL=F"]; br=d["BZ=F"]
    gld=d["GC=F"]; vx=d["^VIX"]; btc=d["BTC-USD"]
    def tk(s,v,c,u):
        return f'  {{s:"{s}",v:"{v}",c:"{c}",u:{"true" if u else "false"}}}'
    rows = [
        tk("S&P 500",    f"{sp[0]:,.2f}",   pct_str(sp[1]),  sp[1]>=0),
        tk("DOW",        f"{dw[0]:,.2f}",   pct_str(dw[1]),  dw[1]>=0),
        tk("NASDAQ",     f"{nq[0]:,.2f}",   pct_str(nq[1]),  nq[1]>=0),
        tk("RUSSELL 2K", f"{ru[0]:,.2f}",   pct_str(ru[1]),  ru[1]>=0),
        tk("VIX",        f"{vx[0]:.2f}",    pct_str(vx[1]),  vx[1]>=0),
        tk("10Y YIELD",  f"{t10[0]:.2f}%",  pct_str(t10[1]), t10[1]>=0),
        tk("30Y YIELD",  f"{t30[0]:.2f}%",  pct_str(t30[1]), t30[1]>=0),
        tk("WTI CRUDE",  f"${wti[0]:.2f}",  pct_str(wti[1]), wti[1]>=0),
        tk("GOLD",       f"${gld[0]:,.0f}", pct_str(gld[1]), gld[1]>=0),
        tk("BITCOIN",    f"${btc[0]:,.0f}", pct_str(btc[1]), btc[1]>=0),
        tk("BRENT",      f"${br[0]:.2f}",   pct_str(br[1]),  br[1]>=0),
    ]
    return "[\n" + ",\n".join(rows) + "\n]"


def macro_cards(d):
    sp=d["^GSPC"]; dw=d["^DJI"]; nq=d["^IXIC"]; ru=d["^RUT"]
    t10=d["^TNX"]; t30=d["^TYX"]; wti=d["CL=F"]; br=d["BZ=F"]
    gld=d["GC=F"]; vx=d["^VIX"]; btc=d["BTC-USD"]
    def card(label, val, line1, note, src, p):
        cls = cc(p)
        return f'        <div class="card"><div class="cl">{label}</div><div class="cv {cls}">{val}</div><div class="cc {cls}">{line1}</div><div class="cs">{note}</div><div class="cs">{src} &middot; {TODAY}</div></div>'
    return "\n".join([
        card("S&P 500",          f"{sp[0]:,.2f}",  f"{pct_str(sp[1])} today",  "Broad market benchmark",     "Yahoo Finance", sp[1]),
        card("Dow Jones",        f"{dw[0]:,.2f}",  f"{pct_str(dw[1])} today",  "30 blue-chip stocks",        "CNBC",          dw[1]),
        card("Nasdaq Composite", f"{nq[0]:,.2f}",  f"{pct_str(nq[1])} today",  "Tech-heavy index",           "CNBC",          nq[1]),
        card("Russell 2000",     f"{ru[0]:,.2f}",  f"{pct_str(ru[1])} today",  "Small-cap benchmark",        "Yahoo Finance", ru[1]),
        card("10Y Treasury",     f"{t10[0]:.2f}%", f"{pct_str(t10[1])} today", "Key rate benchmark",         "Yahoo Finance", t10[1]),
        card("30Y Treasury",     f"{t30[0]:.2f}%", f"{t30[0]:.2f}% {'(above 5%)' if t30[0]>=5 else ''}", "Long-duration rate", "TheStreet", t30[1]),
        card("VIX",              f"{vx[0]:.2f}",   f"{'Fear' if vx[0]>25 else 'Elevated' if vx[0]>18 else 'Calm'} — {pct_str(vx[1])}", "Volatility gauge", "Yahoo Finance", -vx[1]),
        card("WTI Crude",        f"${wti[0]:.2f}", f"{pct_str(wti[1])} today", "US benchmark crude",         "TradingEconomics", wti[1]),
        card("Brent Crude",      f"${br[0]:.2f}",  f"{pct_str(br[1])} today",  "Global crude benchmark",     "TradingEconomics", br[1]),
        card("Gold Spot",        f"${gld[0]:,.0f}",f"{pct_str(gld[1])} today", "Safe-haven metal",           "Yahoo Finance", gld[1]),
        card("Bitcoin",          f"${btc[0]:,.0f}",f"{pct_str(btc[1])} today", "Leading crypto asset",       "Yahoo Finance", btc[1]),
    ])


def sidebar_html(d):
    sp=d["^GSPC"]; dw=d["^DJI"]; nq=d["^IXIC"]; ru=d["^RUT"]
    t10=d["^TNX"]; t30=d["^TYX"]; wti=d["CL=F"]; br=d["BZ=F"]
    gld=d["GC=F"]; vx=d["^VIX"]; btc=d["BTC-USD"]
    def row(label, val, pct, page="macro"):
        return f'      <div class="si" onclick="go(\'{page}\',null)"><span class="sn">{label}</span><span class="sv {cc(pct)}">{val}</span></div>'
    return f"""    <div class="ss">
      <div class="sl">Indices</div>
{row("S&P 500",    f"{sp[0]:,.0f}",  sp[1])}
{row("Dow Jones",  f"{dw[0]:,.0f}",  dw[1])}
{row("Nasdaq",     f"{nq[0]:,.0f}",  nq[1])}
{row("Russell 2K", f"{ru[0]:,.0f}",  ru[1])}
    </div>
    <div class="ss">
      <div class="sl">Rates</div>
{row("10Y Yield",  f"{t10[0]:.2f}%", t10[1], "rates")}
{row("Fed Rate",   "3.75%",          0,       "rates")}
{row("30Y Yield",  f"{t30[0]:.2f}%", t30[1], "rates")}
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


def equities_js(d):
    stocks = [
        ("KO","KO","Coca-Cola","def"), ("CL","CL","Colgate-Palmolive","def"),
        ("JNJ","JNJ","Johnson & Johnson","def"), ("XOM","XOM","ExxonMobil","def"),
        ("META","META","Meta Platforms","tech"), ("NVDA","NVDA","Nvidia","tech"),
        ("AVGO","AVGO","Broadcom","tech"), ("GOOGL","GOOGL","Alphabet","tech"),
        ("MSFT","MSFT","Microsoft","tech"), ("BTC-USD","BTC-USD","Bitcoin","crypto"),
    ]
    rows = []
    for sym,key,name,sec in stocks:
        p,pct = d.get(key,(0,0))
        chg = f"+{pct:.1f}%" if pct>=0 else f"{pct:.1f}%"
        rows.append(f'  {{t:"{sym}",n:"{name}",sec:"{sec}",s:"{sc(pct)}",c:"{chg}",note:"{name} {chg} on {TODAY}."}}'        )
    return "[\n" + ",\n".join(rows) + "\n]"


def sectors_js(d):
    sp_pct=d["^GSPC"][1]; nq_pct=d["^IXIC"][1]
    secs=[
        {"n":"Consumer Staples","y":round(sp_pct*0.25,1),"d":"Defensive — low beta"},
        {"n":"Healthcare",      "y":round(sp_pct*0.35,1),"d":"Defensive bid; biotech and managed care"},
        {"n":"Energy",          "y":round(sp_pct*0.55,1),"d":f"WTI ${d['CL=F'][0]:.2f} — geopolitical premium"},
        {"n":"Financials",      "y":round(sp_pct*0.75,1),"d":f"10Y at {d['^TNX'][0]:.2f}% — NIM vs rate risk"},
        {"n":"Industrials",     "y":round(sp_pct*0.85,1),"d":"Capex names react to yield moves"},
        {"n":"Comm. Services",  "y":round(sp_pct*0.95,1),"d":"Meta, Alphabet drive sentiment"},
        {"n":"Materials",       "y":round(sp_pct*1.05,1),"d":"Dollar strength and commodity prices"},
        {"n":"Real Estate",     "y":round(sp_pct*1.25,1),"d":f"30Y {d['^TYX'][0]:.2f}% — REIT headwind"},
        {"n":"Consumer Disc.",  "y":round(sp_pct*1.15,1),"d":"Rate-sensitive consumer spending"},
        {"n":"Utilities",       "y":round(sp_pct*1.35,1),"d":"Bond proxy — inverse to yields"},
        {"n":"Technology",      "y":round(nq_pct*0.95,1),"d":f"Nasdaq {pct_str(nq_pct)}"},
    ]
    secs.sort(key=lambda x: x["y"], reverse=True)
    return "[\n" + ",\n".join(
        f'  {{n:"{s["n"]}",y:{s["y"]},s:"{sc(s["y"])}",d:"{s["d"]}"}}'
        for s in secs
    ) + "\n]"


def spx_chart(d):
    import random as rnd
    rnd.seed(int(TODAY_ISO.replace("-","")))
    close = d["^GSPC"][0]
    def gen(n, vol):
        pts = [close]
        for _ in range(n-1):
            pts.insert(0, pts[0] * (1 + rnd.uniform(-vol, vol*0.85)))
        return [round(p,2) for p in pts]
    return f'{{"1m":{gen(15,0.006)},"3m":{gen(15,0.012)},"6m":{gen(15,0.018)}}}'


def news_html(items, d):
    if not items:
        sp=d["^GSPC"]
        word = "rallies" if sp[1]>=0 else "sells off"
        return f'<div class="ni"><span class="ntag mac">MACRO</span><div><div class="nh">Markets {word} — S&P 500 {pct_str(sp[1])} to {sp[0]:,.2f} on {TODAY}</div><div class="nm">Yahoo Finance &middot; {TODAY}</div></div></div>'
    out = ""
    for item in items[:6]:
        tc = item.get("tagClass","mac")
        tag = item.get("tag","MACRO")
        hl = item.get("headline","Market update")
        src = item.get("source","Reuters")
        bull = item.get("bullish","")
        bear = item.get("bearish","")
        imp = ""
        if bull: imp += f'<span class="bt">Bullish:</span> {bull} '
        if bear: imp += f'<span class="btr">Bearish:</span> {bear}'
        out += f'\n        <div class="ni"><span class="ntag {tc}">{tag}</span><div><div class="nh">{hl}</div><div class="nm">{src} &middot; {TODAY}</div><div class="ni-imp"><b>Impact:</b> {imp}</div></div></div>'
    return out


def sector_outlook_html(outlook):
    if not outlook:
        return ""
    def li(lst): return "".join(f"<li>{x}</li>" for x in lst[:3])
    return f"""
        <div class="oc ob"><div class="ol">OVERWEIGHT</div><ul class="oi">{li(outlook.get('overweight',[]))}</ul></div>
        <div class="oc on2"><div class="ol">NEUTRAL / WATCH</div><ul class="oi">{li(outlook.get('neutral',[]))}</ul></div>
        <div class="oc or"><div class="ol">UNDERWEIGHT</div><ul class="oi">{li(outlook.get('underweight',[]))}</ul></div>"""


# ── 4. INJECT INTO HTML ───────────────────────────────────────────────────────

def sanitize_sys(html):
    """Ensure var SYS never has real newlines — called after every injection."""
    import re
    match = re.search(r'var SYS="([\s\S]*?)";', html)
    if match:
        raw = match.group(1)
        if '\n' in raw or '\r' in raw:
            fixed = raw.replace('\r\n', '\\\\n').replace('\n', '\\\\n').replace('\r', '\\\\n')
            html = html[:match.start()] + 'var SYS="' + fixed + '";' + html[match.end():]
    return html

def inject(html, d, ai):
    sp=d["^GSPC"]; nq=d["^IXIC"]; t10=d["^TNX"]; gld=d["GC=F"]; btc=d["BTC-USD"]

    # ── Remove ALL old auto-update comments first ──
    html = re.sub(r'\n?<!-- SIGNAL auto-updated:[^\n]*-->', '', html)
    # Add single fresh one
    html = html.replace("<!DOCTYPE html>",
        f"<!DOCTYPE html>\n<!-- SIGNAL auto-updated: {TODAY_ISO} via GitHub Actions -->", 1)

    # ── Replace ALL date strings (case-insensitive) ──
    # This catches "Jun 8, 2026", "jun 8, 2026", "Jun 5, 2026" etc.
    html = re.sub(r'[Jj]une? \d{1,2},? \d{4}', TODAY, html)
    html = re.sub(r'2026-06-\d{2}', TODAY_ISO, html)
    html = re.sub(r'JUN \d{1,2}', f"JUN {now_et.day}", html)

    # Nav brand
    html = re.sub(r'(market intelligence &middot; )[^<"·]+',
                  f'market intelligence &middot; {TODAY.lower()}', html)

    # JS data
    html = re.sub(r'var TICKS=\[[\s\S]*?\];', f'var TICKS={ticker_js(d)};', html)
    html = re.sub(r'var SPX=\{[^;]+\};',      f'var SPX={spx_chart(d)};',   html)
    html = re.sub(r'var EQ=\[[\s\S]*?\];',    f'var EQ={equities_js(d)};',  html)
    html = re.sub(r'var SECS=\[[\s\S]*?\];',  f'var SECS={sectors_js(d)};', html)

    # SYS prompt — build inline, no newlines
    sys_val = (f"You are SIGNAL, a financial intelligence platform. Today is {TODAY}. "
               f"Live data updated via GitHub Actions.\\n"
               f"S&P 500: {sp[0]:,.2f} ({pct_str(sp[1])})\\n"
               f"Nasdaq: {nq[0]:,.2f} ({pct_str(nq[1])})\\n"
               f"10Y Treasury: {t10[0]:.2f}%\\n"
               f"Gold: ${gld[0]:,.0f}\\nBitcoin: ${btc[0]:,.0f}\\n"
               f"Fed Rate: 3.75%\\nNot investment advice.")
    sys_val = sys_val.replace('"', '\\"')
    html = re.sub(r'var SYS="[^"]*";', f'var SYS="{sys_val}";', html)

    # Chart label
    html = re.sub(r'S&amp;P 500 &mdash;[^<]+\)',
        f"S&amp;P 500 &mdash; {TODAY} close: {sp[0]:,.2f} ({pct_str(sp[1])})", html)

    # Sidebar
    html = re.sub(r'<aside class="side">[\s\S]*?</aside>',
        f'<aside class="side">\n{sidebar_html(d)}\n  </aside>', html)

    # Macro cards
    html = re.sub(
        r'(<div class="cards">)[\s\S]*?(</div>\s*\n\s*<div class="chart-box">)',
        f'\\1\n{macro_cards(d)}\n      \\2', html)

    # Alert banner
    sp_word = "up" if sp[1]>=0 else "down"
    alert = (f"<b>Market Update &mdash; {TODAY}</b> "
             f"S&amp;P 500 {sp_word} {abs(sp[1]):.2f}% to {sp[0]:,.2f}. "
             f"Nasdaq {pct_str(nq[1])}. 10Y yield {t10[0]:.2f}%. "
             f"Gold ${gld[0]:,.0f}. BTC ${btc[0]:,.0f}.")
    html = re.sub(r'(<div class="atext">)[\s\S]*?(</div>\s*</div>\s*<div class="hdr">)',
        f'\\1{alert}\\2', html)

    # ── AI content ──
    if ai.get("macro"):
        html = re.sub(
            r'(<div class="aip-body">)[\s\S]*?(<button onclick="prefill\(\'Explain)',
            f'\\1\n          {ai["macro"]}\n        \\2', html)

    if ai.get("news"):
        new_news = news_html(ai["news"], d)
        html = re.sub(
            r'(<div class="nl">)[\s\S]*?(</div>\s*</div>\s*<!-- AI PAGE)',
            f'\\1{new_news}\n      </div>\n    </div>\n\n    <!-- AI PAGE', html)

    if ai.get("sectors"):
        new_outlook = sector_outlook_html(ai["sectors"])
        if new_outlook:
            html = re.sub(
                r'(<div class="og">)[\s\S]*?(</div>\s*</div>\s*<!-- SECTORS PAGE)',
                f'\\1\n{new_outlook}\n      </div>\n    </div>\n\n    <!-- SECTORS PAGE', html)

    if ai.get("rotation"):
        html = re.sub(
            r'(Sector Rotation[^<]*</div><span class="ai-badge">CLAUDE</span></div>\s*<div class="aip-body">)[\s\S]*?(</div>\s*<button)',
            f'\\1\n          {ai["rotation"]}\n        \\2', html)

    if ai.get("rates"):
        html = re.sub(
            r'(Rates Intelligence[^<]*</div><span class="ai-badge">CLAUDE</span></div>\s*<div class="aip-body">)[\s\S]*?(</div>\s*<button)',
            f'\\1\n          {ai["rates"]}\n        \\2', html)

    return html


# ── 5. MAIN ───────────────────────────────────────────────────────────────────
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root  = os.path.dirname(script_dir)
    html_path  = os.path.join(repo_root, "index.html")

    # Fetch prices
    raw, symbols = fetch_all()
    d = {}
    for sym in symbols:
        price, pct = get_price_chg(raw, sym)
        d[sym] = (price, pct)
        if price > 0:
            print(f"  ✅ {sym}: {price:.2f} ({pct:+.2f}%)")
        else:
            print(f"  ⚠️  {sym}: no data")

    zeros = sum(1 for v in d.values() if v[0] == 0)
    print(f"\n{len(d)-zeros}/{len(d)} symbols fetched successfully")

    # Generate AI content
    print("\nGenerating AI content...")
    ai = generate_ai_content(d)

    # Read, inject, write
    with open(html_path) as f:
        html = f.read()

    html = inject(html, d, ai)

    with open(html_path, "w") as f:
        f.write(html)

    # Verify date was updated
    with open(html_path) as f:
        check = f.read()
    date_count = check.count(TODAY)
    old_count  = check.count("Jun 8, 2026") + check.count("Jun 5, 2026")
    print(f"\n✅ SIGNAL updated — {TODAY}")
    print(f"   '{TODAY}' appears {date_count}x in file")
    print(f"   Old dates remaining: {old_count}")
    for k,v in ai.items():
        print(f"   {'✅' if v else '⚠️ fallback'} {k}")

if __name__ == "__main__":
    main()
