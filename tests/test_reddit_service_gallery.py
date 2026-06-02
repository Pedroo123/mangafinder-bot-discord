import pytest
from unittest.mock import MagicMock, patch
from service.reddit_service import RedditService

@pytest.fixture
def reddit_service():
    with patch('asyncpraw.Reddit'):
        service = RedditService()
        return service

def test_get_best_image_gallery(reddit_service):
    submission = MagicMock()
    submission.is_gallery = True
    submission.gallery_data = {
        "items": [{"media_id": "img1"}]
    }
    submission.media_metadata = {
        "img1": {
            "s": {"u": "https://preview.redd.it/img1.jpg?width=640&amp;crop=smart&amp;auto=webp&amp;s=123"}
        }
    }
    # Should handle is_gallery and unescape URL
    assert reddit_service._get_best_image(submission) == "https://preview.redd.it/img1.jpg?width=640&crop=smart&auto=webp&s=123"

def test_get_best_image_gallery_preview_fallback(reddit_service):
    submission = MagicMock()
    submission.is_gallery = True
    submission.gallery_data = {
        "items": [{"media_id": "img1"}]
    }
    submission.media_metadata = {
        "img1": {
            "p": [{"u": "https://preview.redd.it/img1_thumb.jpg?width=108&amp;crop=smart&amp;auto=webp&amp;s=456"}]
        }
    }
    # Should fallback to 'p' if 's' is missing
    assert reddit_service._get_best_image(submission) == "https://preview.redd.it/img1_thumb.jpg?width=108&crop=smart&auto=webp&s=456"

def test_get_best_image_gallery_missing_metadata(reddit_service):
    submission = MagicMock()
    submission.is_gallery = True
    submission.gallery_data = {"items": [{"media_id": "img1"}]}
    submission.media_metadata = {}
    submission.preview = {"images": [{"source": {"url": "https://example.com/preview.jpg"}}]}

    # Should fallback to preview if gallery metadata is missing/incomplete
    assert reddit_service._get_best_image(submission) == "https://example.com/preview.jpg"
