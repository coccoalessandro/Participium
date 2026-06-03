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

@pytest.fixture
def second_citizen_driver(driver):
    wait = WebDriverWait(driver, 10)
    
    driver.get('http://localhost:5173')
    wait.until(expected_conditions.element_to_be_clickable((By.ID, 'register-link'))).click()
    
    unique_suffix = str(time.time()).replace('.', '')
    unique_email = f"follower_{unique_suffix}@example.com"
    
    wait.until(expected_conditions.visibility_of_element_located((By.ID, 'register-username'))).send_keys(f"user_{unique_suffix}")
    driver.find_element(By.ID, 'register-first-name').send_keys('Follower')
    driver.find_element(By.ID, 'register-last-name').send_keys('Test')
    driver.find_element(By.ID, 'register-email').send_keys(unique_email)
    driver.find_element(By.ID, 'register-password').send_keys('Follower123!')
    
    submit_btn = driver.find_element(By.ID, 'register-submit')
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
    submit_btn.click()
    
    verify_link = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'verification-link')))
    verify_url = verify_link.get_attribute('href')
    driver.get(verify_url) 
    
    driver.get('http://localhost:5173')
    wait.until(expected_conditions.element_to_be_clickable((By.ID, 'login-link'))).click()
    username_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'login-identifier')))
    username_box.clear()
    username_box.send_keys(unique_email)

    psw_box = driver.find_element(By.ID, 'login-password')
    psw_box.clear()
    psw_box.send_keys('Follower123!')

    driver.find_element(By.ID, 'login-submit').click()
    
    wait.until(expected_conditions.visibility_of_element_located((By.ID, 'logout-button')))
    
    yield driver


def find_by_id(webdriver, widget_id):
    return webdriver.find_element(By.ID, widget_id)

def test_uc07_follow_report(second_citizen_driver): 
    wait = WebDriverWait(second_citizen_driver, 10)

    home_button = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'nav-home')))
    home_button.click()

    # wait for at least one report row to appear and click it
    first_row = wait.until(expected_conditions.element_to_be_clickable(
        (By.CSS_SELECTOR, "tr[id^='public-report-row-']")
    ))
    second_citizen_driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", first_row)
    
    open_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'public-report-row-2-open-link')))
    open_button.click()

    # wait for the follow button to appear and click it
    follow_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'follow-button')))

    follow_button.click() # double click because otherwise it does not really click.
    follow_button.click()

    # assert success message is displayed or button state changes
    unfollow_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'follow-button')))
    
    assert unfollow_button.text == "Unfollow report"

    
def test_uc07_already_following_ext3a(second_citizen_driver):
    wait = WebDriverWait(second_citizen_driver, 10)

    home_button = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'nav-home')))
    home_button.click()

    # navigate to the report
    first_row = wait.until(expected_conditions.element_to_be_clickable(
        (By.CSS_SELECTOR, "tr[id^='public-report-row-']")
    ))
    second_citizen_driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", first_row)
    
    open_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'public-report-row-2-open-link')))
    open_button.click()

    # 1. Follow the report first (using the double click hack)
    follow_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'follow-button')))
    follow_button.click()
    follow_button.click()

    # 2. Refresh the page to simulate visiting a report we ALREADY follow
    second_citizen_driver.refresh()

    # 3. Assert the button immediately loads as 'Unfollow report'
    unfollow_button = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'follow-button')))
    assert unfollow_button.text == "Unfollow report"


def test_uc07_not_authenticated_ext3b(driver):
    driver.get('http://localhost:5173')
    wait = WebDriverWait(driver, 10)

    home_button = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'nav-home')))
    home_button.click()

    first_row = wait.until(expected_conditions.element_to_be_clickable(
        (By.CSS_SELECTOR, "tr[id^='public-report-row-']")
    ))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", first_row)
    
    open_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'public-report-row-2-open-link')))
    open_button.click()

    # assert the system asks the user to log in (redirects to login form)
    login_button = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'nav-login')))
    assert login_button.is_displayed()