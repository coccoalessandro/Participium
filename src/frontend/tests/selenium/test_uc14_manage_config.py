import pytest 

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import uuid

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

def test_uc14_manage_categories_success(admin_logged_in_driver):
    wait = WebDriverWait(admin_logged_in_driver, 10)

    #  Insertion of a new category with unique name
    new_category_name = f"Sicurezza Urbana {uuid.uuid4().hex[:6]}"
    
    cat_input = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'admin-new-category-name')))
    admin_logged_in_driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cat_input)
    cat_input.clear()
    cat_input.send_keys(new_category_name)

    # Save the configuration
    submit_btn = admin_logged_in_driver.find_element(By.ID, 'admin-new-category-submit')
    submit_btn.click()

    # Verify that the new category is displayed in the list
    saved_category = wait.until(expected_conditions.visibility_of_element_located(
        (By.XPATH, f"//*[contains(text(), '{new_category_name}')]")
    ))
    
    assert saved_category.is_displayed()


def test_uc14b_manage_categories_already_in_use(admin_logged_in_driver):
    wait = WebDriverWait(admin_logged_in_driver, 10)

    # Insertion of a new category with a name already in use
    new_category_name = f"Other"
    
    cat_input = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'admin-new-category-name')))
    admin_logged_in_driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cat_input)
    cat_input.clear()
    cat_input.send_keys(new_category_name)

    # Save the configuration
    submit_btn = admin_logged_in_driver.find_element(By.ID, 'admin-new-category-submit')
    submit_btn.click()

    error_message = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'admin-error')))
    
    assert error_message.is_displayed()