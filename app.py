import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

DVLA_URL = "https://driver-vehicle-licensing.api.gov.uk/vehicle-enquiry/v1/vehicles"

def dvla_lookup(reg: str) -> dict:
    """
    Returns DVLA response if DVLA_X_API_KEY is present.
    Raises if DVLA returns an error.
    """
    api_key = os.environ.get("DVLA_X_API_KEY")
    if not api_key:
        raise RuntimeError("DVLA_X_API_KEY_NOT_SET")

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {"registrationNumber": reg}
    r = requests.post(DVLA_URL, json=payload, headers=headers, timeout=20)
    r.raise_for_status()
    return r.json()

def fallback_report(reg: str) -> dict:
    """
    Minimal "free report" while DVLA key is pending.
    We keep the schema stable so the Custom GPT Action can work.
    """
    return {
        "reg": reg,
        "status": "FALLBACK_ACTIVE",
        "make": None,
        "year": None,
        "fuel": None,
        "engine_cc": None,
        "colour": None,
        "mot_status": None,
        "tax_status": None,
        "note": "DVLA key pending. Add DVLA_X_API_KEY in Render env vars to enable live DVLA data."
    }

@app.get("/lookup")
def lookup():
    reg = request.args.get("reg", "").strip().upper().replace(" ", "")
    if not reg:
        return jsonify({"error": "Missing reg"}), 400

    try:
        dvla = dvla_lookup(reg)
        report = {
            "reg": reg,
            "status": "DVLA_OK",
            "make": dvla.get("make"),
            "year": dvla.get("yearOfManufacture"),
            "fuel": dvla.get("fuelType"),
            "engine_cc": dvla.get("engineCapacity"),
            "colour": dvla.get("colour"),
            "mot_status": dvla.get("motStatus"),
            "tax_status": dvla.get("taxStatus"),
        }
        return jsonify(report)
    except Exception as e:
        # Fallback mode: no key yet or DVLA temporarily unavailable
        rep = fallback_report(reg)
        rep["error"] = str(e)
        return jsonify(rep), 200

@app.get("/")
def home():
    return "Franco Lookup OK (fallback enabled if DVLA key missing)"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5050"))
    app.run(host="0.0.0.0", port=port)
