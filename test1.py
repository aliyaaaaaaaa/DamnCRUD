from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import traceback
import os
from selenium.common.exceptions import NoSuchElementException, TimeoutException

class TestLoginValid:
    def __init__(self, base_url="http://localhost/damncrud"):
        self.base_url = base_url
        self.driver = None

        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

            self.service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
            self.driver.maximize_window()
            
        except Exception as e:
            print(f"Error saat inisialisasi driver: {str(e)}")
            traceback.print_exc()

    def setup(self):
        self.driver.get(f"{self.base_url}/login.php")
        self.login_as_admin()

    def teardown(self):
        self.driver.quit()

    def login_as_admin(self):
        wait = WebDriverWait(self.driver, 10)
        username_field = wait.until(
            EC.visibility_of_element_located((By.XPATH, "//input[@name='username' or @type='text']"))
        )
        username_field.clear()
        username_field.send_keys("admin")
        password_field = wait.until(
            EC.visibility_of_element_located((By.XPATH, "//input[@name='password' or @type='password']"))
        )
        password_field.clear()
        password_field.send_keys("nimda666!")
        login_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' or contains(text(), 'Login')]"))
        )
        login_button.click()

        print("\nVerifikasi Expected Result:")
        print("1. Verifikasi Login berhasil")
        dashboard_found = wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Dashboard') or contains(text(), 'Admin Panel')]"))
        )
        if dashboard_found:
            print("  ✓ Berhasil masuk ke dashboard")

        print("2. Verifikasi Redirect ke Dashboard")
        current_url = self.driver.current_url
        if "dashboard" in current_url.lower() or "admin" in current_url.lower():
            print(f"  ✓ Redirect sukses: {current_url}")
        else:
            print(f"  ✗ Redirect gagal, URL sekarang: {current_url}")
                
        print("3. Verifikasi Session User")
        cookies = self.driver.get_cookies()
        session_cookies = [cookie for cookie in cookies if "session" in cookie["name"].lower() or "phpsessid" in cookie["name"].lower()]

        if session_cookies:
            print(f"  ✓ Session ditemukan: {session_cookies[0]['name']} = {session_cookies[0]['value']}")
        else:
            print("  ✗ Tidak ada session cookie ditemukan")

    def create_contact(self):
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.url_contains("index.php"))
        print("Klik 'Add New Contact'")
        try:
            add_contact_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'create-contact')]"))
            )
            add_contact_button.click()
        except TimeoutException:
            print("  ✗ Tombol 'Add New Contact' tidak ditemukan.")
            return

        print("Isi form dengan data valid")
        wait.until(EC.visibility_of_element_located((By.NAME, "name"))).send_keys("Test User")
        wait.until(EC.visibility_of_element_located((By.NAME, "email"))).send_keys("test@test.com")
        wait.until(EC.visibility_of_element_located((By.NAME, "phone"))).send_keys("1234567890")
        wait.until(EC.visibility_of_element_located((By.NAME, "title"))).send_keys("Tester")

        print("Klik tombol 'Save'")
        try:
            save_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Save']"))
            )
            save_button.click()
        except TimeoutException:
            print("  ✗ Tombol 'Save' tidak ditemukan.")
            return

        print("Verifikasi hasil yang diharapkan untuk 'Buat Kontak'")
        wait.until(EC.url_contains("index.php"))

        search_field = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='search']")))
        search_field.clear()
        search_field.send_keys("Test User")

        try:
            contact_row = wait.until(
                EC.presence_of_element_located((By.XPATH, "//td[contains(text(), 'Test User')]"))
            )
            print("  ✓ Kontak baru berhasil dibuat dan ditemukan di tabel")
        except TimeoutException:
            print("  ✗ Kontak baru tidak ditemukan di tabel")

    def update_contact(self):
        self.driver.get(f"{self.base_url}/index.php")
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.url_contains("index.php"))
        print("Klik tombol 'edit' pada salah satu kontak")
        try:
            edit_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'btn-outline btn-success') and contains(text(), 'edit')]"))
            )
            edit_button.click()
        except TimeoutException:
            print("  ✗ Tombol 'edit' tidak ditemukan.")
            return

        print("Ubah data dan submit form")
        name_field = wait.until(EC.visibility_of_element_located((By.NAME, "name")))
        name_field.clear()
        name_field.send_keys("Updated User")
        print("Klik tombol 'Update'")
        try:
            update_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Update']"))
            )
            update_button.click()
        except TimeoutException:
            print("  ✗ Tombol 'Update' tidak ditemukan.")
            return

        print("Verifikasi hasil yang diharapkan untuk 'Update Kontak'")
        wait.until(EC.url_contains("index.php"))

        search_field = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='search']")))
        search_field.clear()
        search_field.send_keys("Updated User")

        try:
            contact_row = wait.until(
                EC.presence_of_element_located((By.XPATH, "//td[contains(text(), 'Updated User')]"))
            )
            print("  ✓ Kontak berhasil diupdate dan ditemukan di tabel")
        except TimeoutException:
            print("  ✗ Kontak yang diupdate tidak ditemukan di tabel")

    def delete_contact(self):
        self.driver.get(f"{self.base_url}/index.php")
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.url_contains("index.php"))
        print("Cari kontak dengan nama 'David Deacon' dan klik tombol 'delete'")
        
        # Cari baris yang mengandung nama 'David Deacon'
        try:
            contact_row = wait.until(
                EC.presence_of_element_located((By.XPATH, "//tr[td[contains(text(), 'David Deacon')]]"))
            )
            print("Klik tombol 'delete'")
            delete_button = contact_row.find_element(By.XPATH, ".//a[contains(@class, 'btn-outline btn-danger') and contains(text(), 'delete')]")
            delete_button.click()
        except TimeoutException:
            print("  ✗ Tombol 'delete' tidak ditemukan.")
            return

        print("Konfirmasi delete")
        try:
            alert = self.driver.switch_to.alert
            alert.accept()  # or alert.dismiss() if you want to cancel
            print("  ✓ Alert diterima.")
        except Exception as e:
            print(f"  ✗ Gagal menangani alert: {e}")
            return

        print("Verifikasi hasil yang diharapkan untuk 'Hapus Kontak'")
        wait.until(EC.url_contains("index.php"))

        # Gunakan search bar untuk memverifikasi kontak yang dihapus
        search_field = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='search']")))
        search_field.clear()
        search_field.send_keys("David Deacon")

        # Verifikasi bahwa kontak yang dihapus tidak muncul di tabel
        try:
            contact_row = wait.until(
                EC.presence_of_element_located((By.XPATH, "//td[contains(text(), 'David Deacon')]"))
            )
            print("  ✗ Kontak yang dihapus masih ditemukan di tabel")
        except TimeoutException:
            print("  ✓ Kontak berhasil dihapus dan tidak ditemukan di tabel")

    def update_profile(self):
        self.driver.get(f"{self.base_url}/index.php")
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.url_contains("index.php"))
        print("Akses halaman profil")
        profile_link = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Profil')]"))
        )
        profile_link.click()

        print("Unggah foto profil baru")
        upload_field = wait.until(EC.visibility_of_element_located((By.NAME, "image")))
        upload_field.send_keys(os.path.abspath("C:/Users/Hana/Pictures/aliya.jpg"))

        submit_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' or contains(text(), 'Change')]"))
        )
        submit_button.click()

        # Tunggu beberapa saat untuk memastikan halaman telah diperbarui
        wait.until(EC.invisibility_of_element_located((By.XPATH, "//*[contains(text(), 'Ekstensi tidak diijinkan')]")))

        # Verifikasi bahwa pesan error tidak muncul
        try:
            error_message = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Ekstensi tidak diijinkan')]")
            if error_message.is_displayed():
                print("  ✗  Verifikasi gagal: Pesan error muncul.")
            else:
                print("  ✓  Verifikasi berhasil: Pesan error tidak muncul.")
        except NoSuchElementException:
            print("  ✓  Verifikasi berhasil: Pesan error tidak muncul.")

    def run_all_tests(self):
        try:
            self.setup()
            self.create_contact()
            self.update_contact()
            self.delete_contact()
            self.update_profile()
        finally:
            self.teardown()

if __name__ == "__main__":
    test = TestLoginValid()
    test.run_all_tests()
