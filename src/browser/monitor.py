from datetime import datetime, timezone
import time
import sys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from src.config.settings import Settings
from src.notifier.telegram import TelegramNotifier
from src.models.parser import ModelParser

class BrowserMonitor:
    def __init__(self, driver: WebDriver, notifier: TelegramNotifier, settings: Settings):
        self.driver = driver
        self.notifier = notifier
        self.settings = settings
        self.current_url = settings.URL
        self.previous_models = set()
        self._last_scheduled_check = datetime.now(timezone.utc)

    def run(self):
        self._log("Browser monitor started.")
        
        while True:
            if not self.notifier.is_running():
                time.sleep(self.settings.REFRESH_INTERVAL)
                continue

            try:
                self._handle_url_changes()
                self._do_login()
                self._monitoring_loop()
            except Exception:
                self.notifier.notify_error(exc_info=sys.exc_info(), context="monitor setup/run")
                time.sleep(self.settings.REFRESH_INTERVAL)

    def _handle_url_changes(self):
        new_url = self.notifier.get_url()
        if new_url and new_url != self.current_url:
            self.current_url = new_url
            self.previous_models.clear()

            self._log("URL changed, cleared previous models.")

    def _check_login_required(self) -> bool:
        try:
            login_button = self.driver.find_element(By.CLASS_NAME, "login-button")
            return login_button.is_displayed()
        except:
            return False
        
    def _do_login(self):
        self.driver.get("https://vtp.audi.com/ademanlwb/i/s/controller.do#filter/models")

        try:
            wait = WebDriverWait(self.driver, 3)
            login_button = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "login-button")))
            
            login_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "login-button")))
            self.driver.find_element(By.NAME, "username").send_keys(self.settings.USERNAME)
            self.driver.find_element(By.NAME, "password").send_keys(self.settings.PASSWORD)

            login_button.click()
            time.sleep(2)
            self._log("Login performed.")
        except Exception:
            self._log("Already logged in or login failed.")

    def _monitoring_loop(self):
        while self.notifier.is_running():
            if self._check_login_required():
                self._log("Login required, performing login...")
                self._do_login()
                continue

            self._check_scheduled_runs()
            self._handle_reset_request()
            self._handle_url_changes()
            self._check_models()

            # self._log("Page refreshed.")

    def _check_scheduled_runs(self):
        now = datetime.now(timezone.utc)
        time_since_last_check = (now - self._last_scheduled_check).total_seconds()

        if time_since_last_check >= self.settings.SCHEDULED_CHECK_INTERVAL:
            self._do_scheduled_check()
            self._last_scheduled_check = now
        
    def _do_scheduled_check(self):
        self.driver.get("https://vtp.audi.com/ademanlwb/i/s/controller.do#filter/models")
        time.sleep(2)
        
        div = self.driver.find_element(By.CSS_SELECTOR, ".vtp-resultcount span.num")

        self.notifier.send_notification(f"🕒  {time.strftime('%Y-%m-%d %H:%M:%S')}: {int(div.text.strip())} results found.")
        self._log("Scheduled check completed.")

    def _handle_reset_request(self):
        if self.notifier.is_reset_requested():
            self.previous_models.clear()
            self._log("Models reset.")

    def _check_models(self):
        self.driver.get(self.current_url)
        time.sleep(max(self.settings.REFRESH_INTERVAL, 2))

        parser = ModelParser(self.driver, self.previous_models)
        models = parser.parse_models_from_url(self.current_url)
        if models:
            model_strings = [f"{model.name} ({model.count})" for model in models]
            self.previous_models.update(model.name for model in models)

            self.notifier.send_notification("🔥  New models found!\n\n" + "\n".join(model_strings) + f"\n\n{self.current_url}")

    def _log(self, message: str):
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')}: {message}")