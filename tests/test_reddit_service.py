import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from service.reddit_service import RedditService

@pytest.fixture
def reddit_service():
    with patch('asyncpraw.Reddit'):
        service = RedditService()
        return service

def test_get_best_image_direct_link(reddit_service):
    submission = MagicMock()
    submission.url = "https://example.com/image.jpg"
    submission.preview = {}
    submission.thumbnail = "default"

    assert reddit_service._get_best_image(submission) == "https://example.com/image.jpg"

def test_get_best_image_preview(reddit_service):
    submission = MagicMock()
    submission.url = "https://example.com/post"
    submission.preview = {
        'images': [{
            'source': {'url': "https://example.com/preview.jpg&amp;auth=123"}
        }]
    }
    submission.thumbnail = "default"

    # Should unescape &amp;
    assert reddit_service._get_best_image(submission) == "https://example.com/preview.jpg&auth=123"

def test_get_best_image_thumbnail_fallback(reddit_service):
    submission = MagicMock()
    submission.url = "https://example.com/post"
    del submission.preview
    submission.thumbnail = "https://example.com/thumb.jpg"

    assert reddit_service._get_best_image(submission) == "https://example.com/thumb.jpg"

@pytest.mark.asyncio
async def test_search_subreddit_calls_praw(reddit_service):
    # Mocking the async iterator for search
    mock_submission = MagicMock()
    mock_submission.id = "123"
    mock_submission.title = "Test Post"
    mock_submission.url = "https://reddit.com/test"
    mock_submission.permalink = "/r/test/comments/123"
    mock_submission.author = "tester"
    mock_submission.created_utc = 1234567890
    mock_submission.score = 100
    mock_submission.num_comments = 10
    mock_submission.subreddit = "manga"
    mock_submission.name = "t3_123"
    mock_submission.thumbnail = "self"

    mock_search_results = AsyncMock()
    mock_search_results.__aiter__.return_value = [mock_submission]

    reddit_service.reddit.subreddit.return_value.search.return_value = mock_search_results

    result = await reddit_service.search_subreddit("manga", "One Piece")

    assert len(result['posts']) == 1
    assert result['posts'][0]['title'] == "Test Post"
    assert result['after'] == "t3_123"
    reddit_service.reddit.subreddit.assert_called_with("manga")

def test_get_best_image_gallery(reddit_service):
    submission = MagicMock()
    submission.is_gallery = True
    submission.gallery_data = {
        'items': [{'media_id': 'img1'}]
    }
    submission.media_metadata = {
        'img1': {
            'status': 'valid',
            's': {'u': "https://example.com/gallery1.jpg&amp;v=1"}
        }
    }
    submission.preview = {}
    submission.thumbnail = "default"

    assert reddit_service._get_best_image(submission) == "https://example.com/gallery1.jpg&v=1"

def test_get_best_image_gallery_invalid(reddit_service):
    submission = MagicMock()
    submission.is_gallery = True
    submission.gallery_data = {
        'items': [{'media_id': 'img1'}]
    }
    submission.media_metadata = {
        'img1': {
            'status': 'failed'
        }
    }
    submission.preview = {}
    submission.url = "https://example.com/post"
    submission.thumbnail = "https://example.com/thumb.jpg"

    assert reddit_service._get_best_image(submission) == "https://example.com/thumb.jpg"
