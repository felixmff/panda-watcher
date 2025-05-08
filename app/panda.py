import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import logging
from typing import List, Tuple


class PandaClient:
    def __init__(self) -> None:
        """Initializes the browser with desired options and loads environment variables."""
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

    def login(self) -> None:
        """
        Logs into the PANDA system using credentials from environment variables.
        """
        self.driver.get("https://panda.uni-paderborn.de/login/index.php")
        time.sleep(2)

        self.driver.find_element(By.NAME, "username").send_keys(os.getenv("PANDA_USERNAME"))
        self.driver.find_element(By.NAME, "password").send_keys(os.getenv("PANDA_PASSWORD") + Keys.RETURN)
        time.sleep(5)

    def fetch_resources(self, course_ids: list) -> List[Tuple[str, str, str, str]]:
        """
        Visits each course and collects unique resource links.

        Args:
            course_ids (list): List of course IDs to process.

        Returns:
            list: A list of tuples (course_id, course_name, resource_name, resource_url).
        """
        resources = []
        for course_id in course_ids:
            logging.info(f"Fetching resources with course ID {course_id}")
            self.driver.get(f"https://panda.uni-paderborn.de/course/view.php?id={course_id}")

            course_name = self.driver.title.replace("Kurs: ", "").replace(" | PANDA", "").strip()
            time.sleep(3)

            elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='mod/']")
            seen = set()
            for el in elements:
                name = el.text.strip()
                url = el.get_attribute("href")
                key = (course_id, url)

                if name and key not in seen:
                    seen.add(key)
                    resources.append((course_id, course_name, name, url))

        return resources