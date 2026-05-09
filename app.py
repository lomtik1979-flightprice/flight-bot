from flask import Flask, render_template, request
import sqlite3
import requests
from serpapi import GoogleSearch
from datetime import datetime, timedelta
import random
import os

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

    if not route:
        return {"flights": []}

    route = route.upper().strip()

    try:
        origin, dest = route.split("-")

    except:
        return {
            "error": "Invalid route format",
            "flights": []
        }

    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    max_price = request.args.get("max_price")

    if not date_from or not date_to:

        return {
            "error": "Missing dates",
            "flights": []
        }

    params = {

        "engine": "google_flights",

        "departure_id": origin,

        "arrival_id": dest,

        "outbound_date": date_from,

        "return_date": date_to,

        "currency": "USD",

        "hl": "en",

        # 🔥 ВСТАВЬ СВОЙ НОВЫЙ API KEY
        "api_key": "7b49e9ba112999eb5c2fdc88c63249130212492f2ec3088aa690a211b21e0924"
    }

    try:

        print("========== SERPAPI REQUEST ==========")
        print(params)
        print("=====================================")

        search = GoogleSearch(params)

        results = search.get_dict()

        print("========== SERPAPI RESPONSE ==========")
        print(results)
        print("======================================")

        best_flights = results.get(
            "best_flights",
            []
        )

        flights = []

        for f in best_flights:

            price = f.get("price", 0)

            try:

    numeric_price = int(
        str(price).replace("$", "")
    )

except:

    numeric_price = 0

if max_price:

    if numeric_price > int(max_price):
        continue

            flights.append({

                "price": numeric_price,

                "dep": date_from,

                "arr": date_to
            })

            # сохраняем в БД
            conn = sqlite3.connect("flights.db")
            c = conn.cursor()

            c.execute(
                "INSERT INTO flights VALUES (?, ?, ?)",
                (
                    route,
                    date_from,
                    price
                )
            )

            conn.commit()
            conn.close()

        return {"flights": flights}

    except Exception as e:

        print("========== SERPAPI ERROR ==========")
        print(str(e))
        print("===================================")

        return {
            "error": str(e),
            "flights": []
        }

# -----------------------------
# КАЛЕНДАРЬ
# -----------------------------
@app.route("/api/calendar")
def calendar():

    route = request.args.get("route")

    if not route:
        return {"dates": []}

    route = route.upper().strip()

    conn = sqlite3.connect("flights.db")
    c = conn.cursor()

    c.execute("""
        SELECT date, MIN(price)
        FROM flights
        WHERE route=?
        GROUP BY date
        ORDER BY date
    """, (route,))

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

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )