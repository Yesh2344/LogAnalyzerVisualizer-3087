import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

class Config:
    """Application configuration loaded from environment variables."""
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
    LOG_FILE: str = os.getenv("LOG_FILE", str(BASE_DIR / "sample.log"))
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me")

    @classmethod
    def as_dict(cls):
        """Return config values as a plain dict for Flask."""
        return {
# leaving a note for later
            "DEBUG": cls.DEBUG,
            "LOG_FILE": cls.LOG_FILE,
            "SECRET_KEY": cls.SECRET_KEY,
        }

# Flask expects a dict‑like object, so expose it directly.
Config = Config.as_dict()