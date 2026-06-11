---
date: 2026-06-11
topic: reading-guide
---

# Reading Guide Requirements

## Summary

Add a first-class Reading Guide workflow for papers, long articles, and reports. A Reading Guide is a saved page under `wiki/readings/` that helps a human follow a source's argument, while Source Summary remains the shorter, searchable, evidence-oriented wiki entry.

---

## Problem Frame

Current source summary pages are good wiki entry points: they preserve metadata, core claims, linked entities, linked concepts, raw evidence, and index visibility. They are less good as a reading companion because they compress a source into facts and links.

The user has a separate need when asking "帮我详细解读一下这篇论文": they want a narrative explanation that rebuilds the paper's logic, explains why each part matters, and makes the source easier to understand before extracting stable wiki knowledge. A time-based note example showed that this style is useful, but storing it outside the wiki fragments the knowledge base and makes later retrieval weaker.

---

## Key Decisions

- **Reading Guide is its own page type:** Save detailed readings under `wiki/readings/`, not `raw/` and not `wiki/topics/`.
- **Source Summary and Reading Guide coexist:** Source Summary stays short and searchable; Reading Guide carries the long-form explanation. They should link to each other.
- **Explicit request trigger:** Create a Reading Guide only when the user asks for detailed interpretation, close reading, or help understanding the source's logic.
- **Lecture-style structure:** The body should read like a guided explanation rather than a rigid section-by-section extraction template.
- **Light evidence posture:** Reading Guide prioritizes readability and personal understanding. Strong claims, numeric claims, corrections, and disputed judgments should point back to Source Summary or raw evidence rather than making the guide the primary evidence source.
- **Discoverability by default:** Reading Guides enter `index.md` under a dedicated Readings section.
- **Update in place:** Later detailed readings of the same source update the existing Reading Guide by default.

---

## Requirements

**Page Type and Storage**

- R1. The toolchain must define `wiki/readings/` as the home for Reading Guide pages.
- R2. `raw/` must remain reserved for original sources and derived source text, not agent-authored explanation.
- R3. Reading Guides must support papers, long articles, and reports in V1.
- R4. Reading Guide filenames should default to `<source title> - Reading Guide.md`.

**Relationship to Existing Pages**

- R5. Reading Guides must coexist with Source Summary pages rather than replacing them.
- R6. A Reading Guide should link to its Source Summary when one exists.
- R7. A Source Summary should link to the Reading Guide when one exists.
- R8. Reading Guides must be indexed in a dedicated Readings section by default.

**Creation and Update Behavior**

- R9. The workflow should create a Reading Guide only when the user explicitly asks for detailed interpretation, close reading, or help understanding a source.
- R10. The workflow must not automatically create Reading Guides during every ingest.
- R11. When a Reading Guide already exists for the same source, the default behavior is to update it instead of creating a duplicate.
- R12. Existing guide matching should be conservative: same raw hash, same source URL, explicit Source Summary link, or explicit alias.

**Reading Experience**

- R13. The guide should be narrative and explanatory, organized around how a person understands the source.
- R14. The guide should cover the source's problem, motivation, core idea, method or system, key results, trade-offs, limitations, relationship to existing wiki knowledge, and takeaway.
- R15. The guide may use source-specific headings instead of forcing every source into the same section order.
- R16. The guide should avoid becoming a dense fact card; Source Summary already serves that role.

**Evidence and Trust**

- R17. Reading Guides do not require paragraph-level provenance in V1.
- R18. Strong claims, numeric details, paper conclusions, disputed judgments, and corrections should route readers back to Source Summary or raw evidence.
- R19. Reading Guides should make their relationship to evidence visible through frontmatter and top-level links, even when the body is light on citations.
- R20. Reading Guides should not be treated as the primary evidence source for stable entity, concept, or topic claims.

---

## Actors

- A1. **Reader:** The user trying to understand a source's argument and remember its role in the domain.
- A2. **Agent:** The LLM agent that reads a source and writes or updates the Reading Guide.
- A3. **Wiki Maintainer:** The user or agent maintaining index, source summaries, and long-term wiki consistency.

