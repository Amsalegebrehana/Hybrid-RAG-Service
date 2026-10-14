import logging
from pathlib import Path

from hybrid_rag.ingest.chunker import Chunk, chunker
from hybrid_rag.ingest.ingest import Cleaner, FileLoader, MDFileCleaner, TXTFileCleaner

logger = logging.getLogger(__name__)

CLEANERS: dict[str, type[Cleaner]] = {
    '.md': MDFileCleaner,
    '.txt': TXTFileCleaner,
}


def ingest_directory(root: str | Path) -> list[Chunk]:

    root = Path(root)
    chunks: list[Chunk] = []
    
    for path in sorted(root.rglob('*')):
        cleaner_cls = CLEANERS.get(path.suffix.lower())
        if cleaner_cls is None or not path.is_file():
            continue

        file = FileLoader(path).load()
        source = path.relative_to(root).as_posix()
        try:
            text = cleaner_cls(file.content).clean()

        except UnicodeDecodeError:
            logger.warning('Skipping %s: not valid UTF-8', source)

            continue

        file_chunks = chunker.chunk(text, source)
        if not file_chunks:
            logger.warning('Skipping %s: no text after cleaning', source)
            continue
        chunks.extend(file_chunks) 
    return chunks 
 