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

@pytest.fixture
def admin_logged_in_driver(driver):
    driver.get('http://localhost:5173')
    wait = WebDriverWait(driver, 10)

    # 1. Click login button
    login_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'login-link')))
    login_button.click()

    # 2. Insert credentials
    username_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'login-identifier')))
    username_box.clear()
    username_box.send_keys('admin@example.com')

    password_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'login-password')))
    password_box.clear()
    password_box.send_keys('Admin123!')

    # 3. Click on submit
    do_login_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'login-submit')))
    do_login_button.click()

    # 4. wait until log
    wait.until(expected_conditions.visibility_of_element_located((By.ID, 'logout-button')))
 
    yield driver

def find_by_id(webdriver, widget_id):
    return webdriver.find_element(By.ID, widget_id)

def test_uc13_view_private_statistics_success(admin_logged_in_driver):
    driver = admin_logged_in_driver
    wait = WebDriverWait(driver, 10)

    # Check that admin is already on the admin page after login
    admin_page = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'admin-page')))
    assert admin_page.is_displayed()

    statistics_section = wait.until(expected_conditions.presence_of_element_located((By.ID, 'admin-statistics-section')))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", statistics_section)
    assert statistics_section.is_displayed()

    # Reports by status
    reports_by_status = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'admin-metric-item-reports-by-status')))
    assert reports_by_status.is_displayed()
    # Aspettiamo che appaiano i dati veri e propri (gli 'li')
    reports_by_status_items = wait.until(expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, '#admin-metric-item-reports-by-status-list li')))
    assert len(reports_by_status_items) > 0

    # Reports by type
    reports_by_type = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'admin-metric-item-reports-by-type')))
    assert reports_by_type.is_displayed()
    reports_by_type_items = wait.until(expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, '#admin-metric-item-reports-by-type-list li')))
    assert len(reports_by_type_items) > 0

    # Reports by reporter
    reports_by_reporter = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'admin-metric-item-reports-by-reporter')))
    assert reports_by_reporter.is_displayed()
    reports_by_reporter_items = wait.until(expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, '#admin-metric-item-reports-by-reporter-list li')))
    assert len(reports_by_reporter_items) > 0

    # Top 1 percent by type
    top_1_percent = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'admin-metric-item-top-1-percent-by-type')))
    assert top_1_percent.is_displayed()
    top_1_percent_items = wait.until(expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, '#admin-metric-item-top-1-percent-by-type-list li')))
    assert len(top_1_percent_items) > 0

    # Top 5 percent by type
    top_5_percent = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'admin-metric-item-top-5-percent-by-type')))
    assert top_5_percent.is_displayed()
    top_5_percent_items = wait.until(expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, '#admin-metric-item-top-5-percent-by-type-list li')))
    assert len(top_5_percent_items) > 0
    
    