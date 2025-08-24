from fastapi import FastAPI, Header, HTTPException, Body
from datetime import datetime, timezone

app = FastAPI(title="My Sensors API")

API_KEY = "replace-me"

SENSORS = {
    "lab-1": {
        "device_id": "lab-1",
        "ts": datetime.now(timezone.utc).isoformat(),
        "metrics": {"temp_c": 24.6, "humidity": 48.2},
        "status": "ok",
        "labels": {"room": "A1"}
    }
}

def check_auth(x_api_key: str | None):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="bad key")

@app.get("/sensors")
def list_sensors(x_api_key: str | None = Header(None)):
    check_auth(x_api_key)
    return [
        {"device_id": s["device_id"], "last_seen": s["ts"], "labels": s.get("labels", {})}
        for s in SENSORS.values()
    ]

@app.get("/sensors/{device_id}")
def read_sensor(device_id: str, x_api_key: str | None = Header(None)):
    check_auth(x_api_key)
    if device_id not in SENSORS:
        raise HTTPException(status_code=404, detail="not found")
    return SENSORS[device_id]

@app.get("/sensors/{device_id}/history")
def read_history(device_id: str, since: str | None = None, limit: int = 100,
                 x_api_key: str | None = Header(None)):
    check_auth(x_api_key)
    if device_id not in SENSORS:
        raise HTTPException(status_code=404, detail="not found")
    # Demo: return N copies of the latest reading with synthetic times
    base = SENSORS[device_id].copy()
    return [base for _ in range(min(limit, 10))]

@app.post("/sensors/{device_id}/command")
def send_command(device_id: str, payload: dict = Body(...), x_api_key: str | None = Header(None)):
    check_auth(x_api_key)
    if device_id not in SENSORS:
        raise HTTPException(status_code=404, detail="not found")
    # TODO: push to device (MQTT, etc.)
    return {"ok": True, "device_id": device_id, "accepted": payload, "message": "Command queued"}
