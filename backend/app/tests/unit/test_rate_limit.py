from app.core.rate_limit import RateLimitError, check_rate_limit


def test_rate_limit_retry_after_is_dynamic() -> None:
    key = "test-rate-limit-retry-after-dynamic"
    check_rate_limit(key=key, limit=1, window_seconds=3)
    try:
        check_rate_limit(key=key, limit=1, window_seconds=3)
    except RateLimitError as error:
        retry_after = int(error.details["retry_after"])
        assert 1 <= retry_after <= 3
    else:
        raise AssertionError("Expected RateLimitError")
