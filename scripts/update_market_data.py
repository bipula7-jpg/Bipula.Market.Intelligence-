name: Daily Market Data Update

on:
  schedule:
    - cron: "30 13 * * 1-5"   # 9:30 AM ET — market open
    - cron: "05 20 * * 1-5"   # 4:05 PM ET — right after close
  workflow_dispatch:

permissions:
  contents: write

env:
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true

jobs:
  update-market-data:
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4.2.2

      - name: Set up Python
        uses: actions/setup-python@v5.6.0
        with:
          python-version: "3.12"

      - name: Cache pip dependencies
        uses: actions/cache@v4.2.3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run market data + AI content update
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: python scripts/update_market_data.py

      - name: Commit and push updated index.html
        run: |
          git config user.name  "SIGNAL Bot"
          git config user.email "signal-bot@users.noreply.github.com"
          git add index.html
          git diff --staged --quiet || git commit -m "📊 Market update — $(date -u +'%Y-%m-%d %H:%M UTC')"
          git push
