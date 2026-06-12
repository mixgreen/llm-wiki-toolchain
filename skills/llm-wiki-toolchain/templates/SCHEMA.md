# Wiki Schema — <WIKI_NAME>

> This document defines the conventions for this LLM Wiki instance.
> The LLM agent reads this on every session to understand how to operate.
> Co-evolve this with the agent as you discover what works.

## Domain

<Topic description — what this wiki is about, scope, boundaries>

## Directory Structure

```
<wiki-root>/
├── raw/                      # Immutable source documents; every file requires sha256 metadata when possible
├── wiki/
│   ├── entities/             # People, organizations, products, ion species, etc.
│   ├── concepts/             # Ideas, theories, frameworks, techniques
│   ├── topics/               # Broader synthesis pages, source summaries, domain overviews
│   ├── comparisons/          # Side-by-side analyses and trade-off comparisons
│   ├── readings/             # Detailed reading guides for papers, long articles, and reports
│   └── queries/              # Filed query results worth preserving
├── _archive/                 # Archived wiki pages; ignored by lint unless explicitly included
├── _meta/
│   └── topic-map.md          # Human-friendly navigation by theme/route/question
├── index.md                  # Full catalog of current wiki pages
├── log.md                    # Current-year activity log; rotated by year and 500-entry limit
└── SCHEMA.md                 # This file
```

## Raw Source Policy

- `raw/` is immutable. Do not silently overwrite raw source files.
- Every raw file should carry or be accompanied by `sha256` metadata.
- Re-ingesting a source requires recomputing the hash.
- If the hash changes, treat it as source drift and ask whether to create a new version or update wiki pages.
- For derived readable versions (for example PDF → Markdown or source code → readable Markdown), preserve the original file and the derived file; record provenance between them.

Recommended raw frontmatter for text-like raw files:

```yaml
---
source_url: ""
source_type: article | paper | book_chapter | note | code | pdf | other
ingested: YYYY-MM-DD
sha256: <hex digest of body content>
---
```

## Page Conventions

### All Current Wiki Pages

- Use Obsidian `[[wikilinks]]` for cross-references.
- Include YAML frontmatter with at minimum: `tags`, `created`, `updated`.
- Concept/topic/comparison/query pages must include `status: draft|reviewed|stable`.
- `confidence: low|medium|high` is recommended when a page contains analytical claims.
- If a page has unresolved contradiction or controversy, add `contested: true` and `contradictions: [...]`.
- Filenames and `[[wikilinks]]` must match exactly, including spaces and capitalization.
- First section after title: a 1-2 sentence TL;DR.

## Tag Taxonomy

- Before bulk writing pages, define the wiki's top-level tag taxonomy in this SCHEMA.
- Prefer a small, stable vocabulary; add new tags here before using them anywhere.
- Every tag used on a page should be auditable against this taxonomy.
- Large wikis should treat tag audit as a routine lint check.

### Entity Pages (`wiki/entities/`)

- Frontmatter: `tags: [entity, <category>]`, `created`, `updated`, `source_count`.
- Sections: Overview, Key Facts, Relationships, Sources.
- Link to concepts, topics, comparisons, and source summaries that reference this entity.

### Concept Pages (`wiki/concepts/`)

- Frontmatter: `tags: [concept]`, `created`, `updated`, `status`, optional `confidence`.
- Sections: Definition, Significance, Evidence, Counterpoints, Related Concepts, Sources.
- Use paragraph-level provenance when synthesizing 3+ sources.

### Topic Pages (`wiki/topics/`)

- Frontmatter: `tags: [topic, <subtopic>]`, `created`, `updated`, `status`, optional `confidence`.
- Sections: Overview, Key Points, Analysis, Open Questions, Sources.
- Source summaries and domain overview pages go here.

### Source Summary Pages (`wiki/topics/`)

- Use for compact single-source entries. A Source Summary should give a 2-3 minute view of the source's main line without replacing a Reading Guide.
- Include a dedicated `Source Spine` / `来源主线` section with Problem, Approach, Key Claim, Limitation, and Wiki Impact.
- For papers, preserve the research logic: research question, method or system, main result, limitation, and wiki impact.
- For non-paper sources, adapt the labels when useful but preserve the five-part spine.
- Order `核心要点` by the source's logic rather than by entity, tag, or model-interest order.
- Strong claims, numeric details, paper conclusions, disputed judgments, and corrections require a raw locator or a Raw Evidence entry.
- A Source Summary may link to a Reading Guide for explanation, but stable claims should still route back to raw evidence.
- When materially updating an older Source Summary, add the Source Spine if missing; do not run a full migration only for format parity.

### Comparison Pages (`wiki/comparisons/`)

- Frontmatter: `tags: [comparison, <subtopic>]`, `created`, `updated`, `status`, optional `confidence`.
- Sections: Comparison Objects, Dimensions, Table, Synthesis/Verdict, Open Questions, Sources.
- Strongly prefer paragraph-level provenance.

