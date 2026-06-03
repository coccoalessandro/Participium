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


def test_uc06_view_report_details_success(driver):
    driver.get('http://localhost:5173')
    wait = WebDriverWait(driver, 10)

    # wait for at least one report row to appear
    first_row = wait.until(expected_conditions.element_to_be_clickable(
        (By.CSS_SELECTOR, "tr[id^='public-report-row-']")
    ))
    
    # scroll to the row and click it to open details
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", first_row)
    
    open_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'public-report-row-2-open-link')))
    open_button.click()
    
    # wait for the report detail page to load
    report_title = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'report-detail-title')))
    report_description = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'report-detail-description')))
    report_status = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'report-detail-status')))
    report_category = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'report-detail-category')))
    report_map = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'report-detail-map-card')))
    report_photos = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'report-detail-photos-card')))
    report_status_history = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'status-history-card')))

    # assert that the main details are displayed
    assert report_title.is_displayed()
    assert report_description.is_displayed()
    assert report_status.is_displayed()
    assert report_category.is_displayed()
    assert report_map.is_displayed()
    assert report_photos.is_displayed()
    assert report_status_history.is_displayed()


def test_uc06_view_report_not_found_ext2a(driver):
    # navigate directly to a fake/non-existent report ID
    driver.get('http://localhost:5173/reports/999999999')
    wait = WebDriverWait(driver, 10)

    # wait for the 'not found' error message to appear
    error_message = wait.until(expected_conditions.visibility_of_element_located(
        (By.ID, 'report-detail-error')
    ))    
    # assert the error message is displayed
    assert error_message.is_displayed()
