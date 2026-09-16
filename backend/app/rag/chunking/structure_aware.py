import re
import hashlib
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class DocumentChunkDto(BaseModel):
    chunk_index: int
    section: str
    subsection: Optional[str] = None
    page: Optional[int] = None
    text: str
    metadata: Dict[str, Any]


class StructureAwareChunker:
    """
    Structure-aware document chunker conforming to Section 8 & 9.
    Splits authoritative institutional and technical documentation into meaningful logical units
    rather than naive, arbitrary fixed-character windows.
    """

    def __init__(self, target_chunk_words: int = 250, overlap_words: int = 30):
        self.target_chunk_words = target_chunk_words
        self.overlap_words = overlap_words

    def chunk_markdown(
        self,
        markdown_text: str,
        doc_metadata: Optional[Dict[str, Any]] = None
    ) -> List[DocumentChunkDto]:
        chunks: List[DocumentChunkDto] = []
        metadata = doc_metadata or {}

        # Split on Markdown headers (# Header 1, ## Header 2, ### Header 3)
        section_pattern = re.compile(r"(^#{1,3}\s+.+$)", re.MULTILINE)
        splits = section_pattern.split(markdown_text)

        current_section = "Introduction"
        current_subsection = None
        chunk_index = 0

        i = 0
        while i < len(splits):
            part = splits[i].strip()
            if not part:
                i += 1
                continue

            if part.startswith("#"):
                # Header encountered
                if part.startswith("###"):
                    current_subsection = part.lstrip("#").strip()
                elif part.startswith("##"):
                    current_section = part.lstrip("#").strip()
                    current_subsection = None
                else:
                    current_section = part.lstrip("#").strip()
                    current_subsection = None
                i += 1
                continue

            # Section body text
            words = part.split()
            if len(words) <= self.target_chunk_words:
                chunks.append(
                    DocumentChunkDto(
                        chunk_index=chunk_index,
                        section=current_section,
                        subsection=current_subsection,
                        text=part,
                        metadata={**metadata, "word_count": len(words)},
                    )
                )
                chunk_index += 1
            else:
                # Sub-chunk with sliding window overlap
                step = self.target_chunk_words - self.overlap_words
                for start in range(0, len(words), step):
                    sub_words = words[start : start + self.target_chunk_words]
                    sub_text = " ".join(sub_words)
                    chunks.append(
                        DocumentChunkDto(
                            chunk_index=chunk_index,
                            section=current_section,
                            subsection=current_subsection,
                            text=sub_text,
                            metadata={**metadata, "word_count": len(sub_words), "sub_chunk": True},
                        )
                    )
                    chunk_index += 1
            i += 1

        return chunks

    @staticmethod
    def calculate_content_hash(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()


structure_chunker = StructureAwareChunker()
