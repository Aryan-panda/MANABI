import pytest
from app.memory.manager import MemoryManager


def test_confidence_escalation():
    # 1 observation -> low
    assert MemoryManager._calculate_confidence(1) == "low"
    # 2 observations -> medium
    assert MemoryManager._calculate_confidence(2) == "medium"
    assert MemoryManager._calculate_confidence(3) == "medium"
    assert MemoryManager._calculate_confidence(4) == "medium"
    # 5+ observations -> high
    assert MemoryManager._calculate_confidence(5) == "high"
    assert MemoryManager._calculate_confidence(10) == "high"
