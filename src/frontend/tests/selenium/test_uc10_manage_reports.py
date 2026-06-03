import pytest 

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions
import os
import uuid

@pytest.fixture
def driver(): 
    d = webdriver.Chrome()
    yield d
    d.quit()

@pytest.fixture
def operator_driver(driver):
    driver.get('http://localhost:5173')
    wait = WebDriverWait(driver, 10)

    login_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'login-link')))
    login_button.click()

    username_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'login-identifier')))
    username_box.clear()
    username_box.send_keys('admin@example.com')

    password_box = driver.find_element(By.ID, 'login-password')
    password_box.clear()
    password_box.send_keys('Admin123!')

    driver.find_element(By.ID, 'login-submit').click()

    wait.until(expected_conditions.visibility_of_element_located((By.ID, 'logout-button')))
 
    yield driver

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

@pytest.fixture
def create_pending_report():
    temp_driver = webdriver.Chrome()
    wait = WebDriverWait(temp_driver, 10)
    
    try:
        temp_driver.get('http://localhost:5173')
        
        # Login as a citizen
        wait.until(expected_conditions.element_to_be_clickable((By.ID, 'login-link'))).click()
        username_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'login-identifier')))
        username_box.clear()
        username_box.send_keys('citizen@example.com')
        psw_box = temp_driver.find_element(By.ID, 'login-password')
        psw_box.clear()
        psw_box.send_keys('Citizen123!')
        temp_driver.find_element(By.ID, 'login-submit').click()
        
        wait.until(expected_conditions.visibility_of_element_located((By.ID, 'logout-button')))
        
        # Create report
        wait.until(expected_conditions.element_to_be_clickable((By.ID, 'nav-new-report'))).click()
        
        title_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'report-title')))
        unique_title = f"Buca pericolosa {uuid.uuid4().hex[:6]}"
        title_box.send_keys(unique_title)
        
        temp_driver.find_element(By.ID, 'report-description').send_keys('Descrizione di test')
        wait.until(expected_conditions.element_to_be_clickable((By.ID, 'new-report-map'))).click() 
        
        photo_submit = wait.until(expected_conditions.presence_of_element_located((By.ID, 'report-photos')))
        current_dir = os.path.dirname(os.path.abspath(__file__))
        photo_path = os.path.join(current_dir, 'image_test', 'photo1.jpg')
        photo_submit.send_keys(photo_path)
        
        submit_btn = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'new-report-submit')))
        temp_driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
        submit_btn.click()
        
        wait.until(expected_conditions.visibility_of_element_located((By.ID, 'report-detail-title')))
        
        return unique_title
    
    finally:
        temp_driver.quit()


def test_uc10_manage_report_success(operator_driver, create_pending_report):
    wait = WebDriverWait(operator_driver, 10)

    title = create_pending_report

    op_btn = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'nav-operator')))
    op_btn.click()

    # Changes the status
    first_row = wait.until(expected_conditions.element_to_be_clickable(
    (By.CSS_SELECTOR, "tr[id^='pending-report-row-']")
))
    assign_btn = first_row.find_element(By.CSS_SELECTOR, "[id^='pending-report-assign']")
    assign_btn.click()

    operator_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    first_row = wait.until(expected_conditions.element_to_be_clickable(
    (By.CSS_SELECTOR, "tr[id^='assigned-report-row-']")
))
    status_dropdown = first_row.find_element(By.CSS_SELECTOR, "[id^='assigned-report-status']")
    Select(status_dropdown).select_by_visible_text("Suspended")

    # Waits for the update button
    submit_update = first_row.find_element(By.CSS_SELECTOR, "[id^='assigned-report-update']")
    submit_update.click()

    operator_driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", first_row)
    open_detail_btn = first_row.find_element(By.CSS_SELECTOR, "[id$='-open-detail']")
    open_detail_btn.click()

    status_value = wait.until(expected_conditions.visibility_of_element_located((By.ID, "report-detail-status")))
    assert "Status: Suspended" == status_value.text

def test_uc10_rejected_without_motivation_ext5a(operator_driver, create_pending_report):
    wait = WebDriverWait(operator_driver, 10)
    create_pending_report

    op_btn = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'nav-operator')))
    op_btn.click()

    first_row_pending = wait.until(expected_conditions.element_to_be_clickable(
        (By.CSS_SELECTOR, "tr[id^='pending-report-row-']")
    ))
    assign_btn = first_row_pending.find_element(By.CSS_SELECTOR, "[id^='pending-report-assign']")
    assign_btn.click()

    operator_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    first_row_assigned = wait.until(expected_conditions.element_to_be_clickable(
        (By.CSS_SELECTOR, "tr[id^='assigned-report-row-']")
    ))
    status_dropdown = first_row_assigned.find_element(By.CSS_SELECTOR, "[id^='assigned-report-status']")
    Select(status_dropdown).select_by_visible_text("Rejected")

    submit_update = first_row_assigned.find_element(By.CSS_SELECTOR, "[id^='assigned-report-update']")
    submit_update.click()

    error_message = wait.until(expected_conditions.visibility_of_element_located(
        (By.CSS_SELECTOR, "[id*='operator-error']")
    ))
    assert error_message.is_displayed()
