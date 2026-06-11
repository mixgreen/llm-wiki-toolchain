# Reading Guide Workflow

Reading Guide is the workflow for preserving a detailed, human-readable explanation of a paper, long article, or report. It helps the reader follow the source's argument without turning the guide into the primary evidence source for the wiki.

V1 is documentation- and template-led. It does not add a generator script, does not automatically create Reading Guides during ordinary ingest, and does not put agent-authored explanation in `raw/`.

## When to Create

Create or update a Reading Guide only when the user explicitly asks for detailed interpretation, close reading, or help understanding a long-form source.

Trigger examples:

- "帮我详细解读一下这篇论文"
- "精读这篇文章"
- "讲透这篇 report"
- "帮我理清这篇论文的逻辑"

Do not create a Reading Guide for ordinary source ingest unless the user asks for the detailed reading.

## Default Destination and Name

The default destination is `wiki/readings/`.

The default filename is:

```text
<source title> - Reading Guide.md
```

Prefer the canonical source title from the Source Summary when one exists. If the source title is ambiguous, ask before creating a new guide.

## Relationship to Source Summary

Reading Guide and Source Summary coexist.

- Source Summary stays short, searchable, and evidence-oriented.
- Reading Guide carries the narrative explanation and reading path.
- Reading Guide links to Source Summary when one exists.
- Source Summary links back to Reading Guide when one exists.

If Source Summary does not exist, ask whether to create it through the normal ingest workflow before or alongside the Reading Guide. Do not let Reading Guide silently replace it.

## Reading Guide Match

Before creating a new guide, check for an existing guide.

Update an existing Reading Guide when any of these match:

- same raw sha256
- same source URL
- explicit Source Summary link
- explicit alias

Fuzzy title similarity is not enough. Ask before merging or updating when the match is uncertain.

## Evidence Boundary

Reading Guide helps comprehension. It is not the primary evidence source for stable wiki claims.

V1 does not require paragraph-level provenance, but the guide should point readers back to Source Summary or raw evidence for:

- strong claims
- numeric details
- paper conclusions
- disputed judgments
- corrections to existing wiki knowledge

Use Source Summary and raw evidence when updating entity, concept, topic, or comparison pages. Do not cite Reading Guide alone as proof for stable claims.

## Recommended Shape

The guide should read like a lecture-style explanation rather than a fact card. Source-specific headings are allowed.

Common sections:

- Why this source matters
- What problem it is trying to solve
- Core idea
- Method, system, or argument structure
- Key results
- Trade-offs and limitations
- Relationship to existing wiki knowledge
- What to remember after reading

Avoid copying the Source Summary structure. A guide that only lists facts belongs in Source Summary, not Reading Guide.

## Index and Log

Reading Guides are indexed by default in the Readings section of `index.md`.

Set `indexed: false` only when the guide is scratch, private, low-confidence, or explicitly kept out of the index.

Creating or materially updating a Reading Guide requires a log entry:

```markdown
## [YYYY-MM-DD] reading | Reading Guide Title
- Created/Updated: [[Reading Guide Title]]
- Source Summary: [[Source Summary Title]]
- Source: <source title>
- Evidence boundary: strong claims route to Source Summary/raw
```

Formatting-only edits do not need log entries.
