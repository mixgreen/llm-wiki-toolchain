---
date: 2026-06-12
topic: source-summary-quality
---

# Source Summary Quality Requirements

## Summary

Improve Source Summary generation so each source page gives a 2-3 minute view of the source's main line: problem, approach, key claim, limitation, and wiki impact. The page should stay shorter and more evidence-oriented than a Reading Guide, but no longer read like disconnected bullet points.

---

## Problem Frame

Current Source Summary pages are useful as wiki entry points, but their default template makes it easy for agents to write a loose set of facts. That is enough for indexing, yet it can leave the reader unable to recover the source's argument without opening the raw file or asking for a Reading Guide.

The project now has `wiki/readings/` for detailed explanation and `Readable Wiki Page` rules for prose quality. Source Summary needs its own quality contract between those two: compact enough for search and maintenance, structured enough to preserve the source's logic.

---

## Key Decisions

- **Source Summary becomes a compressed main line:** It should help the reader understand the source's problem, approach, main claim, limitation, and wiki impact in a few minutes.
- **Reading Guide remains the long explanation:** Source Summary should not absorb lecture-style detail or become a second Reading Guide.
- **Source Spine is a required section:** A dedicated `Source Spine` / `来源主线` section gives agents a stable place to express the source's logic.
- **Core points follow source logic:** `核心要点` should be ordered by the source's argument, not by whatever facts the model found interesting.
- **Evidence stays balanced:** Only strong claims, numeric details, paper conclusions, disputed judgments, and corrections require raw locators.

---

## Requirements

**Page Purpose**

- R1. Source Summary pages must give a 2-3 minute understanding of a source's main line.
- R2. Source Summary pages must remain shorter, more searchable, and more evidence-oriented than Reading Guides.
- R3. Source Summary pages must not replace Reading Guides for detailed interpretation or close reading.

**Source Spine**

- R4. Source Summary pages must include a dedicated `Source Spine` / `来源主线` section.
- R5. The Source Spine must cover Problem, Approach, Key Claim, Limitation, and Wiki Impact.
- R6. Each Source Spine field should be short enough to scan quickly, usually one sentence or one compact bullet.
- R7. For papers, the Source Spine should preserve the paper's research logic rather than only listing topic tags.
- R8. For non-paper sources, the same section may use source-appropriate wording while preserving the five-part spine.

**Core Points**

- R9. `核心要点` must be ordered by the source's logic.
- R10. `核心要点` should contain reusable knowledge points, not a second abstract.
- R11. Ordinary explanatory points may stay lightweight when they do not make strong or disputed claims.
- R12. Strong claims, numeric details, paper conclusions, disputed judgments, and corrections must include a raw locator or point to a Raw Evidence entry.

**Evidence Boundary**

- R13. Raw locators must use source-stable references such as page, section, paragraph, timestamp, or raw file path when available.
- R14. A Source Summary may link to a Reading Guide for explanation, but stable claims should still route back to raw evidence.
- R15. Source Summary generation must preserve source titles, URLs, hashes, page numbers, formulas, direct quotes, and code blocks.

**Readability**

- R16. The first screen must tell the reader what the source is about and why it matters to this wiki.
- R17. Paragraphs should avoid mixing problem, method, result, limitation, and follow-up work in one block.
- R18. The page should avoid inflated significance language, generic positive conclusions, and chatbot residue.

---

## Actors

- A1. **Reader:** Uses the Source Summary to understand whether a source matters and where to go next.
- A2. **Agent:** Generates or updates the Source Summary during ingest.
- A3. **Wiki Maintainer:** Uses the page to connect raw sources, Reading Guides, entities, concepts, topics, and future maintenance work.

---

## Key Flows

- F1. Generate a Source Summary during ingest
  - **Trigger:** The user approves ingest for a source.
  - **Actors:** A1, A2
  - **Steps:** The agent reads the source, writes the Source Spine, orders core points by the source's logic, adds entity and concept links, records raw evidence where required, and keeps long explanation out of the summary.
  - **Outcome:** The page gives a compact main-line understanding of the source and a stable path to evidence.
  - **Covered by:** R1-R18

- F2. Link a Source Summary to a Reading Guide
  - **Trigger:** A detailed Reading Guide exists or is created for the same source.
  - **Actors:** A1, A2, A3
  - **Steps:** The Source Summary links to the Reading Guide for detailed interpretation, while strong claims continue to point back to raw evidence.
  - **Outcome:** The reader can choose quick orientation or full explanation without confusing the two page roles.
  - **Covered by:** R2, R3, R14

- F3. Update an older Source Summary
  - **Trigger:** The agent touches a source page that predates the Source Spine convention.
  - **Actors:** A2, A3
  - **Steps:** The agent adds the Source Spine, reorders core points by source logic, and adds locators only where evidence rules require them.
  - **Outcome:** Existing pages can improve incrementally without requiring a full wiki migration.
  - **Covered by:** R4-R12, R16-R18

---

## Acceptance Examples

- AE1. Given a paper source, when the agent creates a Source Summary, then the page includes a `来源主线` section covering Problem, Approach, Key Claim, Limitation, and Wiki Impact.
- AE2. Given a Source Summary has five core points, when a reader scans them, then they follow the source's argument order rather than alphabetical, entity-first, or model-interest order.
- AE3. Given a core point states a numeric result or paper conclusion, when the page is saved, then that point includes a raw locator or points to a Raw Evidence entry.
- AE4. Given a detailed Reading Guide exists, when the Source Summary links to it, then the Source Summary still keeps stable claims tied to raw evidence rather than citing the Reading Guide alone.
- AE5. Given an older Source Summary lacks a Source Spine, when it is materially updated, then the agent adds the section without forcing a full migration of unrelated pages.

---

## Scope Boundaries

### In Scope

- Define Source Summary generation quality as a first-class requirement.
- Add a dedicated Source Spine convention.
- Clarify how `核心要点` should be ordered.
- Clarify which claims require raw locators.
- Preserve the boundary between Source Summary and Reading Guide.

### Deferred

- A generator script for Source Summary pages.
- Automatic migration of all existing Source Summary pages.
- Full paragraph-level provenance for every Source Summary paragraph.
- Cross-source synthesis inside ordinary Source Summary pages.

### Out of Scope

- Moving detailed Reading Guide prose into `wiki/topics/`.
- Treating Reading Guides as the evidence source for stable claims.
- Rewriting raw sources or derived raw text for readability.
- Changing the overall wiki directory structure.

---

## Success Criteria

- A reader can understand a source's main line from its Source Summary in 2-3 minutes.
- Source Summary pages remain visibly different from Reading Guides.
- Strong claims in Source Summary pages are easier to verify.
- Agents have a stable structure that reduces scattered bullet summaries.
- Existing source pages can be improved incrementally when touched.

---

## Sources

- `skills/llm-wiki-toolchain/templates/page-templates/source-summary.md`
- `skills/llm-wiki-toolchain/templates/page-templates/reading-guide.md`
- `skills/llm-wiki-toolchain/references/reading-guide-workflow.md`
- `skills/llm-wiki-toolchain/references/readable-wiki-page-standard.md`
- `docs/brainstorms/2026-06-11-reading-guide-requirements.md`
