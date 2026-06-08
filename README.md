# SIGNAL — Market Intelligence Platform
### Auto-updating financial dashboard powered by Claude AI

> Live market data · Updated daily after close · Deployed via GitHub Pages

---

## What This Is

A Bloomberg-style market intelligence dashboard that:
- **Auto-updates every weekday at 6:30 PM ET** via GitHub Actions
- Pulls live price data for indices, treasuries, commodities, equities, and crypto
- Feeds current market context to a Claude AI research assistant
- Deploys automatically to GitHub Pages — no server required

---

## Setup Instructions (One-Time)

### 1. Create your GitHub repository
```bash
git init signal-market-intelligence
cd signal-market-intelligence
# Add all files from this folder
git add .
git commit -m "Initial SIGNAL deployment"
git remote add origin https://github.com/YOUR_USERNAME/signal-market-intelligence.git
git push -u origin main
```

### 2. Enable GitHub Pages
- Go to your repo → **Settings** → **Pages**
- Source: **Deploy from a branch**
- Branch: `main` · Folder: `/ (root)`
- Save → your site will be live at `https://YOUR_USERNAME.github.io/signal-market-intelligence/`

### 3. Enable GitHub Actions
- Go to **Settings** → **Actions** → **General**
- Under "Workflow permissions" → select **Read and write permissions**
- Save

### 4. That's it
The workflow at `.github/workflows/update.yml` will run automatically every weekday at 6:30 PM ET. It fetches live data, rewrites `index.html`, commits, and pushes — GitHub Pages picks up the change within ~2 minutes.

---

## Manual Update
To trigger an update immediately:
- Go to your repo → **Actions** → **Daily Market Data Update** → **Run workflow**

---

## File Structure
```
signal-market-intelligence/
├── index.html                          ← The dashboard (auto-rewritten daily)
├── requirements.txt                    ← Python dependencies (yfinance, requests)
├── scripts/
│   └── update_market_data.py           ← Fetches data + regenerates index.html
└── .github/
    └── workflows/
        └── update.yml                  ← GitHub Actions schedule
```

---

## Data Sources
- **Equities & Indices**: yfinance / Yahoo Finance (free, no API key required)
- **Commodities**: yfinance futures contracts
- **AI Analysis**: Anthropic Claude API (your existing key in index.html)

---

## Customization

### Add or remove tracked stocks
Edit the `SYMBOLS` dict and `stocks` list in `scripts/update_market_data.py`

### Change update time
Edit the cron schedule in `.github/workflows/update.yml`:
```yaml
- cron: "30 23 * * 1-5"   # 6:30 PM ET (23:30 UTC), Mon–Fri
```

### Add more data points
The script is modular — each section (cards, ticker bar, sidebar, AI prompt) is a separate function.

---

*Built by Bee Aryal · SIGNAL Market Intelligence · Not investment advice*
