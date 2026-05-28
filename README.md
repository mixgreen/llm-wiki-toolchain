# llm-wiki-toolchain

**中文文档**: [README.zh-CN.md](./README.zh-CN.md)

Obsidian-based LLM Wiki knowledge base management system.

This toolchain helps you maintain structured knowledge bases with:
- Raw source integrity checks (SHA-256)
- Organized page types: entities, concepts, topics, comparisons, queries
- Focused linting after ingestion
- Archive policies and topic maps
- Paragraph-level provenance with Markdown footnotes
- Chinese-first conventions for Obsidian workflows

## Installation

### Option 1: curl (recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/mixgreen/llm-wiki-toolchain/main/install.sh | bash
```

This will:
1. Download the toolchain
2. Detect installed AI agents (Claude, Gemini, Codex, OpenClaw, Hermes)
3. Let you select which agents to install into (interactive checkbox menu)
4. Automatically add loader notes to each agent's configuration

### Option 2: npm/npx

```bash
npx llm-wiki-toolchain
```

Or install globally first:

```bash
npm install -g llm-wiki-toolchain
llm-wiki-toolchain
```

Same interactive installation process as curl.

### Option 3: Manual installation

Clone the repository and manually copy to your agent's skill directory:

```bash
git clone https://github.com/mixgreen/llm-wiki-toolchain.git
```

Then follow the agent-specific instructions below.

## Claude Code

Recommended location:

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/mixgreen/llm-wiki-toolchain.git ~/.claude/skills/llm-wiki-toolchain
```

Then add a short loader note to your Claude Code project or global instructions. For example, in `CLAUDE.md`:

```markdown
## Agent skills

When working with Obsidian LLM Wiki knowledge bases, load and follow:
`~/.claude/skills/llm-wiki-toolchain/SKILL.md`.

Resolve linked files relative to that directory, especially:
- scripts/init.py
- scripts/lint.py
- templates/
- references/
```

If your Claude Code setup already uses a different skill directory, clone the repository there and update the path above.

## Gemini CLI

Recommended location:

```bash
mkdir -p ~/.gemini/skills
git clone https://github.com/mixgreen/llm-wiki-toolchain.git ~/.gemini/skills/llm-wiki-toolchain
```

Then add a loader note to your Gemini instructions file. Common choices are a project `GEMINI.md` or your global Gemini context file if your setup uses one:

```markdown
## Agent skills

When the task involves an LLM Wiki, Obsidian knowledge base, source ingest, wiki lint, or wiki querying, read and follow:
`~/.gemini/skills/llm-wiki-toolchain/SKILL.md`.

Resolve relative paths from `~/.gemini/skills/llm-wiki-toolchain/`.
```

## Codex CLI

Recommended location:

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/mixgreen/llm-wiki-toolchain.git ~/.codex/skills/llm-wiki-toolchain
```

Then add a loader note to your Codex instructions. Depending on your setup this may be a project `AGENTS.md` or a global Codex instructions file:

```markdown
## Agent skills

When working on LLM Wiki / Obsidian knowledge-base tasks, use this skill:
`~/.codex/skills/llm-wiki-toolchain/SKILL.md`.

Read the skill before acting. Supporting scripts and templates are relative to:
`~/.codex/skills/llm-wiki-toolchain/`.
```

## OpenClaw

Recommended location:

```bash
mkdir -p ~/.openclaw/skills
git clone https://github.com/mixgreen/llm-wiki-toolchain.git ~/.openclaw/skills/llm-wiki-toolchain
```

Then add a loader note to your OpenClaw instructions file (typically `OPENCLAW.md` in project root or global config):

```markdown
## Agent skills

When working with Obsidian LLM Wiki knowledge bases, load and follow:
`~/.openclaw/skills/llm-wiki-toolchain/SKILL.md`.

Resolve linked files relative to that directory, especially:
- scripts/init.py
- scripts/lint.py
- templates/
- references/
```

## Hermes Agent

For Hermes Agent, clone directly under the profile's skills directory:

```bash
mkdir -p ~/.hermes/skills/note-taking
git clone https://github.com/mixgreen/llm-wiki-toolchain.git ~/.hermes/skills/note-taking/llm-wiki-toolchain
```

Then in a new Hermes session the skill should be available as:

```text
skill_view(name='llm-wiki-toolchain')
```

If using a named Hermes profile, use that profile's skill directory instead:

```bash
mkdir -p ~/.hermes/profiles/<profile>/skills/note-taking
git clone https://github.com/mixgreen/llm-wiki-toolchain.git ~/.hermes/profiles/<profile>/skills/note-taking/llm-wiki-toolchain
```

## Initialize a new wiki

```bash
python3 scripts/init.py "<vault-or-parent-path>" "<wiki-name>" --topic "<topic>"
```

Example:

```bash
python3 ~/.hermes/skills/note-taking/llm-wiki-toolchain/scripts/init.py \
  "$HOME/Documents" "My LLM Wiki" --topic "AI research notes"
```

## Run lint

```bash
python3 scripts/lint.py "<wiki-root>"
python3 scripts/lint.py "<wiki-root>" --json
python3 scripts/lint.py "<wiki-root>" --pages "wiki/concepts/PageA.md,wiki/topics/PageB.md"
python3 scripts/lint.py "<wiki-root>" --stale
python3 scripts/lint.py "<wiki-root>" --tags
```

## Update

Pull the latest version from GitHub:

```bash
cd ~/.hermes/skills/note-taking/llm-wiki-toolchain  # or your chosen install path
git pull
```

## Structure

```text
.
├── SKILL.md
├── scripts/
│   ├── init.py
│   └── lint.py
├── templates/
│   ├── SCHEMA.md
│   ├── index.md
│   ├── log.md
│   ├── topic-map.md
│   └── page-templates/
└── references/
```

## Config file reference

Quick lookup for where to put the skill loader note in each CLI:

| CLI | Install path | Instruction file |
|-----|-------------|-----------------|
| Claude Code | `~/.claude/skills/llm-wiki-toolchain/` | `CLAUDE.md` (project root or `~/.claude/CLAUDE.md`) |
| Gemini CLI | `~/.gemini/skills/llm-wiki-toolchain/` | `GEMINI.md` (project root or global context) |
| Codex CLI | `~/.codex/skills/llm-wiki-toolchain/` | `AGENTS.md` (project root or `~/.codex/AGENTS.md`) |
| OpenClaw | `~/.openclaw/skills/llm-wiki-toolchain/` | `OPENCLAW.md` (project root or global config) |
| Hermes Agent | `~/.hermes/skills/note-taking/llm-wiki-toolchain/` | Auto-discovered; load with `skill_view(name='llm-wiki-toolchain')` |

## Notes

This repository is a skill package, not a standalone Python package. It is intended to be consumed by agent systems that can read instruction files plus supporting scripts/templates.

The exact global instruction file differs between agent CLIs and user setups. If your local Claude/Gemini/Codex configuration uses a different instruction path, keep the clone command and adapt only the loader note path.