### Reading Guide Pages (`wiki/readings/`)

- Frontmatter: `tags: [reading, <subtopic>]`, `created`, `updated`, `source_title`, `source_type`, `source_url`, `source_summary`, `raw_path`, `raw_sha256`, `status`, `confidence`, `indexed`.
- Use for papers, long articles, and reports when the user explicitly asks for detailed interpretation, close reading, or help understanding the source's logic.
- Reading Guides coexist with Source Summary pages and should link to the Source Summary when one exists.
- Source Summary pages should link back to a Reading Guide when one exists.
- Reading Guides are indexed by default in the Readings section of `index.md`.
- Reading Guides do not require paragraph-level provenance in V1.
- Strong claims, numeric details, paper conclusions, disputed judgments, and corrections should point back to the Source Summary or raw evidence.
- Do not put agent-authored Reading Guides in `raw/`, and do not treat them as the primary evidence source for stable wiki claims.
- Apply a Readable Wiki Page pass before saving. Split overloaded paragraphs, follow the source's argument, remove AI-sounding filler, and preserve quotes, formulas, code, raw excerpts, hashes, URLs, page numbers, and file paths.

## Readability Conventions

Readable wiki pages should help a future reader understand the material without weakening evidence discipline.

- Reading Guides require a readability pass.
- Topic source summaries use a light pass; keep them short, searchable, evidence-oriented, and organized around the Source Spine.
- Concept, entity, comparison, and query pages use a medium pass; improve paragraph clarity without loosening citations.
- Raw sources are never humanized or rewritten.
- Index, log, and topic-map pages receive only clarity and format cleanup.
- Prefer one job per paragraph: problem, mechanism, result, limitation, relationship, or open question.
- Avoid inflated significance language, generic positive conclusions, chatbot residue, mechanical boldface, and title-case headings when sentence-style headings are more natural.

### Query Pages (`wiki/queries/`)

- Frontmatter: `tags: [query, <subtopic>]`, `created`, `updated`, `status`, `confidence`, `answer_version`, `indexed`, `basis_pages`.
- Default status is `reviewed`; default confidence is `medium`. Use `draft` / `low` for exploratory archives and usually set `indexed: false`.
- Query Archives live in `wiki/queries/` by default. Convert to concepts, entities, comparisons, or topics only when deliberately reshaping the answer into a stable page type.
- Basis Pages are required for every Query Archive and should state what each page contributed.
- Raw Evidence is required for strong claims, disputed judgments, numeric details, paper conclusions, or corrections to existing wiki knowledge.
- Follow-Up Actions use only `[open]`, `[done]`, and `[dropped]`.
- Answer Version is stored in `answer_version`. Increment it only when new evidence, correction, or follow-up work materially changes the answer. Formatting and typo fixes do not increment it.
- Set `indexed: false` for scratch, private, low-confidence, or explicitly unindexed archives.

## Paragraph-Level Provenance

Use Markdown footnotes for paragraph-level provenance. Do not use `^[raw/...]` inline markers.

```markdown
该方法要求相位空间轨迹在门末闭合。[^source-ms-gate]

## 段落级来源

[^source-ms-gate]: raw/papers/ms-gate-1999.md，第 3 节
```

Use this for:
- Concept pages synthesizing 3+ sources
- Entity pages with `source_count >= 3`
- Topic overview pages
- Comparison pages
- Serious query archive pages

## Linking Conventions

- Dense linking is good — when in doubt, link.
- Every source summary page must link to all entities and concepts it references.
- Entity/concept pages must link back to relevant sources or source summaries.
- Concept pages should link to related concepts.
- Use `[[Page Name|display text]]` for readable links.

## Ingest Workflow

### Ingest Plan Gate

Meaningful ingest work starts with an Ingest Plan before any writes. The plan is a chat-rendered report only; it must not create, update, archive, delete, or overwrite `raw/`, `wiki/`, `index.md`, or `log.md`.

Use Ingest Plan for papers, articles, PDFs, URLs, external local files, and batch sources. Tiny Note Exception: a small pasted note may be captured directly only when the user explicitly asks for direct capture. Papers, articles, PDFs, URLs, and batch sources cannot use this exception.

An Ingest Plan contains:

- Source Summary: source type, readiness, identity, proposed Raw Destination.
- Candidate Knowledge Items: Entity, Concept, Claim.
- Page Impact: source summary page impact separated from Entity/Concept/Claim candidates.
- Risks and Confirmations.
- Recommended Next Step.

Allowed page operations are `create`, `update`, `merge`, `skip`, and `needs-confirmation`. `archive` is not an Ingest Plan operation.

Existing Page Match is conservative: exact page stem, exact `[[wikilink]]`, or explicit alias only. Fuzzy, translated, spacing-different, and filename-similar matches require confirmation.

Source identity rules:

