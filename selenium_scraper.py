from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from seleniumwire import webdriver
from seleniumwire.utils import decode
import pandas as pd
import json


TARGET_URL = "https://www.cambridgeenglish.org/find-a-centre/find-an-exam-centre/"

options = webdriver.ChromeOptions()
options.add_argument("auto-open-devtools-for-tabs")
options.add_argument("start-maximised")
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# Elements we want to interact with and how to find them
LOCATION_DROPDOWN = (By.ID, "location")
SEARCH_BUTTON = (By.CLASS_NAME, "btn.btn-primary.m-0")
POP_UP_CLOSE_BUTTON = (By.CLASS_NAME, "fancybox-item.fancybox-close")
LOADING_BACKDROP = (By.CLASS_NAME, "backdrop")


def wait_for_element_to_appear(driver, element, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(element))


def wait_for_element_to_disappear(driver, element, timeout=10):
    WebDriverWait(driver, timeout).until_not(EC.presence_of_element_located(element))


def wait_for_element_to_appear(length, element):
    WebDriverWait(driver, length).until(EC.presence_of_element_located(element))


def wait_for_element_to_disappear(length, element):
    WebDriverWait(driver, length).until_not(EC.presence_of_element_located(element))


def check_for_loading_screen():
    try:
        wait_for_element_to_disappear(20, loading_backdrop_by_class_name)
    except NoSuchElementException:
        pass


def close_pop_up():
    try:
        find_element(*pop_up_close_button_by_class_name).click()
    except NoSuchElementException:
        pass


def iterate_through_location_list():
    # For each country in location list the following steps will be performed

    location_count = len(Select(find_element(*location_element_by_id)).options)
    location_count = 2
    for index in range(0, location_count):
        # Wait for the location element to appear
        wait_for_element_to_appear(length=10, element=location_element_by_id)
        # Select the location element based on the index number
        select_element(find_element(*location_element_by_id)).select_by_index(index)
        # Wait for the search button to appear
        wait_for_element_to_appear(length=30, element=search_button_by_class_name)

        # Attempt to click the search button 
        # Set status of click to false
        clicked = False

        # While the search button remains unclicked check for a loading screen or a pop up and deal with them
        while not clicked:
            try:
                find_element(*search_button_by_class_name).click()
                clicked = True

            # If the click is intercepted by either the loading screen or pop up these are dealt with
            except ElementClickInterceptedException:
                check_for_loading_screen()
                close_pop_up()


def get_network_responses(outfile):

    final_dataframe = []
    for request in driver.requests:
        if request.url == "https://apis.cambridgeassessment.org.uk/ce/v1/find-a-centre/centres" \
                and request.response.status_code != 500:
            response = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
            response = response.decode("utf8")
            json_data = json.loads(response)
            response_as_dataframe = pd.json_normalize(json_data, errors='ignore')
            response_as_dataframe = response_as_dataframe[['CentreId', 'Name', 'Longitude', 'Latitude']]
            final_dataframe.append(response_as_dataframe)

    final_dataframe = pd.concat(final_dataframe)
    final_dataframe.to_csv(outfile, index=False)
    print(final_dataframe)


if __name__ == '__main__':
    driver.get(TARGET_URL)
    driver.maximize_window()
    iterate_through_location_list()
    get_network_responses(outfile=Path("Centre_Locations.csv"))
