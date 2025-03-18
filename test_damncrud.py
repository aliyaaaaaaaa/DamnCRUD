import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import pymysql
import logging

logging.basicConfig(level=logging.INFO)

# Tunggu hingga database siap
time.sleep(5)

@pytest.fixture(scope="class")
def setup(request):
    """ Setup Selenium WebDriver untuk pengujian dengan Chrome """
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Headless untuk CI/CD
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")  # Tambahan untuk debugging

    # Gunakan ChromeDriver dari container Docker, bukan ChromeDriverManager
    driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver", options=chrome_options)
    driver.maximize_window()

    # Base URL menggunakan nama service Docker
    base_url = "http://my_app:8000"  # Pastikan ini sesuai dengan docker-compose
    driver.get(f"{base_url}/login.php")
    time.sleep(2)  # Pastikan halaman sudah termuat

    request.cls.driver = driver
    request.cls.base_url = base_url
    yield
    driver.quit()

@pytest.mark.usefixtures("setup")
class TestDamnCrud:
    def test_login_as_admin(self):
        """ ✅ Test Login sebagai Admin """
        wait = WebDriverWait(self.driver, 20)
        
        logging.info("Halaman saat ini: %s", self.driver.current_url)
        time.sleep(2)
        
        try:
            username_field = wait.until(EC.visibility_of_element_located((By.NAME, "username")))
            username_field.send_keys("admin")
            
            password_field = wait.until(EC.visibility_of_element_located((By.NAME, "password")))
            password_field.send_keys("nimda666!")
            
            login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
            login_button.click()
            
            time.sleep(3)
            logging.info("URL setelah login: %s", self.driver.current_url)
            
            dashboard = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Dashboard') or contains(text(), 'Howdy')]")))
            logging.info("Dashboard ditemukan: %s", dashboard.text)
            
        except Exception as e:
            logging.error("Error saat login: %s", str(e))
            logging.error("HTML halaman saat ini: %s", self.driver.page_source)
            pytest.fail("Login gagal")
        
        assert "index.php" in self.driver.current_url.lower()
        
        # Tambahkan delay sebelum tes berikutnya
        time.sleep(2)

    def test_create_contact(self):
        """ ✅ Test Pembuatan Kontak Baru """
        wait = WebDriverWait(self.driver, 20)

        # Pastikan sudah login jika belum
        if "index.php" not in self.driver.current_url:
            self.test_login_as_admin()
        
        # Pastikan sudah masuk ke halaman utama
        self.driver.get(f"{self.base_url}/index.php")
        time.sleep(2)  # Tambahkan delay

        # Klik tombol 'Add New Contact'
        add_contact_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'create-contact')]")))
        add_contact_button.click()

        # Isi form
        wait.until(EC.visibility_of_element_located((By.NAME, "name"))).send_keys("Test User")
        wait.until(EC.visibility_of_element_located((By.NAME, "email"))).send_keys("test@test.com")
        wait.until(EC.visibility_of_element_located((By.NAME, "phone"))).send_keys("1234567890")
        wait.until(EC.visibility_of_element_located((By.NAME, "title"))).send_keys("Tester")

        # Klik tombol 'Save'
        save_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Save']")))
        save_button.click()

        # Verifikasi kontak berhasil dibuat
        wait.until(EC.url_contains("index.php"))
        search_field = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='search']")))
        search_field.send_keys("Test User")

        contact_row = wait.until(EC.presence_of_element_located((By.XPATH, "//td[contains(text(), 'Test User')]")))
        assert contact_row is not None

    def test_update_contact(self):
        """ ✅ Test Update Kontak """
        wait = WebDriverWait(self.driver, 20)

        # Akses halaman utama
        self.driver.get(f"{self.base_url}/index.php")
        wait.until(EC.url_contains("index.php"))

        # Klik tombol 'edit' kontak pertama
        edit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'btn-success') and contains(text(), 'edit')]")))
        edit_button.click()

        # Ubah data
        name_field = wait.until(EC.visibility_of_element_located((By.NAME, "name")))
        name_field.clear()
        name_field.send_keys("Updated User")

        # Klik tombol 'Update'
        update_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Update']")))
        update_button.click()

        # Verifikasi kontak berhasil diperbarui
        wait.until(EC.url_contains("index.php"))
        search_field = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='search']")))
        search_field.send_keys("Updated User")

        contact_row = wait.until(EC.presence_of_element_located((By.XPATH, "//td[contains(text(), 'Updated User')]")))
        assert contact_row is not None

    def test_delete_contact(self):
        """ ✅ Test Hapus Kontak """
        wait = WebDriverWait(self.driver, 20)

        # Akses halaman utama
        self.driver.get(f"{self.base_url}/index.php")
        wait.until(EC.url_contains("index.php"))

        # Pastikan kontak "Test User" dibuat dulu jika belum ada
        try:
            search_field = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='search']")))
            search_field.clear()
            search_field.send_keys("Test User")
            time.sleep(1)  # Beri waktu untuk hasil pencarian
            
            # Cek apakah kontak ditemukan
            contact_exists = len(self.driver.find_elements(By.XPATH, "//td[contains(text(), 'Test User')]")) > 0
            
            # Jika kontak tidak ada, buat dulu
            if not contact_exists:
                # Bersihkan hasil pencarian
                search_field.clear()
                
                # Klik tombol 'Add New Contact'
                add_contact_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'create-contact')]")))
                add_contact_button.click()

                # Isi form
                wait.until(EC.visibility_of_element_located((By.NAME, "name"))).send_keys("Test User")
                wait.until(EC.visibility_of_element_located((By.NAME, "email"))).send_keys("test@test.com")
                wait.until(EC.visibility_of_element_located((By.NAME, "phone"))).send_keys("1234567890")
                wait.until(EC.visibility_of_element_located((By.NAME, "title"))).send_keys("Tester")

                # Klik tombol 'Save'
                save_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Save']")))
                save_button.click()
                
                # Kembali ke halaman utama dan cari kontak
                wait.until(EC.url_contains("index.php"))
                search_field = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='search']")))
                search_field.send_keys("Test User")
            
            # Cari dan hapus kontak
            contact_row = wait.until(EC.presence_of_element_located((By.XPATH, "//tr[td[contains(text(), 'Test User')]]")))
            delete_button = contact_row.find_element(By.XPATH, ".//a[contains(@class, 'btn-danger') and contains(text(), 'delete')]")
            delete_button.click()

            # Konfirmasi delete
            alert = self.driver.switch_to.alert
            alert.accept()
            
        except Exception as e:
            pytest.fail(f"Gagal menemukan atau menghapus kontak: {str(e)}")

        # Verifikasi kontak sudah dihapus
        wait.until(EC.url_contains("index.php"))
        search_field = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='search']")))
        search_field.clear()  # Clear dulu field pencarian
        search_field.send_keys("Test User")
        time.sleep(1)  # Berikan waktu untuk hasil pencarian

        # Pastikan tidak ada hasil pencarian dengan nama Test User
        assert len(self.driver.find_elements(By.XPATH, "//td[contains(text(), 'Test User')]")) == 0

    def test_update_profile(self):
        """ ✅ Test Update Foto Profil """
        wait = WebDriverWait(self.driver, 20)

        # Akses halaman profil
        self.driver.get(f"{self.base_url}/index.php")
        profile_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Profil')]")))
        profile_link.click()

        # Unggah gambar baru
        upload_field = wait.until(EC.visibility_of_element_located((By.NAME, "image")))
        upload_field.send_keys(os.path.abspath("image/aliya.jpg"))

        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
        submit_button.click()

        # Verifikasi tidak ada pesan error
        error_messages = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Ekstensi tidak diijinkan')]")
        assert len(error_messages) == 0
