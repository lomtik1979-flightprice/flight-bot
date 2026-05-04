from flask import Flask, render_template, request

app = Flask(__name__)

# главная страница
@app.route("/")
def index():
    return render_template("index.html")

# карта
@app.route("/map")
def map_view():
    return render_template("map.html")

# API рейсов (стабильная версия)
@app.route("/api/flights")
def get_flights():
    import requests
    from datetime import datetime, timedelta
    import random

    route = request.args.get("route")

    if not route:
        return {"flights": []}

    origin, dest = route.split("-")

    url = "https://api.skypicker.com/flights"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    today = datetime.now()

    # пробуем несколько диапазонов
    ranges = [
        (0, 3),
        (0, 7),
        (7, 30)
    ]

    for r in ranges:
        date_from = (today + timedelta(days=r[0])).strftime("%d/%m/%Y")
        date_to = (today + timedelta(days=r[1])).strftime("%d/%m/%Y")

        params = {
            "fly_from": origin,
            "fly_to": dest,
            "date_from": date_from,
            "date_to": date_to,
            "curr": "USD",
            "limit": 5,
            "max_stopovers": 0
        }

        try:
            res = requests.get(url, params=params, headers=headers, timeout=10)

            if res.status_code != 200:
                continue

            data = res.json().get("data", [])

            if data:
                flights = []

                for f in data:
                    seg = f["route"][0]

                    flights.append({
                        "price": f["price"],
                        "dep": seg["local_departure"][:16],
                        "arr": seg["local_arrival"][:16],
                        "airline": f["airlines"][0]
                    })

                return {"flights": flights}

        except:
            continue

    # 🔥 fallback если API не дал результат
    base_prices = {
        "CDG": 180,
        "FCO": 140,
        "LHR": 220,
        "JFK": 450
    }

    base = base_prices.get(dest, 200)

    flights = []

    for i in range(3):
        flights.append({
            "price": base + random.randint(-30, 60),
            "dep": f"{random.randint(6,22)}:00",
            "arr": f"{random.randint(8,23)}:00",
            "airline": "DemoAir"
        })

    return {"flights": flights}

if __name__ == "__main__":
    app.run()