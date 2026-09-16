import threading
from typing import Dict, List, Tuple, Optional


class Metric:
    def __init__(self, name: str, description: str, label_names: Optional[List[str]] = None):
        self.name = name
        self.description = description
        self.label_names = tuple(label_names or [])
        self._lock = threading.Lock()

    def _labels_key(self, labels: Dict[str, str]) -> Tuple[Tuple[str, str], ...]:
        return tuple(sorted((k, str(labels.get(k, ""))) for k in self.label_names))

    def _format_labels(self, label_tuple: Tuple[Tuple[str, str], ...]) -> str:
        if not label_tuple:
            return ""
        items = [f'{k}="{v}"' for k, v in label_tuple]
        return "{" + ",".join(items) + "}"


class Counter(Metric):
    def __init__(self, name: str, description: str, label_names: Optional[List[str]] = None):
        super().__init__(name, description, label_names)
        self._values: Dict[Tuple[Tuple[str, str], ...], float] = {}

    def inc(self, amount: float = 1.0, **labels):
        if amount < 0:
            raise ValueError("Counter increments must be non-negative")
        key = self._labels_key(labels)
        with self._lock:
            self._values[key] = self._values.get(key, 0.0) + amount

    def get(self, **labels) -> float:
        key = self._labels_key(labels)
        with self._lock:
            return self._values.get(key, 0.0)

    def to_prometheus(self) -> List[str]:
        lines = [
            f"# HELP {self.name} {self.description}",
            f"# TYPE {self.name} counter",
        ]
        with self._lock:
            if not self._values and not self.label_names:
                lines.append(f"{self.name} 0")
            for label_tuple, val in self._values.items():
                lbl_str = self._format_labels(label_tuple)
                lines.append(f"{self.name}{lbl_str} {val}")
        return lines


class Gauge(Metric):
    def __init__(self, name: str, description: str, label_names: Optional[List[str]] = None):
        super().__init__(name, description, label_names)
        self._values: Dict[Tuple[Tuple[str, str], ...], float] = {}

    def set(self, value: float, **labels):
        key = self._labels_key(labels)
        with self._lock:
            self._values[key] = float(value)

    def inc(self, amount: float = 1.0, **labels):
        key = self._labels_key(labels)
        with self._lock:
            self._values[key] = self._values.get(key, 0.0) + amount

    def dec(self, amount: float = 1.0, **labels):
        key = self._labels_key(labels)
        with self._lock:
            self._values[key] = self._values.get(key, 0.0) - amount

    def get(self, **labels) -> float:
        key = self._labels_key(labels)
        with self._lock:
            return self._values.get(key, 0.0)

    def to_prometheus(self) -> List[str]:
        lines = [
            f"# HELP {self.name} {self.description}",
            f"# TYPE {self.name} gauge",
        ]
        with self._lock:
            for label_tuple, val in self._values.items():
                lbl_str = self._format_labels(label_tuple)
                lines.append(f"{self.name}{lbl_str} {val}")
        return lines


class Histogram(Metric):
    DEFAULT_BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)

    def __init__(
        self,
        name: str,
        description: str,
        label_names: Optional[List[str]] = None,
        buckets: Optional[Tuple[float, ...]] = None,
    ):
        super().__init__(name, description, label_names)
        self.buckets = tuple(sorted(buckets or self.DEFAULT_BUCKETS))
        # Store per label: {"sum": x, "count": y, "buckets": {bucket_le: count}}
        self._data: Dict[Tuple[Tuple[str, str], ...], Dict] = {}

    def observe(self, value: float, **labels):
        val = float(value)
        key = self._labels_key(labels)
        with self._lock:
            if key not in self._data:
                self._data[key] = {
                    "sum": 0.0,
                    "count": 0,
                    "buckets": {b: 0 for b in self.buckets},
                }
            entry = self._data[key]
            entry["sum"] += val
            entry["count"] += 1
            for b in self.buckets:
                if val <= b:
                    entry["buckets"][b] += 1

    def to_prometheus(self) -> List[str]:
        lines = [
            f"# HELP {self.name} {self.description}",
            f"# TYPE {self.name} histogram",
        ]
        with self._lock:
            for label_tuple, entry in self._data.items():
                lbl_dict = dict(label_tuple)
                # Buckets
                for b in self.buckets:
                    b_labels = dict(lbl_dict)
                    b_labels["le"] = str(b)
                    b_lbl_str = self._format_labels(tuple(sorted(b_labels.items())))
                    lines.append(f"{self.name}_bucket{b_lbl_str} {entry['buckets'][b]}")
                # +Inf
                inf_labels = dict(lbl_dict)
                inf_labels["le"] = "+Inf"
                inf_lbl_str = self._format_labels(tuple(sorted(inf_labels.items())))
                lines.append(f"{self.name}_bucket{inf_lbl_str} {entry['count']}")
                # Sum & Count
                base_lbl_str = self._format_labels(label_tuple)
                lines.append(f"{self.name}_sum{base_lbl_str} {entry['sum']:.6f}")
                lines.append(f"{self.name}_count{base_lbl_str} {entry['count']}")
        return lines


class MetricsRegistry:
    def __init__(self):
        self._metrics: List[Metric] = []
        self._lock = threading.Lock()

    def register(self, metric: Metric):
        with self._lock:
            self._metrics.append(metric)
        return metric

    def generate_metrics_text(self) -> str:
        lines: List[str] = []
        with self._lock:
            for metric in self._metrics:
                lines.extend(metric.to_prometheus())
        return "\n".join(lines) + "\n"


# Global Platform Registry
registry = MetricsRegistry()

# System Metrics
HTTP_REQUESTS_TOTAL = registry.register(
    Counter("manabi_http_requests_total", "Total HTTP requests handled by platform", ["method", "endpoint", "status"])
)
HTTP_REQUEST_DURATION_SECONDS = registry.register(
    Histogram("manabi_http_request_duration_seconds", "HTTP request processing duration in seconds", ["method", "endpoint"])
)
LLM_REQUESTS_TOTAL = registry.register(
    Counter("manabi_llm_requests_total", "Total calls made to Model Gateway providers", ["provider", "model", "status"])
)
LLM_LATENCY_SECONDS = registry.register(
    Histogram("manabi_llm_latency_seconds", "Model Gateway latency in seconds", ["provider", "model"])
)
LLM_TOKENS_TOTAL = registry.register(
    Counter("manabi_llm_tokens_total", "Tokens consumed across providers", ["provider", "model", "type"])
)
RAG_RETRIEVALS_TOTAL = registry.register(
    Counter("manabi_rag_retrievals_total", "Total pgvector similarity retrievals", ["agent", "status"])
)
RAG_RETRIEVAL_LATENCY_SECONDS = registry.register(
    Histogram("manabi_rag_retrieval_latency_seconds", "RAG retrieval latency in seconds", ["agent"])
)
TOOL_EXECUTIONS_TOTAL = registry.register(
    Counter("manabi_tool_executions_total", "Deterministic tool executions", ["tool", "status"])
)
CACHE_OPERATIONS_TOTAL = registry.register(
    Counter("manabi_cache_operations_total", "Redis cache operations", ["operation", "status"])
)
ACTIVE_AGENTS_GAUGE = registry.register(
    Gauge("manabi_registered_agents", "Number of registered domain agents in system", ["agent_id"])
)
