from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
from selenium import webdriver


def get_driver():
    gecko_driver = r'C:\Users\Malcolm\OneDrive\Documents\geckodriver.exe'
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options, executable_path=gecko_driver)
    driver.fullscreen_window()
    return driver


def element_exists_by_id(driver, id):
    try:
        return driver.find_element_by_id(id).is_displayed()
    except NoSuchElementException:
        return False


def element_exists_by_xpath(driver, xpath):
    try:
        return driver.find_element_by_xpath(xpath).is_displayed()
    except NoSuchElementException:
        return False


def element_exists_by_class(driver, cls):
    try:
        return driver.find_element_by_class_name(cls).is_displayed()
    except NoSuchElementException:
        return False

