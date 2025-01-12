# Укажите путь к вашему веб-драйверу
driver_path = '/Users/ivan/Downloads/chromedriver-mac-arm64/chromedriver'

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from selenium.webdriver.chrome.service import Service
webdriver.Chrome(service=Service(driver_path))

# Инициализация веб-драйвера
driver = webdriver.Chrome()

try:
    # Открытие страницы Aviasales
    driver.get('https://www.aviasales.ru/search/MOW2101LED28011')

    # Ожидание загрузки страницы
    wait = WebDriverWait(driver, 40)

#     # Ввод города отправления
#     departure_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Откуда']")))
#     print(departure_input)
#     departure_input.clear()
#     departure_input.send_keys('Москва')
#     time.sleep(1)  # Небольшая пауза для автозаполнения
#     departure_input.send_keys(Keys.ENTER)

#     # Ввод города прибытия
#     arrival_input = driver.find_element(By.XPATH, "//input[@placeholder='Куда']")
#     arrival_input.clear()
#     arrival_input.send_keys('Париж')
#     time.sleep(1)  # Небольшая пауза для автозаполнения
#     arrival_input.send_keys(Keys.ENTER)

#     # Выбор даты отправления
#     departure_date_input = driver.find_element(By.XPATH, "//button[contains(text(), 'Когда')]")
#     departure_date_input.click()
#     # Выбор конкретной даты
#     date_to_select = driver.find_element(By.XPATH, "//input[contains(text(), 'Эконом')]")
#     date_to_select.click()

#     # Выбор даты возвращения
#     return_date_input = driver.find_element(By.XPATH, "//input[@placeholder='Обратно']")
#     return_date_input.click()
#     # Выбор конкретной даты
#     date_to_select = driver.find_element(By.XPATH, "//div[@data-date='2025-01-25']")
#     date_to_select.click()

#     # Выбор бизнес-класса
#     class_selector = driver.find_element(By.XPATH, "//button[contains(text(), 'Эконом')]")
#     class_selector.click()
#     business_class_option = driver.find_element(By.XPATH, "//div[contains(text(), 'Бизнес')]")
#     business_class_option.click()

#     # Нажатие кнопки поиска
#     search_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Найти билеты')]")
#     search_button.click()

#     # Ожидание результатов поиска
#     wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'search-results')]")))

finally:
    # Закрытие браузера
    time.sleep(30)  # Время на просмотр результатов
    driver.quit()

from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
import time

# from fake_useragent import UserAgent
# import random
# import requests
# from selenium.webdriver.common.proxy import Proxy, ProxyType

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


# def get_working_proxies():
#     """Получение списка рабочих прокси"""
#     try:
#         # Можно использовать бесплатные прокси или платные сервисы
#         proxy_urls = [
#             'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
#             'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt'
#         ]
        
#         proxies = []
#         for url in proxy_urls:
#             response = requests.get(url)
#             proxies.extend(response.text.strip().split('\n'))
        
#         working_proxies = []
#         for proxy in proxies:
#             try:
#                 response = requests.get('https://www.aviasales.ru', 
#                                      proxies={'http': f'http://{proxy}', 'https': f'http://{proxy}'}, 
#                                      timeout=5)
#                 if response.status_code == 200:
#                     working_proxies.append(proxy)
#             except:
#                 continue
#             if len(working_proxies) >= 5:  # Получаем первые 5 рабочих прокси
#                 break
                
#         return working_proxies
#     except:
#         return []

# def setup_driver(proxy=None):
#     """Настройка драйвера с прокси и user-agent"""
#     options = Options()
#     #options.add_argument('--headless')
#     options.add_argument('--window-size=1920,1080')
#     options.add_argument('--disable-gpu')
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
    
#     # Добавляем случайный user-agent
#     ua = UserAgent()
#     user_agent = ua.random
#     options.add_argument(f'user-agent={user_agent}')
    
#     # Добавляем прокси если он предоставлен
#     if proxy:
#         proxy_option = Proxy()
#         proxy_option.proxy_type = ProxyType.MANUAL
#         proxy_option.http_proxy = proxy
#         proxy_option.ssl_proxy = proxy
        
#         capabilities = webdriver.DesiredCapabilities.CHROME
#         proxy_option.add_to_capabilities(capabilities)
        
#         driver = webdriver.Chrome(options=options, desired_capabilities=capabilities)
#     else:
#         driver = webdriver.Chrome(options=options)
    
#     # Установка таймаутов
#     driver.set_page_load_timeout(30)
#     driver.implicitly_wait(10)
    
