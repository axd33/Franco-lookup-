import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

DVLA_URL = "https://driver-vehicle-licensing.api.gov.uk/vehicle-enquiry/v1/vehicles"

def dvla_lookup(reg: str) -> dict:
    headers = {
        "x-api-key": os.environ["DVLA_X_API_KEY"],
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {"registrationNumber": reg}
    r = requests.post(DVLA_URL, json=payload, headers=headers, timeout=20)
    r.raise_for_status()
    return r.json()

@app.get("/lookup")
def lookup():
    reg = request.args.get("reg", "").strip().upper().replace(" ", "")
    if not reg:
        return jsonify({"error": "Missing reg"}), 400

    dvla = dvla_lookup(reg)

    return jsonify({
        "reg": reg,
        "make": dvla.get("make"),
        "year": dvla.get("yearOfManufacture"),
        "fuel": dvla.get("fuelType"),
        "engine_cc": dvla.get("engineCapacity"),
        "colour": dvla.get("colour"),
        "mot_status": dvla.get("motStatus"),
        "tax_status": dvla.get("taxStatus"),
    })

@app.get("/")
def home():
    return "Franco Lookup OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5050"))
    app.run(host="0.0.0.0", port=port)
