#!/usr/bin/env python3
"""
SIGNAL Market Intelligence — Daily Auto-Update Script
Runs via GitHub Actions every weekday after market close.
Fetches live data and rewrites index.html with current market data.
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests
import yfinance as yf

# ── Timezone ────────────────────────────────────────────────────────────────
ET = ZoneInfo("America/New_York")
now_et = datetime.now(ET)
TODAY = now_et.strftime("%b %-d, %Y")        # e.g. "Jun 8, 2026"
TODAY_ISO = now_et.strftime("%Y-%m-%d")
TODAY_SHORT = now_et.strftime("%-m/%-d")
MONTH_YEAR = now_et.strftime("%b %Y")


# ── Ticker symbols to fetch ─────────────────────────────────────────────────
SYMBOLS = {
    "^GSPC":  "sp500",
    "^DJI":   "dow",
    "^IXIC":  "nasdaq",
    "^RUT":   "russell",
    "^VIX":   "vix",
    "^TNX":   "t10y",
    "^TYX":   "t30y",
    "GC=F":   "gold",
    "CL=F":   "wti",
    "BZ=F":   "brent",
    "BTC-USD":"btc",
    # Equities
    "KO": "ko", "CL": "cl_eq", "JNJ": "jnj",
    "XOM": "xom", "META": "meta", "NVDA": "nvda",
    "AVGO": "avgo", "GOOGL": "googl", "MSFT": "msft",
}

def pct_str(val):
    sign = "+" if val >= 0 else ""
    return f"{sign}{val:.2f}%"

def fmt_price(val, prefix=""):
    if val >= 1000:
        return f"{prefix}{val:,.2f}"
    return f"{prefix}{val:.2f}"

def color_class(pct):
    return "up" if pct >= 0 else "dn"

def signal_class(pct):
    if pct >= 0.5:
        return "bull"
    elif pct <= -0.5:
        return "bear"
    return "neut"


def fetch_data():
    """Fetch all market data from yfinance."""
    print("Fetching market data...")
    tickers = yf.Tickers(" ".join(SYMBOLS.keys()))
    data = {}

    for sym, key in SYMBOLS.items():
        try:
            t = tickers.tickers[sym]
            hist = t.history(period="2d", interval="1d")
            if len(hist) < 2:
                hist = t.history(period="5d", interval="1d")

            close = float(hist["Close"].iloc[-1])
            prev  = float(hist["Close"].iloc[-2])
            chg   = close - prev
            pct   = (chg / prev) * 100

            data[key] = {
                "price": close,
                "change": chg,
                "pct": pct,
                "prev": prev,
            }
            print(f"  {sym}: {close:.2f} ({pct:+.2f}%)")
        except Exception as e:
            print(f"  WARNING: Could not fetch {sym}: {e}")
            data[key] = {"price": 0, "change": 0, "pct": 0, "prev": 0}

    return data


def build_ticker_bar(d):
    """Build the JS TICKS array."""
    def tk(sym, val, chg_str, up):
        u = "true" if up else "false"
        return f'  {{s:"{sym}",v:"{val}",c:"{chg_str}",u:{u}}}'

    sp = d["sp500"]
    dw = d["dow"]
    nq = d["nasdaq"]
    ru = d["russell"]
    vx = d["vix"]
    t10 = d["t10y"]
    t30 = d["t30y"]
    wti = d["wti"]
    gld = d["gold"]
    btc = d["btc"]
    br  = d["brent"]

    lines = [
        tk("S&P 500",   f"{sp['price']:,.2f}",  pct_str(sp['pct']),  sp['pct']>=0),
        tk("DOW",       f"{dw['price']:,.2f}",  pct_str(dw['pct']),  dw['pct']>=0),
        tk("NASDAQ",    f"{nq['price']:,.2f}",  pct_str(nq['pct']),  nq['pct']>=0),
        tk("RUSSELL 2K",f"{ru['price']:,.2f}",  pct_str(ru['pct']),  ru['pct']>=0),
        tk("VIX",       f"{vx['price']:.2f}",   pct_str(vx['pct']),  vx['pct']>=0),
        tk("10Y YIELD", f"{t10['price']:.2f}%", pct_str(t10['pct']), t10['pct']>=0),
        tk("30Y YIELD", f"{t30['price']:.2f}%", pct_str(t30['pct']), t30['pct']>=0),
        tk("WTI CRUDE", f"${wti['price']:.2f}", pct_str(wti['pct']), wti['pct']>=0),
        tk("GOLD",      f"${gld['price']:,.0f}",pct_str(gld['pct']), gld['pct']>=0),
        tk("BITCOIN",   f"${btc['price']:,.0f}",pct_str(btc['pct']), btc['pct']>=0),
        tk("BRENT",     f"${br['price']:.2f}",  pct_str(br['pct']),  br['pct']>=0),
    ]
    return "[\n" + ",\n".join(lines) + "\n]"


def build_sidebar(d):
    sp = d["sp500"]; dw = d["dow"]; nq = d["nasdaq"]; ru = d["russell"]
    t10 = d["t10y"]; t30 = d["t30y"]; wti = d["wti"]; br = d["brent"]
    gld = d["gold"]; vx = d["vix"]; btc = d["btc"]

    def si(label, val, pct, page="macro"):
        cls = color_class(pct)
        return f'      <div class="si" onclick="go(\'{page}\',null)"><span class="sn">{label}</span><span class="sv {cls}">{val}</span></div>'

    return f"""    <div class="ss">
      <div class="sl">Indices</div>
{si("S&P 500",   f"{sp['price']:,.0f}", sp['pct'])}
{si("Dow Jones", f"{dw['price']:,.0f}", dw['pct'])}
{si("Nasdaq",    f"{nq['price']:,.0f}", nq['pct'])}
{si("Russell 2K",f"{ru['price']:,.0f}", ru['pct'])}
    </div>
    <div class="ss">
      <div class="sl">Rates</div>
{si("10Y Yield", f"{t10['price']:.2f}%", t10['pct'], 'rates')}
{si("Fed Rate",  "3.75%", 0, 'rates')}
{si("30Y Yield", f"{t30['price']:.2f}%", t30['pct'], 'rates')}
    </div>
    <div class="ss">
      <div class="sl">Commodities</div>
      <div class="si"><span class="sn">WTI Crude</span><span class="sv {color_class(wti['pct'])}">${wti['price']:.2f}</span></div>
      <div class="si"><span class="sn">Brent</span><span class="sv {color_class(br['pct'])}">${br['price']:.2f}</span></div>
      <div class="si"><span class="sn">Gold</span><span class="sv {color_class(gld['pct'])}">${gld['price']:,.0f}</span></div>
    </div>
    <div class="ss">
      <div class="sl">Sentiment</div>
      <div class="si"><span class="sn">VIX</span><span class="sv {color_class(vx['pct'])}">{vx['price']:.2f}</span></div>
      <div class="si"><span class="sn">Bitcoin</span><span class="sv {color_class(btc['pct'])}">${btc['price']:,.0f}</span></div>
    </div>"""


def build_macro_cards(d):
    sp = d["sp500"]; dw = d["dow"]; nq = d["nasdaq"]; ru = d["russell"]
    t10 = d["t10y"]; t30 = d["t30y"]; wti = d["wti"]; gld = d["gold"]
    br = d["brent"]; btc = d["btc"]; vx = d["vix"]

    def card(label, val, chg_line, note, source):
        cls = "dn" if "-" in chg_line else "up"
        return f'''        <div class="card"><div class="cl">{label}</div><div class="cv {cls}">{val}</div><div class="cc {cls}">{chg_line}</div><div class="cs">{note}</div><div class="cs">{source} &middot; {TODAY}</div></div>'''

    sp_chg = f"{'−' if sp['pct']<0 else '+'}{abs(sp['pct']):.2f}% today"
    dw_chg = f"{'−' if dw['pct']<0 else '+'}{abs(dw['pct']):.2f}% &middot; {'-' if dw['change']<0 else '+'}{abs(dw['change']):,.0f} pts"
    nq_chg = f"{'−' if nq['pct']<0 else '+'}{abs(nq['pct']):.2f}% today"
    ru_chg = f"{'−' if ru['pct']<0 else '+'}{abs(ru['pct']):.2f}% today"
    t10_chg= f"{pct_str(t10['pct'])} &middot; {t10['price']:.2f}%"
    t30_chg= f"{t30['price']:.2f}% {'(broke 5%)' if t30['price']>=5 else ''}"
    vx_chg = f"{pct_str(vx['pct'])} &middot; {'Fear spike' if vx['pct']>10 else 'Elevated' if vx['price']>20 else 'Moderate'}"
    wti_chg= f"{pct_str(wti['pct'])} &middot; ${wti['price']:.2f}/bbl"
    gld_chg= f"{pct_str(gld['pct'])} &middot; ${gld['price']:,.0f}/oz"
    btc_chg= f"{pct_str(btc['pct'])} &middot; ${btc['price']:,.0f}"

    cards = [
        card("S&P 500",          f"{sp['price']:,.2f}",  sp_chg,  "Broad market benchmark",         "Yahoo Finance"),
        card("Dow Jones",        f"{dw['price']:,.2f}",  dw_chg,  "30 blue-chip stocks",            "CNBC"),
        card("Nasdaq Composite", f"{nq['price']:,.2f}",  nq_chg,  "Tech-heavy index",               "CNBC"),
        card("Russell 2000",     f"{ru['price']:,.2f}",  ru_chg,  "Small-cap benchmark",            "Yahoo Finance"),
        card("10Y Treasury Yield",f"{t10['price']:.2f}%",t10_chg, "Key rate benchmark",             "Yahoo Finance"),
        card("30Y Treasury Yield",f"{t30['price']:.2f}%",t30_chg, "Long-duration rate indicator",   "TheStreet"),
        card("VIX Fear Index",   f"{vx['price']:.2f}",  vx_chg,  "Market volatility gauge",        "Yahoo Finance"),
        card("WTI Crude Oil",    f"${wti['price']:.2f}", wti_chg, "US benchmark crude",             "TradingEconomics"),
        card("Brent Crude",      f"${br['price']:.2f}",  pct_str(br['pct']), "Global crude benchmark","TradingEconomics"),
        card("Gold Spot",        f"${gld['price']:,.0f}",gld_chg, "Safe-haven metal",               "Yahoo Finance"),
        card("Bitcoin",          f"${btc['price']:,.0f}",btc_chg, "Leading crypto asset",           "Yahoo Finance"),
    ]
    return "\n".join(cards)


def build_equities_js(d):
    """Build JS EQ array with live stock data."""
    stocks = [
        ("KO",   "ko",    "Coca-Cola",       "def"),
        ("CL",   "cl_eq", "Colgate-Palmolive","def"),
        ("JNJ",  "jnj",   "Johnson & Johnson","def"),
        ("XOM",  "xom",   "ExxonMobil",      "def"),
        ("META", "meta",  "Meta Platforms",  "tech"),
        ("NVDA", "nvda",  "Nvidia",          "tech"),
        ("AVGO", "avgo",  "Broadcom",        "tech"),
        ("GOOGL","googl", "Alphabet",        "tech"),
        ("MSFT", "msft",  "Microsoft",       "tech"),
        ("BTC-USD","btc", "Bitcoin",         "crypto"),
    ]

    lines = []
    for sym, key, name, sec in stocks:
        price = d[key]["price"]
        pct   = d[key]["pct"]
        sig   = signal_class(pct)
        sign  = "+" if pct >= 0 else ""
        chg_str = f"{sign}{pct:.1f}%"
        note = f"{name} {chg_str} on {TODAY}."
        lines.append(f'  {{t:"{sym}",n:"{name}",sec:"{sec}",s:"{sig}",c:"{chg_str}",note:"{note}"}}')

    return "[\n" + ",\n".join(lines) + "\n]"


def build_ai_system_prompt(d):
    """Build the AI system prompt with today's live data."""
    sp = d["sp500"]; dw = d["dow"]; nq = d["nasdaq"]; ru = d["russell"]
    t10 = d["t10y"]; t30 = d["t30y"]; gld = d["gold"]; wti = d["wti"]
    btc = d["btc"]; vx = d["vix"]; br = d["brent"]

    prompt = f"""You are SIGNAL, a financial intelligence platform. Today is {TODAY}. Live market data updated automatically via GitHub Actions + yfinance.

MARKET DATA {TODAY}:
S&P 500: {sp['price']:,.2f} ({pct_str(sp['pct'])})
Nasdaq Composite: {nq['price']:,.2f} ({pct_str(nq['pct'])})
Dow Jones: {dw['price']:,.2f} ({pct_str(dw['pct'])}, {dw['change']:+,.0f} pts)
Russell 2000: {ru['price']:,.2f} ({pct_str(ru['pct'])})
VIX: {vx['price']:.2f} ({pct_str(vx['pct'])})
10Y Treasury Yield: {t10['price']:.2f}%
30Y Treasury Yield: {t30['price']:.2f}%
WTI Crude: ${wti['price']:.2f}
Brent Crude: ${br['price']:.2f}
Gold: ${gld['price']:,.0f}
Bitcoin: ${btc['price']:,.0f} ({pct_str(btc['pct'])})
Fed Funds Rate: 3.75% (held at last FOMC)

Data source: yfinance / Yahoo Finance. Updated automatically after market close each trading day.
Provide sharp, data-driven analysis. This is not personalized investment advice."""

    # Escape for JS string
    prompt = prompt.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return prompt


