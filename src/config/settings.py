from dataclasses import dataclass, field
import os
from typing import List
from dotenv import load_dotenv
load_dotenv()

@dataclass
class Settings:
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID")
    
    # Browser Configuration
    URL: str = "https://vtp.audi.com/ademanlwb/i/s%7C10,AAGE,AAGG,AAFE,AAFX,AAFU,AADQ,AACT,AAEY,AAGA,AAFZ,AAGF,AAGH,AAFY,AAFV/controller.do#filter/models"
    USERNAME: str = os.getenv("VTP_USERNAME")
    PASSWORD: str = os.getenv("VTP_PASSWORD")
    
    # Monitoring Configuration
    REFRESH_INTERVAL: int = 5 # seconds (min. 5)
    SCHEDULED_CHECK_INTERVAL: int = 6 # hours
    IDLE_PERIODS: List[str] = field(default_factory=lambda: ["22:00-06:00"]) # "HH:MM-HH:MM" (local time), separated by commas (e.g., ["22:30-06:00", "12:00-13:00"])