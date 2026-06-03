import pytest 

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions

@pytest.fixture
def driver(): 
    d = webdriver.Chrome()
    yield d
    d.quit()

def find_by_id(webdriver, widget_id):
    return webdriver.find_element(By.ID, widget_id)


def test_uc08_export_link_visible(driver):
    driver.get('http://localhost:5173')
    wait = WebDriverWait(driver, 10)

    # wait for the export link to appear
    export_link = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'public-export-link')))

    # assert the link is displayed and points to the export endpoint
    assert export_link.is_displayed()
    href = export_link.get_attribute('href')
    assert '/reports/export' in href


def test_uc08_export_href_reflects_status_filter(driver):
    driver.get('http://localhost:5173')
    wait = WebDriverWait(driver, 10)

    # wait for the filter form to appear
    wait.until(expected_conditions.visibility_of_element_located((By.ID, 'public-filter-form')))

    # select 'Resolved' from the status dropdown
    status_select = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'public-filter-status')))
    Select(status_select).select_by_visible_text('Resolved')

    # wait for the filter submit button and click it
    filter_submit = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'public-filter-submit')))
    filter_submit.click()

    # wait for the export link href to reflect the active filter
    wait.until(lambda d: 'Resolved' in (d.find_element(By.ID, 'public-export-link').get_attribute('href') or ''))

    # assert the export href contains the 'Resolved' filter parameter
    export_href = driver.find_element(By.ID, 'public-export-link').get_attribute('href')
    assert 'Resolved' in export_href

