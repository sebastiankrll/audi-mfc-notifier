from datetime import datetime, timezone, timedelta
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
        self.refresh_interval = max(self.settings.REFRESH_INTERVAL, 5)
        self.previous_models = set()
        self._last_scheduled_check = datetime.now(timezone.utc)
        self.offline_periods = self._parse_idle_periods()

    def run(self):
        self._log("Browser monitor started.")
        
        while True:
            if not self.notifier.is_running():
                time.sleep(self.refresh_interval)
                continue

            try:
                self._monitoring_loop()
            except Exception:
                self.notifier.notify_error(exc_info=sys.exc_info(), context="monitor setup/run")
                time.sleep(self.refresh_interval)

    def _monitoring_loop(self):
        self.driver.get(self.current_url)

        while self.notifier.is_running():
            is_offline, seconds_until_end = self._is_idle_period()
            if is_offline:
                self._log("Offline period — idling...")
                time.sleep(min(seconds_until_end, 300))
                continue

            self._detect_site_status()

    def _detect_site_status(self):
        self.driver.refresh()
        time.sleep(self.refresh_interval)

        try:
            if self.driver.find_element(By.CLASS_NAME, "login-button"):
                self._do_login()
                return
        except Exception:
            pass

        try:
            if self.driver.find_element(By.CSS_SELECTOR, ".vtp-resultcount span.num"):
                self._check_scheduled_runs()
                self._handle_reset_request()
                self._handle_url_changes()
                self._check_models()
                return
        except Exception:
            self.notifier.notify_error(exc_info=sys.exc_info(), context="model check")
            pass

        self._log("Site unavailable — idling before retry...")
        time.sleep(300)
        
    def _do_login(self):
        try:
            login_button = self.driver.find_element(By.CLASS_NAME, "login-button")
            self.driver.find_element(By.NAME, "username").send_keys(self.settings.USERNAME)
            self.driver.find_element(By.NAME, "password").send_keys(self.settings.PASSWORD)

            login_button.click()
            time.sleep(2)
            
            self._log("Login performed.")
        except Exception:
            self._log("Already logged in or login failed.")

    def _check_scheduled_runs(self):
        now = datetime.now(timezone.utc)
        
        # Check if new hour compared to last check
        if now.hour != self._last_scheduled_check.hour:
            hours_since_last = (now - self._last_scheduled_check).total_seconds() / 3600
            if hours_since_last >= self.settings.SCHEDULED_CHECK_INTERVAL:
                self._do_scheduled_check()
        
    def _do_scheduled_check(self):
        self.driver.get("https://vtp.audi.com/ademanlwb/i/s/controller.do#filter/models")
        time.sleep(2)
        
        div = self.driver.find_element(By.CSS_SELECTOR, ".vtp-resultcount span.num")

        self.notifier.send_notification(f"🕒  {time.strftime('%Y-%m-%d %H:%M')}: {int(div.text.strip())} results found.")
        self._last_scheduled_check = datetime.now(timezone.utc)
        self._log("Scheduled check completed.")

    def _handle_reset_request(self):
        if self.notifier.is_reset_requested():
            self.previous_models.clear()
            self._log("Models reset.")

    def _handle_url_changes(self):
        new_url = self.notifier.get_url()
        if new_url and new_url != self.driver.current_url:
            self.current_url = new_url
            self.previous_models.clear()

            self.driver.get(self.current_url)

            self._log("URL changed, cleared previous models.")

    def _check_models(self):
        parser = ModelParser(self.driver, self.previous_models)
        models = parser.parse_models_from_url(self.current_url)
        if models:
            model_strings = [f"{model.name} ({model.count})" for model in models]
            self.previous_models.update(model.name for model in models)

            self.notifier.send_notification("🔥  New models found!\n\n" + "\n".join(model_strings) + f"\n\n{self.current_url}")

    def _log(self, message: str):
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')}: {message}")

    def _parse_idle_periods(self):
        periods = []
        for period in self.settings.IDLE_PERIODS:
            try:
                start_str, end_str = period.split("-")
                start_time = datetime.strptime(start_str.strip(), "%H:%M").time()
                end_time = datetime.strptime(end_str.strip(), "%H:%M").time()
                periods.append((start_time, end_time))
            except Exception:
                self.notifier.notify_error(context="invalid offline period format")
                self._log(f"Invalid offline period format: {period}")
        return periods
    
    def _is_idle_period(self) -> tuple[bool, float]:
        now = datetime.now()
        current_time = now.time()

        for start_time, end_time in self.offline_periods:
            if start_time <= end_time:
                # Same day (e.g., 12:00-13:00)
                if start_time <= current_time < end_time:
                    end_datetime = datetime.combine(now.date(), end_time)
                    seconds_left = (end_datetime - now).total_seconds()
                    return True, seconds_left
            else:
                # Overnight (e.g., 22:30-06:00)
                if current_time >= start_time or current_time < end_time:
                    if current_time >= start_time:
                        end_datetime = datetime.combine(now.date() + timedelta(days=1), end_time)
                    else:
                        end_datetime = datetime.combine(now.date(), end_time)
                    seconds_left = (end_datetime - now).total_seconds()
                    return True, seconds_left

        return False, 0