# Cross-Skill Capability Sync Pattern

When a skill that powers an L3 capability in [[Hermes能力阶梯]] is upgraded, propagate changes to the capability-tracking wiki. This is the recipe validated in the project-notebook skill v2 upgrade (2026-05-14).

## Trigger

A skill's SKILL.md is patched with new capabilities, scripts, or workflow sections. The skill itself should contain a "Skill 自身维护：能力追踪" section defining the sync contract (see project-notebook SKILL.md for the template).

## Sync Recipe

### 1. Audit what changed

Identify the delta:
- New Python scripts → L1 tool entities
- New workflows/protocols → Update L3 capability concept + detail page
- New design decisions → Decision record page
- New L4 instances → Instance entity page
- Dependency changes → Update dependency stack in L2 skill entity + L3 detail page

### 2. Create entity pages (L1/L2/L4)

Use execute_code for batch creation — 5+ pages created in one call beats N individual write_file calls:

```python
from hermes_tools import write_file

BASE = "/path/to/Hermes能力阶梯"

# L1 tool entity
write_file(f"{BASE}/wiki/entities/tools/<tool>.md", """...""")

# L2 skill entity (update if exists, create if new)
write_file(f"{BASE}/wiki/entities/skills/<skill>.md", """...""")

# L4 instance entity (if applicable)
write_file(f"{BASE}/wiki/entities/instances/<instance>.md", """...""")
```

### 3. Create/update L3 pages

- **Concept page** (`wiki/concepts/capabilities/`): If new capability, create. If existing, update capability list.
- **Detail page** (`wiki/topics/capability-details/`): Full workflow mermaid diagram + dependency stack + instances table + decision links.
- **Decision record** (`wiki/topics/decisions/`): Background, alternatives considered, decision, rationale, consequences.

### 4. Update 能力全景图

This is the most complex update. The mermaid graph needs:
- New nodes in the correct L0-L4 subgraph
- New edges for dependencies
- Updated inventory tables (L4/L3/L2/L1/L0)
- Updated decision records table
- Updated 待建设能力 list

Use the full file rewrite pattern — the mermaid graph restructuring is too complex for targeted patches:

```python
from hermes_tools import write_file
# Read current version, build updated version with all changes, write back
write_file(f"{BASE}/wiki/topics/capability-maps/能力全景图.md", updated_content)
```

### 5. Update index.md

Add new pages under correct sections. Update page count. Use [[wikilink]] format for all entries (not plain text) to avoid lint errors.

### 6. Verify with lint.py

```bash
python3 .../llm-wiki-toolchain/scripts/lint.py "<wiki-root>"
```

Target: zero orphans, zero broken links, index consistency. If orphans remain, add inbound wikilinks from parent entity pages.

### 7. Log both sides

- Hermes能力阶梯 `log.md`: Standard ingest format
- Source skill's notebook (e.g., DILU): `sync` entry

## Pitfalls

- **Don't use plain text for L4 instances in index.md.** The lint script checks wikilink resolution — `DILU-离子阱测控系统` fails, `[[DILU-离子阱测控系统]]` passes if the page exists.
- **Mermaid node IDs must be unique.** Adding a new node like `ProjNB` means checking it doesn't collide with existing IDs.
- **execute_code read_file returns cached results.** If you read a file earlier in the conversation with the terminal read_file tool, execute_code's read_file may return a cache hit with `status: unchanged`. Use terminal or write_file directly for content you already know.
- **Orphans from leaf tools are expected.** init.py, query.py are leaf nodes — add an inbound link from the parent skill entity page to satisfy lint.
