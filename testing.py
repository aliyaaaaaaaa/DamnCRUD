import sys
import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions

class RegisterTestCase(unittest.TestCase):
    def setUp(self):
        options = webdriver.FirefoxOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        server = 'http://localhost:4444'  # Sesuaikan endpoint Selenium jika diperlukan
        self.browser = webdriver.Remote(command_executor=server, options=options)
        
    def test_invalid_login(self):
        if len(sys.argv) > 1:
            url = sys.argv[1] + "/login.php"
        else:
            url = "http://localhost/login.php"
        self.browser.get(url)
        self.browser.find_element(By.ID, "inputUsername").send_keys("wronguser")
        self.browser.find_element(By.ID, "inputPassword").send_keys("wrongpass")
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)
        # Updated locator to target the error message as per the HTML structure
        error_message = self.browser.find_element(By.CSS_SELECTOR, "div.checkbox.mb-3 label").text.strip()
        self.assertEqual(error_message, "Damn, wrong credentials!!")

    def test_valid_login(self):
        if len(sys.argv) > 1:
            url = sys.argv[1] + "/login.php"
        else:
            url = "http://localhost/login.php"
        self.browser.get(url)
        self.browser.find_element(By.ID, "inputUsername").send_keys("admin")
        self.browser.find_element(By.ID, "inputPassword").send_keys("nimda666!")
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)
        self.assertIn("Dashboard", self.browser.page_source)

    def test_sqli_login(self):
        if len(sys.argv) > 1:
            login_url = sys.argv[1] + "/login.php"
        else:
            login_url = "http://localhost/login.php"

        self.browser.get(login_url)

        # Masukkan payload SQL Injection
        self.browser.find_element(By.ID, "inputUsername").send_keys("' OR '1'='1")
        self.browser.find_element(By.ID, "inputPassword").send_keys("' OR '1'='1")
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)

        # Periksa apakah berhasil login dengan mengecek apakah teks "Dashboard" ada di halaman
        self.assertIn("Dashboard", self.browser.page_source, "SQL Injection login should not be successful!")
        self.assertIn("Damn, wrong credentials!!", self.browser.page_source, "Cant Logged In, SQLI Failed")

    def test_update_contact(self):
        if len(sys.argv) > 1:
            login_url = sys.argv[1] + "/login.php"
            update_url = sys.argv[1] + "/update.php?id=1"
        else:
            login_url = "http://localhost/login.php"
            update_url = "http://localhost/update.php?id=1"
        self.browser.get(login_url)
        self.browser.find_element(By.ID, "inputUsername").send_keys("admin")
        self.browser.find_element(By.ID, "inputPassword").send_keys("nimda666!")
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)
        self.browser.get(update_url)
        name_field = self.browser.find_element(By.NAME, "name")
        name_field.clear()
        name_field.send_keys("Updated Contact")
        self.browser.find_element(By.XPATH, "//input[@type='submit']").click()
        time.sleep(2)
        self.assertIn("Updated Contact", self.browser.page_source)

    def test_xss_detection(self):
        if len(sys.argv) > 1:
            login_url = sys.argv[1] + "/login.php"
            xss_url = sys.argv[1] + "/vpage.php"
        else:
            login_url = "http://localhost/login.php"
            xss_url = "http://localhost/vpage.php"
        # Login first
        self.browser.get(login_url)
        self.browser.find_element(By.ID, "inputUsername").send_keys("admin")
        self.browser.find_element(By.ID, "inputPassword").send_keys("nimda666!")
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)
        # Navigate to the XSS page and submit the payload
        self.browser.get(xss_url)
        xss_payload = '<script>alert("xss")</script>'
        self.browser.find_element(By.NAME, "thing").send_keys(xss_payload)
        self.browser.find_element(By.XPATH, "//input[@type='submit']").click()
        time.sleep(2)
        try:
            # If an alert appears, it means the XSS payload executed
            alert = self.browser.switch_to.alert
            self.assertEqual(alert.text, "xss")
            alert.accept()  # Dismiss the alert
        except Exception as e:
            self.fail("XSS alert not triggered.")

    def tearDown(self):
        self.browser.quit()

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], verbosity=2, warnings='ignore')