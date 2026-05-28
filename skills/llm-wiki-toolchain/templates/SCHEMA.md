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

### Comparison Pages (`wiki/comparisons/`)

- Frontmatter: `tags: [comparison, <subtopic>]`, `created`, `updated`, `status`, optional `confidence`.
- Sections: Comparison Objects, Dimensions, Table, Synthesis/Verdict, Open Questions, Sources.
- Strongly prefer paragraph-level provenance.

### Query Pages (`wiki/queries/`)

- Frontmatter: `tags: [query, <subtopic>]`, `created`, `updated`, `status`, optional `confidence`.
- Save only valuable answers that would be painful to re-derive.
- Include original question, synthesized answer, source pages, and follow-up actions.

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

### Single-source ingest

1. Read the source.
2. Extract candidate entities/concepts.
3. Pre-scan the existing wiki with `search_files` to detect existing pages.
4. Present a plan to the user when there are ambiguous matches or broad updates.
5. Save raw source with `sha256` metadata when writing to `raw/`.
6. Create/update source summary, entity, concept, topic, comparison, or query pages as appropriate.
7. Update `index.md`.
8. Append to `log.md`.
9. Run focused lint for the pages touched by this ingest; report only new issues involving those pages.

### Batch ingest

Use when the user says “批量 / 一批 / 这些文件 / 整个目录” or equivalent.

1. Read all sources first.
2. Identify all entities/concepts across the batch.
3. Search existing wiki once for all candidates.
4. Present an ingest plan: raw files, new pages, updated pages, risk/ambiguity.
5. If the batch touches more than 10 wiki pages, confirm scope before writing.
6. Create/update pages in one pass.
7. Update `index.md` and `log.md` once.
8. Run focused lint for touched pages.

## Query Conventions

- Always read `index.md` first to locate relevant pages.
- For larger wikis, also use `search_files` over wiki pages.
- Cite source pages with `[[wikilinks]]`.
- Offer to file valuable answers as new pages in `wiki/queries/` or `wiki/comparisons/`.

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
