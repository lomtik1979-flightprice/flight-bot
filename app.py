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
    route = request.args.get("route")
    max_price = request.args.get("max_price")

    if not route:
        return {"flights": []}

    origin, dest = route.split("-")

    today = datetime.now()
    date_from = today.strftime("%d/%m/%Y")
    date_to = (today + timedelta(days=30)).strftime("%d/%m/%Y")

    url = "https://api.skypicker.com/flights"

    params = {
        "fly_from": origin,
        "fly_to": dest,
        "date_from": date_from,
        "date_to": date_to,
        "curr": "USD",
        "limit": 10
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        res = requests.get(url, params=params, headers=headers)

        if res.status_code != 200:
            return {"flights": []}

        data = res.json()

        flights = []

        for f in data.get("data", []):
            seg = f["route"][0]
            price = f["price"]

            if max_price and price > int(max_price):
                continue

            flights.append({
                "price": price,
                "dep": seg["local_departure"],
                "arr": seg["local_arrival"]
            })

        return {"flights": flights}

    except:
        return {"flights": []}


if __name__ == "__main__":
    app.run(port=5000, debug=True)