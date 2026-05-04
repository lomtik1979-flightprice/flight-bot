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
    max_price = request.args.get("max_price")

    if not route:
        return {"flights": []}

    origin, dest = route.split("-")

    url = "https://api.skypicker.com/flights"

    today = datetime.now()

    # пробуем несколько диапазонов дат
    ranges = [
        (0, 3),
        (0, 7),
        (0, 30),
        (7, 60)
    ]

    def search(date_from, date_to):
        params = {
            "fly_from": origin,
            "fly_to": dest,
            "date_from": date_from,
            "date_to": date_to,
            "curr": "USD",
            "limit": 10,
            "max_stopovers": 0
        }

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        try:
            res = requests.get(url, params=params, headers=headers)

            if res.status_code != 200:
                return []

            return res.json().get("data", [])
        except:
            return []

    # ищем по разным датам
    for r in ranges:
        df = (today + timedelta(days=r[0])).strftime("%d/%m/%Y")
        dt = (today + timedelta(days=r[1])).strftime("%d/%m/%Y")

        results = search(df, dt)

        if results:
            flights = []

            for f in results:
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

    return {"flights": []}

if __name__ == "__main__":
    app.run(port=5000, debug=True)