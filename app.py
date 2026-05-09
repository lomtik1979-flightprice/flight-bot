from flask import Flask, render_template, request
import sqlite3
import requests
from serpapi import GoogleSearch
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

    if not route:
        return {"flights": []}

    try:
        origin, dest = route.split("-")
    except:
        return {"flights": []}

    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")

    params = {

        "engine": "google_flights",

        "departure_id": origin,

        "arrival_id": dest,

        "outbound_date": date_from,

        "return_date": date_to,

        "currency": "USD",

        "hl": "en",

        "api_key": "26e06478b4b9a2349b9f9373c8ec8f3c7de19e56fa5bb93771a6a741634e51db"
    }

    try:
        print(params)

        search = GoogleSearch(params)

        results = search.get_dict()

        best_flights = results.get(
            "best_flights",
            []
        )

        flights = []

        for f in best_flights:

            price = f.get("price", 0)

            flights.append({

                "price": price,

                "dep": date_from,

                "arr": date_to
            })

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