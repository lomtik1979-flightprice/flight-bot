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

    import random

    # 🔥 демо генератор (всегда есть цены)
    demo_prices = [150, 180, 220, 260, 310]

    flights = []

    for p in demo_prices:
        flights.append({
            "price": p + random.randint(-20, 20),
            "dep": f"{random.randint(6,20)}:00",
            "arr": f"{random.randint(8,23)}:00"
        })

    return {"flights": flights}

if __name__ == "__main__":
    app.run(port=5000, debug=True)