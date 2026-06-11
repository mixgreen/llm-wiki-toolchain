# Ingest Plan Requirements

Date: 2026-06-11
Status: Draft

## Summary

Add an `Ingest Plan` workflow to make source ingestion reviewable before any wiki files are written. The plan should reduce mistaken writes and lower review burden, especially for paper reading, while preserving the current LLM Wiki model: raw sources remain traceable, wiki pages remain curated, and the human stays in control of what gets written.

The workflow is intentionally not a hands-free ingest system. It produces a chat-rendered Markdown report, asks for explicit approval, and only then may the agent proceed with the existing ingest flow.

## Problem

The current ingest workflow is described well in `skills/llm-wiki-toolchain/SKILL.md`, but many important steps depend on the agent following instructions correctly: pre-scanning existing pages, identifying fuzzy matches, detecting source drift, deciding whether to create or update pages, and keeping the human from being overloaded by batch input.

That creates three recurring risks:

- Duplicate or near-duplicate pages are created because existing page matches were not surfaced early.
- Existing pages are silently updated when the match was ambiguous.
- Batch sources overwhelm the user, making review less effective even if the agent technically can process them.

## Goals

- Make ingestion decisions visible before any wiki write happens.
- Keep single-source review as the primary, comfortable path.
- Support batch review without normalizing large, overload-prone workflows.
- Separate deterministic file/page checks from semantic judgment.
- Preserve source traceability through hash, URL, and proposed raw destination.
- Make paper ingestion easier by showing a lightweight paper-specific lens before full ingest.

## Non-Goals

- Do not write or modify wiki files during plan creation.
- Do not save the plan as a wiki artifact.
- Do not perform cross-source synthesis in v1.
- Do not turn the plan tool into paragraph-level RAG, embedding search, chunk reranking, or a literature review system.
- Do not include `archive` as an ingest-time page operation.
- Do not fully archive web pages, download images, or clean attachments during URL review.

## Core Concepts

The canonical vocabulary is defined in `CONTEXT.md`. The most important terms for this feature are:

- `Ingest Plan`: a pre-write review of how one or more sources would change a wiki.
- `Deterministic Plan Skeleton`: the script-generated file/page-level scan.
- `Semantic Plan Review`: the agent-authored interpretation layer.
- `Candidate Knowledge Item`: an extracted Entity, Concept, or Claim.
- `Page Operation`: one of create, update, merge, skip, or needs-confirmation.
- `Plan Approval`: explicit user approval before any wiki write.

## User Flow

### Single Source

Single-source review is the default path.

1. User provides a source: raw file, external local file, URL, or pasted content.
2. The tool/agent creates an `Ingest Plan Report` in chat.
3. The report is source-first: it starts with source identity and readiness, then shows candidate knowledge items and page impact.
4. User chooses one of three outcomes:
   - Proceed with this plan.
   - Narrow the plan.
   - Revise classifications.
5. Only after approval may the agent write raw files, source summary pages, entity pages, concept pages, index entries, and log entries.

### Batch Sources

Batch review is supported but treated as overload-prone.

1. User provides multiple sources.
2. The report becomes page-first when needed, emphasizing impacted pages and review scope.
3. A review is overload-prone when it covers more than five sources or more than ten impacted wiki pages.
4. Overload-prone review must recommend narrowing before proceeding, unless the user explicitly confirms the broad scope.

### Tiny Note Exception

Small user-provided notes may bypass the full plan only when the user explicitly asks for direct capture. Papers, articles, PDFs, URLs, and batch sources do not qualify.

## Report Shape

The default output is a chat-rendered Markdown report. JSON is secondary and exists for tests and automation.

Canonical sections:

1. `Source Summary`
   - Source path or URL.
   - Source type.
   - Source readiness: text-ready, text-extractable, or requires-derived-text.
   - sha256 when available.
   - Source identity result.
   - Proposed raw destination for external sources.

2. `Candidate Knowledge Items`
   - Entities with reason.
   - Concepts with reason.
   - Claims with source excerpt or locator.

3. `Page Impact`
   - Source Summary Page impact.
   - Candidate page operations: create, update, merge, skip, or needs-confirmation.
   - Conservative existing-page matching: exact page stem, exact wikilink, or explicit alias only.

4. `Risks and Confirmations`
   - Source drift.
   - Fuzzy or translated page matches.
   - Overload-prone review.
   - Non-text source limitations.
   - Domain-boundary concerns.

5. `Recommended Next Step`
   - Proceed, narrow, or revise.
   - For overload-prone review, prefer narrowing.

6. `Machine Data`
   - Optional structured data, or emitted separately in JSON mode.

## Source Identity Rules

- Same sha256 means the same source.
- Same URL with a different sha256 means source drift and requires confirmation.
- Similar title or filename is only a weak duplicate hint.
- New external sources may receive a proposed raw destination, but plan creation does not write raw files.

## Source Readiness

- `text-ready`: markdown, txt, or already extracted text.
- `text-extractable`: PDF, docx, URL, or similar source where text extraction may work.
- `requires-derived-text`: image, scan, video, presentation, or other source requiring OCR, transcription, or manual summary.

The plan must not pretend that non-text material has been fully understood unless usable derived text exists.

## Paper Lens

For research papers, the plan should include a lightweight `Paper Lens`:

- Research question.
- Method.
- Main contribution.
- Limitations.
- Follow-up value.

This is not a full paper review and does not replace the eventual Source Summary Page.

## Success Criteria

- User can see all proposed page operations before writing.
- Ambiguous existing-page matches are not silently treated as updates.
- Source drift is surfaced as needs-confirmation.
- Single-source plans fit comfortably in one to two screens for ordinary sources.
- Batch plans warn when the scope exceeds five sources or ten impacted pages.
- Claims in the plan always include an excerpt or locator.
- Approved ingest should produce fewer focused-lint issues than the current instruction-only workflow.

## Open Questions

- What exact CLI name should expose the deterministic skeleton?
- Should JSON mode mirror the Markdown sections exactly or use a more compact schema?
- Should the first implementation live as a new script or as an option on an existing script?
- How should explicit aliases be represented so conservative page matching can use them reliably?

