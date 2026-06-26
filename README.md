# 🛰️ Pluto — AI Retail Crowd Analytics

> Real-time retail analytics powered by Computer Vision.

Pluto transforms any CCTV or webcam into an intelligent retail analytics system capable of tracking customer movement, measuring dwell time, estimating occupancy, and generating actionable business insights.

---

## 🚀 Features

- 👤 Real-time person detection using YOLOv8
- 🎯 Zone-based customer tracking
- 📈 Live occupancy monitoring
- ⏱️ Customer dwell time analysis
- 🚪 Automatic entry & exit counting
- 📊 Daily analytics report generation
- ⚠️ Crowd risk scoring
- 💾 Persistent daily state recovery
- 📄 CSV analytics export
- 🧩 Modular Python architecture

---

# Demo

> *(Demo GIF coming soon)*

![Demo](assets/demo.gif)

---

# Screenshots

### Live Detection

![Detection](assets/detection.png)

### Daily Analytics

![Analytics](assets/analytics.png)

---

# System Architecture

```
                 Camera / CCTV
                       │
                       ▼
               YOLOv8 Person Detection
                       │
                       ▼
                Custom Tracker
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
      Zone Analysis        Dwell Time
             │                   │
             └─────────┬─────────┘
                       ▼
               Analytics Engine
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
     Live Dashboard          CSV Reports
```

---

# Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Backend |
| YOLOv8 | Person Detection |
| OpenCV | Video Processing |
| CSV | Data Storage |
| Git | Version Control |

---

# Project Structure

```
retail-crowd-analytics/

├── analytics.py
├── config.py
├── detector.py
├── main.py
├── reports.py
├── storage.py
├── tracker.py
├── utils.py
│
├── daily_summary.csv
├── people_log.csv
│
├── assets/
│
└── README.md
```

---

# Analytics Generated

Pluto automatically computes:

- Total Visits
- Peak Hour
- Peak Hour Count
- Average Dwell Time
- Maximum Dwell Time
- Peak Occupancy
- Crowd Risk Score

Example:

| Date | Visits | Peak Hour | Avg Dwell | Risk |
|------|---------|-----------|------------|------|
| 2026-06-25 | 25 | 18:00 | 2.9 s | 0.10 |

---

# Use Cases

- 🛒 Retail Stores
- 🏬 Shopping Malls
- 🎓 Universities
- 🏢 Offices
- 🏥 Hospitals
- 🏪 Supermarkets

---

# Installation

Clone the repository

```bash
git clone https://github.com/rithish-dev/retail-crowd-analytics.git
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run

```bash
python main.py
```

---

# Roadmap

## ✅ Completed

- Real-time Detection
- Entry/Exit Counting
- Dwell Time
- Analytics Reports
- Risk Score
- Modular Codebase

## 🚧 In Progress

- Interactive Dashboard
- Occupancy Graphs
- Heatmaps

## 🔮 Planned

- Multi-camera Support
- Web Dashboard
- PDF Reports
- Cloud Deployment
- Email Alerts
- Queue Detection
- REST API
- Mobile Dashboard

---

# Why Pluto?

Traditional CCTV systems only record footage.

Pluto converts video streams into business intelligence by extracting customer behavior and occupancy analytics in real time.

---

# Author

**K. Rithish**

Embedded Systems • Computer Vision • AI

GitHub:
https://github.com/rithish-dev

LinkedIn:
https://www.linkedin.com/in/krithish-embedded5/

---

# License

MIT License
