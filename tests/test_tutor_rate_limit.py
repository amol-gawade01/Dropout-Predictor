from backend.app.api.routes.tutor import gemini_rate_limit_http_exception


def test_gemini_rate_limit_response_is_retryable_and_user_friendly():
    error = gemini_rate_limit_http_exception()

    assert error.status_code == 429
    assert error.headers == {"Retry-After": "60"}
    assert "Gemini quota" in error.detail
    assert "RESOURCE_EXHAUSTED" not in error.detail
    assert "generativelanguage.googleapis.com" not in error.detail
