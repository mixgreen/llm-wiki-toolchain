# Ingest Plan Workflow

Ingest Plan is the default pre-write gate for meaningful source ingestion. It is a plan/report only: it must not create, update, archive, delete, or overwrite any `raw/` or `wiki/` file.

Use it for papers, articles, PDFs, URLs, external files, and batch sources. The only exception is the Tiny Note Exception: a small pasted note may be captured directly when the user explicitly asks for direct capture. Papers, articles, PDFs, URLs, and batch sources cannot use that exception.

## Two-Layer Review

### Deterministic Plan Skeleton

Run the script first when local source inputs are available:

```bash
python3 <SKILL_DIR>/scripts/ingest_plan.py "<wiki-root>" "<source>" [more sources]
```

Use `--json` only for tests or automation:

```bash
python3 <SKILL_DIR>/scripts/ingest_plan.py "<wiki-root>" "<source>" --json
```

The script owns file/page facts only:

- source type and readiness
- source body hash when available
- proposed sha256 sidecar path for binary raw files such as PDFs
- existing raw identity, including Source Drift
- proposed Raw Destination
- current page inventory
- conservative Source Summary Page impact
- overload-prone review flag

It does not extract final Entity, Concept, or Claim items. It renders placeholders so the agent can complete Semantic Plan Review in chat.

### Semantic Plan Review

After the skeleton, the agent reads the source and completes the report. Candidate Knowledge Items are limited to:

- Entity: name, reason, proposed operation
- Concept: name, reason, proposed operation
- Claim: claim text, excerpt or locator, proposed operation

Claims require an excerpt or locator. Entity and Concept candidates require a reason.

## Page Operations

Allowed operations:

- `create`
- `update`
- `merge`
- `skip`
- `needs-confirmation`

`archive` is not an Ingest Plan operation. Archive remains a separate maintenance workflow after explicit user approval.

Existing Page Match is conservative. Automatic update matches are allowed only for:

- exact page stem
- exact `[[wikilink]]`
- explicit alias in frontmatter

Spacing differences, translation differences, case-only similarity, filename similarity, and fuzzy matches require confirmation.

## Source Identity

Treat source identity as follows:

- Same `sha256`: same source.
- Same `source_url` plus different `sha256`: Source Drift, confirmation required.
- Similar filenames: weak duplicate hint only, confirmation required.
- URL without extracted text/hash: source is not identity-complete yet.

External sources may receive a proposed Raw Destination, but the plan must not write it.

Binary raw files use adjacent hash sidecars instead of YAML frontmatter. For example, an approved ingest of `raw/papers/example.pdf` should also write `raw/papers/example.pdf.sha256`, whose first non-comment line is the sha256 of the entire PDF file.

## Source Readiness

- `text-ready`: can be read directly as text or Markdown.
- `text-extractable`: requires extraction, such as PDF, HTML, docx, or URL.
- `requires-derived-text`: image, audio, video, slide deck, or other source needing a derived text layer before semantic review.

For `requires-derived-text`, report the limitation clearly and ask whether to derive text before continuing.

## Report Shape

The chat report should keep this section order:

1. Source Summary
2. Candidate Knowledge Items
3. Page Impact
4. Risks and Confirmations
5. Recommended Next Step
6. Machine Data, optional

Single-source reports should be source-first and short enough to review comfortably. Batch reports should warn when they cover more than five sources or more than ten impacted pages.

For research papers, include a Paper Lens:

- research question
- method
- main contribution
- limitations
- follow-up value

## Approval Boundary

After presenting the report, ask the user to choose:

- proceed: execute the approved ingest workflow
- narrow: reduce source or page scope
- revise: correct classifications, matches, or operations

Do not write to `raw/`, `wiki/`, `index.md`, or `log.md` until the user explicitly approves the plan.

Ingest Plan v1 explains Source-to-Wiki Impact only. It must not perform cross-source synthesis or literature review.
