import asyncio
import os
import random
import time
from typing import Dict

import httpx
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

ANOMALY_SERVICE_URL = os.getenv(
    "ANOMALY_SERVICE_URL",
    "http://anomaly-detector:8001",
)

app = FastAPI(title="SignalGuard Demo Application")

# Prometheus metrics
REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total HTTP requests",
    ["endpoint", "status"],
)
ERROR_COUNT = Counter(
    "app_request_errors_total",
    "Total error responses",
    ["endpoint"],
)
REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds",
    "Request latency in seconds",
    ["endpoint"],
)

ORDERS_TOTAL = Counter(
    "app_orders_total",
    "Total simulated orders",
)
PAYMENTS_TOTAL = Counter(
    "app_payments_total",
    "Total simulated successful payments",
)

# In memory stats for the custom dashboard
stats = {
    "total_requests": 0,
    "total_errors": 0,
    "per_service": {
        "orders": {"requests": 0, "errors": 0},
        "payments": {"requests": 0, "errors": 0},
    },
}

# Serve the static dashboard
app.mount(
    "/dashboard",
    StaticFiles(directory="static", html=True),
    name="dashboard",
)


@app.get("/", response_class=HTMLResponse)
async def root() -> HTMLResponse:
    """Redirect root to dashboard."""
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.get("/health")
async def health():
    return {"status": "ok"}


def record_request(endpoint: str, status: int, duration: float, is_error: bool) -> None:
    REQUEST_COUNT.labels(endpoint=endpoint, status=str(status)).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
    stats["total_requests"] += 1
    stats["per_service"][endpoint]["requests"] += 1

    if is_error:
        ERROR_COUNT.labels(endpoint=endpoint).inc()
        stats["total_errors"] += 1
        stats["per_service"][endpoint]["errors"] += 1


async def simulate_request(endpoint: str) -> Dict:
    """Simulate work for a given endpoint and update metrics."""
    start = time.perf_counter()

    # Simulate processing time
    base_latency = random.uniform(0.03, 0.3)

    # Occasionally create a latency spike
    if random.random() < 0.05:
        base_latency += random.uniform(0.3, 0.8)

    await asyncio.sleep(base_latency)

    # Base error probability
    if endpoint == "orders":
        error_prob = 0.08
    else:
        error_prob = 0.12

    # Occasionally simulate an incident burst
    if random.random() < 0.04:
        error_prob = 0.6

    is_error = random.random() < error_prob
    status_code = 500 if is_error else 200

    if endpoint == "orders" and not is_error:
        ORDERS_TOTAL.inc()
    if endpoint == "payments" and not is_error:
        PAYMENTS_TOTAL.inc()

    duration = time.perf_counter() - start
    record_request(endpoint, status_code, duration, is_error)

    return {
        "endpoint": endpoint,
        "status": status_code,
        "duration": duration,
        "error": is_error,
    }


@app.get("/orders")
async def orders():
    result = await simulate_request("orders")
    if result["status"] != 200:
        return JSONResponse(
            {"detail": "Order processing failed", "meta": result},
            status_code=500,
        )
    return {"message": "Order processed", "meta": result}


@app.get("/payments")
async def payments():
    result = await simulate_request("payments")
    if result["status"] != 200:
        return JSONResponse(
            {"detail": "Payment failed", "meta": result},
            status_code=500,
        )
    return {"message": "Payment processed", "meta": result}


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/api/dashboard/summary")
async def dashboard_summary():
    total_requests = stats["total_requests"]
    total_errors = stats["total_errors"]
    error_rate = (
        total_errors / total_requests if total_requests > 0 else 0.0
    )

    services = {}
    for svc, svc_stats in stats["per_service"].items():
        svc_req = svc_stats["requests"]
        svc_err = svc_stats["errors"]
        svc_err_rate = svc_err / svc_req if svc_req > 0 else 0.0
        services[svc] = {
            "requests": svc_req,
            "errors": svc_err,
            "errorRate": svc_err_rate,
        }

    return {
        "totalRequests": total_requests,
        "totalErrors": total_errors,
        "errorRate": error_rate,
        "services": services,
    }


@app.get("/api/dashboard/anomalies")
async def dashboard_anomalies():
    """Proxy anomalies from anomaly service to keep calls same origin for the browser."""
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{ANOMALY_SERVICE_URL}/api/anomalies",
                timeout=3.0,
            )
            r.raise_for_status()
            return JSONResponse(r.json())
    except Exception:
        return JSONResponse(
            {
                "status": "error",
                "message": "Anomaly service unavailable",
            },
            status_code=503,
        )


async def traffic_loop():
    """Background loop that creates synthetic traffic."""
    while True:
        # A few requests per tick
        for _ in range(5):
            endpoint = random.choice(["orders", "payments"])
            asyncio.create_task(simulate_request(endpoint))
        await asyncio.sleep(1.0)


@app.on_event("startup")
async def on_startup():
    asyncio.create_task(traffic_loop())
