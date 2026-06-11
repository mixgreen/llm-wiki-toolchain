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

**Query Archive**:
A saved wiki page for a reusable answer to a user or research question, preserving how the answer was derived. Its default location is `wiki/queries/`; only answers that have been deliberately converted into stable concepts, entities, comparisons, or broader topic pages should leave that directory.
_Avoid_: saved answer, query note, topic page

**Archive-Worthy Query**:
A query whose answer is worth offering to preserve as a Query Archive. A query is archive-worthy when it reuses multiple wiki pages or raw evidence, produces a reusable synthesis or decision, is likely to be asked again, reveals wiki follow-up work, or the user explicitly asks to keep it.
_Avoid_: valuable answer, important query

**Answer Version**:
The version number of a Query Archive's substantive answer. It starts at 1 when archived and increments only when new evidence, correction, or follow-up work materially changes the answer; formatting, copy edits, and typo fixes do not increment it.
_Avoid_: page version, package version

**Basis Page**:
A wiki page that materially supports a Query Archive answer. Basis Pages are required for every Query Archive and should state what each page contributed to the answer.
_Avoid_: related page, citation

**Raw Evidence**:
The raw source evidence behind a strong or consequential Query Archive claim. Raw Evidence is required when the answer includes strong claims, disputed judgments, numeric details, paper conclusions, or corrections to existing wiki knowledge.
_Avoid_: source, reference

**Indexed Query Archive**:
A Query Archive that is discoverable through `index.md` and treated as a current knowledge entry. Query Archives are indexed by default unless they are scratch, private, low-confidence, or explicitly kept out of the index.
_Avoid_: listed answer, public query

**Follow-Up Action**:
A proposed next maintenance or research step recorded by a Query Archive, such as creating a concept page, updating an entity, rereading raw evidence, upgrading to a comparison, or running an Ingest Plan. Follow-Up Actions are not executed automatically during query archiving.
_Avoid_: todo, next step, automatic update

**Follow-Up Action Status**:
The lightweight state of a Follow-Up Action in a Query Archive. Valid states are open, done, and dropped; Query Archives do not track owners, due dates, or project-management priority.
_Avoid_: task status, priority

**Query Archive Title**:
The reusable title of a Query Archive, written as the research question or answer domain rather than the user's raw chat phrasing. The original user question is preserved inside the page body.
_Avoid_: chat title, raw question as filename

**Canonical Question**:
The reusable form of the question that a Query Archive answers after compressing multi-turn context. It may differ from the user's raw wording but must preserve the actual intent.
_Avoid_: rewritten prompt, final prompt

**Question Context**:
The minimal background needed to understand a Query Archive's Canonical Question when the answer depends on multi-turn conversation. It excludes unrelated chat, confirmation noise, and exploratory detours.
_Avoid_: chat transcript, conversation history

**Comparison Upgrade**:
The deliberate conversion of a Query Archive into a long-lived comparison page when the answer's main value is maintaining a reusable side-by-side matrix. It is recorded as a Follow-Up Action unless the user explicitly asks to create the comparison page now.
_Avoid_: automatic comparison, query comparison

**Query Evidence Chain**:
The provenance path for a Query Archive: the query page cites Basis Pages, and strong claims cite Raw Evidence through those pages or direct locators. Query Archives do not create raw copies of the chat answer by default.
_Avoid_: chat raw, answer source

**Review Note**:
An optional note in a Query Archive explaining important search or judgment context, such as why a page was not used or why a source was considered out of scope. It is not a complete search log.
_Avoid_: search log, audit trail

**Query Log Entry**:
The `log.md` entry for creating or materially updating a Query Archive. It records the query title, whether the page was created or updated, the Answer Version, Basis Pages, and Follow-Up Action count.
_Avoid_: activity note, query history

**Archive Confirmation**:
The lightweight confirmation shown before writing a Query Archive. It summarizes title, destination, index status, Answer Version, Basis Pages, Raw Evidence readiness, Follow-Up Actions, status, and confidence; it is not a separate plan artifact.
_Avoid_: query plan, archive plan

**Query Archive Match**:
The conservative match used before creating a Query Archive. Exact title, explicit alias, or clearly same original question may update an existing Query Archive; fuzzy thematic similarity requires confirmation and may remain a linked separate page.
_Avoid_: duplicate query, similar answer

**Query Archive Metadata**:
The required frontmatter and body fields that make a Query Archive reusable: status, confidence, Answer Version, index status, Basis Pages, original question, answer summary, synthesized answer, Follow-Up Actions, and revision notes, with Raw Evidence and Review Notes added when required.
_Avoid_: query template fields, archive fields

**Query Archive Workflow**:
The first-class workflow for preserving Archive-Worthy Query answers as wiki knowledge. V1 is documentation- and template-led, with no separate script; it writes the Query Archive, updates index when indexed, and records a Query Log Entry after Archive Confirmation.
_Avoid_: query script, saved chat workflow
