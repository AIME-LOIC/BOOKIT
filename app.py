from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import json
import os
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("BOOKIT_SECRET_KEY", "change-this-in-production")

ADMIN_USER = os.environ.get("BOOKIT_ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("BOOKIT_ADMIN_PASS", "password")


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)

    return decorated


def load_buses():
    if not os.path.exists("base.json"):
        return []
    try:
        with open("base.json") as f:
            return json.load(f) or []
    except Exception:
        return []


def save_buses(buses):
    with open("base.json", "w") as f:
        json.dump(buses, f, indent=4)


def remove_expired_buses():
    buses = load_buses()
    now = datetime.now()
    updated = []
    for b in buses:
        try:
            bus_dt = datetime.strptime(f"{b.get('date')} {b.get('time')}", "%Y-%m-%d %H:%M")
            if bus_dt + timedelta(minutes=1) > now:
                updated.append(b)
        except Exception:
            updated.append(b)
    if len(updated) != len(buses):
        save_buses(updated)
    return updated


@app.route("/")
def index():
    buses = remove_expired_buses()
    return render_template("index.html", buses=buses)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if username == ADMIN_USER and password == ADMIN_PASS:
            session["logged_in"] = True
            next_url = request.args.get("next") or url_for("admin")
            return redirect(next_url)
        error = "Invalid username or password"
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/admin")
@login_required
def admin():
    buses = remove_expired_buses()
    return render_template("admin.html", buses=buses)


@app.route("/add_bus", methods=["POST"])
@login_required
def add_buses():
    data = request.get_json(silent=True)
    if not data:
        data = request.form.to_dict()

    required = ["company_name", "from", "to", "time", "date", "price", "plate_id", "seats"]
    missing = [k for k in required if not data.get(k)]
    if missing:
        return (
            jsonify({"success": False, "message": f"Missing fields: {', '.join(missing)}"}),
            400,
        )

    try:
        seats = int(data["seats"])
        price = float(data["price"])
    except Exception:
        return (
            jsonify({"success": False, "message": "Invalid numeric value for seats or price"}),
            400,
        )

    bus = {
        "company_name": data["company_name"],
        "from": data["from"],
        "to": data["to"],
        "time": data["time"],
        "date": data["date"],
        "price": price,
        "plate_id": data["plate_id"],
        "seats": seats,
        "ready": True,
    }

    buses = load_buses()
    if any(b.get("plate_id") == bus["plate_id"] for b in buses):
        return (
            jsonify({"success": False, "message": "Bus with this plate_id already exists"}),
            400,
        )

    buses.append(bus)
    save_buses(buses)
    return jsonify({"success": True, "message": "Bus added", "bus": bus})


@app.route("/get_buses")
def get_buses():
    buses = remove_expired_buses()
    return jsonify(buses)


@app.route("/book/<plate_id>")
def book_page(plate_id):
    buses = load_buses()
    bus = next((b for b in buses if b.get("plate_id") == plate_id), None)
    if not bus:
        return render_template("book.html", bus=None, error="Bus not found")
    return render_template("book.html", bus=bus, error=None)


@app.route("/book/<plate_id>", methods=["POST"])
def book_seats(plate_id):
    data = request.get_json(silent=True) or {}
    try:
        count = int(data.get("count", 1))
    except Exception:
        return jsonify({"success": False, "message": "Invalid count"}), 400

    if count <= 0:
        return jsonify({"success": False, "message": "Count must be positive"}), 400

    buses = load_buses()
    updated = []
    seat_booked = False
    seats_left = None

    for b in buses:
        if b.get("plate_id") == plate_id:
            current = int(b.get("seats", 0))
            if current >= count:
                b["seats"] = current - count
                seats_left = b["seats"]
                seat_booked = True
        updated.append(b)

    save_buses(updated)

    if seat_booked:
        return jsonify({"success": True, "seats_left": seats_left, "message": "Seats booked successfully"})

    return jsonify({"success": False, "message": "Not enough seats or bus not found"}), 400


if __name__ == "__main__":
    app.run(port=8000, debug=True)

