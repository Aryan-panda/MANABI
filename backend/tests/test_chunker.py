import pytest
from app.rag.chunking.structure_aware import StructureAwareChunker, DocumentChunkDto


def test_chunk_markdown_headers():
    chunker = StructureAwareChunker(target_chunk_words=50, overlap_words=10)
    sample_markdown = """# Section 1: Attendance Policy
All students must maintain 75% attendance to sit for examinations.

## Medical Condonation
Students with medical certificates may be condoned between 65% and 75%.

## Severe Shortage
Below 65% attendance is un-condonable and requires course repetition.
"""
    chunks = chunker.chunk_markdown(sample_markdown)
    assert len(chunks) >= 3

    sections = [c.section for c in chunks]
    assert "Attendance Policy" in sections or "Section 1: Attendance Policy" in sections
    assert "Medical Condonation" in sections
    assert "Severe Shortage" in sections

    for c in chunks:
        assert isinstance(c, DocumentChunkDto)
        assert len(c.text) > 0
        assert c.chunk_index >= 0


def test_content_hash():
    text_a = "Sample academic syllabus text"
    text_b = "Sample academic syllabus text"
    text_c = "Different academic text"

    hash_a = StructureAwareChunker.calculate_content_hash(text_a)
    hash_b = StructureAwareChunker.calculate_content_hash(text_b)
    hash_c = StructureAwareChunker.calculate_content_hash(text_c)

    assert hash_a == hash_b
    assert hash_a != hash_c
    assert len(hash_a) == 64  # SHA-256 hex string length
