# Multi-RAG Multimodal with Reflexive Orchestration for the Argentine Energy Sector

Multimodal Multi-RAG architecture with reflexive orchestration for knowledge management in high-complexity domains. Applied to the Argentine regulated energy sector (ENRE, CAMMESA, RenovAr).

## What is this?

A specialized information-retrieval system that organizes knowledge across four domains —legal, tax, financial and accounting— of the energy sector into independent modules (silos), coordinated by a reflexive component that detects its own uncertainty.

Unlike a traditional monolithic RAG, this architecture:
- Segregates semantic domains into independent vector indexes
- Implements an **epistemic veto** when the evidence is insufficient
- Mitigates **cognitive offloading** through intentional friction
- Produces full **traceability** for every decision

## Tech stack

- **Ingestion:** Docling (multimodal, all formats); RAPTOR + ColPali → planned (financial silo)
- **Chunking:** structure-aware via Docling (native section hierarchy; tables kept atomic)
- **Memory / Vector DB:** PostgreSQL + pgvector (vectors + graph + ledger in a single database)
- **Embeddings:** sentence-transformers (`BAAI/bge-m3`, 1024d)
- **Generation:** LiteLLM (swappable model: Claude / Gemini / local via Ollama)
- **Orchestration:** LangGraph (planned)
- **Evaluation / veto:** RAGAS + conformal prediction (planned)

## Status

🚧 Work in progress — Master's thesis, Data Mining & Knowledge Management, Universidad Austral.

**Base pipeline working** ✅: ingestion → Docling structure-aware chunking → embeddings → PostgreSQL/pgvector → cosine retrieval → **citation-grounded generation** (answers grounded in evidence, citing the source and abstaining when the context is insufficient). **Next:** kNN silo router, multi-signal veto, Golden Dataset + experiment.

## Notes

This system operates over a **Spanish-language** regulatory corpus. The codebase and public documentation here are in English for an international audience. The detailed thesis design documents are maintained privately in Spanish, as they belong to a thesis defended in Spanish.

**Author:** Lucas Brusasca
**Advisor:** Hernán Merlino