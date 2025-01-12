import os
import json
import requests
from serpapi import GoogleSearch
from datetime import datetime
import re
from bs4 import BeautifulSoup
from typing import Optional, Dict, Tuple

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from twocaptcha import TwoCaptcha

from dotenv import load_dotenv

load_dotenv()


class TravelAssistant:
    def __init__(self):
        self.serpapi_key = os.getenv("SERPAPI_KEY")
        self.gpt_key = os.getenv("GPT_TUNNEL_KEY")
        self._airport_codes_cache = {}  # кэш для хранения уже найденных кодов

    def get_airport_code(self, city: str) -> Optional[str]:
        """
        Get airport IATA code for city using online database
        Returns first found airport code for the city
        """
        # Проверяем кэш
        if city.lower() in self._airport_codes_cache:
            return self._airport_codes_cache[city.lower()]

        try:
            url = "https://www.nationsonline.org/oneworld/IATA_Codes/airport_code_list.htm"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")

            # Находим таблицу с кодами
            tables = soup.find_all("table")
            print(tables)

            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) >= 3:  # убеждаемся, что есть все нужные колонки
                        city_name = cols[0].text.strip().lower()
                        iata_code = cols[2].text.strip()

                        # Проверяем, совпадает ли город
                        if city.lower() in city_name:
                            # Сохраняем в кэш
                            self._airport_codes_cache[city.lower()] = iata_code
                            return iata_code
            print("iata_code", iata_code)
            return None
        except Exception as e:
            print(f"Error getting airport code: {e}")
            return None

    def construct_aviasales_url(
        self,
        from_city: str,
        to_city: str,
        depart_date: str,
        return_date: str,
        passengers: int = 1,
        travel_class: str = "",
    ) -> Optional[str]:
        """Construct Aviasales URL based on parameters"""

        try:
            # Add class suffix if specified
            class_suffix = (
                travel_class + str(passengers) if travel_class else str(passengers)
            )

            print(
                f"https://www.aviasales.ru/search/{from_city}{depart_date}{to_city}{return_date}{class_suffix}"
            )

            return f"https://www.aviasales.ru/search/{from_city}{depart_date}{to_city}{return_date}{class_suffix}"
        except Exception as e:
            print(f"Error constructing URL: {e}")
            return None

    def get_llm_response(self, prompt):
        """Get response from LLM"""
        url = "https://gptunnel.ru/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.gpt_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "system",
                    "content": """You are a knowledgeable travel assistant. 
                    You help users plan their trips by providing detailed recommendations 
                    about places to visit. When providing recommendations, include relevant 
                    details about each place, such as historical significance, 
                    cultural importance, or unique features. Write recommendations only in RUSSIAN!!!
                    Add neccessary links to hotels/places/attractions!
                    
                    If prompt ask to analyze the prompt, then follow the instructions in it. Write analysis in ENGLISH.
                    """,
                },
                {"role": "user", "content": prompt},
            ],
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"Failed to get LLM response {response}")

    def search_places(self, location):
        """Search for places using Google Search API"""
        params = {
            "q": f"top tourist attractions in {location}",
            "location": location,
            "hl": "en",
            "gl": "us",
            "google_domain": "google.com",
            "api_key": self.serpapi_key,
        }

        search = GoogleSearch(params)
        return search.get_dict()

    def process_query(self, user_query: str) -> str:
        """Process user query and return formatted response"""
        analysis_prompt = f"""
        Analyze this travel query: "{user_query}"
        1. What is the main destination? Write the 3-letter code (IATA code) of the city
        2. What is the departure city? If not mentioned, assume MOW
        3. What are the travel dates? Write only in ddmm format (for example 25 May: 2505) If not mentioned, for start date 2101 and 2701 for end date
        4. How many passengers? Write only number. If not mentioned, assume 1
        5. What is the preferred travel class (economy - '' /comfort - 'w'/business - 'c'/first - 'f')? If not mentioned, assume economy - ''
        6. Are there any specific interests or preferences mentioned?
        7. What is the budget level (budget/business/vip)?
        Provide your analysis in JSON format only in ENGLISH with keys: "destination", "departure_city", "start_date", "end_date", 
        "passengers", "travel_class", "interests", "budget_level"
        """

        try:
            analysis = self.get_llm_response(analysis_prompt)
            analysis = analysis.strip()
            if analysis.startswith("```json"):
                analysis = analysis[7:]  # Remove ```json
            if analysis.endswith("```"):
                analysis = analysis[:-3]  # Remove trailing ```
            analysis = analysis.strip()
            print(analysis)
            analysis_data = json.loads(analysis)

            # Get flight options
            aviasales_url = self.construct_aviasales_url(
                analysis_data["departure_city"],
                analysis_data["destination"],
                analysis_data["start_date"],
                analysis_data["end_date"],
                analysis_data["passengers"],
                analysis_data.get("travel_class", ""),
            )

            # Search for places
            search_results = self.search_places(analysis_data["destination"])

            # Generate recommendations using LLM
            recommendation_prompt = f"""
            Create a comprehensive travel plan for {analysis_data["destination"]} based on a {analysis_data["budget_level"]} budget.
            
            Please provide three different travel plans only in RUSSIAN!!!:

            1. Budget Travel Plan (Economy class, hostels/budget hotels, public transport)
            - Daily budget: $50-100 for accommodation and activities
            - Focus on free attractions and budget-friendly options
            
            2. Business Travel Plan (Business class, 4-star hotels, mix of transport)
            - Daily budget: $200-500 for accommodation and activities
            - Focus on comfort and efficiency
            
            3. VIP Travel Plan (First class, 5-star hotels, private transport)
            - Daily budget: $1000+ for accommodation and activities
            - Focus on luxury experiences and exclusive access
            
            Search results for attractions:
            {json.dumps(search_results.get('top_sights', {}).get('sights', []), ensure_ascii=False, indent=2)}

            For each plan include:
            1. Accommodation options
            2. Daily activities and attractions
            3. Travel recommendations of transportation (in Russian "Передвижение")
            4. Dining suggestions
            5. Estimated total budget

            Format each section with markdown and include practical details like:
            - Specific hotel names and prices
            - Restaurant recommendations with price ranges
            - Activity costs and booking tips

            VERY VITAL! Представь три разных плана путешествия только на РУССКОМ языке в виде таблицы с тремя столбцами: Budget, Business, VIP.
            Формат таблицы:
            "Категория	Budget (Эконом)	Business (Бизнес)	VIP (Люкс)"
            Для каждого столбца (Budget, Business, VIP) укажи:
            Конкретные названия отелей, ресторанов, достопримечательностей.
            Примерные цены на проживание, питание, транспорт и мероприятия.
            Практические советы по бронированию (например, ссылки на сайты или приложения).
            VITAL: Вся информация должна быть представлена в виде таблицы, чтобы клиенту было удобно сравнивать три варианта путешествия.
            В ТАБЛИЦЕ НЕ ПИШИ ТЕКСТ ЖИРНЫМ ШРИФТОМ ИЛИ КУРСИВОМ!!!
            
            End with booking links and contact information for recommended services in separate text!

            At the end add the link for checking available flights at Aviasales site: {aviasales_url}. Here customer can already find the right routes of fligtes and prices

            Write text only in RUSSIAN!
            """

            screenshot_path = "images/screenshot.png"
            self.take_screenshot(aviasales_url, screenshot_path)

            final_response = self.get_llm_response(recommendation_prompt)

            final_response += f" [Посмотреть на сайте]({aviasales_url})"
            # final_response += f"\n\n[![Скриншот сайта]({screenshot_path})]({aviasales_url})\n\n"

            return final_response, aviasales_url

        except Exception as e:
            print(f"Error processing query: {e}")
            return f"Sorry, an error occurred while processing your request: {str(e)}"

    @staticmethod
    def take_screenshot(url: str, screenshot_path: str) -> None:
        """Take a screenshot of the given URL and save it to the specified path."""
        service = Service("/Users/ivan/Downloads/chromedriver-mac-arm64/chromedriver")
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        # Add more Chrome options to make the browser more realistic
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--start-maximized")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        captcha_key = os.getenv("CAPTCHA_KEY")

        driver = webdriver.Chrome(service=service, options=options)
        solver = TwoCaptcha(captcha_key)

        try:
            # Set page load timeout
            driver.set_page_load_timeout(30)

            # Navigate to the URL
            driver.get(url)
            print("Page loaded successfully")

            # Wait for any initial loading to complete
            time.sleep(5)

            try:
                # Wait for reCAPTCHA iframe to be present
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'iframe[src*="recaptcha"]')
                    )
                )
                print("Found reCAPTCHA iframe")

                # Handle reCAPTCHA
                iframe = driver.find_element(
                    By.CSS_SELECTOR, 'iframe[src*="recaptcha"]'
                )
                iframe_src = iframe.get_attribute("src")

                sitekey_match = re.search(r"k=([^&]+)", iframe_src)

                if sitekey_match:
                    sitekey = sitekey_match.group(1)
                    print(f"Found sitekey: {sitekey}")

                    result = solver.recaptcha(sitekey=sitekey, url=url, invisible=1)

                    driver.execute_script(
                        f"document.querySelector('textarea[name=\"g-recaptcha-response\"]').innerHTML = '{result['code']}';"
                    )
                    print("Inserted reCAPTCHA response")

            except Exception as captcha_error:
                print("Taking screenshot...")
                driver.save_screenshot(screenshot_path)
                print(f"reCAPTCHA handling failed: {captcha_error}")
                return

            # Wait for content to load with multiple possible conditions
            try:
                WebDriverWait(driver, 30).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CLASS_NAME, "product-list")),
                        EC.presence_of_element_located(
                            (By.CLASS_NAME, "search-results")
                        ),
                        EC.presence_of_element_located((By.CLASS_NAME, "tickets-list")),
                        EC.presence_of_element_located((By.TAG_NAME, "main")),
                    )
                )
                print("Main content loaded")
            except:
                print("Timeout waiting for main content, taking screenshot anyway")

            # Give the page more time to fully render
            time.sleep(10)

            # Scroll the page to capture all content
            total_height = driver.execute_script("return document.body.scrollHeight")
            viewport_height = driver.execute_script("return window.innerHeight")
            current_position = 0

            while current_position < total_height:
                driver.execute_script(f"window.scrollTo(0, {current_position});")
                current_position += viewport_height
                time.sleep(0.5)

            # Scroll back to top
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)

            # Take screenshot
            print("Taking screenshot...")
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            # Take a screenshot of the error state
            error_screenshot_path = f"{screenshot_path}"
            driver.save_screenshot(error_screenshot_path)
            print(f"Error screenshot saved to {error_screenshot_path}")
            raise
        finally:
            driver.quit()


# assistant = TravelAssistant()
# screenshot_path = 'images/screenshot.png'
# assistant.take_screenshot('https://www.aviasales.ru/search/MOW2101LON27011', screenshot_path)

# def take_screenshot(self, url: str, screenshot_path: str) -> None:
#     """Take a screenshot of the given URL and save it to the specified path."""
#     service = Service('/Users/ivan/Downloads/chromedriver-mac-arm64/chromedriver')
#     options = webdriver.ChromeOptions()
#     options.add_argument('--headless')
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')

#     driver = webdriver.Chrome(service=service, options=options)
#     try:
#         driver.get(url)
#         WebDriverWait(driver, 25).until(
#             EC.presence_of_element_located((By.TAG_NAME, 'body'))
#         )
#         time.sleep(10)
#         driver.save_screenshot(screenshot_path)
#     finally:
#         driver.quit()
