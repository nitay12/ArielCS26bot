import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Configuration settings loaded from environment variables"""

    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    FILE_SEARCH_STORE_NAME = os.getenv("FILE_SEARCH_STORE_NAME")
    BOT_PASSWORD = os.getenv("BOT_PASSWORD")
    USERS_FILE = "data/users.json"


settings = Settings()
