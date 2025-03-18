import sys
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By

@pytest.fixture(scope="function")
def browser():
    """Fixture untuk setup dan teardown Selenium WebDriver."""
    options = webdriver.FirefoxOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    server = 'http://localhost:4444'  # Sesuaikan jika endpoint Selenium berbeda
    driver = webdriver.Remote(command_executor=server, options=options)
    yield driver
    driver.quit()

@pytest.mark.parametrize("username,password,expected_message", [
    ("wronguser", "wrongpass", "Damn, wrong credentials!!"),
    ("admin", "nimda666!", "Dashboard")
])
def test_login(browser, username, password, expected_message):
    """Test valid dan invalid login."""
    url = sys.argv[1] + "/login.php" if len(sys.argv) > 1 else "http://localhost/login.php"
    browser.get(url)
    browser.find_element(By.ID, "inputUsername").send_keys(username)
    browser.find_element(By.ID, "inputPassword").send_keys(password)
    browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(2)
    assert expected_message in browser.page_source

def test_sqli_login(browser):
    """Test SQL Injection pada form login."""
    url = sys.argv[1] + "/login.php" if len(sys.argv) > 1 else "http://localhost/login.php"
    browser.get(url)
    browser.find_element(By.ID, "inputUsername").send_keys("' OR '1'='1")
    browser.find_element(By.ID, "inputPassword").send_keys("' OR '1'='1")
    browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(2)
    assert "Damn, wrong credentials!!" in browser.page_source, "SQL Injection seharusnya gagal!"

def test_update_contact(browser):
    """Test update kontak."""
    login_url = sys.argv[1] + "/login.php" if len(sys.argv) > 1 else "http://localhost/login.php"
    update_url = sys.argv[1] + "/update.php?id=1" if len(sys.argv) > 1 else "http://localhost/update.php?id=1"
    
    browser.get(login_url)
    browser.find_element(By.ID, "inputUsername").send_keys("admin")
    browser.find_element(By.ID, "inputPassword").send_keys("nimda666!")
    browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(2)
    
    browser.get(update_url)
    name_field = browser.find_element(By.NAME, "name")
    name_field.clear()
    name_field.send_keys("Updated Contact")
    browser.find_element(By.XPATH, "//input[@type='submit']").click()
    time.sleep(2)
    
    assert "Updated Contact" in browser.page_source

def test_xss_detection(browser):
    """Test XSS Injection."""
    login_url = sys.argv[1] + "/login.php" if len(sys.argv) > 1 else "http://localhost/login.php"
    xss_url = sys.argv[1] + "/vpage.php" if len(sys.argv) > 1 else "http://localhost/vpage.php"
    
    browser.get(login_url)
    browser.find_element(By.ID, "inputUsername").send_keys("admin")
    browser.find_element(By.ID, "inputPassword").send_keys("nimda666!")
    browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(2)
    
    browser.get(xss_url)
    xss_payload = '<script>alert("xss")</script>'
    browser.find_element(By.NAME, "thing").send_keys(xss_payload)
    browser.find_element(By.XPATH, "//input[@type='submit']").click()
    time.sleep(2)
    
    try:
        alert = browser.switch_to.alert
        assert alert.text == "xss", "XSS tidak terdeteksi!"
        alert.accept()
    except Exception:
        pytest.fail("XSS alert tidak muncul.")

