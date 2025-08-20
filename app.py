from flask import Flask, request, jsonify, send_file
from collections import defaultdict

app = Flask(__name__, static_folder="static", static_url_path="/static")

# ---- Config ----
CAPACITY = {
    "car": 100,
    "bike": 200,
    "rickshaw": 50,
    "bus": 20
}
FEES = {
    "car": 100,
    "bike": 30,
    "rickshaw": 50,
    "bus": 200
}

# ---- State ----
parking = {
    "car": [],
    "bike": [],
    "rickshaw": [],
    "bus": []
}
earnings = defaultdict(int)

# ---- Helpers ----
def vlabel(vtype: str) -> str:
    return {
        "car": "Car",
        "bike": "Bike",
        "rickshaw": "Rickshaw",
        "bus": "Bus"
    }.get(vtype, vtype.capitalize())

def ok(msg): return (msg, 200)
def bad(msg): return (msg, 400)

# ---- Routes (Frontend) ----
@app.route("/")
def home():
    return send_file("index.html")

# ---- API Routes ----
@app.route("/enter", methods=["POST"])
def enter():
    vtype = request.form.get("type")
    vnum = request.form.get("number", "").strip()

    if not vtype or not vnum:
        return bad("⚠ Missing vehicle type or number.")

    if vtype not in parking:
        return bad("⚠ Invalid vehicle type.")

    if len(parking[vtype]) >= CAPACITY[vtype]:
        return ok(f"❌ Parking full for {vlabel(vtype)}s.")

    if vnum in parking[vtype]:
        return ok(f"⚠ {vlabel(vtype)} {vnum} is already parked.")

    parking[vtype].append(vnum)
    earnings[vtype] += FEES[vtype]
    return ok(f"✅ {vlabel(vtype)} {vnum} entered. Fee = ₹{FEES[vtype]}")

@app.route("/exit", methods=["POST"])
def exit_vehicle():
    vtype = request.form.get("type")
    vnum = request.form.get("number", "").strip()

    if not vtype or not vnum:
        return bad("⚠ Missing vehicle type or number.")

    if vtype not in parking:
        return bad("⚠ Invalid vehicle type.")

    if vnum not in parking[vtype]:
        return ok(f"❌ {vlabel(vtype)} {vnum} not found.")

    parking[vtype].remove(vnum)
    return ok(f"🚗 {vlabel(vtype)} {vnum} exited.")

@app.route("/cost", methods=["POST"])
def cost():
    vtype = request.form.get("type")
    if not vtype:
        return bad("⚠ Missing vehicle type.")
    if vtype not in earnings:
        return bad("⚠ Invalid vehicle type.")
    return ok(f"💰 Total {vlabel(vtype)} collection = ₹{earnings[vtype]}")

@app.route("/total", methods=["POST"])
def total():
    total_amt = sum(earnings.values())
    return ok(f"💵 Total amount collected = ₹{total_amt}")

@app.route("/space", methods=["POST"])
def space():
    lines = [
        f"🚘 Cars: {len(parking['car'])}/{CAPACITY['car']}",
        f"🏍️ Bikes: {len(parking['bike'])}/{CAPACITY['bike']}",
        f"🛺 Rickshaws: {len(parking['rickshaw'])}/{CAPACITY['rickshaw']}",
        f"🚌 Buses: {len(parking['bus'])}/{CAPACITY['bus']}",
    ]
    return ok("\n".join(lines))

@app.route("/state", methods=["GET"])
def state():
    """Dashboard state for the UI (JSON)."""
    return jsonify({
        "capacity": CAPACITY,
        "counts": {k: len(v) for k, v in parking.items()},
        "earnings": dict(earnings),
        "parking": parking
    })

if __name__ == "__main__":
    app.run(debug=True)
