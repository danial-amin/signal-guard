# 📡 SignalGuard Observability Platform

**AI-ready observability stack with synthetic microservices, Prometheus metrics, anomaly detection, Grafana dashboards, and a live GitHub Pages demo (simulated).**

---

## 🔍 Overview

**SignalGuard** is an end-to-end observability demo environment designed to showcase:

* Production-grade **monitoring & observability practices**
* Instrumentation of **microservices** using Prometheus metrics
* A separate **Python anomaly detection service** that behaves like an early-stage AIOps layer
* **Grafana dashboards** for system and service health
* A **modern web dashboard** (GitHub Pages) with live-updating charts and simulated incident patterns

This project demonstrates how monitoring, metrics pipelines, anomaly detection, and dashboards can be composed into a *coherent observability platform*—the same architectural pattern used in real SRE, Ops, and AIOps workflows.

---

## 🌐 Live Demo (GitHub Pages)

### 🔸 Static Dashboard (Simulated Metrics)

A beautiful, responsive dashboard runs entirely in the browser, generating synthetic Prometheus-style metrics and anomaly detection events:

👉 **[https://danial-amin.github.io/signalguard-observability/](https://danial-amin.github.io/signalguard-observability/)**
*(Replace with your repo’s actual Pages URL)*

It uses:

* Real-time charts (Chart.js)
* Synthetic microservice metrics
* Fake anomaly detection with realistic spikes, jitter, and incident windows
* The same visual theme as your portfolio

This is perfect for interviews—no backend required.

---

## 🏗️ Architecture

```text
signalguard-observability
├── services/
│   ├── app/                   # FastAPI microservice
│   │   ├── app.py             # Routes + Prometheus metrics + synthetic load
│   │   ├── static/            # Frontend assets (for local dashboard)
│   │   └── Dockerfile
│   │
│   ├── anomaly-detector/      # Python anomaly detection service
│       ├── detector.py        # Pulls metrics from Prometheus
│       └── Dockerfile
│
├── observability/
│   ├── prometheus/            # Scrape config & rules
│   └── grafana/               # Provisioning + dashboards
│
├── docs/                      # GitHub Pages dashboard (simulated)
│   ├── index.html
│   ├── styles.css
│   └── script.js
│
├── docker-compose.yml
└── README.md
```

---

## 🚀 Features

### 🧩 1. **Synthetic Microservices (FastAPI)**

The app generates:

* Latency histograms
* Error rate spikes
* Request throughput
* Business metrics
* Background load generation

All exported as **Prometheus metrics**.

---

### 🤖 2. **Anomaly Detection Service**

A standalone microservice:

* Queries Prometheus ranges (via HTTP API)
* Computes a statistical anomaly score
* Emits:

  * `signalguard_anomaly_flag`
  * `signalguard_anomaly_score`

This models a lightweight AIOps system.

---

### 📈 3. **Prometheus & Grafana**

Auto-provisioned using Docker:

* Prometheus scrapes:

  * FastAPI microservice
  * Anomaly detector service
* Grafana dashboard JSON loads automatically
* Contains:

  * Latency p95
  * Error rate
  * Throughput
  * Anomaly score panels

---

### 💠 4. **Standalone GitHub Pages Dashboard**

* Completely static
* NO backend required
* Runs on simulated data
* Beautiful glassmorphism UI
* Real-time charts
* Synthetic anomalies
* Ideal for interviews or recruiters

---

## 🛠️ Running the Full System (Local Deployment)

**Requirements:**

* Docker
* Docker Compose

### 🔧 Step 1 — Clone Repo

```bash
git clone https://github.com/danial-amin/signalguard-observability
```

### 🔧 Step 2 — Run the stack

```bash
docker-compose build
docker-compose up
```

### 🌐 Services

| Service                 | Description                       | URL                                                                |
| ----------------------- | --------------------------------- | ------------------------------------------------------------------ |
| FastAPI Microservice    | Synthetic endpoints + metrics     | [http://localhost:8000](http://localhost:8000)                     |
| FastAPI Local Dashboard | Interactive dashboard             | [http://localhost:8000/dashboard](http://localhost:8000/dashboard) |
| Prometheus              | Metrics explorer                  | [http://localhost:9090](http://localhost:9090)                     |
| Grafana                 | Dashboards (login: admin / admin) | [http://localhost:3000](http://localhost:3000)                     |
| Anomaly Detector API    | Exposes anomaly flags             | [http://localhost:8001](http://localhost:8001)                     |

---

## 🚦 GitHub Pages Deployment (Static Demo)

This repo includes a **docs/** folder that GitHub Pages serves automatically.

### How it works:

* Every 5 seconds, the dashboard generates:

  * Synthetic request counts
  * Synthetic error rates
  * Anomaly detection patterns
* No backend required
* Perfectly safe to load anywhere

---

## 📁 Repository Structure (Expanded)

```text
docs/
 ├── index.html       # Dashboard page
 ├── styles.css       # Theme from your portfolio style
 └── script.js        # Fake metric generator + charts + anomaly logic
services/
 ├── app/
 │   ├── app.py       # FastAPI service + Prometheus instrumentation
 │   ├── static/      # For local dashboard rendering
 │   └── Dockerfile
 └── anomaly-detector/
     ├── detector.py  # Pulls Prometheus data, computes anomalies
     └── Dockerfile
observability/
 ├── prometheus.yml   # Scrape config
 └── grafana/
     └── dashboards/  # Auto-loaded Grafana dashboard JSON
docker-compose.yml     # Full stack launcher
```

---

## 🎯 Why This Project Matters (Interview-Ready Explanation)

This project demonstrates:

### ✔ **Observability Architecture**

* Microservice instrumentation
* Metrics pipelines
* Prometheus scraping
* Grafana provisioning
* Real-time monitoring

### ✔ **AIOps Foundations**

* Automated anomaly detection
* Metric-driven incident detection
* Flags + scoring + thresholds
* Modular ML microservice pattern

### ✔ **System Design Skills**

* Independent services
* Clean dockerized environment
* Clear separation of concerns
* Realistic production-like pipeline

### ✔ **Frontend + UX**

* Custom dashboard
* Charts, alerts, anomaly cards
* Modern, responsive UI

This makes you look both **engineering-strong** AND **design-aware** — a combination that companies like Kyndryl, Supercell, Samsung, and Oura *love*.

---

## 📌 Suggested Talking Points for Kyndryl

When they ask “Tell us about a recent project”:

> I recently built an observability demo platform called *SignalGuard*.
> It’s a dockerized environment that simulates a microservices ecosystem instrumented with Prometheus metrics and a separate anomaly detection service.
>
> The idea was to demonstrate how monitoring pipelines—latency, error rates, throughput, business metrics—can be augmented by a light ML layer for early-stage AIOps.
>
> It also includes a Grafana dashboard and a standalone web dashboard deployed on GitHub Pages that simulates Prometheus-style metrics for demo and interview purposes.

---

## 📜 License

MIT License

---

## 🤝 Contributions

Open to pull requests, improvements, and extensions—especially around:

* Additional anomaly detection techniques
* Predictive models
* More microservices
* Histogram-based ML inputs

---

If you want, I can also create:

* A **GIF preview** for the README
* A **badge set** (Docker, FastAPI, Prometheus, Grafana, Chart.js)
* A **short LinkedIn announcement** post
* A **portfolio section description** for danial-amin.github.io