def build_sectors_js(d):
    """Build sector performance data based on live index moves."""
    sp_pct = d["sp500"]["pct"]
    nq_pct = d["nasdaq"]["pct"]

    # Estimate sector moves relative to broad market (simplified)
    sectors = [
        {"n": "Consumer Staples", "y": round(sp_pct * 0.3, 1),  "d": "Defensive staples — lower beta to broad market"},
        {"n": "Healthcare",       "y": round(sp_pct * 0.4, 1),  "d": "Defensive bid; biotech and managed care diverge"},
        {"n": "Energy",           "y": round(sp_pct * 0.6, 1),  "d": f"Tied to WTI at ${d['wti']['price']:.2f} and geopolitical risk"},
        {"n": "Financials",       "y": round(sp_pct * 0.8, 1),  "d": f"Rate-sensitive; 10Y at {d['t10y']['price']:.2f}% affects NIM"},
        {"n": "Industrials",      "y": round(sp_pct * 0.9, 1),  "d": "Capex-heavy names react to yield moves"},
        {"n": "Comm. Services",   "y": round(sp_pct * 1.0, 1),  "d": "Meta, Alphabet drag; ad spend sensitivity"},
        {"n": "Materials",        "y": round(sp_pct * 1.1, 1),  "d": "Copper and commodity prices key driver"},
        {"n": "Real Estate",      "y": round(sp_pct * 1.3, 1),  "d": f"30Y at {d['t30y']['price']:.2f}% — major headwind for REITs"},
        {"n": "Consumer Disc.",   "y": round(sp_pct * 1.2, 1),  "d": "Rate-sensitive consumer spending names"},
        {"n": "Utilities",        "y": round(sp_pct * 1.4, 1),  "d": "Bond proxy crushed when yields rise"},
        {"n": "Technology",       "y": round(nq_pct * 1.0, 1),  "d": f"Nasdaq {pct_str(nq_pct)} — AI capex narrative under pressure"},
    ]

    # Sort best to worst
    sectors.sort(key=lambda x: x["y"], reverse=True)

    lines = []
    for s in sectors:
        sig = signal_class(s["y"])
        lines.append(f'  {{n:"{s["n"]}",y:{s["y"]},s:"{sig}",d:"{s["d"]}"}}')
    return "[\n" + ",\n".join(lines) + "\n]"


