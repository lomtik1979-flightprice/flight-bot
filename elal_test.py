from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

driver.get("https://www.elal.com")

print("Ждём загрузку...")
time.sleep(5)

# 🔹 закрываем cookies
try:
    btn = driver.find_element(By.XPATH, "//button[contains(text(),'I understand')]")
    btn.click()
    print("Cookies закрыты")
except:
    print("Cookie не найден")

time.sleep(3)

# 🔹 кликаем именно по "הזמנת טיסה"
try:
    flight_btn = driver.find_element(By.XPATH, "//*[contains(text(),'הזמנת טיסה')]")
    flight_btn.click()
    print("Нажали 'הזמנת טיסה'")
except:
    print("Кнопка не найдена")

time.sleep(10)

# 🔹 читаем страницу
body = driver.find_element(By.TAG_NAME, "body").text

driver.quit()

# 🔹 ищем цены
lines = body.split("\n")

prices = []
for line in lines:
    if "$" in line or "USD" in line:
        prices.append(line)

if prices:
    print("Найденные цены:")
    for p in prices[:10]:
        print(p)
else:
    print("Цены не найдены")