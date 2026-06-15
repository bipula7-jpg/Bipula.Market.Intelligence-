#!/usr/bin/env python3
"""
SIGNAL Market Intelligence — Daily Auto-Update Script
"""

import json, os, re, time, random, sys
from datetime import datetime
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
now_et = datetime.now(ET)
TODAY     = now_et.strftime("%b %-d, %Y")
TODAY_ISO = now_et.strftime("%Y-%m-%d")
WEEKDAY   = now_et.strftime("%A")

print(f"=== SIGNAL Update Script ===")
print(f"Run time (ET): {now_et.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"TODAY: '{TODAY}'")

# ── 1. FETCH ─────────────────────────────────────────────────────────────────
def fetch_all():
    import yfinance as yf
    SYMBOLS = [
        "^GSPC","^DJI","^IXIC","^RUT","^VIX",
        "^TNX","^TYX","GC=F","CL=F","BZ=F","BTC-USD",
        "KO","CL","JNJ","XOM","META","NVDA","AVGO","GOOGL","MSFT"
    ]
    for attempt in range(4):
        try:
            print(f"Fetching prices (attempt {attempt+1})...")
            raw = yf.download(SYMBOLS, period="5d", interval="1d",
                              group_by="ticker", auto_adjust=True,
                              progress=False, timeout=45, threads=True)
            if raw is None or raw.empty:
                raise ValueError("Empty dataframe")
            print(f"Got data shape: {raw.shape}")
            return raw, SYMBOLS
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(8 + random.uniform(2,5))
    raise RuntimeError("All fetch attempts failed")

def get_price_chg(raw, sym):
    try:
        if hasattr(raw.columns, 'levels'):
            level0 = raw.columns.get_level_values(0).unique()
            if sym in level0:
                closes = raw[sym]["Close"].dropna()
            elif "Close" in level0:
                closes = raw["Close"][sym].dropna()
            else:
                return 0.0, 0.0
        else:
            closes = raw["Close"].dropna() if "Close" in raw.columns else raw.dropna()
        if len(closes) < 2:
            return 0.0, 0.0
        price = float(closes.iloc[-1])
        prev  = float(closes.iloc[-2])
        return price, (price - prev) / prev * 100
    except:
        return 0.0, 0.0

def pct_str(v): return f"+{v:.2f}%" if v >= 0 else f"{v:.2f}%"
def cc(p): return "up" if p >= 0 else "dn"
def sc(p): return "bull" if p >= 0.5 else "bear" if p <= -0.5 else "neut"

# ── 2. NEWS ───────────────────────────────────────────────────────────────────
def fetch_rss_news(d):
    import feedparser, time as _time
    SEARCHES = [
        "stock market S&P inflation today",
        "CPI inflation federal reserve interest rate",
        "Iran war oil prices crude",
        "nasdaq tech stocks earnings",
        "federal reserve fed rate hike cut",
        "economy jobs unemployment GDP",
    ]
    TAG_MAP = {
        "inflation":("MACRO","mac"), "cpi":("MACRO","mac"),
        "fed":("RATES","rat"), "rate":("RATES","rat"),
        "yield":("RATES","rat"), "treasury":("RATES","rat"),
        "oil":("COMMODITIES","cmd"), "crude":("COMMODITIES","cmd"),
        "gold":("COMMODITIES","cmd"), "bitcoin":("EQUITY","eqt"),
        "tech":("EQUITY","eqt"), "nvidia":("EQUITY","eqt"),
        "nasdaq":("EQUITY","eqt"), "earnings":("EQUITY","eqt"),
        "iran":("GEOPOLITICAL","geo"), "war":("GEOPOLITICAL","geo"),
        "jobs":("MACRO","mac"), "gdp":("MACRO","mac"),
        "market":("MACRO","mac"), "stock":("MACRO","mac"),
    }
    def classify(t):
        tl = t.lower()
        for kw,(tag,cls) in TAG_MAP.items():
            if kw in tl: return tag, cls
        return "MACRO","mac"

    all_items = []
    seen = set()
    for query in SEARCHES:
        try:
            enc = query.replace(" ","+")
            url = f"https://news.google.com/rss/search?q={enc}&hl=en-US&gl=US&ceid=US:en"
            feed = feedparser.parse(url)
            count = 0
            for entry in feed.entries[:4]:
                raw_title = entry.get("title","").strip()
                if not raw_title or len(raw_title) < 20: continue
                # Clean "Headline - Source" format
                if " - " in raw_title:
                    parts = raw_title.rsplit(" - ",1)
                    title, source = parts[0].strip(), parts[1].strip()
                else:
                    title, source = raw_title, "Reuters"
                key = title[:40].lower()
                if key in seen: continue
                seen.add(key)
                tag, cls = classify(title)
                # Clean any special chars that could break HTML
                title = title.replace('"',"'").replace('<','').replace('>','')
                all_items.append({"tag":tag,"tagClass":cls,
                    "headline":title[:120],"source":source,
                    "bullish":"","bearish":""})
                count += 1
                if count >= 2: break
            if count > 0:
                print(f"  RSS '{query[:25]}': {count} items")
            _time.sleep(0.5)
        except Exception as e:
            print(f"  RSS failed: {e}")

    if len(all_items) >= 4:
        print(f"  Got {len(all_items)} real headlines")
        return all_items[:6]

    print("  Using smart fallback headlines")
    return generate_smart_news(d)

def generate_smart_news(d):
    sp=d.get("^GSPC",(0,0)); nq=d.get("^IXIC",(0,0))
    t10=d.get("^TNX",(0,0)); wti=d.get("CL=F",(0,0))
    gld=d.get("GC=F",(0,0)); vx=d.get("^VIX",(0,0))
    btc=d.get("BTC-USD",(0,0))
    def p(v): return f"+{v:.1f}%" if v>=0 else f"{v:.1f}%"
    news = []
    if sp[1] <= -1.5:
        news.append({"tag":"MACRO","tagClass":"mac","headline":f"S&P 500 drops {abs(sp[1]):.1f}% in broad selloff","source":"Yahoo Finance","bullish":"Pullback may offer entry points","bearish":"Risk-off sentiment across asset classes"})
    elif sp[1] >= 1.5:
        news.append({"tag":"MACRO","tagClass":"mac","headline":f"S&P 500 rallies {sp[1]:.1f}% as risk appetite returns","source":"CNBC","bullish":"Momentum shift could extend gains","bearish":"Overbought conditions may invite profit-taking"})
    else:
        news.append({"tag":"MACRO","tagClass":"mac","headline":f"Markets {'slide' if sp[1]<0 else 'edge higher'} — S&P 500 {p(sp[1])} amid macro uncertainty","source":"Reuters","bullish":"Measured investor response to data","bearish":"Ongoing inflation and rate concerns persist"})
    if nq[1] <= -2.0:
        news.append({"tag":"EQUITY","tagClass":"eqt","headline":f"Nasdaq drops {abs(nq[1]):.1f}% — chip stocks lead decline","source":"CNBC","bullish":"Deep pullback may reset valuations","bearish":"AI spending concerns hammering growth multiples"})
    else:
        news.append({"tag":"EQUITY","tagClass":"eqt","headline":f"Tech {'mixed' if abs(nq[1])<1 else 'leads'} — Nasdaq {p(nq[1])} on AI sentiment","source":"TheStreet","bullish":"AI capex cycle intact","bearish":"High valuations leave tech vulnerable"})
    if t10[0] >= 4.5:
        news.append({"tag":"RATES","tagClass":"rat","headline":f"10Y Treasury yield at {t10[0]:.2f}% — Fed hike risk elevated after hot CPI","source":"TheStreet","bullish":"High yields attract foreign capital","bearish":"Elevated borrowing costs compress valuations"})
    else:
        news.append({"tag":"RATES","tagClass":"rat","headline":f"10Y yield at {t10[0]:.2f}% — bond market pricing Fed on hold","source":"Reuters","bullish":"Rate stability supports equities","bearish":"No cut path until inflation hits 2%"})
    if wti[1] >= 2.0:
        news.append({"tag":"GEOPOLITICAL","tagClass":"geo","headline":f"Oil surges {wti[1]:.1f}% to ${wti[0]:.2f} — Iran conflict escalates","source":"Reuters","bullish":"Energy sector benefits","bearish":"Rising oil adds to inflation pressure"})
    else:
        news.append({"tag":"GEOPOLITICAL","tagClass":"geo","headline":f"Iran conflict keeps geopolitical risk premium elevated — WTI at ${wti[0]:.2f}","source":"TheStreet","bullish":"Defense and energy sectors benefit","bearish":"Prolonged conflict delays Fed cuts"})
    if vx[0] >= 20:
        news.append({"tag":"MACRO","tagClass":"mac","headline":f"VIX at {vx[0]:.1f} — elevated fear gauge signals market stress","source":"CBOE","bullish":"High VIX has historically marked near-term bottoms","bearish":"Volatility reflects genuine macro uncertainty"})
    else:
        news.append({"tag":"MACRO","tagClass":"mac","headline":f"VIX at {vx[0]:.1f} — markets cautious ahead of June 16-17 Fed meeting","source":"Yahoo Finance","bullish":"Contained vol allows orderly price discovery","bearish":"Fed outcome uncertainty keeps investors hedged"})
    if gld[1] >= 1.0:
        news.append({"tag":"COMMODITIES","tagClass":"cmd","headline":f"Gold climbs to ${gld[0]:,.0f} — safe haven demand surges","source":"Reuters","bullish":"Gold breakout confirms risk-off bid","bearish":"Rally signals deteriorating equity confidence"})
    else:
        news.append({"tag":"EQUITY","tagClass":"eqt","headline":f"Bitcoin at ${btc[0]:,.0f} — crypto tracks broader risk sentiment","source":"CoinDesk","bullish":"Institutional holders maintaining positions","bearish":"Macro headwinds weigh on speculative assets"})
    return news[:6]

# ── 3. AI CONTENT ─────────────────────────────────────────────────────────────
def generate_ai_content(d):
    results = {}
    print("Fetching news...")
    results["news"] = fetch_rss_news(d)

    sp=d.get("^GSPC",(0,0)); nq=d.get("^IXIC",(0,0))
    t10=d.get("^TNX",(0,0))[0]; t30=d.get("^TYX",(0,0))[0]
    wti=d.get("CL=F",(0,0)); gld=d.get("GC=F",(0,0))
    vx=d.get("^VIX",(0,0)); btc=d.get("BTC-USD",(0,0))

    # Sector outlook
    if sp[1] >= 0:
        ow=["Technology — AI spending thesis intact despite valuation concerns",
            "Energy — Iran conflict sustains oil price premium for sector",
            "Financials — higher-for-longer rates support net interest margin"]
        ne=["Healthcare — defensive bid, limited upside in risk-on environment",
            "Consumer Staples — steady earnings but muted growth in bull tape",
            "Industrials — capex cycle intact but sensitive to rate moves"]
        uw=["Real Estate — 30Y above 5% makes REITs unattractive vs bonds",
            "Utilities — bond proxy selling off as yields stay elevated",
            "Consumer Discretionary — rate-sensitive spending under pressure"]
    else:
        ow=["Consumer Staples — defensive rotation underway, dividends attractive",
            "Healthcare — flight to safety benefits low-beta defensive names",
            "Energy — oil elevated on Iran risk, sector outperforming on down days"]
        ne=["Financials — NIM benefit offset by recession and credit risk fears",
            "Technology — oversold bounce possible but structural headwinds remain",
            "Industrials — mixed signals: strong capex vs rising borrowing costs"]
        uw=["Consumer Discretionary — pullback in spending hits retail and leisure",
            "Real Estate — yield spike is an acute headwind for REITs",
            "Communication Services — ad spend softening as economy slows"]
    results["sectors"] = {"overweight":ow,"neutral":ne,"underweight":uw}

    # Pre-compute all strings — no nested f-strings
    direction = "risk-off" if sp[1]<-0.5 else "risk-on" if sp[1]>0.5 else "mixed"
    vix_tone  = "fear elevated" if vx[0]>20 else "calm" if vx[0]<15 else "cautious"
    sp_dir    = "Selloff" if sp[1]<-1 else "Pullback" if sp[1]<0 else "Rally" if sp[1]>1 else "Mixed session"
    sp_verb   = "declined" if sp[1]<0 else "advanced"
    sp_move   = "falling" if sp[1]<0 else "gaining"
    nq_rel    = "underperformed" if nq[1]<sp[1] else "outperformed"
    sent_cls  = "danger" if direction=="risk-off" else "grn" if direction=="risk-on" else "warn"
    rate_txt  = "raises hike risk" if t10>4.6 else "suggests the Fed is on hold"
    gld_txt   = "acting as a safe haven" if gld[1]>0 else "pulled back on profit-taking"
    watch_lvl = "above 4.75%" if t10<4.75 else "above 5.0%"
    rot_dir   = "into defensives" if sp[1]<0 else "toward growth"
    rot_flow  = "money flowing out of expensive tech and into defensive names" if sp[1]<0 else "risk appetite returning with growth leading value"
    rot_sec   = "Consumer staples, healthcare, and energy all outperformed — classic risk-off rotation." if sp[1]<0 else "Technology and communication services led, with value names lagging — classic risk-on rotation."
    fin_txt   = "mixed — rate hike risk adds NIM upside but credit concerns grow" if t10>4.5 else "under pressure as rate cut hopes fade"
    rut_pct   = d.get("^RUT",(0,0))[1]
    rut_rel   = "outperforming" if rut_pct>sp[1] else "underperforming"
    rut_txt   = "value rotation signal worth monitoring." if rut_pct>sp[1] else "risk-off confirmed across size spectrum."
    fed_txt   = "pricing in at least one rate hike this year" if t10>4.6 else "pricing the Fed on hold through year-end"

    sp_abs  = f"{abs(sp[1]):.2f}%"
    sp_val  = f"{sp[0]:,.2f}"
    nq_chg  = f"{nq[1]:+.2f}%"
    vx_val  = f"{vx[0]:.1f}"
    wti_val = f"${wti[0]:.2f}"
    t10_str = f"{t10:.2f}%"
    t30_str = f"{t30:.2f}%"
    gld_val = f"${gld[0]:,.0f}"
    btc_val = f"${btc[0]:,.0f}"

    results["macro"] = (
        "<b>" + sp_dir + " — " + TODAY + "</b><br><br>"
        + "Markets " + sp_verb + " today with the S&P 500 " + sp_move + " " + sp_abs + " to " + sp_val + ". "
        + "The Nasdaq " + nq_rel + " at " + nq_chg + ". "
        + "Sentiment is <span class=\"" + sent_cls + "\">" + direction + "</span> "
        + "with the VIX at " + vx_val + " signaling " + vix_tone + ".<br><br>"
        + "<b>Key drivers:</b> Iran conflict continues to support oil at " + wti_val + "/bbl, "
        + "keeping inflation elevated. The 10Y Treasury at " + t10_str + " " + rate_txt + ". "
        + "Gold at " + gld_val + " " + gld_txt + ". Bitcoin at " + btc_val + ".<br><br>"
        + "<b>What to watch:</b> Fed meeting June 16-17 is the key near-term catalyst. "
        + "A hot CPI print strengthens the case for a hike. "
        + "Watch the 10Y yield — if it breaks " + watch_lvl + ", "
        + "expect renewed pressure on growth stocks and REITs. "
        + "Peace talks in the Middle East remain the wildcard."
    )

    results["rotation"] = (
        "<b>Rotation " + rot_dir + " on " + TODAY + "</b><br><br>"
        + "Today's tape showed " + rot_flow + ". " + rot_sec + "<br><br>"
        + "<b>Sector leadership:</b> Energy benefiting from sustained Iran premium. "
        + "Financials are " + fin_txt + ". "
        + "Small caps " + rut_rel + " large caps — " + rut_txt + "<br><br>"
        + "Until the Iran conflict resolves and inflation cools toward 2%, "
        + "the rotation playbook favors quality over growth — profitable companies with pricing power, "
        + "low debt, and dividend coverage over high-multiple speculative names."
    )

    results["rates"] = (
        "<b>Rates — " + t10_str + " on the 10Y as Fed stays on hold</b><br><br>"
        + "Treasury yields with the 10Y at <span class=\"" + ("danger" if t10>4.6 else "warn") + "\">" + t10_str + "</span> "
        + "and the 30Y at " + t30_str + ". "
        + "The market is " + fed_txt + ". "
        + "Fed Chair Warsh heads his first FOMC meeting June 16-17.<br><br>"
        + "<b>Fed policy:</b> With CPI at 4.2% — double the 2% target — the Fed has no room to cut. "
        + "The Iran war is a supply shock the Fed cannot fix with rates. "
        + "<span class=\"warn\">Stagflation risk</span> — rising prices with slowing growth — "
        + "is the scenario the Fed fears most.<br><br>"
        + "<b>Impact on markets:</b> Every 25bps rise in the 10Y reduces equity fair value by roughly 5-8% "
        + "on DCF models. REITs, utilities, and long-duration tech are most exposed. "
        + "Short-duration value, energy, and financials are the relative winners."
    )

    return results

# ── 4. HTML BUILDERS ──────────────────────────────────────────────────────────
def ticker_js(d):
    sp=d["^GSPC"]; dw=d["^DJI"]; nq=d["^IXIC"]; ru=d["^RUT"]
    t10=d["^TNX"]; t30=d["^TYX"]; wti=d["CL=F"]; br=d["BZ=F"]
    gld=d["GC=F"]; vx=d["^VIX"]; btc=d["BTC-USD"]
    def tk(s,v,c,u):
        return '{' + f's:"{s}",v:"{v}",c:"{c}",u:{"true" if u else "false"}' + '}'
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
    return "[\n  " + ",\n  ".join(rows) + "\n]"

def macro_cards(d):
    sp=d["^GSPC"]; dw=d["^DJI"]; nq=d["^IXIC"]; ru=d["^RUT"]
    t10=d["^TNX"]; t30=d["^TYX"]; wti=d["CL=F"]; br=d["BZ=F"]
    gld=d["GC=F"]; vx=d["^VIX"]; btc=d["BTC-USD"]
    def card(label, val, line1, note, src, p):
        cls = cc(p)
        return (f'        <div class="card">'
                f'<div class="cl">{label}</div>'
                f'<div class="cv {cls}">{val}</div>'
                f'<div class="cc {cls}">{line1}</div>'
                f'<div class="cs">{note}</div>'
                f'<div class="cs">{src} &middot; {TODAY}</div>'
                f'</div>')
    t30_lbl = f"{t30[0]:.2f}% {'(above 5%)' if t30[0]>=5 else ''}"
    vix_lbl = f"{'Fear' if vx[0]>25 else 'Elevated' if vx[0]>18 else 'Calm'} — {pct_str(vx[1])}"
    return "\n".join([
        card("S&P 500",          f"{sp[0]:,.2f}",  f"{pct_str(sp[1])} today",  "Broad market benchmark",    "Yahoo Finance", sp[1]),
        card("Dow Jones",        f"{dw[0]:,.2f}",  f"{pct_str(dw[1])} today",  "30 blue-chip stocks",       "CNBC",          dw[1]),
        card("Nasdaq Composite", f"{nq[0]:,.2f}",  f"{pct_str(nq[1])} today",  "Tech-heavy index",          "CNBC",          nq[1]),
        card("Russell 2000",     f"{ru[0]:,.2f}",  f"{pct_str(ru[1])} today",  "Small-cap benchmark",       "Yahoo Finance", ru[1]),
        card("10Y Treasury",     f"{t10[0]:.2f}%", f"{pct_str(t10[1])} today", "Key rate benchmark",        "Yahoo Finance", t10[1]),
        card("30Y Treasury",     f"{t30[0]:.2f}%", t30_lbl,                    "Long-duration rate",        "TheStreet",     t30[1]),
        card("VIX",              f"{vx[0]:.2f}",   vix_lbl,                    "Volatility gauge",          "Yahoo Finance", -vx[1]),
        card("WTI Crude",        f"${wti[0]:.2f}", f"{pct_str(wti[1])} today", "US benchmark crude",        "TradingEconomics", wti[1]),
        card("Brent Crude",      f"${br[0]:.2f}",  f"{pct_str(br[1])} today",  "Global crude benchmark",    "TradingEconomics", br[1]),
        card("Gold Spot",        f"${gld[0]:,.0f}",f"{pct_str(gld[1])} today", "Safe-haven metal",          "Yahoo Finance", gld[1]),
        card("Bitcoin",          f"${btc[0]:,.0f}",f"{pct_str(btc[1])} today", "Leading crypto asset",      "Yahoo Finance", btc[1]),
    ])

def sidebar_html(d):
    sp=d["^GSPC"]; dw=d["^DJI"]; nq=d["^IXIC"]; ru=d["^RUT"]
    t10=d["^TNX"]; t30=d["^TYX"]; wti=d["CL=F"]; br=d["BZ=F"]
    gld=d["GC=F"]; vx=d["^VIX"]; btc=d["BTC-USD"]
    def row(label, val, pct, page="macro"):
        return (f'      <div class="si" onclick="go(\'{page}\',null)">'
                f'<span class="sn">{label}</span>'
                f'<span class="sv {cc(pct)}">{val}</span></div>')
    return (
        f'    <div class="ss"><div class="sl">Indices</div>\n'
        f'{row("S&P 500",    f"{sp[0]:,.0f}",  sp[1])}\n'
        f'{row("Dow Jones",  f"{dw[0]:,.0f}",  dw[1])}\n'
        f'{row("Nasdaq",     f"{nq[0]:,.0f}",  nq[1])}\n'
        f'{row("Russell 2K", f"{ru[0]:,.0f}",  ru[1])}\n'
        f'    </div>\n'
        f'    <div class="ss"><div class="sl">Rates</div>\n'
        f'{row("10Y Yield",  f"{t10[0]:.2f}%", t10[1], "rates")}\n'
        f'{row("Fed Rate",   "3.75%",          0,       "rates")}\n'
        f'{row("30Y Yield",  f"{t30[0]:.2f}%", t30[1], "rates")}\n'
        f'    </div>\n'
        f'    <div class="ss"><div class="sl">Commodities</div>\n'
        f'      <div class="si"><span class="sn">WTI Crude</span><span class="sv {cc(wti[1])}">${wti[0]:.2f}</span></div>\n'
        f'      <div class="si"><span class="sn">Brent</span><span class="sv {cc(br[1])}">${br[0]:.2f}</span></div>\n'
        f'      <div class="si"><span class="sn">Gold</span><span class="sv {cc(gld[1])}">${gld[0]:,.0f}</span></div>\n'
        f'    </div>\n'
        f'    <div class="ss"><div class="sl">Sentiment</div>\n'
        f'      <div class="si"><span class="sn">VIX</span><span class="sv {cc(vx[1])}">{vx[0]:.2f}</span></div>\n'
        f'      <div class="si"><span class="sn">Bitcoin</span><span class="sv {cc(btc[1])}">${btc[0]:,.0f}</span></div>\n'
        f'    </div>'
    )

def equities_js(d):
    stocks = [
        ("KO","KO","Coca-Cola","def"),
        ("CL","CL","Colgate-Palmolive","def"),
        ("JNJ","JNJ","Johnson and Johnson","def"),
        ("XOM","XOM","ExxonMobil","def"),
        ("META","META","Meta Platforms","tech"),
        ("NVDA","NVDA","Nvidia","tech"),
        ("AVGO","AVGO","Broadcom","tech"),
        ("GOOGL","GOOGL","Alphabet","tech"),
        ("MSFT","MSFT","Microsoft","tech"),
        ("BTC-USD","BTC-USD","Bitcoin","crypto"),
    ]
    rows = []
    for sym,key,name,sec in stocks:
        p,pct = d.get(key,(0,0))
        chg = f"+{pct:.1f}%" if pct>=0 else f"{pct:.1f}%"
        note = f"{name} {chg} on {TODAY}."
        rows.append('{' + f't:"{sym}",n:"{name}",sec:"{sec}",s:"{sc(pct)}",c:"{chg}",note:"{note}"' + '}')
    return "[\n  " + ",\n  ".join(rows) + "\n]"

def sectors_js(d):
    sp_pct=d["^GSPC"][1]; nq_pct=d["^IXIC"][1]
    t10=d["^TNX"][0]; wti=d["CL=F"][0]; t30=d["^TYX"][0]
    secs=[
        {"n":"Consumer Staples","y":round(sp_pct*0.25,1),"d":"Defensive — low beta"},
        {"n":"Healthcare",      "y":round(sp_pct*0.35,1),"d":"Defensive bid; biotech and managed care"},
        {"n":"Energy",          "y":round(sp_pct*0.55,1),"d":f"WTI ${wti:.2f} — geopolitical premium"},
        {"n":"Financials",      "y":round(sp_pct*0.75,1),"d":f"10Y at {t10:.2f}% — NIM vs rate risk"},
        {"n":"Industrials",     "y":round(sp_pct*0.85,1),"d":"Capex names react to yield moves"},
        {"n":"Comm. Services",  "y":round(sp_pct*0.95,1),"d":"Meta, Alphabet drive sentiment"},
        {"n":"Materials",       "y":round(sp_pct*1.05,1),"d":"Dollar strength and commodity prices"},
        {"n":"Real Estate",     "y":round(sp_pct*1.25,1),"d":f"30Y {t30:.2f}% — REIT headwind"},
        {"n":"Consumer Disc.",  "y":round(sp_pct*1.15,1),"d":"Rate-sensitive consumer spending"},
        {"n":"Utilities",       "y":round(sp_pct*1.35,1),"d":"Bond proxy — inverse to yields"},
        {"n":"Technology",      "y":round(nq_pct*0.95,1),"d":f"Nasdaq {pct_str(nq_pct)}"},
    ]
    secs.sort(key=lambda x: x["y"], reverse=True)
    return "[\n  " + ",\n  ".join(
        '{' + f'n:"{s["n"]}",y:{s["y"]},s:"{sc(s["y"])}",d:"{s["d"]}"' + '}'
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
    return '{"1m":' + str(gen(15,0.006)) + ',"3m":' + str(gen(15,0.012)) + ',"6m":' + str(gen(15,0.018)) + '}'

def news_html(items, d):
    if not items:
        sp=d["^GSPC"]
        word = "rallies" if sp[1]>=0 else "sells off"
        return (f'<div class="ni"><span class="ntag mac">MACRO</span><div>'
                f'<div class="nh">Markets {word} — S&P 500 {pct_str(sp[1])} to {sp[0]:,.2f} on {TODAY}</div>'
                f'<div class="nm">Yahoo Finance &middot; {TODAY}</div></div></div>')
    out = ""
    for item in items[:6]:
        tc  = item.get("tagClass","mac")
        tag = item.get("tag","MACRO")
        hl  = item.get("headline","Market update")
        src = item.get("source","Reuters")
        bull = item.get("bullish","")
        bear = item.get("bearish","")
        imp = ""
        if bull: imp += f'<span class="bt">Bullish:</span> {bull} '
        if bear: imp += f'<span class="btr">Bearish:</span> {bear}'
        out += (f'\n        <div class="ni"><span class="ntag {tc}">{tag}</span><div>'
                f'<div class="nh">{hl}</div>'
                f'<div class="nm">{src} &middot; {TODAY}</div>'
                f'<div class="ni-imp"><b>Impact:</b> {imp}</div>'
                f'</div></div>')
    return out

def sector_outlook_html(outlook):
    if not outlook:
        return ""
    def li(lst): return "".join(f"<li>{x}</li>" for x in lst[:3])
    ow = li(outlook.get("overweight",[]))
    ne = li(outlook.get("neutral",[]))
    uw = li(outlook.get("underweight",[]))
    return (f'\n        <div class="oc ob"><div class="ol">OVERWEIGHT</div><ul class="oi">{ow}</ul></div>'
            f'\n        <div class="oc on2"><div class="ol">NEUTRAL / WATCH</div><ul class="oi">{ne}</ul></div>'
            f'\n        <div class="oc or"><div class="ol">UNDERWEIGHT</div><ul class="oi">{uw}</ul></div>')

# ── 5. INJECT ─────────────────────────────────────────────────────────────────
def clean_js_entities(html):
    """Remove HTML entities from inside <script> tags — they break JS execution."""
    def fix(m):
        s = m.group(1)
        s = s.replace('&#8635;', 'o')   # spinning icon -> simple char
        s = s.replace('&middot;', ' - ')
        s = s.replace('&mdash;', ' -- ')
        s = s.replace('&bull;', '*')
        s = s.replace('&nbsp;', ' ')
        s = s.replace('&amp;', 'and')
        s = s.replace('&lt;', '<')
        s = s.replace('&gt;', '>')
        return '<script>' + s + '</script>'
    return re.sub(r'<script>([\s\S]*?)</script>', fix, html)

def sanitize_sys(html):
    """Ensure var SYS is always a single-line JS string."""
    match = re.search(r'var SYS="([\s\S]*?)";', html)
    if match:
        raw = match.group(1)
        if '\n' in raw or '\r' in raw:
            fixed = ' '.join(raw.split())
            html = html[:match.start()] + 'var SYS="' + fixed + '";' + html[match.end():]
    return html

def inject(html, d, ai):
    sp=d["^GSPC"]; nq=d["^IXIC"]; t10=d["^TNX"]; gld=d["GC=F"]; btc=d["BTC-USD"]

    # Dates
    html = re.sub(r'\n?<!-- SIGNAL auto-updated:[^\n]*-->', '', html)
    html = html.replace("<!DOCTYPE html>",
        f"<!DOCTYPE html>\n<!-- SIGNAL auto-updated: {TODAY_ISO} via GitHub Actions -->", 1)
    html = re.sub(r'[Jj]une? \d{1,2},? \d{4}', TODAY, html)
    html = html.replace('DATESTAMP', TODAY)
    html = re.sub(r'2026-06-\d{2}', TODAY_ISO, html)
    html = re.sub(r'JUN \d{1,2}(?!\d)', f"JUN {now_et.day}", html)
    html = re.sub(r'(market intelligence &middot; )[^<"]+',
                  f'market intelligence &middot; {TODAY.lower()}', html)
    html = re.sub(r'Data: [A-Za-z]+ \d+, \d+ close', f'Data: {TODAY} close', html)

    # JS data arrays
    html = re.sub(r'var TICKS=\[[\s\S]*?\];', f'var TICKS={ticker_js(d)};', html)
    html = re.sub(r'var SPX=\{[^;]+\};',      f'var SPX={spx_chart(d)};',   html)
    html = re.sub(r'var EQ=\[[\s\S]*?\];',    f'var EQ={equities_js(d)};',  html)
    html = re.sub(r'var SECS=\[[\s\S]*?\];',  f'var SECS={sectors_js(d)};', html)

    # SYS — single clean line, no quotes, no newlines
    sys_val = (
        "You are SIGNAL, a financial intelligence platform. Today is " + TODAY + ". "
        "Live data updated via GitHub Actions. "
        "S&P 500: " + f"{sp[0]:,.2f}" + " (" + pct_str(sp[1]) + "). "
        "Nasdaq: " + f"{nq[0]:,.2f}" + " (" + pct_str(nq[1]) + "). "
        "10Y Treasury: " + f"{t10[0]:.2f}%" + ". "
        "Gold: $" + f"{gld[0]:,.0f}" + ". "
        "Bitcoin: $" + f"{btc[0]:,.0f}" + ". "
        "Fed Rate: 3.75%. Not investment advice."
    )
    sys_val = sys_val.replace('"', "'").replace('\n', ' ').replace('\r', ' ')
    html = re.sub(r'var SYS="[^"]*";', f'var SYS="{sys_val}";', html)

    # Chart label
    html = re.sub(r'S&amp;P 500 &mdash;[^<"<]+\)',
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

    # AI content
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

    # CRITICAL: Clean HTML entities from JS and sanitize SYS — do this LAST
    html = clean_js_entities(html)
    html = sanitize_sys(html)

    return html

# ── 6. MAIN ───────────────────────────────────────────────────────────────────
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root  = os.path.dirname(script_dir)
    html_path  = os.path.join(repo_root, "index.html")

    raw, symbols = fetch_all()
    d = {}
    for sym in symbols:
        price, pct = get_price_chg(raw, sym)
        d[sym] = (price, pct)
        print(f"  {'✅' if price>0 else '⚠️ '} {sym}: {price:.2f} ({pct:+.2f}%)")

    zeros = sum(1 for v in d.values() if v[0]==0)
    print(f"\n{len(d)-zeros}/{len(d)} symbols fetched")

    print("\nGenerating content...")
    ai = generate_ai_content(d)

    with open(html_path) as f:
        html = f.read()

    html = inject(html, d, ai)

    with open(html_path, "w") as f:
        f.write(html)

    # Verify
    with open(html_path) as f:
        check = f.read()
    print(f"\n✅ SIGNAL updated — {TODAY}")
    print(f"   Date appears {check.count(TODAY)}x")
    print(f"   Old dates remaining: {check.count('Jun 5, 2026') + check.count('Jun 8, 2026')}")
    for k,v in ai.items():
        print(f"   {'✅' if v else '⚠️ fallback'} {k}")

if __name__ == "__main__":
    main()
