---
title: "feat: Improve Source Summary quality"
type: feat
date: 2026-06-12
origin: docs/brainstorms/2026-06-12-source-summary-quality-requirements.md
---

# feat: Improve Source Summary quality

## Summary

Improve Source Summary generation so source pages preserve the source's main line without becoming Reading Guides. The work adds a Source Spine convention, updates Source Summary template guidance, teaches the skill how to write and update these pages, and protects the rule with documentation tests.

---

## Problem Frame

Source Summary pages currently make sources searchable and traceable, but the template can produce scattered bullet summaries. That makes a page easy to index and harder to read when the user wants the source's problem, approach, key claim, limitation, and wiki impact in one compact pass.

The brainstorm defines a middle layer between Source Summary as a fact card and Reading Guide as a long explanation. This plan keeps Source Summary short, evidence-oriented, and update-friendly while giving agents a stable structure for the source's argument.

---

## Requirements

**Page Purpose**

- R1. Source Summary pages must give a 2-3 minute understanding of a source's main line.
- R2. Source Summary pages must stay shorter, more searchable, and more evidence-oriented than Reading Guides.
- R3. Source Summary pages must not replace Reading Guides for detailed interpretation or close reading.

**Source Spine**

- R4. Source Summary conventions and templates must include a dedicated `Source Spine` / `来源主线` section.
- R5. The Source Spine must cover Problem, Approach, Key Claim, Limitation, and Wiki Impact.
- R6. Source Spine fields must stay compact enough for quick scanning.
- R7. Paper Source Summaries must preserve research logic rather than only listing topic tags.
- R8. Non-paper Source Summaries may use source-appropriate wording while preserving the five-part spine.

**Core Points and Evidence**

- R9. `核心要点` must be ordered by the source's logic.
- R10. `核心要点` must contain reusable knowledge points, not a second abstract.
- R11. Ordinary explanatory points may stay lightweight when they do not make strong or disputed claims.
- R12. Strong claims, numeric details, paper conclusions, disputed judgments, and corrections must include a raw locator or point to a Raw Evidence entry.
- R13. Stable claims may link to Reading Guides for explanation, but must route back to raw evidence for proof.

**Readability and Validation**

- R14. The first screen must tell the reader what the source is about and why it matters to the wiki.
- R15. Source Summary guidance must preserve source identifiers such as titles, URLs, hashes, page numbers, formulas, direct quotes, and code blocks.
- R16. Documentation tests must verify the Source Spine, evidence boundary, Reading Guide boundary, and README discovery language.

---

## Scope Boundaries

### In Scope

- Add Source Summary quality guidance to `SKILL.md`.
- Add a dedicated Source Summary quality reference document.
- Update seeded schema conventions for Source Summary pages.
- Update the Source Summary page template with `来源主线`, evidence rules, and readability guidance.
- Update README discovery text if needed so users can understand the improved Source Summary role.
- Add documentation tests for the new conventions.

### Deferred to Follow-Up Work

- A Source Summary generator script.
- Automatic migration of all existing Source Summary pages.
- Full paragraph-level provenance for every Source Summary paragraph.
- Cross-source synthesis inside ordinary Source Summary pages.

### Out of Scope

- Moving detailed Reading Guide prose into `wiki/topics/`.
- Treating Reading Guides as the evidence source for stable claims.
- Rewriting raw sources or derived raw text for readability.
- Changing the overall wiki directory structure.

---

## Key Technical Decisions

- KTD1. **Template-led V1:** The project has recently stabilized new wiki behaviors through references, templates, and tests. Source Summary quality should follow that pattern instead of introducing a generator script before the writing contract is proven.
- KTD2. **Source Spine as the compact argument shape:** A fixed five-part spine gives the agent a durable scaffold while keeping long explanation in Reading Guide.
- KTD3. **Balanced locator rule:** Requiring locators only for strong claims, numeric details, paper conclusions, disputed judgments, and corrections keeps Source Summary usable without weakening traceability.
- KTD4. **Incremental upgrade posture:** Existing Source Summary pages should improve when touched. A full migration would be noisy and is outside this feature's value.
- KTD5. **Documentation tests over runtime tests:** This feature changes agent-facing conventions and seeded templates, so text-level tests are the right regression guard.

