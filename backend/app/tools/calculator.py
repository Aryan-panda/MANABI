import math
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class QPSCalculationInput(BaseModel):
    daily_active_users: int = Field(..., description="Daily active users (DAU)")
    actions_per_user_day: float = Field(..., description="Average requests/actions generated per user per day")
    peak_multiplier: float = Field(default=2.0, description="Multiplier for peak traffic (typically 2x-5x)")
    read_ratio: float = Field(default=0.8, description="Proportion of read operations (0.0 to 1.0)")


class QPSCalculationResult(BaseModel):
    average_total_qps: float
    peak_total_qps: float
    average_read_qps: float
    average_write_qps: float
    peak_read_qps: float
    peak_write_qps: float
    seconds_per_day: int = 86400


class StorageCalculationInput(BaseModel):
    daily_records: int = Field(..., description="Number of new records/writes per day")
    average_record_size_bytes: int = Field(..., description="Average size of a single record in bytes")
    retention_years: float = Field(default=3.0, description="Data retention policy in years")
    indexing_overhead_percent: float = Field(default=25.0, description="Estimated overhead for secondary indexes in %")
    replication_factor: int = Field(default=3, description="Database replication factor")


class StorageCalculationResult(BaseModel):
    daily_raw_mb: float
    annual_raw_gb: float
    total_raw_gb: float
    total_with_indexes_gb: float
    total_with_replication_gb: float
    total_with_replication_tb: float


class BandwidthCalculationInput(BaseModel):
    peak_qps: float
    average_request_payload_bytes: int = 1024  # 1 KB
    average_response_payload_bytes: int = 8192 # 8 KB


class BandwidthCalculationResult(BaseModel):
    ingress_mbps: float
    egress_mbps: float
    total_mbps: float
    total_gbps: float


class CacheSizingInput(BaseModel):
    daily_read_requests: int
    average_cached_object_size_bytes: int
    working_set_percentage: float = Field(default=20.0, description="Pareto working set (typically 20% of items generate 80% of traffic)")
    headroom_multiplier: float = Field(default=1.3, description="Safety headroom buffer (typically 1.2x - 1.5x)")


class CacheSizingResult(BaseModel):
    working_set_gb: float
    recommended_cache_size_gb: float
    recommended_ram_gb: float


class LatencyBudgetInput(BaseModel):
    target_sla_ms: float = Field(default=200.0, description="Target p95/p99 SLA response time in ms")
    network_rtt_ms: float = Field(default=30.0, description="Expected client-to-datacenter roundtrip in ms")
    gateway_proxy_ms: float = Field(default=10.0, description="Nginx/Gateway ingress & egress latency in ms")
    cache_hit_rate: float = Field(default=0.8, description="Expected cache hit probability")
    cache_latency_ms: float = Field(default=2.0, description="Redis cache lookup latency in ms")
    db_query_latency_ms: float = Field(default=25.0, description="PostgreSQL indexed read latency in ms")
    db_queries_per_request: int = Field(default=2, description="Average DB queries on cache miss")


class LatencyBudgetResult(BaseModel):
    target_sla_ms: float
    expected_app_latency_ms: float
    expected_total_p95_ms: float
    is_within_budget: bool
    slack_remaining_ms: float


