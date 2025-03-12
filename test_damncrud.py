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

# Tunggu hingga database siap
time.sleep(5)

# Koneksi ke MySQL (sesuaikan dengan kredensial yang digunakan di aplikasi)
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="",  # Sesuaikan dengan setup di aplikasi
    database="damncrud"
)
cursor = conn.cursor()

# Import database jika belum ada
sql_file = "db/damncrud.sql"
with open(sql_file, "r") as f:
    sql_statements = f.read()
cursor.execute(sql_statements)
conn.commit()

cursor.close()
conn.close()


@pytest.fixture(scope="class")
def setup(request):
    """ Setup Selenium WebDriver untuk pengujian dengan Chrome """
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Diperlukan untuk CI/CD
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()

    base_url = "http://localhost/damncrud"
    driver.get(f"{base_url}/login.php")

    request.cls.driver = driver
    request.cls.base_url = base_url
    yield
    driver.quit()

@pytest.mark.usefixtures("setup")
class TestDamnCrud:
    def test_login_as_admin(self):
        """ ✅ Test Login sebagai Admin """
        wait = WebDriverWait(self.driver, 10)
        
        username_field = wait.until(EC.visibility_of_element_located((By.NAME, "username")))
        username_field.send_keys("admin")
        
        password_field = wait.until(EC.visibility_of_element_located((By.NAME, "password")))
        password_field.send_keys("nimda666!")
        
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
        login_button.click()

        # Verifikasi login berhasil
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Dashboard')]")))
        assert "dashboard" in self.driver.current_url.lower()

    def test_create_contact(self):
        """ ✅ Test Pembuatan Kontak Baru """
        wait = WebDriverWait(self.driver, 10)

        # Pastikan sudah masuk ke halaman utama
        wait.until(EC.url_contains("index.php"))

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
        wait = WebDriverWait(self.driver, 10)

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
        wait = WebDriverWait(self.driver, 10)

        # Akses halaman utama
        self.driver.get(f"{self.base_url}/index.php")
        wait.until(EC.url_contains("index.php"))

        # Cari kontak dengan nama tertentu dan klik tombol 'delete'
        try:
            contact_row = wait.until(EC.presence_of_element_located((By.XPATH, "//tr[td[contains(text(), 'Test User')]]")))
            delete_button = contact_row.find_element(By.XPATH, ".//a[contains(@class, 'btn-danger') and contains(text(), 'delete')]")
            delete_button.click()

            # Konfirmasi delete
            alert = self.driver.switch_to.alert
            alert.accept()
        except:
            pytest.fail("Gagal menemukan atau menghapus kontak.")

        # Verifikasi kontak sudah dihapus
        wait.until(EC.url_contains("index.php"))
        search_field = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='search']")))
        search_field.send_keys("Test User")

        with pytest.raises(Exception):
            wait.until(EC.presence_of_element_located((By.XPATH, "//td[contains(text(), 'Test User')]")))

    def test_update_profile(self):
        """ ✅ Test Update Foto Profil """
        wait = WebDriverWait(self.driver, 10)

        # Akses halaman profil
        self.driver.get(f"{self.base_url}/index.php")
        profile_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Profil')]")))
        profile_link.click()

        # Unggah gambar baru
        upload_field = wait.until(EC.visibility_of_element_located((By.NAME, "image")))
        upload_field.send_keys(os.path.abspath("C:/Users/Hana/Pictures/aliya.jpg"))

        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
        submit_button.click()

        # Verifikasi tidak ada pesan error
        error_messages = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Ekstensi tidak diijinkan')]")
        assert len(error_messages) == 0
