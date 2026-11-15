import pytest
from cloud_storage_tier import process_storage_tenants, monitor_replication_latency

# Example test case:
def test_single_active_hot_tenant():
    tenants = [
        {
            "account_active": True,
            "tier": "hot",
            "has_backup_vault": False,
            "buckets": [{"size_gb": 100, "corrupted": False, "egress_gb": 50}]
        }
    ]
    result = process_storage_tenants(tenants, 10.0)
    assert result["total_billed"] == 2.5
    assert result["status"] == "BILLED"

# TODO: Add test cases to achieve 90-100% on both Line and Branch coverage!

# Input validation tests

def test_invalid_tenants_input():
    with pytest.raises(ValueError):
        process_storage_tenants("invalid", 10.0)


def test_negative_support_fee():
    with pytest.raises(ValueError):
        process_storage_tenants([], -5.0)


# Account status tests

def test_inactive_tenant_is_skipped():
    tenants = [
        {
            "account_active": False,
            "tier": "hot",
            "buckets": [{"size_gb": 100}]
        }
    ]
    result = process_storage_tenants(tenants, 10.0)
    assert result == {"total_billed": 0.0, "status": "ZERO_USAGE"}


# Storage tier tests

def test_cool_tier_billing():
    tenants = [{
        "account_active": True,
        "tier": "cool",
        "buckets": [{"size_gb": 100}]
    }]
    result = process_storage_tenants(tenants, 10.0)
    assert result["total_billed"] == 1.5


def test_archive_tier_billing():
    tenants = [{
        "account_active": True,
        "tier": "archive",
        "buckets": [{"size_gb": 100}]
    }]
    result = process_storage_tenants(tenants, 10.0)
    assert result["total_billed"] == 0.5


def test_invalid_tier_is_flagged():
    tenants = [{
        "account_active": True,
        "tier": "unknown",
        "buckets": [{"size_gb": 100}]
    }]
    result = process_storage_tenants(tenants, 10.0)
    assert result["status"] == "ZERO_USAGE"


# Bucket size tests

def test_zero_and_negative_bucket_sizes_are_flagged():
    tenants = [{
        "account_active": True,
        "tier": "hot",
        "buckets": [
            {"size_gb": 0},
            {"size_gb": -10}
        ]
    }]
    result = process_storage_tenants(tenants, 10.0)
    assert result["status"] == "ZERO_USAGE"


def test_large_bucket_gets_discount():
    tenants = [{
        "account_active": True,
        "tier": "hot",
        "buckets": [{"size_gb": 600}]
    }]
    result = process_storage_tenants(tenants, 10.0)
    assert result["total_billed"] == 13.5


# Corruption tests

def test_corrupted_hot_bucket():
    tenants = [{
        "account_active": True,
        "tier": "hot",
        "buckets": [{"size_gb": 100, "corrupted": True}]
    }]
    result = process_storage_tenants(tenants, 10.0)
    assert result["status"] == "ZERO_USAGE"
    assert result["total_billed"] == 0.0


def test_corrupted_archive_bucket_stops_billing():
    tenants = [{
        "account_active": True,
        "tier": "archive",
        "buckets": [
            {"size_gb": 100},
            {"size_gb": 100, "corrupted": True},
            {"size_gb": 200}
        ]
    }]
    result = process_storage_tenants(tenants, 10.0)
    assert result["total_billed"] == 0.0


# Network egress tests

def test_egress_above_100_gb():
    tenants = [{
        "account_active": True,
        "tier": "hot",
        "buckets": [{"size_gb": 100, "egress_gb": 150}]
    }]
    result = process_storage_tenants(tenants, 10.0)
    assert result["total_billed"] == 6.5


def test_egress_at_100_gb_has_no_extra_charge():
    tenants = [{
        "account_active": True,
        "tier": "hot",
        "buckets": [{"size_gb": 100, "egress_gb": 100}]
    }]
    result = process_storage_tenants(tenants, 10.0)
    assert result["total_billed"] == 2.5


# Backup vault tests

def test_backup_vault_adds_support_fee():
    tenants = [{
        "account_active": True,
        "tier": "hot",
        "has_backup_vault": True,
        "buckets": [{"size_gb": 100}]
    }]
    result = process_storage_tenants(tenants, 10.0)
    assert result["total_billed"] == 12.5


# Audit status test

def test_more_than_four_flagged_buckets_triggers_audit():
    tenants = [{
        "account_active": True,
        "tier": "hot",
        "buckets": [
            {"size_gb": 0},
            {"size_gb": -1},
            {"size_gb": 0},
            {"size_gb": -5},
            {"size_gb": 0}
        ]
    }]
    result = process_storage_tenants(tenants, 10.0)
    assert result["status"] == "AUDIT_FLAGGED"


# Replication latency monitoring tests

def test_empty_cluster_matrix():
    assert monitor_replication_latency([]) == "NO_DATA"


def test_none_cluster_matrix():
    assert monitor_replication_latency(None) == "NO_DATA"


def test_normal_latency_returns_synced():
    cluster = [
        [100, 150, 180],
        [120, 160, 190]
    ]
    assert monitor_replication_latency(cluster) == "SYNCED"


def test_latency_exactly_200_returns_synced():
    cluster = [[200, 200, 200]]
    assert monitor_replication_latency(cluster) == "SYNCED"


def test_single_high_latency_returns_synced():
    cluster = [[250, 100, 150]]
    assert monitor_replication_latency(cluster) == "SYNCED"


def test_two_consecutive_high_latencies_trigger_alert():
    cluster = [[250, 300]]
    assert monitor_replication_latency(cluster) == "SYNC_LAG_ALERT"


def test_two_high_latencies_separated_by_normal_latency():
    cluster = [[250, 100, 300]]
    assert monitor_replication_latency(cluster) == "SYNCED"


def test_alert_in_second_node():
    cluster = [
        [250, 100, 150],
        [220, 240, 100]
    ]
    assert monitor_replication_latency(cluster) == "SYNC_LAG_ALERT"
