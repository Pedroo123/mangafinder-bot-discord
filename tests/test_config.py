import pytest
from unittest.mock import patch
from config import Config

def test_config_validate_missing_vars():
    with patch.object(Config, 'DISCORD_TOKEN', None):
        with pytest.raises(ValueError, match="Missing required environment variables: DISCORD_TOKEN"):
            Config.validate()

def test_config_validate_all_present():
    with patch.object(Config, 'DISCORD_TOKEN', 'token'), \
         patch.object(Config, 'REDDIT_CLIENT_ID', 'id'), \
         patch.object(Config, 'REDDIT_CLIENT_SECRET', 'secret'), \
         patch.object(Config, 'REDDIT_USERNAME', 'user'), \
         patch.object(Config, 'REDDIT_PASSWORD', 'pass'):
        # Should not raise any exception
        Config.validate()
