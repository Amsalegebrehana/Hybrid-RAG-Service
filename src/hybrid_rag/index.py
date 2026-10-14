import logging
import sys

from hybrid_rag.db.store import init_db, replace_chunks
from hybrid_rag.embed.embedder import embedder
from hybrid_rag.ingest.pipeline import ingest_directory

logger = logging.getLogger(__name__)


def index_directory(root: str) -> int:
    init_db()
    chunks = ingest_directory(root)
    if not chunks:
        logger.warning('No chunks found under %s', root)
        return 0
    embeddings = embedder.embed_documents([c.text for c in chunks])
    replace_chunks(chunks, embeddings)
    return len(chunks)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    count = index_directory(sys.argv[1])
    logger.info('Indexed %d chunks', count)
