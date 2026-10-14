from dataclasses import dataclass

from langchain_text_splitters import RecursiveCharacterTextSplitter

from hybrid_rag.core.config import settings


@dataclass
class Chunk:
    source: str
    chunk_index: int
    text: str


class Chunker:
    def __init__(self, chunk_size: int, chunk_overlap: int):
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    def chunk(self, text: str, source: str) -> list[Chunk]:
        return [
            Chunk(source=source, chunk_index=i, text=piece)
            for i, piece in enumerate(self.text_splitter.split_text(text))
        ]


chunker = Chunker(settings.chunk_size, settings.chunk_overlap)
