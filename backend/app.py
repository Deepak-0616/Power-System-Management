from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from model_utils import generate_predicted_dataset, validate_actual_vs_predicted

app = Flask(__name__)
CORS(app)

BASE = "../data"
UPLOADED = f"{BASE}/uploaded"
PREDICTED = f"{BASE}/predicted"
ACTUAL = f"{BASE}/actual"

for d in [UPLOADED, PREDICTED, ACTUAL]:
    os.makedirs(d, exist_ok=True)

SYSTEM = {"halted": False}

@app.route("/api/upload", methods=["POST"])
def upload():
    f = request.files["file"]
    month = request.form["month"]
    f.save(f"{UPLOADED}/{month}.csv")
    return jsonify({"status": "uploaded"})

@app.route("/api/list")
def list_months():
    return jsonify([f.replace(".csv","") for f in os.listdir(UPLOADED)])

@app.route("/api/generate", methods=["POST"])
def generate():
    if SYSTEM["halted"]:
        return jsonify({"error": "SYSTEM HALTED"}), 403

    month = request.json["month"]
    files = [f"{UPLOADED}/{f}" for f in os.listdir(UPLOADED)]
    out = f"{PREDICTED}/predicted_{month}.csv"

    generate_predicted_dataset(files, out)
    return jsonify({"status": "predicted generated"})

@app.route("/api/validate", methods=["POST"])
def validate():
    if SYSTEM["halted"]:
        return jsonify({"error": "SYSTEM HALTED"}), 403

    f = request.files["file"]
    month = request.form["month"]
    actual_path = f"{ACTUAL}/{month}.csv"
    f.save(actual_path)

    predicted_path = f"{PREDICTED}/predicted_{month}.csv"
    error, attack = validate_actual_vs_predicted(actual_path, predicted_path)

    if attack:
        SYSTEM["halted"] = True

    return jsonify({
        "error": error,
        "attack": attack,
        "halted": SYSTEM["halted"]
    })

@app.route("/api/state")
def state():
    return jsonify(SYSTEM)

if __name__ == "__main__":
    app.run(debug=True)
