from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

driver.get("https://www.skyscanner.com/transport/flights/tlv/par/260710/")

print("Ждём загрузку...")
time.sleep(20)

# берём весь текст страницы
body = driver.find_element("tag name", "body").text

driver.quit()

# ищем цены вручную
lines = body.split("\n")

prices = []

for line in lines:
    if "$" in line:
        prices.append(line)

if prices:
    print("Найденные цены:")
    for p in prices[:10]:
        print(p)
else:
    print("Цены не найдены")