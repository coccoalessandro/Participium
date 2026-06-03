import pytest 

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

import time

@pytest.fixture
def driver(): 
    d = webdriver.Chrome()
    yield d
    d.quit()

def find_by_id(webdriver, widget_id):
    return webdriver.find_element(By.ID, widget_id)

def test_uc01_register_success(driver):
    driver.get('http://localhost:5173')
    wait = WebDriverWait(driver, 10)

    # wait for register button to appear
    register_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'register-link')))
    register_button.click()

    # wait for the username box to appear
    username_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'register-username')))
    username_box.clear()

    unique_username = f"user_{str(time.time()).replace('.', '')}"
    username_box.send_keys(unique_username)

    # wait for the first name box to appear
    first_name_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'register-first-name')))
    first_name_box.clear()
    
    first_name_box.send_keys('FirstName')

    # wait for the last name box to appear
    last_name_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'register-last-name')))
    last_name_box.clear()
    
    last_name_box.send_keys('LastName')

    # wait for the email box to appear
    email_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'register-email')))
    email_box.clear()
    
    unique_email = f"mail_{str(time.time()).replace('.', '')}@example.com"
    email_box.send_keys(unique_email)

    # wait for the password box to appear
    password_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'register-password')))
    password_box.clear()
    
    password_box.send_keys('examplePsw123!')

    # wait for the create account button appear
    create_account_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'register-submit')))

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", create_account_button)

    create_account_button.click()

    success_message = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'register-success')))

    #assert success message
    assert success_message.is_displayed()

def test_uc01_register_username_taken_ext4a(driver):
    driver.get('http://localhost:5173')
    wait = WebDriverWait(driver, 10)

    # wait for register button to appear
    register_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'register-link')))
    register_button.click()

    # wait for the username box to appear (use existing username)
    username_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'register-username')))
    username_box.clear()
    username_box.send_keys('citizen') 

    # wait for the first name box to appear
    first_name_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'register-first-name')))
    first_name_box.clear()
    first_name_box.send_keys('New')

    # wait for the last name box to appear
    last_name_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'register-last-name')))
    last_name_box.clear()
    last_name_box.send_keys('User')

    # wait for the email box to appear (use unique email)
    unique_email = f"mail_{str(time.time()).replace('.', '')}@example.com"
    email_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'register-email')))
    email_box.clear()
    email_box.send_keys(unique_email)

    # wait for the password box to appear
    password_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'register-password')))
    password_box.clear()
    password_box.send_keys('Citizen123!')

    # wait for the create account button appear
    create_account_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'register-submit')))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", create_account_button)
    create_account_button.click()

    # assert error message
    error_message = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'register-error')))
    assert error_message.is_displayed()


def test_uc01_register_email_taken_ext4b(driver):
    driver.get('http://localhost:5173')
    wait = WebDriverWait(driver, 10)

    # wait for register button to appear
    register_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'register-link')))
    register_button.click()

    # wait for the username box to appear (use unique username)
    unique_username = f"user_{str(time.time()).replace('.', '')}"
    username_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'register-username')))
    username_box.clear()
    username_box.send_keys(unique_username)

    # wait for the first name box to appear
    first_name_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'register-first-name')))
    first_name_box.clear()
    first_name_box.send_keys('New')

    # wait for the last name box to appear
    last_name_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'register-last-name')))
    last_name_box.clear()
    last_name_box.send_keys('User')

    # wait for the email box to appear (use existing email)
    email_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'register-email')))
    email_box.clear()
    email_box.send_keys('citizen@example.com')

    # wait for the password box to appear
    password_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'register-password')))
    password_box.clear()
    password_box.send_keys('Citizen123!')

    # wait for the create account button appear
    create_account_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'register-submit')))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", create_account_button)
    create_account_button.click()

    # assert error message
    error_message = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'register-error')))
    assert error_message.is_displayed()


def test_uc01_register_missing_field_ext4c(driver):
    driver.get('http://localhost:5173')
    wait = WebDriverWait(driver, 10)

    # wait for register button to appear
    register_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'register-link')))
    register_button.click()

    # wait for the username box to appear
    unique_username = f"user_{str(time.time()).replace('.', '')}"
    username_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'register-username')))
    username_box.clear()
    username_box.send_keys(unique_username)

    # wait for the first name box to appear
    first_name_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'register-first-name')))
    first_name_box.clear()
    first_name_box.send_keys('New')

    # wait for the last name box to appear
    last_name_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'register-last-name')))
    last_name_box.clear()
    last_name_box.send_keys('User')

    # intentionally skip the email box
    
    # wait for the password box to appear
    password_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'register-password')))
    password_box.clear()
    password_box.send_keys('Citizen123!')

    # wait for the create account button appear
    create_account_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'register-submit')))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", create_account_button)
    create_account_button.click()

    # assert form submission is blocked and success message is not displayed
    assert len(driver.find_elements(By.ID, 'register-success')) == 0