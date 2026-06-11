# LLM Wiki Toolchain

This context defines the language for an agent-maintained Obsidian LLM Wiki. It keeps the repository vocabulary stable while workflows and scripts evolve.

## Language

**Ingest Plan**:
A pre-write review of how one or more sources would change a wiki, including candidate knowledge items, existing page matches, proposed page operations, and risks that need confirmation. It does not modify the wiki. Single-source review is the primary mode; batch review is supported but treated as overload-prone and should stay easy to narrow. Its default representation is a human-readable Markdown report; machine-readable JSON is a secondary representation for tests and automation.
_Avoid_: pre-scan, import plan, ingestion checklist

**Ingest Plan Report**:
The chat-rendered Markdown representation of an Ingest Plan. Its canonical sections are Source Summary, Candidate Knowledge Items, Page Impact, Risks and Confirmations, Recommended Next Step, and optional Machine Data. It is not saved as a wiki artifact.
_Avoid_: source summary page, import report

**Deterministic Plan Skeleton**:
The script-generated part of an Ingest Plan that can be derived without semantic judgment, such as source paths, hashes, current wiki pages, index matches, existing raw files, and page-impact placeholders. It operates at file and page level, not paragraph, chunk, embedding, or reranking level.
_Avoid_: automatic ingest, generated plan

**Semantic Plan Review**:
The agent-authored part of an Ingest Plan that requires interpretation, such as Entity, Concept, and Claim extraction, ambiguity assessment, risk explanation, and recommended page operations.
_Avoid_: LLM output, final answer

**Page Operation**:
The proposed effect an Ingest Plan would have on one wiki page or candidate page. Valid operations are create, update, merge, skip, and needs-confirmation; archive is a maintenance action, not an Ingest Plan operation.
_Avoid_: action, write step

**Existing Page Match**:
The conservative match between a Candidate Knowledge Item and a current wiki page. Only exact page stem, exact wikilink, or explicit alias should be treated as an update; similar names, spacing differences, translations, and fuzzy matches require confirmation.
_Avoid_: fuzzy match, similar page

**Overload-Prone Review**:
An Ingest Plan that is likely too broad for comfortable human review. Batch review becomes overload-prone when it covers more than five sources or more than ten impacted wiki pages.
_Avoid_: large batch, big ingest

**Plan Approval**:
An explicit user decision after reviewing an Ingest Plan Report. The valid outcomes are proceed with the plan, narrow the plan, or revise classifications; no wiki write occurs without Plan Approval.
_Avoid_: auto-apply, implicit approval

**Successful Ingest Planning**:
An Ingest Plan is successful when it reduces mistaken wiki writes and lowers human review burden before ingest. It is not measured by how much ingest work it automates.
_Avoid_: automation rate, hands-free ingest

**Tiny Note Exception**:
A narrow exception to mandatory Ingest Planning for small user-provided notes where the user explicitly asks for direct capture. Papers, articles, PDFs, URLs, and batch sources do not qualify.
_Avoid_: quick ingest, bypass

**Source Identity**:
The rule for deciding whether a source is already present in raw storage. Matching sha256 means the same source; matching URL with a different sha256 indicates Source Drift; similar filenames or titles are weak duplicate hints only.
_Avoid_: source name, file identity

**Source Drift**:
A source identity conflict where a known source URL appears with different content hash. Source Drift requires confirmation before the wiki is updated from the changed source.
_Avoid_: changed file, updated source

**Raw Destination**:
The proposed location where an external source should be persisted during approved ingest. An Ingest Plan may recommend a Raw Destination, but it does not create or modify raw files.
_Avoid_: output path, import target

**URL Source Review**:
An Ingest Plan review of a web source using the URL, title, and available text summary needed to judge wiki impact. Complete web archiving, article cleanup, image download, and attachment handling belong to approved ingest, not plan review.
_Avoid_: web archive, webpage import

**Source Readiness**:
The degree to which a source can be reviewed during Ingest Plan creation. Valid readiness levels are text-ready, text-extractable, and requires-derived-text; non-text sources that require OCR, transcription, or manual summarization are not treated as fully understood during plan review.
_Avoid_: file type, parse status

**Source Summary Page**:
A wiki page representing one ingested source as a source-level entry, especially useful for paper reading. It is planned separately from Entity, Concept, and Claim candidates.
_Avoid_: topic candidate, paper note

**Paper Lens**:
The lightweight paper-specific view used in an Ingest Plan for research papers. It covers research question, method, main contribution, limitations, and follow-up value without replacing a full Source Summary Page.
_Avoid_: full paper review, literature review

**Source-to-Wiki Impact**:
The scope boundary for Ingest Plan v1. It explains how each source would affect the current wiki, but does not synthesize across multiple sources.
_Avoid_: cross-source synthesis, literature review

**Source-First Ingest Plan**:
An Ingest Plan organized around understanding one source before reviewing its page impact. This is the default shape for single-source review.
_Avoid_: page-first plan for a single source

**Page-First Ingest Plan**:
An Ingest Plan organized around the wiki pages likely to change before drilling into each source. This is reserved for batch review or overload control.
_Avoid_: source summary list

**Candidate Knowledge Item**:
Something an Ingest Plan extracts from a source as potentially relevant to the wiki. Candidate Knowledge Items are classified as Entity, Concept, or Claim before any page operation is proposed.
_Avoid_: extracted thing, item, note

**Entity**:
A named object that can accumulate facts and relationships across sources, such as a person, organization, product, project, device, or domain-specific object. Entity candidates require a reason in an Ingest Plan, but not a source excerpt.
_Avoid_: actor, object

**Concept**:
An idea, mechanism, method, theory, design principle, or domain construct that can be explained independently and related to other wiki pages. Concept candidates require a reason in an Ingest Plan, but not a source excerpt.
_Avoid_: topic, idea

**Claim**:
A concrete assertion from a source that may support, revise, or contradict existing wiki knowledge. A Claim is evidence-bearing but is not a default standalone page; it requires a source excerpt or locator to be included in an Ingest Plan.
_Avoid_: fact, note, quote
