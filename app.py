from flask import Flask, render_template, request
import sqlite3
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

# -----------------------------
# 🧠 ИНИЦИАЛИЗАЦИЯ БАЗЫ
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
# 🏠 ГЛАВНАЯ
# -----------------------------
@app.route("/")
def index():
    return render_template("index.html")

# -----------------------------
# 🌍 КАРТА
# -----------------------------
@app.route("/map")
def map_view():
    return render_template("map.html")

# -----------------------------
# ✈️ API РЕЙСОВ
# -----------------------------
@app.route("/api/flights")
def get_flights():
    route = request.args.get("route")

    if not route:
        return {"flights": []}

    origin, dest = route.split("-")

    conn = sqlite3.connect("flights.db")
    c = conn.cursor()

    # 🔥 1. ПРОБУЕМ ВЗЯТЬ ИЗ КЕША
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

    # 🔥 2. ЕСЛИ НЕТ — ЗАПРОС К API
    try:
        res = requests.get(
            "https://api.skypicker.com/flights",
            params={
                "fly_from": origin,
                "fly_to": dest,
                "date_from": datetime.now().strftime("%d/%m/%Y"),
                "date_to": (datetime.now() + timedelta(days=30)).strftime("%d/%m/%Y"),
                "curr": "USD",
                "limit": 5
            },
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )

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

            # сохраняем в базу
            c.execute(
                "INSERT INTO flights VALUES (?, ?, ?)",
                (route, seg["local_departure"][:10], price)
            )

        conn.commit()
        conn.close()

        if flights:
            return {"flights": flights}

    except:
        pass

    conn.close()

    # 🔥 3. FALLBACK (если API не ответил)
    return {
        "flights": [
            {"price": 180, "dep": "demo", "arr": "demo"},
            {"price": 240, "dep": "demo", "arr": "demo"},
            {"price": 320, "dep": "demo", "arr": "demo"}
        ]
    }

# -----------------------------
# 📅 КАЛЕНДАРЬ ЦЕН
# -----------------------------
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

# -----------------------------
# 🚀 ЗАПУСК
# -----------------------------
if __name__ == "__main__":
    app.run()