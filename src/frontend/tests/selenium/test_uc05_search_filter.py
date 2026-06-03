import pytest 

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions
from datetime import datetime, timedelta

@pytest.fixture
def driver(): 
    d = webdriver.Chrome()
    yield d
    d.quit()

def find_by_id(webdriver, widget_id):
    return webdriver.find_element(By.ID, widget_id)

def test_uc05_search_filter_success(driver): 
    driver.get('http://localhost:5173')
    wait = WebDriverWait(driver, 10)

    # Wait for the table view to be visible 
    table_view = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'public-report-table')))
    table_body = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'public-report-table-body')))

    # Apply the search filter by category
    category_filter = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'public-filter-category')))
    category_select = Select(category_filter)
    category_select.select_by_visible_text('Roads and Urban Furniture')

    # Apply the search filter by status
    status_filter = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'public-filter-status')))
    status_select = Select(status_filter)
    status_select.select_by_visible_text('Resolved')
    
    # Apply the search filter by date range - set to last 24 hours
    start_date_filter = wait.until(
    expected_conditions.visibility_of_element_located((By.ID, "public-filter-date-from")))

    end_date_filter = wait.until(expected_conditions.visibility_of_element_located((By.ID, "public-filter-date-to")))

    now = datetime.now()
    yesterday = now - timedelta(days=1)

    date_from = yesterday.strftime("%Y-%m-%dT%H:%M")
    date_to = now.strftime("%Y-%m-%dT%H:%M")

    start_date_filter.clear()
    start_date_filter.send_keys(date_from)

    end_date_filter.clear()
    end_date_filter.send_keys(date_to)

    # Change sorting order to ascending (Oldest first)    
    sort_by = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'public-filter-sort')))
    sort_select = Select(sort_by)
    sort_select.select_by_visible_text('Oldest first')

    # Wait for the apply filters button to appear
    apply_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'public-filter-submit')))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", apply_button)
    apply_button.click()

    # assert that at least one report row is displayed
    report_rows = wait.until(expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, '[id^="public-report-row-"]')))
    assert len(report_rows) > 0

 
def test_uc05_search_filter_no_results_ext4a(driver):
    driver.get('http://localhost:5173')
    wait = WebDriverWait(driver, 10)

    # Apply the search filter by category (no reports associated with Waste category)
    category_filter = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'public-filter-category')))
    category_select = Select(category_filter)
    category_select.select_by_visible_text('Waste')

    # wait for the apply filters button to appear and click it
    apply_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'public-filter-submit')))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", apply_button)
    apply_button.click()

    wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, '[id^="public-report-row-"]')) == 0)

    # assert that no report rows are displayed
    report_rows = driver.find_elements(By.CSS_SELECTOR, '[id^="public-report-row-"]')
    assert len(report_rows) == 0