#     return driver


# def wait_for_page_load(driver, timeout=30):
#     """Ожидание загрузки страницы с несколькими проверками"""
#     try:
#         # Ждем, пока исчезнет индикатор загрузки
#         WebDriverWait(driver, timeout).until_not(
#             EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-id='loader']"))
#         )
        
#         # Ждем появления билетов
#         WebDriverWait(driver, timeout).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-id='ticket-preview']"))
#         )
        
#         return True
#     except TimeoutException:
#         return False

# def find_best_flights(origin, destination, departure_date, return_date=None, max_retries=5):
#     working_proxies = get_working_proxies()
#     logger.info(f"Найдено рабочих прокси: {len(working_proxies)}")
    
#     for attempt in range(max_retries):
#         driver = None
#         try:
#             # Выбираем случайный прокси если есть доступные
#             proxy = random.choice(working_proxies) if working_proxies else None
#             driver = setup_driver(proxy)
            
#             # Формируем URL
#             if return_date:
#                 url = f'https://www.aviasales.ru/search/{origin}{departure_date.strftime("%d%m")}{destination}{return_date.strftime("%d%m")}1'
#             else:
#                 url = f'https://www.aviasales.ru/search/{origin}{departure_date.strftime("%d%m")}{destination}1'
            
#             logger.info(f"Попытка {attempt + 1}: Загрузка URL {url}")
#             if proxy:
#                 logger.info(f"Используется прокси: {proxy}")
            
#             # Загружаем страницу с обработкой ошибок
#             try:
#                 driver.get(url)
#             except Exception as e:
#                 logger.error(f"Ошибка при загрузке страницы: {str(e)}")
#                 continue
            
#             # Ожидание загрузки страницы
#             time.sleep(10)
            
#             # Прокручиваем страницу для загрузки всего контента
#             driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#             time.sleep(5)
            
#             # Проверяем загрузку страницы
#             try:
#                 WebDriverWait(driver, 20).until(
#                     EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-test-id='ticket-preview']"))
#                 )
#             except TimeoutException:
#                 logger.warning("Таймаут при ожидании билетов")
#                 continue
            
#             # Проверяем наличие капчи
#             if "captcha" in driver.current_url.lower():
#                 logger.warning("Обнаружена капча")
#                 continue
            
#             # Парсим результаты
#             page = driver.page_source
#             flights = parse_flight_info(page)
            
#             if not flights:
#                 logger.warning("Не найдено билетов")
#                 continue
            
#             cheapest_flight = min(flights, key=lambda x: float(x['price'].replace('₽','').replace(' ','')))
#             fastest_flight = min(flights, key=lambda x: int(x['duration'].split()[0]))
            
#             results = pd.DataFrame([cheapest_flight, fastest_flight])
#             results.index = ['Самый дешевый', 'Самый быстрый']
            
#             logger.info("Успешно получены результаты")
#             return results
            
#         except Exception as e:
#             logger.error(f"Ошибка при попытке {attempt + 1}: {str(e)}")
#             if attempt == max_retries - 1:
#                 raise
        
#         finally:
#             if driver:
#                 driver.quit()
#             time.sleep(random.uniform(3, 7))  # Случайная пауза между попытками
    
#     raise Exception("Не удалось получить результаты после всех попыток")

# def parse_flight_info(page):
#     try:
#         soup = BeautifulSoup(page, 'html.parser')
#         tickets = soup.find_all('div', attrs={'data-test-id': 'ticket-preview'})
        
#         if not tickets:
#             logger.warning("Билеты не найдены на странице")
#             return []
            
#         flights = []
#         for ticket in tickets:
#             try:
#                 flight = {}
#                 # ... (остальной код parse_flight_info остается тем же)
#                 flights.append(flight)
#             except Exception as e:
#                 logger.error(f"Ошибка при парсинге билета: {str(e)}")
#                 continue
                
#         return flights
        
#     except Exception as e:
#         logger.error(f"Ошибка при парсинге страницы: {str(e)}")
#         return []

# # Пример использования
# if __name__ == "__main__":
#     try:
#         origin = 'MOW'
#         destination = 'LED'
#         departure_date = datetime.now() + timedelta(days=2)
#         return_date = departure_date + timedelta(days=7)
        
#         logger.info("Начинаем поиск билетов...")
#         results = find_best_flights(origin, destination, departure_date, return_date)
#         print(results)
        
#     except Exception as e:
#         logger.error(f"Программа завершилась с ошибкой: {str(e)}")