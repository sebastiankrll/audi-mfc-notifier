from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import threading
from src.config.settings import Settings
import traceback
import time
import requests

class TelegramNotifier:
    def __init__(self, settings: Settings):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID

        self._running = threading.Event()
        self._reset_requested = threading.Event()
        self._url_lock = threading.Lock()
        self._url = settings.URL

        self.app = ApplicationBuilder().token(self.bot_token).build()
        self.app.add_handler(CommandHandler("start", self._cmd_start))
        self.app.add_handler(CommandHandler("stop", self._cmd_stop))
        self.app.add_handler(CommandHandler("seturl", self._cmd_seturl))
        self.app.add_handler(CommandHandler("reset", self._cmd_reset))

    def start(self):
        # Blocking; runs in background thread
        self.app.run_polling(poll_interval=1.0)

    def stop(self):
        try:
            self.app.stop()
        except Exception:
            pass


    # -- Handlers (async) --
    async def _cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._running.is_set():
            self._running.set()
            await context.bot.send_message(chat_id=update.effective_chat.id, text="🟢  Monitoring started")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Already running...")

    async def _cmd_stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self._running.is_set():
            self._running.clear()
            await context.bot.send_message(chat_id=update.effective_chat.id, text="🔴  Monitoring stopped")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Already stopped...")

    async def _cmd_seturl(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # /url <url>
        if context.args:
            new_url = " ".join(context.args).strip()
            if "/i/s%7C" not in new_url:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"❌  Please set a filter.")
                return
    
            with self._url_lock:
                self._url = new_url
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🔗  URL set")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: /seturl <url>")

    async def _cmd_reset(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self._reset_requested.set()
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🔄  Resetting previous results...")

    # -- Hooks --
    def is_running(self):
        return self._running.is_set()

    def is_reset_requested(self):
        if self._reset_requested.is_set():
            self._reset_requested.clear()
            return True
        return False

    def get_url(self):
        with self._url_lock:
            return self._url

    def set_url(self, url):
        with self._url_lock:
            self._url = url

    def send_notification(self, message):
        # Synchronous send via Bot API (keeps simple and thread-safe)
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": message}
        try:
            requests.post(url, data=payload, timeout=5)
        except Exception:
            # don't raise in notifier; main loop should continue
            pass

    def notify_error(self, exc_info=None, context: str = None):
        """Send plain traceback to Telegram (truncates to fit)."""
        try:
            if exc_info:
                tb = "".join(traceback.format_exception(*exc_info))
            else:
                tb = traceback.format_exc()

            header = f"❌ Error: {context or 'exception'}\n{time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            msg = header + tb

            # Telegram limit ~4096 chars; leave margin
            if len(msg) > 3900:
                msg = msg[:3900] + "\n\n...[truncated]"

            self.send_notification(msg)
            print(tb)
        except Exception:
            # avoid infinite loops if notifier fails
            print("Failed to send error to Telegram:", traceback.format_exc())