---

## Implementation Units

### U1. Define Source Summary quality workflow

- **Goal:** Teach the skill that Source Summary pages should preserve a compact source main line while staying distinct from Reading Guides.
- **Requirements:** R1-R13
- **Dependencies:** None
- **Files:**
  - `skills/llm-wiki-toolchain/SKILL.md`
  - `skills/llm-wiki-toolchain/references/source-summary-quality.md`
  - `tests/test_source_summary_quality_docs.py`
- **Approach:** Add a concise `SKILL.md` subsection near the ingest/source summary flow. Move detailed guidance into a new reference document that defines Source Spine, core-point ordering, evidence locator rules, Reading Guide boundary, and incremental update behavior.
- **Patterns to follow:** `skills/llm-wiki-toolchain/references/reading-guide-workflow.md` for page-type boundaries; `skills/llm-wiki-toolchain/references/readable-wiki-page-standard.md` for prose and evidence limits.
- **Test scenarios:**
  - Given `SKILL.md`, when searched for Source Summary quality, it names Source Spine and the five fields.
  - Given the new reference, when searched for evidence rules, it requires locators only for strong claims, numeric details, paper conclusions, disputed judgments, and corrections.
  - Given the new reference, when searched for Reading Guide boundaries, it states Source Summary should not absorb long explanation.
  - Covers AE4. Given the new reference, when searched for stable claims, it says Reading Guide is explanatory and raw evidence remains the proof path.
- **Verification:** Agents have a single place to learn how Source Summary differs from Reading Guide and how to write its compact main line.

### U2. Update templates and seeded schema

- **Goal:** Make initialized wikis and new Source Summary pages carry the Source Spine convention by default.
- **Requirements:** R4-R15
- **Dependencies:** U1
- **Files:**
  - `skills/llm-wiki-toolchain/templates/SCHEMA.md`
  - `skills/llm-wiki-toolchain/templates/page-templates/source-summary.md`
  - `tests/test_source_summary_quality_docs.py`
- **Approach:** Add Source Summary page conventions to SCHEMA. Update `source-summary.md` with a dedicated `## 来源主线` section covering Problem, Approach, Key Claim, Limitation, and Wiki Impact. Add comments that keep each field short, order core points by source logic, and require raw locators only for strong evidence cases.
- **Patterns to follow:** Existing page templates use frontmatter plus comments for conditional guidance. Preserve the current Source Summary link sections for entities, concepts, raw material, Reading Guide, and notes.
- **Test scenarios:**
  - Covers AE1. Given `source-summary.md`, when searched, it contains `## 来源主线`.
  - Given `source-summary.md`, when searched, it contains Problem, Approach, Key Claim, Limitation, and Wiki Impact prompts.
  - Covers AE2. Given `source-summary.md`, when searched, it tells agents to order `核心要点` by source logic.
  - Covers AE3. Given `source-summary.md`, when searched, it requires raw locators for numeric results and paper conclusions.
  - Given `SCHEMA.md`, when searched, it documents Source Summary conventions separately from Reading Guide pages.
- **Verification:** New Source Summary pages have the right shape without the agent inventing a local format.

### U3. Refresh user-facing docs and page-template documentation

- **Goal:** Make the improved Source Summary role discoverable without overstating automation.
- **Requirements:** R1-R3, R14, R16
- **Dependencies:** U1, U2
- **Files:**
  - `README.md`
  - `docs/README.en.md`
  - `skills/llm-wiki-toolchain/SKILL.md`
  - `tests/test_source_summary_quality_docs.py`
