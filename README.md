<!-- Hybrid RAG Application -->

This is a hybrid retrieval-augmented generation (RAG) application. It uses a combination of vector search and BM25 to retrieve relevant passages from a Postgres database, reranks them with a cross-encoder, and generates responses using a large language model (LLM) with cited context.