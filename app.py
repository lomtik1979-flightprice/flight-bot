from flask import Flask, render_template, request
import sqlite3
import requests
from datetime import datetime, timedelta
import random

app = Flask(__name__)

# -----------------------------
# БАЗА
# -----------------------------
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

# -----------------------------
# ГЛАВНАЯ
# -----------------------------
@app.route("/")
def index():
    return render_template("index.html")

# -----------------------------
# КАРТА
# -----------------------------
@app.route("/map")
def map_view():
    return render_template("map.html")

# -----------------------------
# API РЕЙСОВ
# -----------------------------
@app.route("/api/flights")
def get_flights():

    route = request.args.get("route")
    max_price = request.args.get("max_price")

    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")

    if not route:
        return {"flights": []}

    route = route.upper().strip()

   try:
    origin, dest = route.split("-")
except:
    return {"flights": []}

valid_airports = [

    "TLV",
    "CDG",
    "MAD",
    "FCO",
    "BCN",
    "LHR",
    "ATH",
    "JFK"
]

if origin not in valid_airports:
    return {"flights": []}

if dest not in valid_airports:
    return {"flights": []}
    except:
        return {"flights": []}

    # aliases
    aliases = {
        "PAR": "CDG",
        "ROM": "FCO",
        "LON": "LHR",
        "NYC": "JFK"
    }

    dest = aliases.get(dest, dest)

    # max price
    try:
        max_price = int(max_price)
    except:
        max_price = 99999

    # даты
    try:
        d1 = datetime.strptime(date_from, "%Y-%m-%d")
        d2 = datetime.strptime(date_to, "%Y-%m-%d")

        days = (d2 - d1).days + 1

        days = min(days, 60)

    except:
        d1 = datetime.now()
        days = 30

    # fallback prices
    base_prices = {
        "CDG": 180,
        "FCO": 140,
        "LHR": 220,
        "JFK": 450
    }

    base = base_prices.get(dest, 200)

    flights = []

    conn = sqlite3.connect("flights.db")
    c = conn.cursor()

    # удаляем старые данные маршрута
    c.execute(
    "DELETE FROM flights WHERE route=?",
    (route,)
)

    for i in range(days):

        dep_date = (
            d1 + timedelta(days=i)
        ).strftime("%Y-%m-%d")

        price = base + random.randint(-40, 60)

        if price > max_price:
            continue

        flights.append({
            "price": price,
            "dep": dep_date,
            "arr": dep_date
        })

        # сохраняем
        c.execute(
            "INSERT INTO flights VALUES (?, ?, ?)",
            (route, dep_date, price)
        )

    conn.commit()
    conn.close()

    return {"flights": flights}

# -----------------------------
# КАЛЕНДАРЬ
# -----------------------------
@app.route("/api/calendar")
def calendar():

    route = request.args.get("route")

    if not route:
        return {"dates": []}

    conn = sqlite3.connect("flights.db")
    c = conn.cursor()

    c.execute("""
        SELECT date, MIN(price)
        FROM flights
        WHERE route=?
        GROUP BY date
        ORDER BY date
    """, (route.upper(),))

    rows = c.fetchall()

    conn.close()

    return {
        "dates": [
            {
                "date": r[0],
                "price": r[1]
            }
            for r in rows
        ]
    }

# -----------------------------
# START
# -----------------------------
if __name__ == "__main__":
    app.run()