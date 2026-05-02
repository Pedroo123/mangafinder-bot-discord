import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
    REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
    REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
    REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "mangafinder-bot/0.1 by Brankksss")

    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

    @classmethod
    def validate(cls):
        required_vars = [
            "REDDIT_CLIENT_ID",
            "REDDIT_CLIENT_SECRET",
            "REDDIT_USERNAME",
            "REDDIT_PASSWORD",
            "DISCORD_TOKEN"
        ]
        missing = [var for var in required_vars if not getattr(cls, var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
