from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import json
import pandas as pd

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Handle preflight OPTIONS
@app.options("/{path:path}")
def options_handler(path: str):
    return Response(status_code=200)

# Load telemetry data
with open("q-vercel-latency.json", "r") as f:
    telemetry = json.load(f)

df = pd.DataFrame(telemetry)

@app.post("/metrics")
def metrics(payload: dict):
    regions = payload["regions"]
    threshold = payload["threshold_ms"]

    filtered = df[df["region"].isin(regions)]
    response = {}

    for region in filtered["region"].unique():
        r = filtered[filtered["region"] == region]

        response[region] = {
            "avg_latency": round(r["latency_ms"].mean(), 2),
            "p95_latency": round(r["latency_ms"].quantile(0.95), 2),
            "avg_uptime": round(r["uptime_pct"].mean(), 2),
            "breaches": int((r["latency_ms"] > threshold).sum())
        }

    return response
