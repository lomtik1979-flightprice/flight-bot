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
    return {
        "flights": [
            {"price": 180, "dep": "08:00", "arr": "12:00"},
            {"price": 240, "dep": "14:00", "arr": "18:00"},
            {"price": 320, "dep": "20:00", "arr": "00:00"}
        ]
    }

if __name__ == "__main__":
    app.run()