---

## Key Flows

- F1. Create a Reading Guide for a source
  - **Trigger:** The user asks for a detailed interpretation, close reading, or explanation of a paper, long article, or report.
  - **Actors:** A1, A2
  - **Steps:** The agent aligns with `SCHEMA.md`, locates or creates the Source Summary context, reads the source, writes a narrative Reading Guide under `wiki/readings/`, links it to the Source Summary, updates `index.md`, and records the work in `log.md`.
  - **Outcome:** The user gets a saved guide that helps them understand the source without replacing the Source Summary.
  - **Covered by:** R1-R10, R13-R19

- F2. Update an existing Reading Guide
  - **Trigger:** The user asks for another detailed reading of a source that already has a guide.
  - **Actors:** A1, A2, A3
  - **Steps:** The agent checks conservative source identity signals, updates the existing guide when the source matches, and avoids creating a duplicate unless the user asks for a separate reading.
  - **Outcome:** The wiki accumulates a better guide for the same source instead of scattered time-based notes.
  - **Covered by:** R11, R12

- F3. Use Reading Guide during later wiki work
  - **Trigger:** The user queries the wiki or asks to synthesize knowledge related to the source.
  - **Actors:** A1, A2
  - **Steps:** The agent may use the Reading Guide to explain the source's logic, but returns to Source Summary and raw evidence for strong claims.
  - **Outcome:** The guide improves comprehension without weakening evidence discipline.
  - **Covered by:** R17-R20

---

## Acceptance Examples

- AE1. Given a source already has a Source Summary, when the user asks "帮我详细解读一下这篇论文", then the agent creates `wiki/readings/<source title> - Reading Guide.md` and links it to the Source Summary.
- AE2. Given a normal ingest request without detailed-reading language, when the agent ingests a paper, then it does not automatically create a Reading Guide.
- AE3. Given a Reading Guide already exists for the same raw hash or source URL, when the user asks for another detailed interpretation, then the agent updates the existing guide by default.
- AE4. Given a Reading Guide includes a numeric benchmark or strong conclusion, when a reader needs evidence, then the guide points back to Source Summary or raw evidence rather than standing alone as proof.
- AE5. Given the wiki index is updated after guide creation, when the user scans `index.md`, then the guide appears under a Readings section rather than Topics.

---

## Scope Boundaries

### In Scope

- Define Reading Guide as a first-class page type and workflow.
- Seed `wiki/readings/` in new wiki structure.
- Add a Reading Guide page template.
- Update Source Summary conventions so summaries and guides can link to each other.
- Add index and log conventions for Reading Guides.
- Update the skill instructions so detailed-reading prompts create or update Reading Guides.

### Deferred

- A generator script for Reading Guides.
- Strict paragraph-level provenance inside Reading Guides.
- Automatic creation of Reading Guides during all paper ingest.
- Multiple dated Reading Guides for the same source.
- Applying Reading Guides to short notes, code sources, podcasts, or videos.

### Out of Scope

- Moving agent-authored explanation into `raw/`.
- Replacing Source Summary with Reading Guide.
- Treating Reading Guide as the primary evidence source for stable wiki claims.
- Reworking all existing source summary pages during V1.

---

## Success Criteria

- A user can ask for a detailed reading and get a saved wiki page that is easier to read than a Source Summary.
- Source Summary pages remain compact and searchable.
- Reading Guide pages are discoverable through a dedicated Readings index section.
- Same-source guides update in place by default.
- The workflow preserves the evidence boundary between explanatory prose and raw/source-backed claims.

---

## Sources

- `skills/llm-wiki-toolchain/SKILL.md` for current ingest, query, Source Summary, and health-check workflows.
- `skills/llm-wiki-toolchain/templates/SCHEMA.md` for seeded wiki structure and page conventions.
- `skills/llm-wiki-toolchain/templates/page-templates/source-summary.md` for the existing Source Summary page shape.
- User-provided QCCD Source Summary example as evidence of the current readability gap.
- User-provided detailed QCCD reading note as evidence of the desired lecture-style reading experience.
