import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
    REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
    REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
    REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "mangafinder-bot/0.1 by Brankksss")

    @classmethod
    def validate(cls):
        required_vars = [
            "DISCORD_TOKEN",
            "REDDIT_CLIENT_ID",
            "REDDIT_CLIENT_SECRET",
            "REDDIT_USERNAME",
            "REDDIT_PASSWORD"
        ]
        missing = [var for var in required_vars if not getattr(cls, var)]
        if missing:
            # When running in Azure, these should be set in the Container App environment
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
