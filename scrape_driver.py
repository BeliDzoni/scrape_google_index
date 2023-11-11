import os
import time
import sys
import argparse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pathlib
import chrome_auto_installer
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class Driver:
    def __init__(self, latitude=44.787197, longitude=20.457273):
        self.driver = self.driver_init()
        self.geoLocationTest(latitude, longitude)
        self.driver.maximize_window()
        self.driver.get('https://www.google.com')

    def __del__(self):
        print("Closing...")
        self.driver.close()
        self.driver.quit()

    def geoLocationTest(self, latitude=44.787197, longitude=20.457273):
        Map_coordinates = dict({
            "latitude": float(latitude),
            "longitude": float(longitude),
            "accuracy": 100
        })
        self.driver.execute_cdp_cmd("Page.setGeolocationOverride", Map_coordinates)

    def driver_init(self):
        options = Options()
        # options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--lang=en-US")
        options.add_argument("--arc-disable-locale-sync")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-search-geolocation-disclosure")
        chrome_auto_installer.install(cwd=True)
        driver = webdriver.Chrome(options=options)
        return driver

    def wait_for_element(self, locator, timeout=30):
        try:
            return WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
        except Exception:
            raise Exception(
                "Couldn't find element with locator: {} , for time period of: {} seconds\n".format(locator[1], timeout))

    def wait_for_element_clickable(self, locator, timeout=30):
        try:
            return WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(locator))
        except Exception:
            raise Exception(
                "Couldn't find element with locator: {} , for time period of: {} seconds\n".format(locator[1], timeout))

    def wait_for_element_to_be_visible(self, locator, timeout=30):
        try:
            return WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(locator))
        except Exception:
            return False

    def wait_for_elements(self, locator, timeout=30):
        try:
            return WebDriverWait(self.driver, timeout).until(EC.visibility_of_any_elements_located(locator))
        except Exception:
            raise Exception(
                "Couldn't find element with locator: {} , for time period of: {} seconds\n".format(locator[1], timeout))


class Scrape(Driver):
    SEARCH_BOX_1 = (By.XPATH, "//form[@action='/search']//input[@type='text']")
    SEARCH_BOX_2 = (By.XPATH, "//form[@action='/search']//textarea")
    PAGES_INDICATOR = (By.XPATH, "//table[@role='presentation']//a[@id='pnnext']")
    LINKS = (By.XPATH, "//div[@id='search' or @id='botstuff']//a//div/cite")
    INFINITE_SCROLL_LOAD_MORE = (By.XPATH, "//span[@class='RVQdVd']")

    def __init__(self, site, keywords, latitude=44.787197, longitude=20.457273):
        super().__init__(latitude, longitude)
        self.site = site
        self.keywords = keywords
        self.pages = 10

    def pages_scrape(self):
        sites = []
        for page in range(self.pages):
            links = self.wait_for_elements(self.LINKS, timeout=120)
            for link in links:
                site_link = link.text
                if 'http' in link.text:
                    sites.append(site_link.split(" ›")[0])
            try:
                self.wait_for_element(self.PAGES_INDICATOR, timeout=5).click()
            except:
                print(f"Only {page + 1} checked")
                break
        return sites

    def infinity_scroll_scrape(self):
        sites = []
        last_links = self.wait_for_elements(self.LINKS, timeout=120)
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            new_links = self.wait_for_elements(self.LINKS, timeout=120)
            if len(new_links) == len(last_links) or len(new_links) > 100:
                break
            last_links = new_links
        # for page in range(self.pages):
            try:
                self.wait_for_element_clickable(self.INFINITE_SCROLL_LOAD_MORE, timeout=10).click()
                time.sleep(5)
            except:
                pass
        # links = self.wait_for_elements(self.LINKS, timeout=120)
        for link in new_links:
            site_link = link.text
            if 'http' in link.text:
                site_link = site_link.split(" ›")[0]
            try:
                site_link_minus_1 = new_links[new_links.index(link) - 1].text
            except:
                site_link_minus_1 = ''
            if site_link not in site_link_minus_1:
                sites.append(site_link.split(" ›")[0])
        return sites

    def position_check(self, sites):
        for s in sites:
            if self.site in s:
                position = sites.index(s) + 1
                break
            else:
                position = f"not in first {len(sites)}"
        return position

    def keyword_position(self, keyword, position, sites):
        file_path = pathlib.Path(f"{self.site.replace('/', '').replace(':', '')}", f'{keyword}_{position}.txt')
        with open(file_path, 'w') as f:
            f.write(f"{self.site} is positioned as " + str(position) + f' for keyword "{keyword}"\n\n')
            for item in sites:
                f.write(str(item) + "\n")

    def total_keyword_position(self, keyword_dict_position):
        folder_path = pathlib.Path(f"{self.site.replace('/', '').replace(':', '')}", "All keyword reports.txt")
        with open(folder_path, 'w') as f:
            for key, item in keyword_dict_position.items():
                f.write(f"For '{key}' position is : {item}.\n")

    def scrape(self):
        keyword_dict_position = {}
        for keyword in self.keywords:
            sites = []
            search_box = self.wait_for_element_to_be_visible(self.SEARCH_BOX_1, timeout=5)
            if not search_box:
                search_box = self.wait_for_element_to_be_visible(self.SEARCH_BOX_2)
            search_box.send_keys(keyword)
            search_box.send_keys(Keys.ENTER)
            if self.wait_for_element_to_be_visible(self.PAGES_INDICATOR, timeout=10):
                sites = self.pages_scrape()
            else:
                sites = self.infinity_scroll_scrape()

            position = self.position_check(sites)

            pathlib.Path(f"{self.site.replace('/', '').replace(':', '')}").mkdir(parents=True, exist_ok=True)
            self.keyword_position(keyword, position, sites)

            self.driver.get('https://www.google.com')
            keyword_dict_position[keyword] = position

        self.total_keyword_position(keyword_dict_position)


# scrape = Scrape('miter.rs', ['inofolic', 'nesto2'], latitude=40.813778, longitude=-74.074310)
# scrape.scrape()
