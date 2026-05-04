from flask import Flask, render_template, request
import sqlite3
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
def init_db():
    conn = sqlite3.connect("flights.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS flights (
            route TEXT,
            date TEXT,
            price INTEGER
        )
    """)
    conn.commit()
    conn.close()

init_db()
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
    route = request.args.get("route")

    if not route:
        return {"flights": []}

    origin, dest = route.split("-")

    conn = sqlite3.connect("flights.db")
    c = conn.cursor()

    # 🔥 пробуем из базы
    c.execute("SELECT price, date FROM flights WHERE route=?", (route,))
    rows = c.fetchall()

    if rows:
        conn.close()
        return {
            "flights": [
                {"price": r[0], "dep": r[1], "arr": r[1]}
                for r in rows[:5]
            ]
        }

    # 🔥 если нет — запрос к API
    url = "https://api.skypicker.com/flights"

    try:
        res = requests.get(url, params={
            "fly_from": origin,
            "fly_to": dest,
            "date_from": datetime.now().strftime("%d/%m/%Y"),
            "date_to": (datetime.now() + timedelta(days=30)).strftime("%d/%m/%Y"),
            "curr": "USD",
            "limit": 5
        }, headers={"User-Agent": "Mozilla/5.0"})

        data = res.json().get("data", [])

        flights = []

        for f in data:
            seg = f["route"][0]
            price = f["price"]

            flights.append({
                "price": price,
                "dep": seg["local_departure"][:16],
                "arr": seg["local_arrival"][:16]
            })

            # сохраняем
            c.execute(
                "INSERT INTO flights VALUES (?, ?, ?)",
                (route, seg["local_departure"][:10], price)
            )

        conn.commit()
        conn.close()

        if flights:
            return {"flights": flights}
@app.route("/api/calendar")
def calendar():
    route = request.args.get("route")

    conn = sqlite3.connect("flights.db")
    c = conn.cursor()

    c.execute("""
        SELECT date, MIN(price)
        FROM flights
        WHERE route=?
        GROUP BY date
    """, (route,))

    rows = c.fetchall()
    conn.close()

    return {
        "dates": [{"date": r[0], "price": r[1]} for r in rows]
    }

    except:
        pass

    conn.close()

    return {"flights": []}

if __name__ == "__main__":
    app.run()