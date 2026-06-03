"""Shared fixtures and helpers for Participium Selenium tests.

Prerequisites:
    pip install selenium pytest
    Backend running on http://localhost:5050 (python wsgi.py)
    Frontend running on http://localhost:5173 (npm run dev)
"""

import os
import struct
import uuid
import zlib

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

BASE_URL = os.getenv("PARTICIPIUM_URL", "http://localhost:5173")
API_BASE_URL = os.getenv("PARTICIPIUM_API_URL", "http://localhost:5050/api/v1")
EXPLICIT_WAIT = 10

# Seeded demo credentials
CITIZEN_EMAIL = "citizen@example.com"
CITIZEN_PASSWORD = "Citizen123!"
OPERATOR_EMAIL = "operator@example.com"
OPERATOR_PASSWORD = "Operator123!"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "Admin123!"

# Seeded category that maps to the demo operator
OPERATOR_CATEGORY = "Roads and Urban Furniture"

# Seeded public report (Resolved — always visible on home page)
SEEDED_PUBLIC_TITLE = "Pothole on Via Roma"


# ---------------------------------------------------------------------------
# Browser fixture  (session-scoped, shared across all tests)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def driver():
    """Create a shared headless Chrome instance for the whole test session."""
    options = Options()
    if os.getenv("CI"):
        options.add_argument("--headless=new")
    else:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,900")

    d = webdriver.Chrome(options=options)
    d.implicitly_wait(0)
    yield d
    d.quit()


@pytest.fixture
def wait(driver):
    """Return an explicit WebDriverWait bound to the session driver."""
    return WebDriverWait(driver, EXPLICIT_WAIT)


# ---------------------------------------------------------------------------
# Element helpers  (mirror the SonicCloud golden-model style)
# ---------------------------------------------------------------------------

def find(driver, element_id: str):
    """Find a single element by HTML id."""
    return driver.find_element(By.ID, element_id)


def finds(driver, element_id: str):
    """Find multiple elements by HTML id."""
    return driver.find_elements(By.ID, element_id)


def find_prefix(driver, prefix: str):
    """Find all elements whose id starts with *prefix*."""
    return driver.find_elements(By.CSS_SELECTOR, f"[id^='{prefix}']")


def wait_for(wait, element_id: str):
    """Wait for a single element by id to be visible."""
    return wait.until(EC.visibility_of_element_located((By.ID, element_id)))


def wait_clickable(wait, element_id: str):
    """Wait for a single element by id to be clickable."""
    return wait.until(EC.element_to_be_clickable((By.ID, element_id)))


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def login(driver, wait, email: str, password: str) -> None:
    """Navigate to /login and authenticate with *email* / *password*."""
    driver.get(f"{BASE_URL}/login")
    wait_for(wait, "login-form")

    el_id = find(driver, "login-identifier")
    el_id.clear()
    el_id.send_keys(email)

    el_pw = find(driver, "login-password")
    el_pw.clear()
    el_pw.send_keys(password)

    # REVISIONE PROF: Clicchiamo e basta, senza aspettare l'URL. 
    # Sarà il test ad aspettare la pagina successiva.
    wait_clickable(wait, "login-submit").click()


def logout(driver, wait) -> None:
    """Click the logout button and wait for the guest navigation to appear."""
    # REVISIONE PROF: Usiamo wait_clickable prima di cliccare
    wait_clickable(wait, "logout-button").click()
    wait_for(wait, "nav-login")


def ensure_logged_out(driver, wait) -> None:
    """Guarantee the browser is in an unauthenticated state."""
    driver.get(BASE_URL)
    try:
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.ID, "nav-login"))
        )
    except Exception:
        logout(driver, wait)


# ---------------------------------------------------------------------------
# Report helpers
# ---------------------------------------------------------------------------

def unique_id() -> str:
    """Return an 8-character hex token for unique test identifiers."""
    return uuid.uuid4().hex[:8]


def _make_minimal_png() -> bytes:
    """Return raw bytes of a valid 1×1 white RGB PNG."""
    def chunk(tag: bytes, data: bytes) -> bytes:
        crc_val = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc_val)

    signature = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    idat_data = zlib.compress(b"\x00\xFF\xFF\xFF")
    return (signature
            + chunk(b"IHDR", ihdr_data)
            + chunk(b"IDAT", idat_data)
            + chunk(b"IEND", b""))


@pytest.fixture(scope="session")
def sample_image(tmp_path_factory):
    """Minimal valid PNG reused across all tests in the session."""
    path = tmp_path_factory.mktemp("media") / "test_photo.png"
    path.write_bytes(_make_minimal_png())
    return str(path)


def create_report(driver, wait, sample_image_path: str,
                  title: str | None = None,
                  category: str = OPERATOR_CATEGORY) -> int:
    """
    Fill and submit the New Report form as the currently logged-in citizen.
    Returns the integer report ID extracted from the redirect URL.
    Precondition: citizen is already logged in.
    """
    title = title or f"Selenium Report {unique_id()}"
    driver.get(f"{BASE_URL}/reports/new")
    wait_for(wait, "report-title")

    find(driver, "report-title").send_keys(title)
    find(driver, "report-description").send_keys("Automated test description.")
    Select(find(driver, "report-category")).select_by_visible_text(category)
    find(driver, "report-photos").send_keys(sample_image_path)
    
    # REVISIONE PROF: wait_clickable per l'invio
    wait_clickable(wait, "new-report-submit").click()

    # Qui manteniamo l'attesa sull'URL perché ci serve per estrarre l'ID dal link
    WebDriverWait(driver, EXPLICIT_WAIT).until(
        lambda d: "/reports/" in d.current_url and "/reports/new" not in d.current_url
    )
    return int(driver.current_url.rstrip("/").split("/")[-1])


def find_public_row_by_title(driver, wait, title: str):
    """
    Locate the public-report <tr> whose title cell contains *title*.
    Returns the row element or raises AssertionError.
    """
    wait_for(wait, "public-report-table-body")
    rows = driver.find_elements(By.CSS_SELECTOR, "tr[id^='public-report-row-']")
    for row in rows:
        row_id = row.get_attribute("id")
        title_el = row.find_element(By.ID, f"{row_id}-title")
        if title in title_el.text:
            return row
    titles = [
        r.find_element(By.ID, f"{r.get_attribute('id')}-title").text
        for r in rows
    ]
    raise AssertionError(
        f"Row with title '{title}' not found. Titles present: {titles}"
    )