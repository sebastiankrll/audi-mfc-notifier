from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
import platform
import shutil

class BrowserFactory:
    @staticmethod
    def create_browser():
        system = platform.system()
        
        if system == "Windows":
            return BrowserFactory._create_windows_browser()
        elif system == "Linux":
            return BrowserFactory._create_linux_browser()
        else:
            raise OSError(f"Unsupported operating system: {system}")

    @staticmethod
    def _create_windows_browser():
        options = EdgeOptions()
        # options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        service = EdgeService(".\\msedgedriver.exe")
        return webdriver.Edge(service=service, options=options)

    @staticmethod
    def _create_linux_browser():
        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        # options.binary_location = "/usr/bin/chromium"

        # return webdriver.Chrome(options=options)
        
        chrome_bin = (
            shutil.which("chromium")
            or shutil.which("chromium-browser")
            or shutil.which("google-chrome")
            or shutil.which("google-chrome-stable")
        )
        if chrome_bin:
            options.binary_location = chrome_bin
            return webdriver.Chrome(options=options)
        else:
            raise FileNotFoundError("Chrome/Chromium binary not found")