def assert_successful_backend_fetches(network_monitor, *, context: str, min_count: int = 1):
    successful_calls = [
        event
        for event in network_monitor.response_events(method="POST", status=200, resource_type="fetch")
        if "/api/" in event["url"] or "trackofy_api_new_live" in event["url"]
    ]
    assert len(successful_calls) >= min_count, (
        f"{context} should trigger at least {min_count} successful backend fetch response(s)."
    )
    return successful_calls
