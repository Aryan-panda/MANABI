import pytest
from app.tools.calculator import (
    EngineeringCalculator,
    QPSCalculationInput,
    StorageCalculationInput,
    BandwidthCalculationInput,
    CacheSizingInput,
    LatencyBudgetInput,
)


def test_qps_calculation():
    inp = QPSCalculationInput(
        daily_active_users=100_000,
        actions_per_user_day=50.0,
        peak_multiplier=2.5,
        read_ratio=0.8,
    )
    result = EngineeringCalculator.calculate_qps(inp)

    # 100,000 * 50 = 5,000,000 requests/day
    # 5,000,000 / 86400 = ~57.87 QPS
    assert round(result.average_total_qps, 1) == 57.9
    assert round(result.peak_total_qps, 1) == round(57.87 * 2.5, 1)
    assert result.average_read_qps + result.average_write_qps == pytest.approx(result.average_total_qps, rel=1e-2)
    assert result.peak_read_qps + result.peak_write_qps == pytest.approx(result.peak_total_qps, rel=1e-2)


def test_storage_calculation():
    inp = StorageCalculationInput(
        daily_records=1_000_000,
        average_record_size_bytes=500,
        retention_years=2.0,
        indexing_overhead_percent=20.0,
        replication_factor=3,
    )
    result = EngineeringCalculator.calculate_storage(inp)

    # 1,000,000 * 500 bytes = 500,000,000 bytes/day = ~476.84 MB/day
    assert result.daily_raw_mb > 400
    assert result.total_with_indexes_gb > result.total_raw_gb
    assert result.total_with_replication_gb == pytest.approx(result.total_with_indexes_gb * 3, rel=1e-2)
    assert result.total_with_replication_tb == pytest.approx(result.total_with_replication_gb / 1024, rel=1e-2)


def test_bandwidth_calculation():
    inp = BandwidthCalculationInput(
        peak_qps=1000.0,
        average_request_payload_bytes=1000,
        average_response_payload_bytes=5000,
    )
    result = EngineeringCalculator.calculate_bandwidth(inp)

    # Ingress: 1000 * 1000 * 8 = 8,000,000 bps = 8 Mbps
    assert result.ingress_mbps == 8.0
    # Egress: 1000 * 5000 * 8 = 40,000,000 bps = 40 Mbps
    assert result.egress_mbps == 40.0
    assert result.total_mbps == 48.0
    assert result.total_gbps == 0.048


def test_cache_sizing():
    inp = CacheSizingInput(
        daily_read_requests=10_000_000,
        average_cached_object_size_bytes=2048, # 2 KB
        working_set_percentage=20.0,
        headroom_multiplier=1.25,
    )
    result = EngineeringCalculator.calculate_cache_size(inp)

    assert result.working_set_gb > 0
    assert result.recommended_cache_size_gb == pytest.approx(result.working_set_gb * 1.25, rel=1e-2)
    assert result.recommended_ram_gb >= result.recommended_cache_size_gb


def test_latency_budget():
    inp = LatencyBudgetInput(
        target_sla_ms=200.0,
        network_rtt_ms=40.0,
        gateway_proxy_ms=10.0,
        cache_hit_rate=0.8,
        cache_latency_ms=2.0,
        db_query_latency_ms=20.0,
        db_queries_per_request=2,
    )
    result = EngineeringCalculator.calculate_latency_budget(inp)

    assert result.is_within_budget is True
    assert result.slack_remaining_ms > 0
    assert result.expected_total_p95_ms < 200.0
