from src.browser.factory import BrowserFactory
from src.browser.monitor import BrowserMonitor
from src.notifier.telegram import TelegramNotifier
from src.config.settings import Settings
import threading

def main():
    notifier = TelegramNotifier(Settings)
    driver = BrowserFactory.create_browser()
    
    monitor = BrowserMonitor(driver, notifier, Settings())
    monitor_thread = threading.Thread(target=monitor.run, daemon=True)
    monitor_thread.start()

    try:
        notifier.start()
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        notifier._running.clear()

if __name__ == "__main__":
    main()