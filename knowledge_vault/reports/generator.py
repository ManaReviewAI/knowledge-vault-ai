from __future__ import annotations

import ollama

from knowledge_vault.config.settings import Settings
from knowledge_vault.search.searcher import SearchResult, format_citations


REPORT_SYSTEM_PROMPT = """You are Knowledge Vault AI, a local-first archive assistant.
Use only the provided archive excerpts.
Every factual claim must cite source file names.
Include short relevant excerpts where useful.
If the excerpts do not contain enough evidence, say so clearly.
Do not invent sources, dates, people, places, species, or events."""


def ollama_unavailable_report(settings: Settings, results: list[SearchResult]) -> str:
    sources = sorted({result.file_name for result in results})
    source_lines = "\n".join(f"- {source}" for source in sources) or "- No source documents found."
    return f"""# AI Summary Unavailable

## Overview
AI summary is unavailable because the configured Ollama model `{settings.ollama_model}` is not installed or Ollama is not reachable.

## Key Findings
- Evidence excerpts were still retrieved from the local archive.
- Review the Evidence Extracts section below for cited source material.

## Evidence Extracts
The UI displays retrieved excerpts with file names and chunk numbers below this message.

## Locations Mentioned
Review the retrieved excerpts below for supported locations.

## Timeline
Review the retrieved excerpts below for dated evidence.

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

    try:
        client = ollama.Client(host=settings.ollama_base_url)
        response = client.chat(
            model=settings.ollama_model,
            messages=[
                {"role": "system", "content": REPORT_SYSTEM_PROMPT},
                {"role": "user", "content": build_report_prompt(user_prompt, results)},
            ],
        )
        return response["message"]["content"]
    except ollama.ResponseError:
        return ollama_unavailable_report(settings, results)
    except ollama.RequestError:
        return ollama_unavailable_report(settings, results)


def generate_structured_report(user_prompt: str, results: list[SearchResult], settings: Settings) -> str:
    if not results:
        return "No relevant archive excerpts were found, so no grounded report can be generated."

    try:
        client = ollama.Client(host=settings.ollama_base_url)
        response = client.chat(
            model=settings.ollama_model,
            messages=[
                {"role": "system", "content": REPORT_SYSTEM_PROMPT},
                {"role": "user", "content": build_structured_report_prompt(user_prompt, results)},
            ],
        )
        return response["message"]["content"]
    except ollama.ResponseError:
        return ollama_unavailable_report(settings, results)
    except ollama.RequestError:
        return ollama_unavailable_report(settings, results)
