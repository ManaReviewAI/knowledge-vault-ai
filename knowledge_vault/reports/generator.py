from __future__ import annotations

from knowledge_vault.config.settings import Settings
from knowledge_vault.search.searcher import SearchResult, format_citations


REPORT_SYSTEM_PROMPT = """You are Knowledge Vault AI, a local-first archive assistant.
Use only the provided archive excerpts.
Every factual claim must cite source file names.
Include short relevant excerpts where useful.
If the excerpts do not contain enough evidence, say so clearly.
Do not invent sources, dates, people, places, species, or events."""


def generate_extractive_report(
    user_prompt: str,
    results: list[SearchResult],
    *,
    structured: bool = False,
) -> str:
    """Create a useful, cited report without an LLM or network service."""

    sources = sorted({result.file_name for result in results})
    findings = "\n".join(
        f"- **{result.file_name}, chunk {result.chunk_index}:** {result.excerpt}"
        for result in results[:5]
    )
    evidence = "\n".join(
        f"- {result.file_name}, chunk {result.chunk_index} — “{result.excerpt}”"
        for result in results
    )
    source_lines = "\n".join(f"- {source}" for source in sources)
    heading = "# Knowledge Vault AI Report" if structured else "# Source-Grounded Archive Report"
    return f"""{heading}

> **Report mode:** Evidence-only extractive report. No Ollama-generated interpretation was used.

## Overview
This local extractive report addresses: {user_prompt}

## Key Findings
{findings}

## Evidence Extracts
{evidence}

## Gaps and Uncertainty
This report is assembled directly from the highest-ranked excerpts. Verify important conclusions against the original documents and refine the search if evidence is incomplete.

## Locations Mentioned
Review the cited excerpts for supported locations.

## Timeline
Review the cited excerpts for supported dates and events.

## Source Documents
{source_lines}
"""


def build_report_prompt(user_prompt: str, results: list[SearchResult]) -> str:
    citations = format_citations(results)
    return f"""User report request:
{user_prompt}

Retrieved archive excerpts:
{citations}

Write a structured report with:
1. Executive summary
2. Key findings
3. Source-cited evidence
4. Gaps, uncertainty, or missing evidence
5. Suggested follow-up searches

Remember: cite source file names and include relevant excerpts."""


def build_structured_report_request(topic: str, location: str = "", timeframe: str = "") -> str:
    parts = [f"Topic: {topic.strip()}"]
    if location.strip():
        parts.append(f"Location: {location.strip()}")
    if timeframe.strip():
        parts.append(f"Timeframe: {timeframe.strip()}")
    return "\n".join(parts)


def build_structured_report_prompt(user_prompt: str, results: list[SearchResult]) -> str:
    citations = format_citations(results)
    return f"""Structured report request:
{user_prompt}

Retrieved archive excerpts:
{citations}

Write the report using exactly these sections:

# Title

## Overview
Write a concise AI summary using only the excerpts.

## Key Findings
Use bullet points. Cite file names in every bullet.

## Evidence Extracts
List the strongest evidence with file name and short excerpt.

## Locations Mentioned
List locations if the excerpts support them. If unclear, say "Not clearly identified in retrieved excerpts."

## Timeline
List dated events if dates are detected in the excerpts. If no dates are detected, say "No dated events detected in retrieved excerpts."

## Source Documents
List source file names used.

Every factual claim must include citations using source file names."""


def generate_report(user_prompt: str, results: list[SearchResult], settings: Settings) -> str:
    if not results:
        return "No relevant archive excerpts were found, so no grounded report can be generated."

    if settings.report_backend.lower().strip() == "extractive":
        return generate_extractive_report(user_prompt, results)
    response = _try_ollama(build_report_prompt(user_prompt, results), settings)
    if response:
        return f"> **Report mode:** Ollama-generated report using `{settings.ollama_model}`.\n\n{response}"
    return generate_extractive_report(user_prompt, results)


def generate_structured_report(user_prompt: str, results: list[SearchResult], settings: Settings) -> str:
    if not results:
        return "No relevant archive excerpts were found, so no grounded report can be generated."

    if settings.report_backend.lower().strip() == "extractive":
        return generate_extractive_report(user_prompt, results, structured=True)
    response = _try_ollama(build_structured_report_prompt(user_prompt, results), settings)
    if response:
        return f"> **Report mode:** Ollama-generated report using `{settings.ollama_model}`.\n\n{response}"
    return generate_extractive_report(user_prompt, results, structured=True)


def _try_ollama(prompt: str, settings: Settings) -> str | None:
    if settings.report_backend.lower().strip() not in {"auto", "ollama"}:
        return None
    try:
        import ollama

        client = ollama.Client(host=settings.ollama_base_url)
        response = client.chat(
            model=settings.ollama_model,
            messages=[
                {"role": "system", "content": REPORT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        return str(response["message"]["content"])
    except (ImportError, KeyError, OSError, RuntimeError):
        return None
    except Exception:
        # Client and connection exception types vary between Ollama releases.
        return None
