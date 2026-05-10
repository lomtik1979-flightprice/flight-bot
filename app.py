from flask import Flask, render_template, request
import sqlite3
from serpapi import GoogleSearch
import os

app = Flask(__name__)

# -----------------------------
# DATABASE
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
# HOME
# -----------------------------
@app.route("/")
def index():

    return render_template("index.html")

# -----------------------------
# MAP
# -----------------------------
@app.route("/map")
def map_view():

    return render_template("map.html")

# -----------------------------
# FLIGHTS API
# -----------------------------
@app.route("/api/flights")
def get_flights():

    route = request.args.get("route")

    if not route:

        return {
            "flights": []
        }

    route = route.upper().strip()

    try:

        origin, dest = route.split("-")

    except:

        return {
            "error": "Invalid route",
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

    # -----------------------------
    # SERPAPI REQUEST
    # -----------------------------
    params = {

        "engine": "google_flights",

        "departure_id": origin,

        "arrival_id": dest,

        "outbound_date": date_from,

        "return_date": date_to,

        "currency": "USD",

        "hl": "en",

        "api_key": os.environ.get(
            "SERPAPI_KEY"
        )
    }

    try:

        print("========== REQUEST ==========")
        print(params)

        search = GoogleSearch(params)

        results = search.get_dict()

        print("========== RESPONSE ==========")
        print(results)
        print("==============================")

        best_flights = results.get(
            "best_flights",
            []
        )

        if not best_flights:

            best_flights = results.get(
                "other_flights",
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

            # -----------------------------
            # MAX PRICE FILTER
            # -----------------------------
            if max_price:

                try:

                    if numeric_price > int(max_price):

                        continue

                except:

                    pass

            # -----------------------------
            # AIRLINE LOGO
            # -----------------------------
            airline_logo = ""

            try:

                airline_logo = f[
                    "airline_logo"
                ]

            except:

                pass

            # -----------------------------
            # CITY IMAGE
            # -----------------------------
            city_image = ""

            try:

                city_image = results[
                    "airports"
                ][0]["arrival"][0]["image"]

            except:

                pass

            # -----------------------------
            # AIRLINE NAME
            # -----------------------------
            airline_name = ""

            try:

                airline_name = f[
                    "flights"
                ][0]["airline"]

            except:

                pass

            # -----------------------------
            # DURATION
            # -----------------------------
            duration = f.get(
                "total_duration",
                0
            )

            # -----------------------------
            # DIRECT FLIGHT
            # -----------------------------
            direct = True

            if "layovers" in f:

                direct = False

            # -----------------------------
            # SAVE FLIGHT
            # -----------------------------
            flights.append({

                "price": numeric_price,

                "dep": date_from,

                "arr": date_to,

                "airline": airline_name,

                "airline_logo": airline_logo,

                "city_image": city_image,

                "duration": duration,

                "direct": direct
            })

            # -----------------------------
            # SAVE TO DATABASE
            # -----------------------------
            conn = sqlite3.connect(
                "flights.db"
            )

            c = conn.cursor()

            c.execute(
                "INSERT INTO flights VALUES (?, ?, ?)",
                (
                    route,
                    date_from,
                    numeric_price
                )
            )

            conn.commit()
            conn.close()

        return {

            "flights": flights
        }

    except Exception as e:

        print("========== ERROR ==========")
        print(str(e))
        print("===========================")

        return {

            "error": str(e),

            "flights": []
        }

# -----------------------------
# CALENDAR
# -----------------------------
@app.route("/api/calendar")
def calendar():

    route = request.args.get("route")

    if not route:

        return {
            "dates": []
        }

    route = route.upper().strip()

    conn = sqlite3.connect(
        "flights.db"
    )

    c = conn.cursor()

    c.execute("""

        SELECT
            date,
            MIN(price)

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