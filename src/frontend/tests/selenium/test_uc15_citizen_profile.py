import pytest 

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import os
import uuid

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

def test_uc15_manage_citizen_profile_success(logged_in_driver):
    driver = logged_in_driver
    wait = WebDriverWait(driver, 10)

    # Click on profile link
    profile_link = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'nav-dashboard')))
    profile_link.click()

    # The profile details are already editable and pre-filled with the current information, wait until they are visible
    username_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'profile-username')))
    first_name_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'profile-first-name')))
    last_name_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'profile-last-name')))
    email_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'profile-email')))
    email_notification_checkbox = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'profile-email-notifications')))
    profile_picture_input = wait.until(expected_conditions.presence_of_element_located((By.ID, 'profile-picture')))

    # Assert current fields are displayed
    assert username_box.is_displayed()
    assert first_name_box.is_displayed()
    assert last_name_box.is_displayed()
    assert email_box.is_displayed()
    assert email_notification_checkbox.is_displayed()

    unique_suffix = uuid.uuid4().hex[:4]
    new_first_name = f'John {unique_suffix}'
    new_last_name = f'Doe {unique_suffix}'

    # Update some profile information (e.g., first name and last name fields)
    first_name_box.clear()
    first_name_box.send_keys(new_first_name)
    last_name_box.clear()
    last_name_box.send_keys(new_last_name)

    # Update profile picture
    profile_picture_path = os.path.abspath('tests/selenium/image_test/photo1.jpg' \
    '')
    assert os.path.exists(profile_picture_path)
    profile_picture_input.send_keys(profile_picture_path)

    # Click on save button to save the changes
    save_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'profile-save')))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_button)
    save_button.click()

    # Assert success message
    success_message = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'profile-success')))
    assert success_message.is_displayed()
    assert success_message.text == 'Profile updated.'

    # Assert updated values are still in the form
    assert first_name_box.get_attribute('value') == new_first_name
    assert last_name_box.get_attribute('value') == new_last_name

def test_uc15_manage_citizen_profile_cancel(logged_in_driver):
    driver = logged_in_driver
    wait = WebDriverWait(driver, 10)

    # Click on profile link
    profile_link = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'nav-dashboard')))
    profile_link.click()

    # Wait for the profile details to be visible
    first_name_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'profile-first-name')))
    last_name_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'profile-last-name')))
    
    # Assert current fields are displayed
    assert first_name_box.is_displayed()
    assert last_name_box.is_displayed()

    # Store previous profile state 
    previous_first_name = first_name_box.get_attribute('value') 
    previous_last_name = last_name_box.get_attribute('value') 
    
    # Modify fields in order to verify that they will not be saved 
    first_name_box.clear() 
    first_name_box.send_keys('NotSavedName') 
    last_name_box.clear() 
    last_name_box.send_keys('NotSavedLastName')

    # User cancels the change by reloading the page without saving
    driver.get('http://localhost:5173/dashboard')

    # Check that the previous profile state is still there
    first_name_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'profile-first-name')))
    last_name_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'profile-last-name')))

    assert first_name_box.get_attribute('value') == previous_first_name
    assert last_name_box.get_attribute('value') == previous_last_name
