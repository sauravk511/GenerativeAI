# Copilot instructions for this repository

Purpose: Help AI code agents become productive quickly with this small RAG (retrieval-augmented generation) Streamlit app that ingests PDFs and answers questions using Groq/LLM and FAISS vectors.

Quick links
- Main app: `4-RAG Document Q&A/app.py`
- Data directory: `4-RAG Document Q&A/research_papers/` (contains PDFs to ingest)
- Dependencies: `requirements.txt`

How to run locally (macOS, Linux)
1. Create & activate a virtual environment:
   - python -m venv .venv
   - source .venv/bin/activate
2. Install dependencies: `pip install -r requirements.txt`
3. Provide API keys in a `.env` (root) file with these names:
   - `OPENAI_API_KEY` (used by OpenAI embeddings)
   - `GROQ_API_KEY` (used by `langchain_groq.ChatGroq`)
4. Start the app (note folder name contains spaces):
   - cd "4-RAG Document Q&A" && streamlit run app.py

What this repo does (big picture)
- Small Streamlit app that:
  - Loads PDFs from `research_papers/` using `PyPDFDirectoryLoader`
  - Splits documents via `RecursiveCharacterTextSplitter` (chunk_size=1000, overlap=200)
  - Creates embeddings with `OpenAIEmbeddings` and stores vectors in FAISS
  - Creates a retrieval chain with `create_retrieval_chain` + an LLM (`ChatGroq` with model `Llama3-8b-8192`) and answers user queries

Important implementation details / patterns to preserve
- app.py relies on `st.session_state` keys:
  - `embeddings`, `loader`, `docs`, `text_splitter`, `final_documents`, `vectors`.
  - The `create_vector_embedding()` helper initializes these values and is triggered from the UI (`st.button("Document Embedding")`).
- Document pipeline currently only uses the first 50 loaded PDFs before splitting: `st.session_state.docs[:50]`.
- Prompt template is defined inline with `ChatPromptTemplate.from_template` and used with `create_stuff_documents_chain`.
- The vector store and retriever are constructed with FAISS: `FAISS.from_documents(...).as_retriever()`.

Repository conventions and gotchas
- Paths are relative to the app directory; `PyPDFDirectoryLoader("research_papers")` expects the `research_papers/` dir next to `app.py`.
- The top-level folder name `4-RAG Document Q&A` contains spaces and `&`-like characters — quote paths when using the shell.
- No test suite or CI files discovered; changes should be validated manually by running the Streamlit UI and verifying vector creation + retrieval.

Common fixes or small improvements (explicit, local to repo)
- Add explicit checks for required env vars and fail fast with a clear error message (app currently sets env vars silently from `.env`).
- Add a CLI/flag to change `chunk_size`, `chunk_overlap`, and the document limit (currently hard-coded)
- Make `research_papers/` path configurable or detect missing/empty data directory and show a helpful Streamlit message.

Where to look when making changes
- `4-RAG Document Q&A/app.py` — core logic and UX
- `requirements.txt` — when adding dependencies, keep it minimal and check compatibility (FAISS vs faiss-cpu etc.)

If you add features
- Keep changes small and test by running `streamlit run app.py` and confirming that the "Document Embedding" button builds FAISS and queries produce answers with the expected context shown in the expander.
- Update the instructions here if you add a script/Makefile/CI workflow, or introduce tests.

Questions for the repo owner (if unclear)
- Should the document ingestion be automatic on first run or remain manual via the button?
- Any preferred constraints on the number of documents / memory footprint we should enforce?

Contact / intent
- If you want edits to this guide, tell me which areas you want more detail on (running examples, a sample `.env`, or suggested tests) and I will iterate.
