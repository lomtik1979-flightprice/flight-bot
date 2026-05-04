import requests

TOKEN = "8684816030:AAHRbtQw29qqHUhTYpT3TYxZYMbb9Zi3tbA"
CHAT_ID = "6456111523"

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

requests.post(url, data={
    "chat_id": CHAT_ID,
    "text": "Бот подключен 🚀"
})