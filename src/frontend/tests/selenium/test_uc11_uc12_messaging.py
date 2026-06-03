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
def operator_driver(driver):
    driver.get('http://localhost:5173')
    wait = WebDriverWait(driver, 10)

    # Click login button
    login_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'login-link')))
    login_button.click()

    # Insert credentials
    username_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'login-identifier')))
    username_box.clear()
    username_box.send_keys('admin@example.com')

    password_box = driver.find_element(By.ID, 'login-password')
    password_box.clear()
    password_box.send_keys('Admin123!')

    # Click on submit
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
    
def test_uc11_uc12_messaging_success(operator_driver, create_pending_report):
    wait = WebDriverWait(operator_driver, 10)

    # Save the title of the report to find it later
    title = create_pending_report

    op_btn = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'nav-operator')))
    op_btn.click()

    # Phase 1: Operator sends message to citizen
    pending_row = wait.until(expected_conditions.element_to_be_clickable(
        (By.XPATH, f"//tr[contains(@id, 'pending-report-row-') and contains(., '{title}')]")
    ))
    assign_btn = pending_row.find_element(By.CSS_SELECTOR, "[id^='pending-report-assign']")
    assign_btn.click()

    operator_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    assigned_row = wait.until(expected_conditions.element_to_be_clickable(
        (By.XPATH, f"//tr[contains(@id, 'assigned-report-row-') and contains(., '{title}')]")
    ))
    operator_driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", assigned_row)

    open_detail_btn = assigned_row.find_element(By.CSS_SELECTOR, "[id$='-open-detail']")
    open_detail_btn.click()

    conversation_box = wait.until(expected_conditions.element_to_be_clickable((By.ID, "report-message-body")))
    conversation_box.send_keys("hello from operator")

    send_btn = wait.until(expected_conditions.element_to_be_clickable((By.ID, "report-message-submit")))
    send_btn.click()


    # Phase 2: Citizen checks message and replies
    logout_btn = wait.until(expected_conditions.element_to_be_clickable((By.ID, "logout-button")))
    logout_btn.click()

    operator_driver.execute_script("window.scrollTo(0, 0);")

    login_link = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'nav-login')))
    login_link.click()

    username_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'login-identifier')))
    username_box.clear()
    username_box.send_keys('citizen@example.com')
    
    password_box = operator_driver.find_element(By.ID, 'login-password')
    password_box.clear()
    password_box.send_keys('Citizen123!')
    
    operator_driver.find_element(By.ID, 'login-submit').click()
    wait.until(expected_conditions.visibility_of_element_located((By.ID, 'logout-button')))

    my_report_row = wait.until(expected_conditions.element_to_be_clickable(
        (By.XPATH, f"//tr[contains(@id, 'my-report-row-') and contains(., '{title}')]")
    ))
    
    operator_driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", my_report_row)
    import time
    time.sleep(0.5) 
    
    open_link = my_report_row.find_element(By.CSS_SELECTOR, "[id$='open-link']")
    open_link.click()

    operator_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    message = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'messages-list')))
    assert message.is_displayed()

    message_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'report-message-body')))
    message_box.send_keys("Hello from citizen")

    send_btn = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'report-message-submit')))
    send_btn.click()


    # Phase 3: Operator checks citizen's reply
    logout_btn = wait.until(expected_conditions.element_to_be_clickable((By.ID, "logout-button")))
    logout_btn.click()

    login_link = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'nav-login')))
    login_link.click()

    username_box = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'login-identifier')))
    username_box.clear()
    username_box.send_keys('admin@example.com')
    
    password_box = operator_driver.find_element(By.ID, 'login-password')
    password_box.clear()
    password_box.send_keys('Admin123!')
    
    operator_driver.find_element(By.ID, 'login-submit').click()
    wait.until(expected_conditions.visibility_of_element_located((By.ID, 'logout-button')))

    op_btn = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'nav-operator')))
    op_btn.click()

    operator_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    assigned_row_final = wait.until(expected_conditions.element_to_be_clickable(
        (By.XPATH, f"//tr[contains(@id, 'assigned-report-row-') and contains(., '{title}')]")
    ))

    open_detail_btn = assigned_row_final.find_element(By.CSS_SELECTOR, "[id$='-open-detail']")
    open_detail_btn.click()

    msg_list = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'messages-list')))
    assert msg_list.is_displayed()


    citizen_reply_visible = wait.until(expected_conditions.visibility_of_element_located(
        (By.XPATH, "//*[contains(text(), 'Hello from citizen')]")
    ))
    assert citizen_reply_visible.is_displayed()


def test_uc11_empty_message_ext3a(operator_driver, create_pending_report):
    wait = WebDriverWait(operator_driver, 10)
    
    title = create_pending_report

    op_btn = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'nav-operator')))
    op_btn.click()

    pending_row = wait.until(expected_conditions.element_to_be_clickable(
        (By.XPATH, f"//tr[contains(@id, 'pending-report-row-') and contains(., '{title}')]")
    ))
    operator_driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pending_row)
    import time
    time.sleep(0.5) 
    
    assign_btn = pending_row.find_element(By.CSS_SELECTOR, "[id^='pending-report-assign']")
    assign_btn.click()

    assigned_row = wait.until(expected_conditions.element_to_be_clickable(
        (By.XPATH, f"//tr[contains(@id, 'assigned-report-row-') and contains(., '{title}')]")
    ))
    operator_driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", assigned_row)
    time.sleep(0.5)
    
    open_detail_btn = assigned_row.find_element(By.CSS_SELECTOR, "[id$='-open-detail']")
    open_detail_btn.click()

    conversation_box = wait.until(expected_conditions.element_to_be_clickable((By.ID, "report-message-body")))
    operator_driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", conversation_box)
    time.sleep(0.5)
    
    conversation_box.clear()

    
    send_btn = wait.until(expected_conditions.element_to_be_clickable((By.ID, "report-message-submit")))
    send_btn.click()

    
    is_valid = operator_driver.execute_script("return arguments[0].checkValidity();", conversation_box)
    assert is_valid is False
    
    validation_message = operator_driver.execute_script("return arguments[0].validationMessage;", conversation_box)
    
    assert validation_message != "" 
