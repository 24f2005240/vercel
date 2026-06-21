# api/index.py
import json
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from statistics import mean
import statistics

app = FastAPI()

# Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_methods=["POST"],  # Only allows POST
    allow_headers=["*"],
)

# Load telemetry data (you can also fetch from URL if data is online)
def load_telemetry():
    # For testing locally, you'd load from file
    # For Vercel, we'll embed the data or fetch from a URL
    # Replace this with actual data loading logic
    with open("q-vercel-latency.json") as f:
        return json.load(f)

def calculate_p95(values):
    """Calculate 95th percentile"""
    return statistics.quantiles(values, n=100)[94] if len(values) > 0 else 0

@app.post("/analytics")
def analyze_latency(request: dict):
    regions = request.get("regions", [])
    threshold_ms = request.get("threshold_ms", 180)
    
    telemetry = load_telemetry()
    
    results = []
    
    for region in regions:
        # Filter records for this region
        region_records = [r for r in telemetry if r.get("region") == region]
        
        if not region_records:
            results.append({
                "region": region,
                "avg_latency": 0,
                "p95_latency": 0,
                "avg_uptime": 0,
                "breaches": 0
            })
            continue
        
        latencies = [r.get("latency_ms", 0) for r in region_records]
        uptimes = [r.get("uptime", 0) for r in region_records]
        
        avg_latency = mean(latencies) if latencies else 0
        p95_latency = calculate_p95(latencies)
        avg_uptime = mean(uptimes) if uptimes else 0
        breaches = sum(1 for lat in latencies if lat > threshold_ms)
        
        results.append({
            "region": region,
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches
        })
    
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
