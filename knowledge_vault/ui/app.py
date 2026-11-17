from __future__ import annotations

import re

import streamlit as st

from knowledge_vault.config.settings import settings
from knowledge_vault.indexing.embeddings import build_embedder
from knowledge_vault.ingestion.loaders import SUPPORTED_EXTENSIONS, discover_files
from knowledge_vault.pipeline import rebuild_index
from knowledge_vault.reports.docx_export import build_report_docx, safe_report_filename
from knowledge_vault.reports.generator import (
    build_structured_report_request,
    generate_report,
    generate_structured_report,
)
from knowledge_vault.search.searcher import semantic_search


st.set_page_config(page_title="Knowledge Vault AI", layout="wide")


@st.cache_resource(show_spinner=False)
def cached_embedder():
    return build_embedder(settings)


def render_sources(results):
    for result in results:
        with st.expander(f"{result.file_name} | chunk {result.chunk_index} | score {result.score:.3f}"):
            st.write(result.excerpt)


def detect_dates(results):
    date_pattern = re.compile(r"\b(?:18|19|20)\d{2}\b|\b\d{1,2}\s+[A-Z][a-z]+\s+(?:18|19|20)\d{2}\b")
    dates = []
    for result in results:
        for match in date_pattern.findall(result.excerpt):
            dates.append((match, result.file_name, result.excerpt))
    return dates


def detect_locations(results, requested_location):
    locations = []
    if requested_location.strip():
        locations.append(requested_location.strip())

    place_pattern = re.compile(
        r"\b(?:Lake|Mount|Mt|River|Te|Port|North|South|East|West)\s+[A-Z][A-Za-z-]*(?:\s+[A-Z][A-Za-z-]*)?\b"
    )
    for result in results:
        locations.extend(place_pattern.findall(result.excerpt))

    return sorted(set(locations))


def render_report_evidence(results, requested_location):
    st.subheader("Evidence Extracts")
    if results:
        render_sources(results)
    else:
        st.warning("No evidence extracts found.")

    locations = detect_locations(results, requested_location)
    st.subheader("Locations Mentioned")
    if locations:
        for location in locations:
            st.write(f"- {location}")
    else:
        st.write("Not clearly identified in retrieved excerpts.")

    dates = detect_dates(results)
    st.subheader("Timeline")
    if dates:
        for date, file_name, excerpt in dates:
            st.write(f"- {date} | {file_name}: {excerpt}")
    else:
        st.write("No dated events detected in retrieved excerpts.")

    st.subheader("Source Documents")
    for file_name in sorted({result.file_name for result in results}):
        st.write(f"- {file_name}")


st.title("Knowledge Vault AI")
st.caption("Local-first archive search and report generation for private document collections.")

with st.sidebar:
    st.header("Local Archive")
    st.write(f"Data folder: `{settings.data_dir}`")
    st.write(f"Vector DB: `{settings.db_dir}`")
    st.write(f"Embedding backend: `{settings.embedding_backend}`")
    st.write(f"Report backend: `{settings.report_backend}`")
    if settings.report_backend in {"auto", "ollama"}:
        st.write(f"Ollama model: `{settings.ollama_model}`")
    st.divider()
    files = discover_files(settings.data_dir)
    st.metric("Supported files found", len(files))
    st.write(", ".join(sorted(SUPPORTED_EXTENSIONS)))
    if st.button("Ingest / Rebuild Index", type="primary"):
        with st.spinner("Reading files, chunking text, and rebuilding the local index..."):
            summary = rebuild_index(settings)
        st.success(f"Indexed {summary.documents} documents into {summary.chunks} chunks.")

tab_search, tab_generate, tab_reports, tab_examples = st.tabs(
    ["Search", "Generate Report", "Freeform Report", "Example Prompts"]
)

with tab_search:
    st.subheader("Semantic Search")
    query = st.text_input("Search your archive", placeholder="wetland restoration evidence")
    limit = st.slider("Results", min_value=3, max_value=20, value=settings.search_results)
    if st.button("Search", disabled=not query.strip()):
        with st.spinner("Searching local vector index..."):
            results = semantic_search(query, cached_embedder(), settings, limit=limit)
        if not results:
            st.warning("No results found. Try ingesting documents first.")
        else:
            render_sources(results)

with tab_generate:
    st.subheader("Generate Report")
    topic = st.text_input("Topic", placeholder="birds mentioned in the archive")
    location = st.text_input("Location (optional)", placeholder="Lake Rotoiti")
    timeframe = st.text_input("Timeframe (optional)", placeholder="1990 to 2020")
    report_limit = st.slider(
        "Evidence excerpts to retrieve",
        min_value=4,
        max_value=20,
        value=10,
        key="structured_report_limit",
    )

    if st.button("Generate Report", type="primary", disabled=not topic.strip(), key="structured_report_button"):
        report_request = build_structured_report_request(topic, location, timeframe)
        search_query = " ".join(part for part in [topic, location, timeframe] if part.strip())

        with st.spinner("Retrieving evidence and generating a cited local report..."):
            results = semantic_search(search_query, cached_embedder(), settings, limit=report_limit)
            report = generate_structured_report(report_request, results, settings)

        st.session_state["structured_report"] = report
        st.session_state["structured_results"] = results
        st.session_state["structured_topic"] = topic
        st.session_state["structured_location"] = location

    if "structured_report" in st.session_state:
        st.markdown(st.session_state["structured_report"])
        st.download_button(
            "Download as .docx",
            data=build_report_docx(
                st.session_state["structured_report"],
                st.session_state.get("structured_results", []),
            ),
            file_name=safe_report_filename(st.session_state.get("structured_topic", "archive")),
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        st.divider()
        render_report_evidence(
            st.session_state.get("structured_results", []),
            st.session_state.get("structured_location", ""),
        )

with tab_reports:
    st.subheader("Generate Freeform Source-Grounded Report")
    prompt = st.text_area(
        "Report prompt",
        height=140,
        placeholder="Generate a report on all birds mentioned in the archive.",
    )
    report_limit = st.slider("Evidence excerpts to retrieve", min_value=4, max_value=20, value=10)
    if st.button("Generate Report", disabled=not prompt.strip()):
        with st.spinner("Retrieving evidence and generating a local report..."):
            results = semantic_search(prompt, cached_embedder(), settings, limit=report_limit)
            report = generate_report(prompt, results, settings)
        st.markdown(report)
        st.divider()
        st.subheader("Retrieved Sources")
        render_sources(results)

with tab_examples:
    st.subheader("Try These")
    st.markdown(
        """
- Generate a report on all birds mentioned in the archive.
- Generate a report on references to Lake Rotoiti between 1990 and 2020.
- Create a timeline of evidence relating to wetland restoration.
- List all documents mentioning kereru.
- List all documents mentioning a named person, place, species, or topic.
"""
    )
    st.info(
        "Privacy: files, extracted text, embeddings, and reports stay local unless you deliberately connect an external model."
    )
