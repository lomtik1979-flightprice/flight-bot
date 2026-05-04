from seleniumwire import webdriver
from seleniumwire.utils import decode
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

# создаём драйвер
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# очищаем старые запросы
driver.requests.clear()

# открываем поиск
driver.get("https://www.skyscanner.com/transport/flights/tlv/par/260715/")

print("Ждём загрузку...")
time.sleep(25)

print("Перехватываем API...")

for request in driver.requests:
    if request.response:
        if "web-unified-search" in request.url:
           # 🔹 ищем минимальные цены по авиакомпаниям
print("\n=== МИНИМАЛЬНЫЕ ЦЕНЫ ===")

try:
    carriers = data["itineraries"]["filterStats"]["carriers"]

    for c in carriers:
        price = c.get("rawMinPrice")
        name = c.get("name")

        if price:
            print(f"{name}: ${price}")

except Exception as e:
    print("Ошибка при извлечении:", e)