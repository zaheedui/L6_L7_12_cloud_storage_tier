from hypothesis import given, strategies as st
from processor import parse_storage_quota, compute_compression_ratio, lookup_bandwidth_tier_rate

@given(st.text() | st.none())
def test_parse_storage_quota_no_crash(s):
    # Using try and except to catch expected exceptions from unvalidated inputs
    try:
        parse_storage_quota(s)
    except (ValueError, TypeError, KeyError, IndexError):
        pass  # Expected failures due to malformed inputs

@given(st.text() | st.none())
def test_compute_compression_ratio_safe(s):
    # Using try and except to catch expected exceptions from unvalidated inputs
    try:
        compute_compression_ratio(s)
    except (ValueError, TypeError, ZeroDivisionError, IndexError):
        pass  # Expected failures due to malformed inputs

@given(st.text() | st.none())
def test_lookup_bandwidth_tier_rate_safe(s):
    # Using try and except to catch expected exceptions from unvalidated inputs
    try:
        lookup_bandwidth_tier_rate(s)
    except (ValueError, TypeError, KeyError):
        pass  # Expected failures due to malformed inputs