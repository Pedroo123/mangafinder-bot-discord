import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
    REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
    REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
    REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "mangafinder-bot/1.0")

    @classmethod
    def validate(cls):
        missing = []
        if not cls.DISCORD_TOKEN: missing.append("DISCORD_TOKEN")
        if not cls.REDDIT_CLIENT_ID: missing.append("REDDIT_CLIENT_ID")
        if not cls.REDDIT_CLIENT_SECRET: missing.append("REDDIT_CLIENT_SECRET")
        if not cls.REDDIT_USERNAME: missing.append("REDDIT_USERNAME")
        if not cls.REDDIT_PASSWORD: missing.append("REDDIT_PASSWORD")

        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
