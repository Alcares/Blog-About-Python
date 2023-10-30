import sys
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from time import sleep
from selenium.webdriver.common.by import By


chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)


def run_driver():
    driver.get('https://blog-test-j33f.onrender.com/')
    menu = driver.find_element(by=By.CSS_SELECTOR, value="#mainNav > div > button")
    driver.implicitly_wait(2)
    menu.click()
    driver.implicitly_wait(2)
    about_nav = driver.find_element(by=By.CSS_SELECTOR, value="#navbarResponsive > ul > li:nth-child(3) > a")
    driver.implicitly_wait(2)
    about_nav.click()
    for i in range(100):
        h1 = driver.find_element(By.CSS_SELECTOR, value="h1")
        sub = driver.find_element(By.CSS_SELECTOR, value=".subheading")
        try:
            ActionChains(driver)\
                .move_to_element(h1)\
                .perform()
            sleep(0.5)
            ActionChains(driver)\
                .move_to_element(sub)\
                .perform()
        except:
            continue
    home = driver.find_element(By.CSS_SELECTOR, value="#mainNav > div > a")
    home.click()
    sleep(1)
    driver.quit()
    sys.exit(0)


if __name__ == '__main__':
    run_driver()