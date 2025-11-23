import asyncio
import os
import time
from typing import Dict

import httpx
from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST

PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")

app = FastAPI(title="SignalGuard Anomaly Service")

ANOMALY_FLAG = Gauge(
    "signalguard_anomaly_flag",
    "Binary anomaly flag per service",
    ["service"],
)
ANOMALY_SCORE = Gauge(
    "signalguard_anomaly_score",
    "Relative anomaly score per service",
    ["service"],
)

state: Dict[str, Dict] = {
    "orders": {"flag": 0, "score": 0.0, "errorRate": 0.0},
    "payments": {"flag": 0, "score": 0.0, "errorRate": 0.0},
}


async def fetch_error_rate(client: httpx.AsyncClient, service: str) -> float:
    # Query error rate over last 5 minutes for this service
    query = f'rate(app_request_errors_total{{endpoint="{service}"}}[5m])'
    resp = await client.get(
        f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": query},
        timeout=5.0,
    )
    data = resp.json()
    try:
        result = data.get("data", {}).get("result", [])
        if result:
            value = float(result[0]["value"][1])
            return value
    except Exception:
        pass
    return 0.0


async def compute_anomalies():
    services = ["orders", "payments"]
    threshold = 0.2  # toy threshold for demo

    async with httpx.AsyncClient() as client:
        for svc in services:
            error_rate = await fetch_error_rate(client, svc)
            score = error_rate / threshold if threshold > 0 else 0.0
            flag = 1 if error_rate > threshold else 0

            state[svc] = {
                "flag": flag,
                "score": score,
                "errorRate": error_rate,
            }

            ANOMALY_FLAG.labels(service=svc).set(flag)
            ANOMALY_SCORE.labels(service=svc).set(score)


async def anomaly_loop():
    while True:
        try:
            await compute_anomalies()
        except Exception as exc:
            print("Anomaly computation error:", exc, flush=True)
        await asyncio.sleep(30)


@app.on_event("startup")
async def on_startup():
    asyncio.create_task(anomaly_loop())


@app.get("/api/anomalies")
async def get_anomalies():
    return JSONResponse(
        {
            "services": state,
            "updatedAt": time.time(),
        }
    )


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