- Same `sha256`: same source.
- Same `source_url` with different `sha256`: source drift; ask for confirmation.
- Similar filenames: weak duplicate hint only.

After the report, ask the user to choose proceed / narrow / revise. Do not write until the user approves the plan.

### Single-source ingest

1. Generate an Ingest Plan and present it in chat.
2. Read the source.
3. Extract candidate Entity, Concept, and Claim items.
4. Pre-scan the existing wiki with `search_files` to detect existing pages.
5. Ask for Plan Approval before writing.
6. Save raw source with `sha256` metadata when writing to `raw/`.
7. Create/update source summary, entity, concept, topic, comparison, reading, or query pages as appropriate.
8. Update `index.md`.
9. Append to `log.md`.
10. Run focused lint for the pages touched by this ingest; report only new issues involving those pages.

### Batch ingest

Use when the user says “批量 / 一批 / 这些文件 / 整个目录” or equivalent.

1. Generate an Ingest Plan before writing.
2. If the batch has more than five sources or more than ten impacted pages, recommend narrowing scope.
3. Read all approved sources.
4. Identify all Entity, Concept, and Claim candidates across the batch.
5. Search existing wiki once for all candidates.
6. Present source-to-wiki impact, risk, and ambiguity.
7. Ask for Plan Approval before writing.
8. Create/update pages in one pass.
9. Update `index.md` and `log.md` once.
10. Run focused lint for touched pages.

## Query Conventions

- Always read `index.md` first to locate relevant pages.
- For larger wikis, also use `search_files` over wiki pages.
- Cite source pages with `[[wikilinks]]`.
- Offer Archive Confirmation for Archive-Worthy Queries: answers that reuse multiple pages or raw evidence, produce reusable synthesis, are likely to be asked again, reveal follow-up work, or the user asks to keep.
- Default to saving approved Query Archives in `wiki/queries/`.
- Before creating a new Query Archive, check for exact title, explicit alias, or clearly same Original Question / Canonical Question.
- Use a Comparison Upgrade only when the user explicitly wants a long-lived comparison page; otherwise record it as a Follow-Up Action.
- Do not save chat answers into `raw/` by default. Query Archives cite Basis Pages, and strong claims cite Raw Evidence.

## Semantic Lint Conventions

Semantic Lint is an LLM-assisted knowledge health review, not an automatic replacement for `lint.py`. It produces structured confirmation candidates before any maintenance write.

Use Semantic Lint for semantic issues that mechanical lint cannot prove:

- Contradiction Candidate
- Missing Page Candidate
- Stale Claim Candidate
- Weak Evidence Candidate
- Index Summary Drift
- Overgrown Page Candidate

Mechanical lint output is Mechanical Lint Signal. It may guide review, but it is not a semantic finding by itself. A Stale Page means `updated` is older than the threshold; a Stale Claim Candidate means a specific claim may be superseded by newer evidence.

Each Semantic Lint finding should include type, title, affected pages, evidence, confidence, severity, recommended action, rationale, and confirmation question. Confidence and severity are separate. Do not update, create, split, or archive pages from Semantic Lint until the finding is confirmed.

## Index and Topic Map

- `index.md` is the complete catalog of current pages.
- `_meta/topic-map.md` is the human-friendly navigation layer.
- Update `index.md` whenever current pages are created, renamed, archived, or deleted.
- Update `topic-map.md` only when adding new domains, routes, major overviews, or reading paths.

## Archive Policy

- Do not physically delete obsolete wiki pages by default.
- Move obsolete, duplicate, superseded, or no-longer-current pages into `_archive/<original-path>/`.
- Remove archived pages from `index.md`.
- Update inbound links to point to the replacement page when one exists.
- Lint ignores `_archive/` unless `--include-archive` is requested.

Archived page frontmatter:

```yaml
archived: true
archived_at: YYYY-MM-DD
archived_reason: "被 [[新页面名]] 取代"
superseded_by: [[新页面名]]
```

## Log Policy

- `log.md` is append-only for the current year.
- Rotate by year first: previous year becomes `log-YYYY.md`.
- If a year exceeds 500 entries, rotate to `log-YYYY-partN.md`.

## Lint Checklist

- [ ] Broken `[[wikilinks]]`?
- [ ] Orphan pages?
- [ ] Index completeness and stale entries?
- [ ] Missing or invalid frontmatter?
- [ ] Missing `status` on concept/topic/comparison/query pages?
- [ ] Invalid `confidence` values?
- [ ] `contested: true` pages missing `contradictions`?
- [ ] Raw files missing `sha256` or showing source drift?
- [ ] Pages over 200 lines that should be split?
- [ ] Pages with `updated` dates older than 90 days compared with current work?
- [ ] Tag audit against SCHEMA taxonomy?
- [ ] `log.md` needs rotation?
- [ ] `_meta/topic-map.md` exists and is useful?

## Custom Conventions

<!-- Add domain-specific conventions below as you discover them -->

- 
