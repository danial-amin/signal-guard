// --- Simple simulation state for fake observability data ---

const SIM_STATE = {
    tick: 0,
    totalRequests: 0,
    totalErrors: 0,
    services: {
      orders: {
        requests: 0,
        errors: 0,
        baselineErrorRate: 0.04
      },
      payments: {
        requests: 0,
        errors: 0,
        baselineErrorRate: 0.08
      }
    }
  };
  
  // Occasionally create incident windows
  function getIncidentMultiplier(serviceName, tick) {
    // Periodic spikes (every ~60–90 seconds)
    const period = serviceName === "orders" ? 14 : 18;
    const phaseOffset = serviceName === "orders" ? 0 : 4;
    const inSpikeWindow = ((tick + phaseOffset) % period) === 0;
  
    if (inSpikeWindow) {
      return 5 + Math.random() * 2; // big spike
    }
  
    // Small random jitters
    if (Math.random() < 0.15) {
      return 1.5 + Math.random();
    }
  
    return 1.0;
  }
  
  // Generate a single summary "tick"
  function generateFakeSummary() {
    SIM_STATE.tick += 1;
  
    const servicesOut = {};
    let totalReqDelta = 0;
    let totalErrDelta = 0;
  
    for (const [name, svc] of Object.entries(SIM_STATE.services)) {
      // Base load per tick
      const baseLoad =
        name === "orders"
          ? 40 + Math.round(Math.random() * 20)
          : 25 + Math.round(Math.random() * 15);
  
      // Error rate with occasional spikes
      const multiplier = getIncidentMultiplier(name, SIM_STATE.tick);
      const noisyErrorRate =
        svc.baselineErrorRate * multiplier * (0.8 + Math.random() * 0.4);
  
      // Clip error rate to [0, 0.6]
      const errorRate = Math.min(0.6, Math.max(0, noisyErrorRate));
  
      const requestsDelta = baseLoad;
      const errorsDelta = Math.round(requestsDelta * errorRate);
  
      svc.requests += requestsDelta;
      svc.errors += errorsDelta;
  
      totalReqDelta += requestsDelta;
      totalErrDelta += errorsDelta;
  
      servicesOut[name] = {
        requests: svc.requests,
        errors: svc.errors,
        errorRate: svc.requests > 0 ? svc.errors / svc.requests : 0
      };
    }
  
    SIM_STATE.totalRequests += totalReqDelta;
    SIM_STATE.totalErrors += totalErrDelta;
  
    const overallErrorRate =
      SIM_STATE.totalRequests > 0
        ? SIM_STATE.totalErrors / SIM_STATE.totalRequests
        : 0;
  
    return {
      totalRequests: SIM_STATE.totalRequests,
      totalErrors: SIM_STATE.totalErrors,
      errorRate: overallErrorRate,
      services: servicesOut
    };
  }
  
  // Derive anomaly info from the simulated summary
  function generateFakeAnomalies(summary) {
    const anomalyServices = {};
    const threshold = 0.20;
  
    for (const [name, svc] of Object.entries(summary.services || {})) {
      const er = svc.errorRate || 0;
      const score = threshold > 0 ? er / threshold : 0;
      const flag = er > threshold ? 1 : 0;
  
      anomalyServices[name] = {
        flag,
        score,
        errorRate: er
      };
    }
  
    return {
      services: anomalyServices,
      updatedAt: Date.now() / 1000
    };
  }
  
  // --- Dashboard DOM + charts wiring (same as before, but no fetch) ---
  
  const totalRequestsEl = document.getElementById("total-requests");
  const errorRateEl = document.getElementById("error-rate");
  const errorCaptionEl = document.getElementById("error-caption");
  const ordersReqEl = document.getElementById("orders-requests");
  const ordersErrEl = document.getElementById("orders-errors");
  const paymentsReqEl = document.getElementById("payments-requests");
  const paymentsErrEl = document.getElementById("payments-errors");
  const lastUpdatedEl = document.getElementById("last-updated");
  const anomalyGridEl = document.getElementById("anomaly-grid");
  
  let timeLabels = [];
  let ordersSeries = [];
  let paymentsSeries = [];
  let errorRateSeries = [];
  
  let requestsChart;
  let errorChart;
  
  function createCharts() {
    const reqCtx = document.getElementById("requests-chart").getContext("2d");
    const errCtx = document.getElementById("error-chart").getContext("2d");
  
    requestsChart = new Chart(reqCtx, {
      type: "line",
      data: {
        labels: timeLabels,
        datasets: [
          {
            label: "Orders",
            data: ordersSeries,
            tension: 0.35
          },
          {
            label: "Payments",
            data: paymentsSeries,
            tension: 0.35
          }
        ]
      },
      options: {
        responsive: true,
        scales: {
          x: {
            ticks: {
              color: "#9aa0b4",
              maxTicksLimit: 7
            },
            grid: { display: false }
          },
          y: {
            ticks: { color: "#9aa0b4" },
            grid: {
              color: "rgba(255, 255, 255, 0.06)"
            }
          }
        },
        plugins: {
          legend: {
            labels: { color: "#f5f7fb" }
          }
        }
      }
    });
  
    errorChart = new Chart(errCtx, {
      type: "line",
      data: {
        labels: timeLabels,
        datasets: [
          {
            label: "Error rate",
            data: errorRateSeries,
            tension: 0.35
          }
        ]
      },
      options: {
        responsive: true,
        scales: {
          x: {
            ticks: {
              color: "#9aa0b4",
              maxTicksLimit: 7
            },
            grid: { display: false }
          },
          y: {
            ticks: {
              color: "#9aa0b4",
              callback: (val) => (val * 100).toFixed(0) + "%"
            },
            grid: {
              color: "rgba(255, 255, 255, 0.06)"
            },
            min: 0,
            max: 0.7
          }
        },
        plugins: {
          legend: {
            labels: { color: "#f5f7fb" }
          }
        }
      }
    });
  }
  
  function pushDataPoint(summary) {
    const now = new Date();
    const label = now.toLocaleTimeString("en-GB", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit"
    });
  
    if (timeLabels.length > 20) {
      timeLabels.shift();
      ordersSeries.shift();
      paymentsSeries.shift();
      errorRateSeries.shift();
    }
  
    timeLabels.push(label);
  
    const services = summary.services || {};
    const orders = services.orders ? services.orders.requests : 0;
    const payments = services.payments ? services.payments.requests : 0;
    const errorRate = summary.errorRate || 0;
  
    ordersSeries.push(orders);
    paymentsSeries.push(payments);
    errorRateSeries.push(errorRate);
  
    requestsChart.update();
    errorChart.update();
  }
  
  function updateSummary(summary) {
    const total = summary.totalRequests || 0;
    const totalErrors = summary.totalErrors || 0;
    const errorRate = summary.errorRate || 0;
    const services = summary.services || {};
  
    totalRequestsEl.textContent = total.toLocaleString();
    errorRateEl.textContent = (errorRate * 100).toFixed(2) + "%";
  
    if (total < 300) {
      errorCaptionEl.textContent = "System is warming up";
    } else if (errorRate < 0.05) {
      errorCaptionEl.textContent = "System is healthy";
    } else if (errorRate < 0.15) {
      errorCaptionEl.textContent = "Mild degradation detected";
    } else {
      errorCaptionEl.textContent = "Incident likely ongoing";
    }
  
    const orders = services.orders || { requests: 0, errors: 0 };
    ordersReqEl.textContent = orders.requests.toLocaleString();
    ordersErrEl.textContent = `${orders.errors} errors`;
  
    const payments = services.payments || { requests: 0, errors: 0 };
    paymentsReqEl.textContent = payments.requests.toLocaleString();
    paymentsErrEl.textContent = `${payments.errors} errors`;
  
    lastUpdatedEl.textContent =
      "Updated: " +
      new Date().toLocaleTimeString("en-GB", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit"
      });
  
    pushDataPoint(summary);
  }
  
  function renderAnomalies(data) {
    anomalyGridEl.innerHTML = "";
  
    const services = data.services || {};
    if (Object.keys(services).length === 0) {
      const div = document.createElement("div");
      div.className = "anomaly-card";
      div.innerHTML =
        "<div class='anomaly-body'>No anomaly data available.</div>";
      anomalyGridEl.appendChild(div);
      return;
    }
  
    Object.keys(services).forEach((name) => {
      const svc = services[name];
      const flag = svc.flag || 0;
      const score = svc.score || 0;
      const errorRate = svc.errorRate || 0;
  
      const card = document.createElement("div");
      card.className = "anomaly-card";
  
      const header = document.createElement("div");
      header.className = "anomaly-title-row";
  
      const title = document.createElement("span");
      title.textContent = name.charAt(0).toUpperCase() + name.slice(1);
  
      const badge = document.createElement("span");
      if (flag === 0 && score < 0.5) {
        badge.className = "badge-ok";
        badge.textContent = "Healthy";
      } else if (flag === 0) {
        badge.className = "badge-warn";
        badge.textContent = "Watch";
      } else if (flag === 1 && score < 2) {
        badge.className = "badge-warn";
        badge.textContent = "Degraded";
      } else {
        badge.className = "badge-danger";
        badge.textContent = "Incident";
      }
  
      header.appendChild(title);
      header.appendChild(badge);
  
      const body = document.createElement("div");
      body.className = "anomaly-body";
      body.textContent =
        flag === 0
          ? "No anomalies detected in recent error rates."
          : "Error rate significantly above normal baseline.";
  
      const metrics = document.createElement("div");
      metrics.className = "anomaly-metric";
      metrics.textContent =
        "Error rate: " +
        (errorRate * 100).toFixed(2) +
        "%  •  Score: " +
        score.toFixed(2);
  
      card.appendChild(header);
      card.appendChild(body);
      card.appendChild(metrics);
  
      anomalyGridEl.appendChild(card);
    });
  }
  
  // "Poll" function now just generates fake data instead of fetch()
  function pollOnce() {
    const summary = generateFakeSummary();
    const anomalies = generateFakeAnomalies(summary);
    updateSummary(summary);
    renderAnomalies(anomalies);
  }
  
  function startPolling() {
    createCharts();
    pollOnce();
    setInterval(pollOnce, 5000);
  }
  
  document.addEventListener("DOMContentLoaded", startPolling);
  