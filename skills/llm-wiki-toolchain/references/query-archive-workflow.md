# Query Archive Workflow

Query Archive is the workflow for preserving an Archive-Worthy Query as reusable wiki knowledge. It keeps the answer, the evidence path, and the follow-up work visible without turning every chat answer into a page.

V1 is documentation- and template-led. It does not create a separate Query Plan, does not add a script, does not automatically edit Basis Pages, and does not save chat answers into `raw/` by default.

## When to Offer Archive

After answering a wiki query, offer Archive Confirmation when the answer is an Archive-Worthy Query. A query is archive-worthy when any of these are true:

- It reuses multiple wiki pages or raw evidence.
- It produces a reusable synthesis, decision, comparison, or trade-off.
- It is likely to be asked again and would be expensive to re-derive.
- It exposes follow-up work for the wiki.
- The user explicitly asks to keep, remember, or save it.

Do not ask to archive every trivial lookup. If the answer is a simple pointer to one page, answer in chat and stop unless the user asks to preserve it.

## Default Destination

The default destination is `wiki/queries/`.

Use other directories only after an explicit conversion:

- `wiki/concepts/` for a stable concept explanation.
- `wiki/entities/` for entity facts.
- `wiki/comparisons/` for a long-lived comparison matrix.
- `wiki/topics/` for broad topic overviews or source summaries.

A comparison-shaped answer should first become a Query Archive unless the user explicitly asks for a Comparison Upgrade now. Otherwise record the upgrade as a Follow-Up Action.

## Archive Confirmation

Before writing, show a lightweight confirmation. It is not a separate Query Plan.

Include:

- Query Archive Title
- destination, usually `wiki/queries/<title>.md`
- `indexed: true|false`
- `answer_version`
- status and confidence
- Basis Pages
- whether Raw Evidence is required and present
- Follow-Up Actions
- whether this creates a new archive or updates an existing one

Valid user outcomes are proceed, revise, or skip.

## Query Archive Match

Before creating a new page, check `wiki/queries/` for an existing archive.

Update an existing Query Archive when there is:

- exact title match
- explicit alias match
- clearly the same Original Question or Canonical Question

Fuzzy thematic similarity requires confirmation. Related but distinct angles can remain separate pages and link to each other.

## Answer Version

`answer_version` starts at `1`.

Increment it only when new evidence, corrections, or follow-up work materially changes the answer. Formatting, copy edits, typo fixes, and section reordering do not increment it.

When incrementing Answer Version:

- update the current answer in place
- add a Revision Note with date and reason
- note changed Basis Pages or Raw Evidence
- append a Query Log Entry

Do not keep full old answer copies in the page by default. Git history preserves exact older text; the page should explain why the answer changed.

## Evidence Rules

Basis Pages are required for every Query Archive. Each Basis Page should state what it contributed.

Raw Evidence is required when the answer includes:

- strong claims
- disputed judgments
- numeric details
- paper conclusions
- corrections to existing wiki knowledge

Raw Evidence should point to `raw/...` with a section, page, paragraph, or other locator when available.

The normal evidence chain is:

```text
Query Archive -> Basis Pages -> Raw Evidence
```

The workflow does not copy the chat answer into `raw/`.

## Follow-Up Actions

Follow-Up Actions record maintenance work that the query revealed. They are not executed automatically during query archiving.

Allowed states:

- `[open]`
- `[done]`
- `[dropped]`

Examples:

- `[open] Create [[Some Concept]] because this answer depends on it repeatedly.`
- `[open] Run an Ingest Plan for a new source mentioned in this query.`
- `[done] Updated [[Some Entity]] Sources after archiving this answer.`
- `[dropped] No separate comparison page needed after review.`

Do not add owners, due dates, priorities, or project-management metadata.

## Index and Log

Query Archives are indexed by default.

Set `indexed: false` when the page is scratch, private, low-confidence, or the user asks to keep it out of index. Non-indexed pages remain in `wiki/queries/` but are not current navigation entries.

Creating or materially updating a Query Archive requires a Query Log Entry:

```markdown
## [YYYY-MM-DD] query | Query Archive Title
- Created/Updated: [[Query Archive Title]]
- answer_version: 1
- Basis Pages: [[Page A]], [[Page B]]
- Follow-Up Actions: 2 open
```

Formatting-only edits do not need log entries.
