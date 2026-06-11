# LLM Wiki Log — <WIKI_NAME>

<!--
  Format for each entry:
  ## [YYYY-MM-DD] <action> | <description>
  - Created: [[page1]], [[page2]]
  - Updated: [[page3]], [[page4]]
  - Key additions: brief note

  Query archive example:
  ## [YYYY-MM-DD] query | Query Archive Title
  - Created/Updated: [[Query Archive Title]]
  - answer_version: 1
  - Basis Pages: [[Page A]], [[Page B]]
  - Follow-Up Actions: 2 open

  Reading guide example:
  ## [YYYY-MM-DD] reading | Reading Guide Title
  - Created/Updated: [[Reading Guide Title]]
  - Source Summary: [[Source Summary Title]]
  - Source: <source title>
  - Evidence boundary: strong claims route to Source Summary/raw

  Parse with: grep "^## \[" log.md | tail -10

  Rotation policy:
  - log.md stores current-year activity by default.
  - At the first write of a new year, archive previous-year log.md as log-YYYY.md.
  - If a single year exceeds 500 entries, archive as log-YYYY-partN.md and continue.
-->

## [<YYYY-MM-DD>] init | Wiki created

- Created: index.md, log.md, SCHEMA.md, _meta/topic-map.md
- Directory structure: raw/, wiki/entities/, wiki/concepts/, wiki/topics/, wiki/comparisons/, wiki/readings/, wiki/queries/, _archive/, _meta/
- Key additions: Initialized LLM Wiki for <WIKI_NAME>