- **Approach:** Update README capability language to explain that Source Summary gives a compressed source main line, while Reading Guide carries detailed explanation. If `SKILL.md` page-template docs mention Source Summary, add the Source Spine and evidence-boundary expectations there too.
- **Patterns to follow:** Recent README updates describe capabilities in one row or short paragraph, then leave detailed workflow behavior to `SKILL.md` and references.
- **Test scenarios:**
  - Given `README.md`, when searched for Source Summary, it describes the compressed main-line role.
  - Given `docs/README.en.md`, when searched, it distinguishes Source Summary from Reading Guide.
  - Given `SKILL.md`, when searched in page-template docs, it names `source-summary.md` and the Source Spine expectation.
- **Verification:** Users can understand the new Source Summary standard from README without assuming there is a new generator script.

### U4. Add regression coverage and version policy check

- **Goal:** Lock the new writing contract into tests and decide release metadata consistently.
- **Requirements:** R16
- **Dependencies:** U1, U2, U3
- **Files:**
  - `tests/test_source_summary_quality_docs.py`
  - `package.json`
  - `.claude-plugin/plugin.json`
- **Approach:** Add dependency-free `unittest` coverage that reads docs and templates as text. Keep package/plugin versions unchanged unless this work is being prepared for merge as a user-visible release; if bumped, keep both files in sync and update tests accordingly.
- **Patterns to follow:** `tests/test_reading_guide_docs.py`, `tests/test_query_archive_docs.py`, and `tests/test_semantic_lint_docs.py` use text assertions to protect agent-facing documentation contracts.
- **Test scenarios:**
  - Given the test suite, when run through the existing npm test script, all tests pass without network or LLM dependencies.
  - Given package and plugin metadata, when read by tests, their versions match.
  - Given modified docs, when whitespace checks run, there are no trailing whitespace errors.
- **Verification:** The Source Summary quality contract is protected from drift across docs, templates, and release metadata.

---

## Acceptance Examples

- AE1. Given a paper source, when the agent creates a Source Summary, then the page includes a `来源主线` section covering Problem, Approach, Key Claim, Limitation, and Wiki Impact.
- AE2. Given a Source Summary has five core points, when a reader scans them, then they follow the source's argument order rather than alphabetical, entity-first, or model-interest order.
- AE3. Given a core point states a numeric result or paper conclusion, when the page is saved, then that point includes a raw locator or points to a Raw Evidence entry.
- AE4. Given a detailed Reading Guide exists, when the Source Summary links to it, then the Source Summary still keeps stable claims tied to raw evidence rather than citing the Reading Guide alone.
- AE5. Given an older Source Summary lacks a Source Spine, when it is materially updated, then the agent adds the section without forcing a full migration of unrelated pages.

---

## Risks and Dependencies

- **Template bloat:** Adding Source Spine can make Source Summary feel too long. Mitigation: keep each spine field to one compact sentence or bullet and keep long explanation in Reading Guide.
- **Evidence overcorrection:** Requiring locators everywhere would slow writing and clutter pages. Mitigation: apply locator requirements only to strong evidence cases.
- **Role confusion with Reading Guide:** Agents may expand Source Summary into a mini guide. Mitigation: repeat the boundary in SKILL, SCHEMA, template comments, README, and tests.
- **Old-page inconsistency:** Existing pages will not all have Source Spine immediately. Mitigation: document incremental upgrade on material updates rather than forcing migration.

---

## Sources

- `docs/brainstorms/2026-06-12-source-summary-quality-requirements.md` for scope, requirements, flows, and acceptance examples.
- `skills/llm-wiki-toolchain/templates/page-templates/source-summary.md` for current Source Summary structure.
- `skills/llm-wiki-toolchain/templates/page-templates/reading-guide.md` for the adjacent detailed-reading template.
- `skills/llm-wiki-toolchain/references/reading-guide-workflow.md` for the Source Summary and Reading Guide boundary.
- `skills/llm-wiki-toolchain/references/readable-wiki-page-standard.md` for readable prose and evidence-preservation rules.
- `tests/test_reading_guide_docs.py`, `tests/test_query_archive_docs.py`, and `tests/test_semantic_lint_docs.py` for documentation-test patterns.
