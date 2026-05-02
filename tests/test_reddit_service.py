import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.service.reddit_service import RedditService

@pytest.fixture
def mock_config():
    with patch("src.service.reddit_service.Config") as mock:
        mock.REDDIT_CLIENT_ID = "dummy_id"
        mock.REDDIT_CLIENT_SECRET = "dummy_secret"
        mock.REDDIT_USERNAME = "dummy_user"
        mock.REDDIT_PASSWORD = "dummy_password"
        mock.REDDIT_USER_AGENT = "dummy_agent"
        yield mock

class AsyncIterator:
    def __init__(self, items):
        self.items = items
        self.index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index >= len(self.items):
            raise StopAsyncIteration
        item = self.items[self.index]
        self.index += 1
        return item

@pytest.mark.asyncio
async def test_search_subreddit_success(mock_config):
    # Setup
    with patch("asyncpraw.Reddit", return_value=MagicMock()) as mock_reddit_class:
        mock_reddit = mock_reddit_class.return_value
        service = RedditService()

        mock_submission = MagicMock()
        mock_submission.id = "123"
        mock_submission.title = "Test Manga"
        mock_submission.url = "https://i.redd.it/test.jpg"
        mock_submission.permalink = "/r/manga/comments/123/test_manga/"
        mock_submission.author = "testuser"
        mock_submission.created_utc = 1600000000
        mock_submission.score = 100
        mock_submission.num_comments = 10
        mock_submission.subreddit = "manga"
        mock_submission.name = "t3_123"
        mock_submission.preview = {
            "images": [{"source": {"url": "https://preview.redd.it/test.jpg&amp;s=123"}}]
        }

        mock_subreddit = MagicMock()
        mock_reddit.subreddit = MagicMock(return_value=mock_subreddit)

        # search() is NOT a coroutine, it returns a generator
        mock_subreddit.search.return_value = AsyncIterator([mock_submission])

        # Execute
        result = await service.search_subreddit("manga", "test query")

        # Assert
        assert len(result["posts"]) == 1
        post = result["posts"][0]
        assert post["id"] == "123"
        assert post["title"] == "Test Manga"
        # Verify HTML unescape
        assert post["thumbnail"] == "https://preview.redd.it/test.jpg&s=123"
        assert result["after"] == "t3_123"

@pytest.mark.asyncio
async def test_search_subreddit_no_results(mock_config):
    with patch("asyncpraw.Reddit", return_value=MagicMock()) as mock_reddit_class:
        mock_reddit = mock_reddit_class.return_value
        service = RedditService()

        mock_subreddit = MagicMock()
        mock_reddit.subreddit = MagicMock(return_value=mock_subreddit)
        mock_subreddit.search.return_value = AsyncIterator([])

        result = await service.search_subreddit("manga", "nonexistent")

        assert len(result["posts"]) == 0
        assert result["after"] is None

def test_get_best_image_logic(mock_config):
    with patch("asyncpraw.Reddit", return_value=MagicMock()):
        service = RedditService()

        # Case 1: Preview available
        sub1 = MagicMock()
        sub1.preview = {"images": [{"source": {"url": "url_preview&amp;s=123"}}]}
        assert service._get_best_image(sub1) == "url_preview&s=123"

        # Case 2: No preview, but direct image URL
        sub2 = MagicMock()
        del sub2.preview
        sub2.url = "https://example.com/image.PNG" # Test case insensitivity
        assert service._get_best_image(sub2) == "https://example.com/image.PNG"

        # Case 3: No preview, no direct image, but thumbnail
        sub3 = MagicMock()
        del sub3.preview
        sub3.url = "https://example.com/post"
        sub3.thumbnail = "http://url_thumb&amp;s=123"
        assert service._get_best_image(sub3) == "http://url_thumb&s=123"

        # Case 4: No image at all
        sub4 = MagicMock()
        del sub4.preview
        sub4.url = "https://example.com/post"
        sub4.thumbnail = "default"
        assert service._get_best_image(sub4) is None
