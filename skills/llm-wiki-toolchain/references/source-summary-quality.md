# Source Summary Quality

Source Summary is the compact source-entry page for a single paper, article, report, note, or other source. It should let a reader understand the source's main line in 2-3 minutes while keeping raw evidence and downstream wiki updates traceable.

Source Summary is not a Reading Guide. Reading Guide carries the longer explanation; Source Summary carries the source's spine, reusable points, links, and evidence path.

## Source Spine

Every Source Summary should include a dedicated Source Spine section.

Use the five-part spine:

- **Problem:** What problem, question, or gap does the source address?
- **Approach:** What method, system, argument, or perspective does it use?
- **Key Claim:** What is the central claim, result, or contribution?
- **Limitation:** What boundary, caveat, or unsolved part matters?
- **Wiki Impact:** Which entity, concept, topic, comparison, query, or follow-up should this source affect?

Keep each field short. One sentence or one compact bullet is usually enough. If the explanation needs multiple paragraphs, put the explanation in a Reading Guide and link to it.

## Paper Sources

For papers, preserve the research logic:

```text
research question -> method / system -> main result -> limitation -> wiki impact
```

Do not replace this with topic tags alone. A paper Source Summary should tell the reader what the paper tried to prove or demonstrate, not merely what domain it belongs to.

## Non-Paper Sources

For non-paper sources, keep the five-part spine but adapt the wording:

- Article: issue -> argument -> main claim -> caveat -> wiki impact
- Report: question -> method / dataset -> finding -> limitation -> wiki impact
- Note: observation -> context -> usable claim -> uncertainty -> wiki impact
- Code source: component -> mechanism -> behavior -> boundary -> wiki impact

The section name can stay `来源主线`; the labels may stay Problem, Approach, Key Claim, Limitation, and Wiki Impact for consistency.

## Core Points

Core points should be ordered by the source's logic. They are not an unordered list of interesting facts.

Prefer this order:

1. The setup or problem claim.
2. The mechanism, method, or argument.
3. The key result or conclusion.
4. The limitation or trade-off.
5. The wiki-facing consequence.

Core points should contain reusable knowledge. They should not become a second abstract, a long explanation, or a copy of the Source Spine.

## Evidence Rules

Ordinary explanatory points can stay lightweight.

Raw locators are required for:

- strong claims
- numeric details
- paper conclusions
- disputed judgments
- corrections to existing wiki knowledge

Use source-stable locators when available: raw path, page, section, paragraph, timestamp, table, figure, or code location.

Reading Guides can explain why a claim matters, but they are not the proof path for stable claims. Stable claims should route back to raw evidence or to Source Summary entries that cite raw evidence.

## Readability Rules

The first screen should tell the reader what the source is and why it matters to this wiki.

Avoid:

- inflated significance language
- generic positive conclusions
- chatbot residue
- long paragraphs that mix problem, approach, result, limitation, and follow-up
- lecture-style expansion that belongs in a Reading Guide

Preserve source identifiers exactly: source titles, URLs, hashes, page numbers, formulas, direct quotes, code blocks, and raw paths.

## Incremental Upgrade

Do not migrate every old Source Summary just because this convention exists.

When an older Source Summary is materially updated, add the Source Spine if it is missing, reorder core points by source logic when practical, and add locators only where the evidence rules require them.

