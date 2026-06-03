import pytest 

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions

@pytest.fixture
def driver(): 
    d = webdriver.Chrome()
    yield d
    d.quit()

def find_by_id(webdriver, widget_id):
    return webdriver.find_element(By.ID, widget_id)


def test_uc09_statistics_sections_visible(driver):
    driver.get('http://localhost:5173')
    wait = WebDriverWait(driver, 10)

    # wait for the total reports metric to appear
    total_reports = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'public-total-reports-metric')))
    assert total_reports.is_displayed()

    # wait for the category statistics section to appear
    category_stats = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'public-category-statistics')))
    assert category_stats.is_displayed()

    # wait for the trend statistics section to appear
    trend_stats = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'public-trend-statistics')))
    assert trend_stats.is_displayed()


def test_uc09_total_reports_nonzero(driver):
    driver.get('http://localhost:5173')
    wait = WebDriverWait(driver, 10)

    # wait for the total reports value to appear
    total_value = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'public-total-reports-value')))

    # assert the count is at least 1 (seeded data must be present)
    assert int(total_value.text) >= 1


def test_uc09_category_stats_list_non_empty(driver):
    driver.get('http://localhost:5173')
    wait = WebDriverWait(driver, 10)

    # wait for the category statistics list to appear
    wait.until(expected_conditions.visibility_of_element_located((By.ID, 'public-category-statistics-list')))

    # assert at least one category stat entry is displayed
    items = driver.find_elements(By.CSS_SELECTOR, "[id^='public-category-stat-']")
    assert len(items) >= 1


def test_uc09_trend_week_granularity(driver):
    driver.get('http://localhost:5173')
    wait = WebDriverWait(driver, 10)

    # wait for the granularity selector to appear
    granularity_select = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'public-stat-granularity')))

    # select 'week' granularity
    Select(granularity_select).select_by_value('week')

    # wait for the trend statistics list to refresh
    trend_list = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'public-trend-statistics-list')))

    # assert the trend list is still displayed with the new granularity
    assert trend_list.is_displayed()


def test_uc09_trend_month_granularity(driver):
    driver.get('http://localhost:5173')
    wait = WebDriverWait(driver, 10)

    # wait for the granularity selector to appear
    granularity_select = wait.until(expected_conditions.element_to_be_clickable((By.ID, 'public-stat-granularity')))

    # select 'month' granularity
    Select(granularity_select).select_by_value('month')

    # wait for the trend statistics list to refresh
    trend_list = wait.until(expected_conditions.visibility_of_element_located((By.ID, 'public-trend-statistics-list')))

    # assert the trend list is still displayed with the new granularity
    assert trend_list.is_displayed()