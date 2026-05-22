import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class Config:
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
    REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
    REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
    REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "mangafinder-bot/1.0 by Brankksss")

    @classmethod
    def validate(cls):
        required_vars = {
            "DISCORD_TOKEN": cls.DISCORD_TOKEN,
            "REDDIT_CLIENT_ID": cls.REDDIT_CLIENT_ID,
            "REDDIT_CLIENT_SECRET": cls.REDDIT_CLIENT_SECRET,
            "REDDIT_USERNAME": cls.REDDIT_USERNAME,
            "REDDIT_PASSWORD": cls.REDDIT_PASSWORD
        }

        missing = [var for var, value in required_vars.items() if not value]

        if missing:
            error_msg = f"Missing required environment variables: {', '.join(missing)}"
            logger.critical(error_msg)
            # When running in Azure, these should be set in the Container App environment
            raise ValueError(error_msg)

        logger.info("Configuration validated successfully.")
