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
def logged_in_driver(driver):
    driver.get('http://localhost:5173')
    wait = WebDriverWait(driver, 10)

    # 1. Click login button
    login_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'login-link')))
    login_button.click()

    # 2. Insert credentials
    username_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'login-identifier')))
    username_box.clear()
    username_box.send_keys('citizen@example.com')

    password_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'login-password')))
    password_box.clear()
    password_box.send_keys('Citizen123!')

    # 3. Click on submit
    do_login_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'login-submit')))
    do_login_button.click()

    # 4. wait until log
    wait.until(expected_conditions.visibility_of_element_located((By.ID, 'logout-button')))
 
    yield driver

def find_by_id(webdriver, widget_id):
    return webdriver.find_element(By.ID, widget_id)

def test_uc16_logout_success(logged_in_driver):
    driver = logged_in_driver
    wait = WebDriverWait(driver, 10)

    # Click logout button
    logout_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'logout-button')))
    logout_button.click()

    # After logout, the public login link should be visible again
    login_button = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'login-title')))

    # Assert session appears terminated from the UI
    assert login_button.is_displayed()