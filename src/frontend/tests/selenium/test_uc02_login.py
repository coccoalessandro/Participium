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

def test_uc02_login_success(driver):
    driver.get('http://localhost:5173')
    wait = WebDriverWait(driver, 10)

    # wait for login button to appear
    login_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'login-link')))
    login_button.click()

    # wait for the username box to appear
    username_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'login-identifier')))
    username_box.clear()
    
    username_box.send_keys('citizen@example.com')

    # wait for the password box to appear
    password_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'login-password')))
    password_box.clear()
    
    password_box.send_keys('Citizen123!')

    # wait for the login button appear
    do_login_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'login-submit')))
    do_login_button.click()

    logout_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'logout-button')))

    #assert logout button
    assert logout_button.is_displayed()

def test_login_invalid_credentials_uc02_ext4a(driver):
    driver.get('http://localhost:5173')
    wait = WebDriverWait(driver, 10)

    # wait for login button to appear
    login_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'login-link')))
    login_button.click()

    # wait for the username box to appear (valid email)
    username_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'login-identifier')))
    username_box.clear()
    username_box.send_keys('citizen@example.com')

    # wait for the password box to appear (wrong password)
    password_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'login-password')))
    password_box.clear()
    password_box.send_keys('WrongPassword!')

    # wait for the login button appear
    do_login_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'login-submit')))
    do_login_button.click()

    # assert error message
    error_message = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'login-error')))
    assert error_message.is_displayed()


def test_login_unverified_account_uc02_ext4b(driver):
    driver.get('http://localhost:5173')
    wait = WebDriverWait(driver, 10)

    # wait for login button to appear
    login_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'login-link')))
    login_button.click()

    # wait for the username box to appear (non verified account)
    username_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'login-identifier')))
    username_box.clear()
    username_box.send_keys('unverified@example.com')

    # wait for the password box to appear
    password_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'login-password')))
    password_box.clear()
    password_box.send_keys('Unverified123!')

    # wait for the login button appear
    do_login_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'login-submit')))
    do_login_button.click()

    # assert unverified error message
    unverified_message = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'login-error')))
    assert unverified_message.is_displayed()
    