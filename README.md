# AUDI MFC Notifier
Monitors Audi's MFC leasing pool for new available car models and sends notifications via Telegram Bot.

## Features
- Automated monitoring of leasing pool
- Telegram bot notifications for new models
- Freely filter by any model
- Configurable refresh intervals
- Scheduled daily checks
- Cross-platform support (Windows/Linux)

## Prerequisites
- Python 3.8+
- Microsoft Edge (Windows) or Chrome/Chromium (Linux) drivers
- Telegram Bot
- MFC (weare.audi) credentials

## Installation

1. Clone the repository:
```sh
git clone https://github.com/yourusername/Audi-MFC-Notifier.git
cd Audi-MFC-Notifier
```

2. Install dependencies:
```sh
pip install -r requirements.txt
```

3. Create a `.env` file with your credentials:
```sh
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
VTP_USERNAME=your_vtp_username
VTP_PASSWORD=your_vtp_password
```

4. Download & install WebDriver (detailed instructions below)

## Usage

1. Start the monitor:
```sh
python main.py
```

2. Telegram Bot Commands:
- `/start` - Start monitoring
- `/stop` - Stop monitoring
- `/seturl <url>` - Set URL with filters
- `/reset` - Clear previous results

## Configuration

Edit `src/config/settings.py` to modify:
- Refresh interval (default: 5 seconds)
- Scheduled check hours (default: 6:00 and 18:00 UTC)
- Default MFC URL and filters

## Notes
- Keep the MFC URL format as: `https://vtp.audi.com/ademanlwb/i/s%7C<filters>`
- The easiest way to set filters is to select the desired models in a browser and copy the URL
- The bot requires an active internet connection
- Ensure proper WebDriver version matches your browser version

## Driver installation

### Windows (Microsoft Edge)
1. Check your Edge version:
   - Open Edge
   - Click '...' menu → Help and feedback → About Microsoft Edge
   - Note the version number (e.g., 118.0.2088.76)

2. Download Edge WebDriver:
   - Visit https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
   - Download the WebDriver version matching your Edge version
   - Extract the downloaded zip file
   - Place `msedgedriver.exe` in the project's root folder

### Linux (Chrome/Chromium)
1. Install Chrome or Chromium:
```sh
# For Ubuntu/Debian
sudo apt update
sudo apt install chromium-browser

# For Fedora
sudo dnf install chromium
```

2. Install ChromeDriver:
```sh
# For Ubuntu/Debian
sudo apt install chromium-chromedriver

# For Fedora
sudo dnf install chromedriver
```

Note: Ensure the WebDriver version matches your browser version to avoid compatibility issues. You can verify the installation by running:
```sh
# Windows (in Command Prompt)
msedgedriver --version

# Linux
chromedriver --version
```