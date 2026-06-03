import pytest 

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

@pytest.fixture
def driver(): 
    d = webdriver.Chrome()
    yield d
    d.quit()

def find_by_id(webdriver, widget_id):
    return webdriver.find_element(By.ID, widget_id)

def test_uc04_browse_map(driver): 
    driver.get('http://localhost:5173')
    wait = WebDriverWait(driver, 10)

    map = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'public-map')))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", map)

    marker = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'public-report-row-2-map-marker')))
    marker.click() # to make the popup appear

    popup = wait.until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, 'leaflet-popup')))
    assert popup.is_displayed() 

    # Click the popup in order to access the report details page
    # This feature is not implemented yet, so the following code is commented out to avoid test failure. Once the feature is implemented, uncomment the code to test it.
    # popup.click()
    # report_details = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'report-detail-title')))
    # assert report_details.is_displayed()