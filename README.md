# Selecta's Dashboards

This repository hosts interactive web dashboards automatically built and deployed by OpenClaw.

## Live Sites
- 🤖 **[Physical AI Market Graph](https://selectacentaur.github.io/market-graph/)**: An interactive force-directed graph tracking the humanoid robotics and physical AI market ecosystem, complete with daily intelligence feeds.
- 🏔️ **[Mt. Hood Training Tracker](https://selectacentaur.github.io/market-graph/training.html)**: A customized PMC (Performance Management Chart) dashboard for tracking the 13-week Mt. Hood Timberline Trail training plan. It automatically syncs with live Google Sheets workout logs to chart fitness (CTL), fatigue (ATL), form (TSB), and plan-vs-actual adherence for weekly mileage and vertical gain.

## Architecture & Automation
- **Frontend**: Lightweight, static HTML/JS utilizing D3.js and Chart.js.
- **Data Pipelines**: OpenClaw runs daily cron jobs (`build_training_ui.py` and `update_live_ui_news.py`) to fetch data from Google Drive and scrape robotics news.
- **Deployment**: The data is compiled into JSON and pushed automatically to this repository, where GitHub Pages serves it statically without requiring backend compute.
