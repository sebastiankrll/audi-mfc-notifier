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
- (Docker)

## Installation
Docker recommended.

## Configuration

Edit `src/config/settings.py` to modify:
- Refresh interval (default: 5 seconds)
- Scheduled heartbeat/check interval
- Default MFC URL and filters
- Idle times

## Notes
- The easiest way to set filters is to select the desired models in a browser and copy the URL
- The bot requires an active internet connection
- Ensure proper WebDriver version matches your browser version
