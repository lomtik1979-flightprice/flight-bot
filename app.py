from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

# 🏠 главная
@app.route("/")
def index():
    return render_template("index.html")

# 🌍 карта
@app.route("/map")
def map_view():
    return render_template("map.html")

# ✈️ API с фильтром цены
@app.route("/api/flights")
def get_flights():
@app.route("/api/flights")
def get_flights():
    route = request.args.get("route")

    if not route:
        return {"flights": []}

    origin, dest = route.split("-")

    url = "https://api.skypicker.com/flights"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        res = requests.get(url, params={
            "fly_from": origin,
            "fly_to": dest,
            "date_from": "01/06/2026",
            "date_to": "30/06/2026",
            "curr": "USD",
            "limit": 5
        }, headers=headers)

        data = res.json().get("data", [])

        flights = []

        for f in data:
            seg = f["route"][0]

            flights.append({
                "price": f["price"],
                "dep": seg["local_departure"][:16],
                "arr": seg["local_arrival"][:16]
            })

        # ✅ если API дал данные
        if flights:
            return {"flights": flights}

    except:
        pass

    # 🔥 fallback (если API не дал ничего)
    demo = [
        {"price": 180, "dep": "08:00", "arr": "12:00"},
        {"price": 250, "dep": "14:00", "arr": "18:00"},
        {"price": 320, "dep": "20:00", "arr": "00:00"}
    ]

    return {"flights": demo}

if __name__ == "__main__":
    app.run(port=5000, debug=True)