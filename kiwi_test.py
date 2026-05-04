import requests

def search_flights():
    url = "https://api.skypicker.com/flights"

    params = {
        "fly_from": "TLV",
        "fly_to": "PAR",
        "date_from": "10/07/2026",
        "date_to": "15/07/2026",
        "direct_flights": 1,
        "curr": "USD",
        "limit": 5
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.get(url, params=params, headers=headers)

    # 🔴 добавим проверку
    if res.status_code != 200:
        print("Ошибка запроса:", res.status_code)
        print(res.text)
        return

    try:
        data = res.json()
    except:
        print("Не JSON ответ:")
        print(res.text[:500])
        return

    if not data.get("data"):
        print("Нет рейсов")
        return

    for f in data["data"]:
        price = f["price"]
        route = f["route"][0]

        print("------")
        print("Цена:", price, "$")
        print("Маршрут:", route["cityFrom"], "→", route["cityTo"])
        print("Дата:", f["local_departure"])


search_flights()