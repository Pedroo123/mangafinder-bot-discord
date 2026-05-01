import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN")
    REDDIT_CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET")
    REDDIT_USERNAME: str = os.getenv("REDDIT_USERNAME")
    REDDIT_PASSWORD: str = os.getenv("REDDIT_PASSWORD")
    REDDIT_USER_AGENT: str = os.getenv("REDDIT_USER_AGENT", "mangafinder-bot/1.0")

    def validate(self):
        missing = []
        for key, value in self.__dict__.items():
            if not value:
                missing.append(key)

        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

config = Config()
