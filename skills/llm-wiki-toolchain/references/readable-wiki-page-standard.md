# Readable Wiki Page Standard

Readable Wiki Page is the writing standard for making generated wiki pages easier to read without weakening evidence discipline. It applies most strongly to Reading Guides, moderately to Topic and Query pages, and only as a clarity check for indexes and logs.

This standard borrows the useful parts of the `humanizer` skill: remove AI-sounding prose, keep claims specific, and make the page sound like a careful reader wrote it for future use. It must not rewrite quoted text, raw evidence, formulas, code, or source identifiers.

## Page-Type Policy

Use different editing strength by page type.

| Page type | Readability pass | Notes |
|-----------|------------------|-------|
| `wiki/readings/` | Required | The guide should feel like a human explanation of the source's logic. |
| `wiki/topics/` source summaries | Light | Keep it searchable and evidence-oriented. Avoid lecture-style expansion. |
| `wiki/concepts/`, `wiki/entities/`, `wiki/comparisons/` | Medium | Prefer clear prose, but keep stable claims tightly sourced. |
| `wiki/queries/` | Medium | Preserve the original question wording. Polish the answer and follow-up actions. |
| `raw/` | None | Do not humanize immutable sources or copied evidence. |
| `index.md`, `log.md`, `_meta/topic-map.md` | Format only | Clarity and brevity matter more than voice. |

## Evidence Boundary

Readability edits must not change what the evidence says.

Do not rewrite:

- direct quotes
- formulas
- code blocks
- raw excerpts
- source titles, URLs, hashes, page numbers, section names, or file paths
- frontmatter values that act as identifiers

When a sentence contains a strong claim, numeric result, paper conclusion, disputed judgment, or correction to existing wiki knowledge, improve the prose around it but preserve or add the pointer back to Source Summary or raw evidence.

## Paragraph Shape

Each paragraph should do one job.

Good paragraph jobs:

- state the problem the source is trying to solve
- explain one mechanism or design choice
- interpret one result
- name one limitation or trade-off
- connect the source to an existing wiki page
- identify one open question

Avoid paragraphs that mix background, mechanism, result, limitation, and future work in one block. If a paragraph needs more than one "and this also means", split it.

## Reading Guide Voice

Reading Guides should follow the source's argument, not the model's summary habits.

Prefer sentences like:

- "作者先把问题限定在..."
- "这个实验的作用是..."
- "这里真正要注意的是..."
- "这个结果支持 X, 但还不能说明 Y."
- "读到这里时, 可以把它和 [[相关概念]] 联系起来."

Avoid sentences like:

- "This highlights the importance of..."
- "This serves as a crucial foundation for..."
- "It is important to note that..."
- "The paper showcases..."
- "In conclusion, this represents a significant step..."

## Humanizer-Style Checklist

Before saving or materially updating a readable wiki page, scan for:

- inflated significance language, such as "pivotal", "crucial", "underscores", "showcases", "testament"
- vague authority, such as "experts argue" or "some sources suggest" without a named source
- formulaic headings followed by one-line warm-up paragraphs
- overuse of bold text for ordinary terms
- rule-of-three lists that make the page look comprehensive without adding precision
- generic positive conclusions
- title-case headings in Chinese or English pages where sentence-style headings would read more naturally
- chatbot residue, such as "here is", "let's dive in", "I hope this helps", or "would you like"

Do not flatten all prose. Technical pages can stay plain. The goal is readable, specific, and source-faithful writing.

## Default Pass Order

1. Verify page type and evidence boundary.
2. Split overloaded paragraphs.
3. Replace AI-sounding claims with concrete explanations.
4. Preserve links, citations, raw paths, hashes, formulas, and quotes.
5. Check that the first screen gives the reader a useful entry point.
6. For Reading Guides, ensure the page explains the source's logic before listing facts.

## Failure Modes

- A beautiful explanation with weak evidence is worse than a plain sourced note.
- A complete summary can still be unreadable if every paragraph has the same rhythm.
- A natural voice can become misleading if it sounds more certain than the source.
- Over-polishing can erase useful technical specificity.
