import json
import pandas as pd
from pathlib import Path

from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException
)

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from seleniumwire import webdriver, utils

from webdriver_manager.chrome import ChromeDriverManager


# Elements we want to interact with and how to find them
LOCATION_DROPDOWN = (By.ID, "location")
SEARCH_BUTTON = (By.CLASS_NAME, "btn.btn-primary.m-0")
POP_UP_CLOSE_BUTTON = (By.CLASS_NAME, "fancybox-item.fancybox-close")
LOADING_BACKDROP = (By.CLASS_NAME, "backdrop")


def initialise_driver(url):
    options = webdriver.ChromeOptions()
    options.add_argument("auto-open-devtools-for-tabs")
    options.add_argument("start-maximised")
    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.get(url)
    return driver


def wait_for_element_to_appear(driver, element, timeout=30):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(element))


def wait_for_element_to_disappear(driver, element, timeout=30):
    WebDriverWait(driver, timeout).until_not(EC.presence_of_element_located(element))


def check_for_loading_screen(driver):
    try:
        wait_for_element_to_disappear(driver, LOADING_BACKDROP, 30)
    except NoSuchElementException:
        pass


def close_pop_up(driver):
    try:
        driver.find_element(*POP_UP_CLOSE_BUTTON).click()
    except NoSuchElementException:
        pass


def iterate_through_location_list(driver):
    # Maximise window
    driver.maximize_window()
    # Get dropdown element
    dropdown = Select(wait_for_element_to_appear(driver, LOCATION_DROPDOWN))
    locations = dropdown.options  # Get the locations
    # Start at 1 to avoid the selection item
    for index in range(1, len(locations) + 1):
        dropdown = Select(wait_for_element_to_appear(driver, LOCATION_DROPDOWN))
        # Select the location element based on the index number
        dropdown.select_by_index(index)
        # Wait for the search button to appear
        button = wait_for_element_to_appear(driver, SEARCH_BUTTON)
        # Attempt to click the search button
        # Set status of click to false
        clicked = False
        # While the search button remains unclicked check for a loading screen or a pop up and deal with them
        while not clicked:
            try:
                button.click()
                clicked = True
            # If the click is intercepted by either the loading screen or pop up these are dealt with
            except ElementClickInterceptedException:
                check_for_loading_screen(driver)
                close_pop_up(driver)


def get_network_responses(outfile):

    response_df_list = []
    for request in driver.requests:
        if request.url == "https://apis.cambridgeassessment.org.uk/ce/v1/find-a-centre/centres" \
                and request.response.status_code != 500:

            response = utils.decode(
                request.response.body,
                request.response.headers.get("Content-Encoding", "identity")
            )
            response = response.decode("utf8")
            json_data = json.loads(response)
            response_df = pd.json_normalize(json_data, errors="ignore")
            response_df = response_df[["CentreId", "Name", "Longitude", "Latitude"]]
            response_df_list.append(response_df)

    final_df = pd.concat(response_df_list)
    final_df.to_csv(outfile, index=False)
    print(final_df)


if __name__ == "__main__":

    TARGET_URL = "https://www.cambridgeenglish.org/find-a-centre/find-an-exam-centre/"
    driver = initialise_driver(TARGET_URL)
    iterate_through_location_list(driver)
    get_network_responses(outfile=Path("Centre_Locations.csv"))
    driver.close()
    driver.quit()
