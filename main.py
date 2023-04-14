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


def driver_init():
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


def wait_for_element(driver, *locator, timeout=30):
    try:
        return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(locator))
    except Exception:
        raise Exception(
            "Couldn't find element with locator: {} , for time period of: {} seconds\n".format(locator[1], timeout))


def wait_for_element_clickable(driver, *locator, timeout=30):
    try:
        return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))
    except Exception:
        raise Exception(
            "Couldn't find element with locator: {} , for time period of: {} seconds\n".format(locator[1], timeout))


def wait_for_element_to_be_visible(driver, *locator, timeout=30):
    try:
        return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))
    except Exception:
        return False


def wait_for_elements(driver, *locator, timeout=30):
    try:
        return WebDriverWait(driver, timeout).until(EC.visibility_of_any_elements_located(locator))
    except Exception:
        raise Exception(
            "Couldn't find element with locator: {} , for time period of: {} seconds\n".format(locator[1], timeout))


def geoLocationTest(driver, latitude=44.787197, longitude=20.457273):
    Map_coordinates = dict({
        "latitude": float(latitude),
        "longitude": float(longitude),
        "accuracy": 100
    })
    driver.execute_cdp_cmd("Page.setGeolocationOverride", Map_coordinates)


def driver_decorator(func):
    def wrapper(site, *args, **kwargs):
        print("Starting...")
        driver = driver_init()
        geoLocationTest(driver, kwargs["latitude"], kwargs["longitude"])
        driver.maximize_window()
        # try:
        func(driver, site, *args)
        # except Exception as e:
        #     print("Something went wrong!")
        #     print(e)
        print("Closing...")
        driver.close()
        driver.quit()

    return wrapper


@driver_decorator
def main(driver, site, *args):
    pages = 10
    keyword_dict_position = {}
    driver.get('https://www.google.com')
    for keyword in args:
        sites = []
        search_box = wait_for_element_to_be_visible(driver, By.XPATH, "//form[@action='/search']//input[@type='text']",5)
        if not search_box:
            search_box = wait_for_element_to_be_visible(driver, By.XPATH,
                                                        "//form[@action='/search']//textarea")
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.ENTER)
        driver.refresh()
        time.sleep(60)
        if wait_for_element_to_be_visible(driver, By.XPATH, "//table[@role='presentation']//a[@id='pnnext']",
                                          timeout=5):
            for page in range(pages):
                links = wait_for_elements(driver, By.XPATH, "//div[@id='search' or @id='botstuff']//a//div/cite",
                                          timeout=120)
                for link in links:
                    site_link = link.text
                    if 'http' in link.text:
                        sites.append(site_link.split(" ›")[0])
                try:
                    wait_for_element(driver, By.XPATH, "//table[@role='presentation']//a[@id='pnnext']",
                                     timeout=5).click()
                except:
                    print(f"Only {page + 1} checked")
                    break
        else:
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            for page in range(pages):
                try:
                    wait_for_element_clickable(driver, By.XPATH, "//span[@class='RVQdVd']", timeout=10).click()
                    time.sleep(5)
                except:
                    pass
            links = wait_for_elements(driver, By.XPATH, "//div[@id='search' or @id='botstuff']//a//div/cite",
                                      timeout=120)
            for link in links:
                site_link = link.text
                if 'http' in link.text:
                    site_link = site_link.split(" ›")[0]
                try:
                    site_link_minus_1 = links[links.index(link) - 1].text
                except:
                    site_link_minus_1 = ''
                if site_link not in site_link_minus_1:
                    sites.append(site_link.split(" ›")[0])

        for s in sites:
            if site in s:
                position = sites.index(s) + 1
                break
            else:
                position = "not in first 100"

        pathlib.Path(f"{site.replace('/', '').replace(':', '')}").mkdir(parents=True, exist_ok=True)
        file_path = pathlib.Path(f"{site.replace('/', '').replace(':', '')}", f'{keyword}_{position}.txt')
        with open(file_path, 'w') as f:
            f.write(f"{site} is positioned as " + str(position) + f' for keyword "{keyword}"\n\n')
            for item in sites:
                f.write(str(item) + "\n")

        driver.get('https://www.google.com')
        keyword_dict_position[keyword] = position

    folder_path = pathlib.Path(f"{site.replace('/', '').replace(':', '')}", "All keyword reports.txt")
    with open(folder_path, 'w') as f:
        for key, item in keyword_dict_position.items():
            f.write(f"For '{key}' position is : {item}.\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--latitude', required=False, default=44.787197)
    parser.add_argument('--longitude', required=False, default=20.457273)
    parser.add_argument('--site', required=True)
    parser.add_argument('--keywords', required=True)
    args = parser.parse_args()

    args.keywords = args.keywords.split(',')
    print(f"Longitude is: {args.longitude}")
    print(f"Latitude is: {args.latitude}")
    print(f"Site is: {args.site}")
    print(f"Keywords are/is: {args.keywords}")

    main(args.site, *args.keywords, longitude=args.longitude, latitude=args.latitude)
