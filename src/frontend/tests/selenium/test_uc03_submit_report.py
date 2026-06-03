import pytest 

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import os

@pytest.fixture
def driver(): 
    d = webdriver.Chrome()
    yield d
    d.quit()

def find_by_id(webdriver, widget_id):
    return webdriver.find_element(By.ID, widget_id)

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

def test_uc03_submit_report_success(logged_in_driver):
    wait = WebDriverWait(logged_in_driver, 10)

    # wait for new report button to appear
    new_report_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'nav-new-report')))
    new_report_button.click()

    # wait for the title box to appear
    title_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'report-title')))
    title_box.clear()
    
    title_box.send_keys('Pothole on Main Street')

    # wait for the description box to appear
    description_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'report-description')))
    description_box.clear()
    
    description_box.send_keys('There is a large pothole on Main Street that is causing damage to vehicles. It needs to be repaired as soon as possible.')

    # wait for the category, latitude, longitude, checkbox anonymous selections to appear
    wait.until(expected_conditions.element_to_be_clickable((By.ID, 'report-category')))
    wait.until(expected_conditions.visibility_of_element_located((By.ID, 'report-latitude')))
    wait.until(expected_conditions.visibility_of_element_located((By.ID, 'report-longitude')))
    wait.until(expected_conditions.element_to_be_clickable((By.ID, 'report-anonymous')))

    # wait for the map to appear
    report_map = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'new-report-map')))
    report_map.click() 

    # wait for the photo selection to appear
    photo_submit = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'report-photos')))

    current_dir = os.path.dirname(os.path.abspath(__file__))
    photo_path = os.path.join(current_dir, 'image_test', 'photo1.jpg')

    photo_submit.send_keys(photo_path)

    # wait for the submit report button to appear
    do_submit_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'new-report-submit')))
    logged_in_driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", do_submit_button) # scroll to the submit button
    do_submit_button.click()

    report_details = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'report-detail-title')))
    assert report_details.is_displayed()


def test_uc03_submit_missing_location_ext3a(logged_in_driver):
    wait = WebDriverWait(logged_in_driver, 10)

    # wait for new report button to appear
    new_report_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'nav-new-report')))
    new_report_button.click()

    # wait for the title box to appear
    title_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'report-title')))
    title_box.clear()
    title_box.send_keys('Pothole on Main Street')

    # wait for the description box to appear
    description_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'report-description')))
    description_box.clear()
    description_box.send_keys('There is a large pothole on Main Street.')

    # intentionally skip the map click (no location selected)

    # wait for the submit report button to appear
    do_submit_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'new-report-submit')))
    logged_in_driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", do_submit_button)
    do_submit_button.click()

    # report details should not be displayed
    assert len(logged_in_driver.find_elements(By.ID, 'report-detail-title')) == 0


def test_uc03_submit_missing_title_ext6a(logged_in_driver):
    wait = WebDriverWait(logged_in_driver, 10)

    # wait for new report button to appear
    new_report_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'nav-new-report')))
    new_report_button.click()

    # intentionally skip the title box

    # wait for the description box to appear
    description_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'report-description')))
    description_box.clear()
    description_box.send_keys('There is a large pothole on Main Street.')

    # wait for the map to appear
    report_map = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'new-report-map')))
    report_map.click() 

    # wait for the submit report button to appear
    do_submit_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'new-report-submit')))
    logged_in_driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", do_submit_button)
    do_submit_button.click()

    # report details should not be displayed
    assert len(logged_in_driver.find_elements(By.ID, 'report-detail-title')) == 0


def test_uc03_submit_too_many_photos_ext6b(logged_in_driver):
    wait = WebDriverWait(logged_in_driver, 10)

    # wait for new report button to appear
    new_report_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'nav-new-report')))
    new_report_button.click()

    # wait for the title box to appear
    title_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'report-title')))
    title_box.clear()
    title_box.send_keys('Pothole on Main Street')

    # wait for the description box to appear
    description_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'report-description')))
    description_box.clear()
    description_box.send_keys('There is a large pothole on Main Street.')

    # wait for the map to appear
    report_map = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'new-report-map')))
    report_map.click() 

    # wait for the photo selection to appear
    photo_submit = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'report-photos')))

    # sumbit 4 photos to trigger the extension 6b error
    current_dir = os.path.dirname(os.path.abspath(__file__))
    photo_path = os.path.join(current_dir, 'image_test', 'photo1.jpg')
    four_photos = "\n".join([photo_path, photo_path, photo_path, photo_path])

    photo_submit.send_keys(four_photos)

    # wait for the submit report button to appear
    do_submit_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'new-report-submit')))
    logged_in_driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", do_submit_button)
    do_submit_button.click()

    # report details should not be displayed
    assert len(logged_in_driver.find_elements(By.ID, 'report-detail-title')) == 0