class EngineeringCalculator:
    """
    Deterministic calculation engine for system capacity planning.
    Guarantees mathematically verified system metrics without LLM arithmetic errors.
    """

    @staticmethod
    def calculate_qps(params: QPSCalculationInput) -> QPSCalculationResult:
        total_daily_requests = params.daily_active_users * params.actions_per_user_day
        avg_qps = total_daily_requests / 86400.0
        peak_qps = avg_qps * params.peak_multiplier

        read_ratio = min(max(params.read_ratio, 0.0), 1.0)
        write_ratio = 1.0 - read_ratio

        return QPSCalculationResult(
            average_total_qps=round(avg_qps, 2),
            peak_total_qps=round(peak_qps, 2),
            average_read_qps=round(avg_qps * read_ratio, 2),
            average_write_qps=round(avg_qps * write_ratio, 2),
            peak_read_qps=round(peak_qps * read_ratio, 2),
            peak_write_qps=round(peak_qps * write_ratio, 2),
        )

    @staticmethod
    def calculate_storage(params: StorageCalculationInput) -> StorageCalculationResult:
        daily_bytes = params.daily_records * params.average_record_size_bytes
        daily_raw_mb = daily_bytes / (1024 * 1024)

        annual_raw_gb = (daily_bytes * 365) / (1024 * 1024 * 1024)
        total_raw_gb = annual_raw_gb * params.retention_years

        index_multiplier = 1.0 + (params.indexing_overhead_percent / 100.0)
        total_with_indexes_gb = total_raw_gb * index_multiplier
        total_with_replication_gb = total_with_indexes_gb * params.replication_factor
        total_with_replication_tb = total_with_replication_gb / 1024.0

        return StorageCalculationResult(
            daily_raw_mb=round(daily_raw_mb, 2),
            annual_raw_gb=round(annual_raw_gb, 2),
            total_raw_gb=round(total_raw_gb, 2),
            total_with_indexes_gb=round(total_with_indexes_gb, 2),
            total_with_replication_gb=round(total_with_replication_gb, 2),
            total_with_replication_tb=round(total_with_replication_tb, 3),
        )

    @staticmethod
    def calculate_bandwidth(params: BandwidthCalculationInput) -> BandwidthCalculationResult:
        # 1 byte = 8 bits
        ingress_bps = params.peak_qps * params.average_request_payload_bytes * 8
        egress_bps = params.peak_qps * params.average_response_payload_bytes * 8

        ingress_mbps = ingress_bps / 1_000_000.0
        egress_mbps = egress_bps / 1_000_000.0
        total_mbps = ingress_mbps + egress_mbps
        total_gbps = total_mbps / 1000.0

        return BandwidthCalculationResult(
            ingress_mbps=round(ingress_mbps, 2),
            egress_mbps=round(egress_mbps, 2),
            total_mbps=round(total_mbps, 2),
            total_gbps=round(total_gbps, 3),
        )

    @staticmethod
    def calculate_cache_size(params: CacheSizingInput) -> CacheSizingResult:
        working_set_fraction = min(max(params.working_set_percentage / 100.0, 0.01), 1.0)
        working_set_records = params.daily_read_requests * working_set_fraction
        working_set_bytes = working_set_records * params.average_cached_object_size_bytes

        working_set_gb = working_set_bytes / (1024 * 1024 * 1024)
        recommended_cache_gb = working_set_gb * params.headroom_multiplier
        # Standard cloud VM RAM sizes (powers of 2)
        recommended_ram_gb = math.pow(2, math.ceil(math.log2(max(recommended_cache_gb, 2))))

        return CacheSizingResult(
            working_set_gb=round(working_set_gb, 2),
            recommended_cache_size_gb=round(recommended_cache_gb, 2),
            recommended_ram_gb=round(recommended_ram_gb, 0),
        )

    @staticmethod
    def calculate_latency_budget(params: LatencyBudgetInput) -> LatencyBudgetResult:
        cache_hit = min(max(params.cache_hit_rate, 0.0), 1.0)
        cache_miss = 1.0 - cache_hit

        # Average app-tier processing time estimated at 15ms
        app_compute_ms = 15.0
        data_tier_ms = (cache_hit * params.cache_latency_ms) + (
            cache_miss * (params.cache_latency_ms + (params.db_queries_per_request * params.db_query_latency_ms))
        )
        internal_processing_ms = app_compute_ms + data_tier_ms
        total_p95_ms = params.network_rtt_ms + params.gateway_proxy_ms + internal_processing_ms

        slack = params.target_sla_ms - total_p95_ms
        is_within_budget = slack >= 0

        return LatencyBudgetResult(
            target_sla_ms=params.target_sla_ms,
            expected_app_latency_ms=round(internal_processing_ms, 2),
            expected_total_p95_ms=round(total_p95_ms, 2),
            is_within_budget=is_within_budget,
            slack_remaining_ms=round(slack, 2),
        )


def calculate_qps(**kwargs) -> Dict[str, Any]:
    res = EngineeringCalculator.calculate_qps(QPSCalculationInput(**kwargs))
    return res.model_dump()


def calculate_storage(**kwargs) -> Dict[str, Any]:
    res = EngineeringCalculator.calculate_storage(StorageCalculationInput(**kwargs))
    return res.model_dump()


def calculate_bandwidth(**kwargs) -> Dict[str, Any]:
    res = EngineeringCalculator.calculate_bandwidth(BandwidthCalculationInput(**kwargs))
    return res.model_dump()


def calculate_cache_size(**kwargs) -> Dict[str, Any]:
    res = EngineeringCalculator.calculate_cache_sizing(CacheSizingInput(**kwargs))
    return res.model_dump()


def calculate_latency_budget(**kwargs) -> Dict[str, Any]:
    res = EngineeringCalculator.calculate_latency_budget(LatencyBudgetInput(**kwargs))
    return res.model_dump()

