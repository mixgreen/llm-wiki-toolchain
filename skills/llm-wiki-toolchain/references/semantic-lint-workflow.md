# Semantic Lint Workflow

Semantic Lint is an LLM-assisted knowledge health review for an LLM Wiki. It surfaces possible semantic issues as structured confirmation candidates, without turning uncertain judgment into deterministic lint errors.

V1 is documentation- and template-led. It does not add `semantic_lint.py`, does not add `lint.py --semantic`, and does not create semantic exit-code behavior. Mechanical `lint.py` output can guide review, but Semantic Lint findings require content reading and human confirmation.

## Scope

Use the narrowest scope that can answer the user's question.

- **Focused Semantic Lint**: default. Review specified pages, recently touched pages, or a small set of pages suggested by mechanical lint.
- **Topic Semantic Lint**: review a topic, tag, concept cluster, or index section.
- **Wiki-Wide Semantic Lint**: review the whole wiki only for small wikis or explicit user requests. Warn that this is overload-prone and suggest narrowing before proceeding.

## Mechanical Lint Signal

Mechanical Lint Signal is input evidence from deterministic checks, not a semantic conclusion.

Useful signals include:

- stale pages from `--stale`
- oversized pages from size checks
- broken links
- missing or invalid quality fields
- `contested: true` pages
- tag taxonomy drift
- index, log, or topic-map consistency issues

Do not rewrite these as Semantic Lint Findings until you read the affected content. A Stale Page means the `updated` date is older than the configured threshold. A Stale Claim Candidate means a specific claim may be superseded by newer evidence.

## Finding Taxonomy

Semantic Lint V1 uses exactly these finding types:

- **Contradiction Candidate**: pages, or parts of one page, appear to make incompatible claims, definitions, numbers, or status judgments.
- **Missing Page Candidate**: an entity or concept is important enough for the wiki but lacks its own page.
- **Stale Claim Candidate**: an existing claim may have been superseded by newer sources, recent log entries, or updated source summaries.
- **Weak Evidence Candidate**: a strong or consequential claim lacks adequate Basis Pages, Raw Evidence, or paragraph-level provenance.
- **Index Summary Drift**: an `index.md` summary no longer matches the current page content or has become misleading.
- **Overgrown Page Candidate**: a page has accumulated multiple semantic topics or responsibilities and may need splitting, restructuring, or conversion to a different page type.

Avoid broad labels such as "bad page" or "needs cleanup". If the issue does not fit the taxonomy, report it in Summary as an observation instead of inventing a new type.

## Finding Shape

Every Semantic Lint Finding must include:

```yaml
type: Contradiction Candidate | Missing Page Candidate | Stale Claim Candidate | Weak Evidence Candidate | Index Summary Drift | Overgrown Page Candidate
title: short finding title
affected_pages:
  - wiki/path/Page.md
evidence:
  - page, section, quote summary, raw locator, or log clue
confidence: low | medium | high
severity: low | medium | high
recommended_action: update page | create page | add evidence | split page | update index | run ingest plan | query archive | dismiss
rationale: why this is a knowledge health issue if confirmed
confirmation_question: the specific question a user or reviewer must answer
```

`confidence` and `severity` are separate:

- `confidence` asks how reliable the finding is.
- `severity` asks how much wiki quality is affected if the finding is true.

A high-severity finding can have low confidence. Keep it visible, but phrase it as a question to confirm.

## Report Shape

Semantic Lint Reports are chat-first and ephemeral by default. Do not save them as wiki pages unless the user explicitly asks, or the analysis itself becomes a reusable Query Archive.

Use this structure:

```markdown
## Summary

- Scope:
- Pages reviewed:
- Mechanical Lint Signal used:
- Overall result:

## High Severity Findings

### <type>: <title>
- affected_pages:
- evidence:
- confidence:
- severity:
- recommended_action:
- rationale:
- confirmation_question:

## Medium / Low Severity Findings

### <type>: <title>
- affected_pages:
- evidence:
- confidence:
- severity:
- recommended_action:
- rationale:
- confirmation_question:

## Confirmation Queue

1. <question>
2. <question>

## Suggested Maintenance Actions

- [ ] <action after confirmation>

## Machine Data

Optional JSON-like mirror for tools or follow-up automation.
```

Omit empty severity sections. Keep the Confirmation Queue short enough for the user to answer.

## No Auto-Fix

Semantic Lint does not modify wiki pages automatically. It outputs confirmation candidates.

Confirmed findings may route into normal maintenance workflows:

- update a page
- create a page
- add Raw Evidence or paragraph-level provenance
- split an overgrown page
- update `index.md`
- run an Ingest Plan for a source
- archive reusable analysis as a Query Archive
- dismiss the finding

Query Archive is optional follow-up only. Do not auto-create Query Archives for ordinary findings; use it when the Semantic Lint analysis is itself likely to be reused as an answer to a recurring question.

## Minimal Procedure

1. Align with `SCHEMA.md`, `index.md`, and recent `log.md`.
2. Choose Focused, Topic, or Wiki-Wide scope.
3. Optionally run or read `lint.py` output as Mechanical Lint Signal.
4. Read the affected pages and relevant raw evidence or source summaries.
5. Produce Semantic Lint Findings using the required shape.
6. Group findings into the report structure.
7. Ask the Confirmation Queue before doing any wiki maintenance.

When the scope is large, prefer two or three high-signal findings over a long uncertain list.