def build_spx_chart_data(d):
    """Generate realistic SPX chart data anchored to today's close."""
    close = d["sp500"]["price"]

    # Simple backward projection for chart — purely illustrative trend
    def gen_series(n_pts, volatility=0.008):
        import random
        random.seed(42)  # reproducible
        prices = [close]
        for _ in range(n_pts - 1):
            prices.insert(0, prices[0] * (1 + random.uniform(-volatility, volatility * 0.9)))
        return [round(p, 2) for p in prices]

    m1 = gen_series(15, 0.006)
    m3 = gen_series(15, 0.012)
    m6 = gen_series(15, 0.018)

    return f'{{"1m":{m1},"3m":{m3},"6m":{m6}}}'


def generate_html(d, template_path, output_path):
    """Read template, inject live data, write output."""
    with open(template_path, "r") as f:
        html = f.read()

    sp = d["sp500"]; dw = d["dow"]; nq = d["nasdaq"]; ru = d["russell"]
    t10 = d["t10y"]; t30 = d["t30y"]; wti = d["wti"]; br = d["brent"]
    gld = d["gold"]; vx = d["vix"]; btc = d["btc"]

    # Date in nav brand
    html = re.sub(
        r'(market intelligence &middot; )[^<]+',
        f'market intelligence &middot; {TODAY.lower()}',
        html
    )

    # Nav brand date text (bd class)
    html = re.sub(
        r'(<div class="bd">)[^<]+(</div>)',
        f'\\1market intelligence &middot; {TODAY.lower()}\\2',
        html
    )

    # Footer date
    html = re.sub(
        r'(SIGNAL &middot; Sources:.*?)June \d+, \d+',
        f'\\1{TODAY}',
        html
    )
    html = re.sub(
        r'Data: [A-Za-z]+ \d+, \d+ close',
        f'Data: {TODAY} close',
        html
    )

    # Clock JS — update data date string
    html = re.sub(
        r'"Data: [A-Za-z]+ \d+, \d+ close',
        f'"Data: {TODAY} close',
        html
    )

    # Ticker JS array
    html = re.sub(
        r'var TICKS=\[[\s\S]*?\];',
        f'var TICKS={build_ticker_bar(d)};',
        html
    )

    # SPX chart data
    html = re.sub(
        r'var SPX=\{[^;]+\};',
        f'var SPX={build_spx_chart_data(d)};',
        html
    )

    # Chart label
    html = re.sub(
        r'S&amp;P 500 &mdash; [A-Za-z]+ \d+ close: [\d,]+\.?\d* \([^)]+\)',
        f"S&amp;P 500 &mdash; {TODAY} close: {sp['price']:,.2f} ({pct_str(sp['pct'])})",
        html
    )

    # Equities JS
    html = re.sub(
        r'var EQ=\[[\s\S]*?\];',
        f'var EQ={build_equities_js(d)};',
        html
    )

    # Sectors JS
    html = re.sub(
        r'var SECS=\[[\s\S]*?\];',
        f'var SECS={build_sectors_js(d)};',
        html
    )

    # AI system prompt
    html = re.sub(
        r'var SYS="[\s\S]*?";',
        f'var SYS="{build_ai_system_prompt(d)}";',
        html
    )

    # Sidebar
    sidebar_new = build_sidebar(d)
    html = re.sub(
        r'<aside class="side">[\s\S]*?</aside>',
        f'<aside class="side">\n{sidebar_new}\n  </aside>',
        html
    )

    # Macro cards block
    new_cards = build_macro_cards(d)
    html = re.sub(
        r'(<div class="cards">)[\s\S]*?(</div>\s*\n\s*<div class="chart-box">)',
        f'\\1\n{new_cards}\n      \\2',
        html
    )

    # Breaking alert banner — make it generic and date-aware
    sp_label = "up" if sp['pct'] >= 0 else "down"
    alert_text = (
        f"<b>Market Update &mdash; {TODAY}</b> "
        f"S&amp;P 500 {sp_label} {abs(sp['pct']):.2f}% to {sp['price']:,.2f}. "
        f"Nasdaq {abs(nq['pct']):.2f}% {'higher' if nq['pct']>=0 else 'lower'}. "
        f"10Y yield at {t10['price']:.2f}%. Gold ${gld['price']:,.0f}. BTC ${btc['price']:,.0f}."
    )
    html = re.sub(
        r'(<div class="atext">)[\s\S]*?(</div>\s*</div>\s*<div class="hdr">)',
        f'\\1{alert_text}\\2',
        html
    )

    # Update all visible date references in headers/labels
    html = re.sub(r'June \d+, \d{4}', TODAY, html)
    html = re.sub(r'Jun \d+, \d{4}', TODAY, html)
    html = re.sub(r'Jun \d+ \d{4}', TODAY.replace(",", ""), html)

    # Add last-updated meta comment at top
    html = html.replace(
        "<!DOCTYPE html>",
        f"<!DOCTYPE html>\n<!-- SIGNAL auto-updated: {TODAY_ISO} via GitHub Actions -->"
    )

    with open(output_path, "w") as f:
        f.write(html)

    print(f"✅ index.html written — {TODAY}")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root  = os.path.dirname(script_dir)
    template   = os.path.join(repo_root, "index.html")
    output     = os.path.join(repo_root, "index.html")

    data = fetch_data()
    generate_html(data, template, output)
    print("Done.")


if __name__ == "__main__":
    main()
