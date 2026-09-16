import pytest
from app.observability.metrics import (
    MetricsRegistry,
    Counter,
    Gauge,
    Histogram,
    registry,
    HTTP_REQUESTS_TOTAL,
)
from app.observability.logger import StructuredJsonFormatter
import logging
import json


def test_counter_increments():
    c = Counter("test_counter", "A test counter", ["env", "status"])
    c.inc(env="prod", status="200")
    c.inc(amount=2.5, env="prod", status="200")
    assert c.get(env="prod", status="200") == 3.5

    lines = c.to_prometheus()
    assert any("# HELP test_counter" in l for l in lines)
    assert any('# TYPE test_counter counter' in l for l in lines)
    assert any('test_counter{env="prod",status="200"} 3.5' in l for l in lines)


def test_counter_negative_error():
    c = Counter("test_counter", "A test counter")
    with pytest.raises(ValueError):
        c.inc(-1)


def test_gauge_operations():
    g = Gauge("test_gauge", "A test gauge", ["service"])
    g.set(10.0, service="auth")
    assert g.get(service="auth") == 10.0
    g.inc(5.0, service="auth")
    assert g.get(service="auth") == 15.0
    g.dec(3.0, service="auth")
    assert g.get(service="auth") == 12.0


def test_histogram_observations():
    h = Histogram("test_hist", "A test histogram", ["path"], buckets=(0.1, 0.5, 1.0))
    h.observe(0.05, path="/api")
    h.observe(0.35, path="/api")
    h.observe(2.5, path="/api")

    prom_lines = "\n".join(h.to_prometheus())
    assert 'test_hist_bucket{le="0.1",path="/api"} 1' in prom_lines
    assert 'test_hist_bucket{le="0.5",path="/api"} 2' in prom_lines
    assert 'test_hist_bucket{le="+Inf",path="/api"} 3' in prom_lines
    assert 'test_hist_count{path="/api"} 3' in prom_lines


def test_structured_json_formatter():
    formatter = StructuredJsonFormatter()
    record = logging.LogRecord(
        name="manabi.test",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Test event message",
        args=(),
        exc_info=None,
    )
    record.correlation_id = "corr-12345"
    record.user_id = "user-789"
    record.latency_ms = 42.5

    formatted = formatter.format(record)
    parsed = json.loads(formatted)
    assert parsed["level"] == "INFO"
    assert parsed["message"] == "Test event message"
    assert parsed["correlation_id"] == "corr-12345"
    assert parsed["user_id"] == "user-789"
    assert parsed["latency_ms"] == 42.5
