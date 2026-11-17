# Knowledge Vault AI

[![CI and Release](https://github.com/ManaReviewAI/knowledge-vault-ai/actions/workflows/ci-release.yml/badge.svg)](https://github.com/ManaReviewAI/knowledge-vault-ai/actions/workflows/ci-release.yml)

Knowledge Vault AI is an open-source, local-first knowledge archive framework for indexing and searching private document collections.

It is designed as a lightweight MVP for small organisations, researchers, CEOs, iwi/hapu entities, legal teams, and community archives that need to work with PDFs, Word documents, text files, CSVs, Markdown files, transcripts, evidence bundles, and related archive material without sending data to the cloud.

This giveaway edition is intentionally simple. It does not include proprietary Mana Review AI cultural assessment logic, compliance workflows, client dashboards, Indigenous data sovereignty contract automation, GIS integration, or council reporting modules.

## What It Does

- Reads files from a local `data/` folder.
- Ingests `.pdf`, `.docx`, `.txt`, `.csv`, and `.md` files.
- Extracts text and basic metadata.
- Splits documents into searchable chunks.
- Stores embeddings in a local ChromaDB vector database.
- Uses a lightweight deterministic local embedder by default, with no model download.
- Supports optional SentenceTransformers and Ollama embeddings.
- Generates useful extractive reports offline and automatically uses Ollama when available.
- Provides semantic search with source file citations and excerpts.
- Generates structured reports from archive search results.
- Provides a guided report UI with topic, optional location, optional timeframe, cited evidence, and `.docx` download.
- Keeps data local by default.

## Privacy Statement

All archive files, extracted text, embeddings, vector indexes, search queries, and generated outputs remain on your own machine by default.

Knowledge Vault AI has no required cloud dependency. It only connects to an external service if you deliberately modify the configuration or code to use one. If you connect an external model or API, you are responsible for understanding what data is sent to that provider.

For sensitive archives, run this tool on a trusted local machine, review access controls, and keep backups of the `data/` and `vault_db/` folders.

## MVP Architecture

```text
knowledge-vault-ai/
  data/                  # User documents and sample dummy documents
  vault_db/              # Local ChromaDB index, created at runtime
  knowledge_vault/
    config/              # Settings and defaults
    ingestion/           # File discovery and text extraction
    indexing/            # Chunking, embeddings, and vector store writes
    search/              # Semantic search and citations
    reports/             # Report prompt templates and Ollama generation
    ui/                  # Streamlit web UI
  scripts/               # CLI helpers
```

## Requirements

- Python 3.10+

Ollama is optional. Without it, Knowledge Vault AI produces local extractive reports from retrieved evidence. To enable LLM-written reports, install the optional integration and pull a model:

```bash
pip install -e .[ollama]
ollama pull qwen3:0.6b
```

## Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

On macOS or Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run The Web UI

```bash
python -m streamlit run knowledge_vault/ui/app.py
```

Then open the local URL shown by Streamlit, usually:

```text
http://localhost:8501
```

### Windows one-command installation

The included installer keeps the virtual environment in a short, stable location under `%LOCALAPPDATA%`, avoiding legacy Windows path-length failures:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_windows.ps1
```

## Add Your Own Documents

Place files in:

```text
data/
```

The `data/` folder is ignored by Git so private archive files are not accidentally published. Harmless demo files are provided in `sample_data/`; copy them into `data/` if you want a quick test archive.

Supported MVP file types:

- PDF
- DOCX
- TXT
- CSV
- Markdown

Then use the UI button **Ingest / Rebuild Index**.

## CLI Usage

Rebuild the local index:

```bash
python scripts/ingest.py
```

Run a semantic search:

```bash
python scripts/search.py "birds mentioned in the archive"
```

Generate a local report. This works offline and uses Ollama automatically when configured:

```bash
python scripts/report.py "Generate a report on all birds mentioned in the archive."
```

In the web UI, use the **Generate Report** tab for a first-pass structured report. It retrieves top archive chunks, generates a cited local report, displays evidence extracts, detects simple locations and dates from retrieved excerpts, and can download the report as a Word `.docx` file.

## Example Prompts

- Generate a report on all birds mentioned in the archive.
- Generate a report on references to Lake Rotoiti between 1990 and 2020.
- Create a timeline of evidence relating to wetland restoration.
- List all documents mentioning kereru.
- List all documents mentioning a named person, place, species, or topic.
- Summarise evidence that supports and contradicts a claim.
- Identify recurring dates, locations, and people in the search results.

## Citation Behaviour

Every search result and report is grounded in retrieved archive chunks. The UI shows:

- Source file name
- Chunk number
- Relevance score
- Excerpt

Report prompts instruct the local LLM to cite source file names and quote relevant excerpts. As with any LLM system, users should verify important claims against the original documents.

## Configuration

Defaults live in `knowledge_vault/config/settings.py`.

Useful environment variables:

```bash
KV_DATA_DIR=data
KV_DB_DIR=vault_db
KV_COLLECTION=knowledge_vault
KV_EMBEDDING_BACKEND=local
KV_SENTENCE_MODEL=all-MiniLM-L6-v2
KV_REPORT_BACKEND=auto
KV_OLLAMA_BASE_URL=http://localhost:11434
KV_OLLAMA_MODEL=qwen3:0.6b
KV_OLLAMA_EMBED_MODEL=nomic-embed-text
```

Embedding backends:

- `local` is the default and needs no model or network access.
- `sentence_transformers` uses a local SentenceTransformers model after `pip install -e .[ml]`.
- `ollama` uses Ollama embeddings after `pip install -e .[ollama]`.

Report backends:

- `auto` uses Ollama when available and otherwise produces an extractive report.
- `extractive` always produces an offline evidence report.
- `ollama` requests the configured Ollama model and falls back safely if it is unavailable.

## Downloads and automated checks

Download the tested release from the [GitHub Releases page](https://github.com/ManaReviewAI/knowledge-vault-ai/releases). Every push and pull request is checked on Python 3.10 and 3.12. The release contains a source ZIP, source archive, and installable Python wheel.

## Limitations

This MVP is intentionally lightweight:

- PDF extraction is text-based and may not handle scanned documents without OCR.
- Image, map, and photo metadata extraction is not included in the MVP.
- No user accounts, permissions, or multi-user dashboard.
- No automated legal privilege workflow.
- No cultural assessment workflow.
- No GIS integration.
- No production-grade audit logs.
- No advanced deduplication.
- No document-level redaction tools.
- No guarantee that generated summaries are complete or legally reliable.

Use this as a local archive assistant, not as a replacement for professional review.

## Example Use Cases

- A researcher indexes interview transcripts, field notes, and reports.
- A small legal team searches evidence bundles and generates first-pass issue summaries.
- A community archive finds references to species, places, people, and dates.
- A CEO searches board papers, memos, and strategy documents locally.
- An iwi or hapu entity explores a private collection while keeping files on a local machine.

## Roadmap

Near-term open-source next steps:

1. Add OCR for scanned PDFs.
2. Add image and EXIF metadata extraction.
3. Add better CSV table summarisation.
4. Add document preview and direct file-opening links.
5. Add incremental indexing instead of full rebuilds.
6. Add export to Markdown, DOCX, and PDF.
7. Add local authentication for shared office machines.
8. Add evaluation tests for citation quality.
9. Add Docker Compose for reproducible local deployment.

Commercial or specialised extensions should be kept separate from this giveaway MVP.
