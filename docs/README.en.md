# llm-wiki-toolchain

> [中文](../README.md)

Agent skill for managing Obsidian-based LLM Wiki knowledge bases. Provides structured ingestion, linting, querying, and archive workflows for AI coding agents.

## Features

- Structured page types: entities, concepts, topics, comparisons, queries
- Raw source integrity (SHA-256 on body content)
- Automated lint: orphans, broken links, index consistency, tag audit, staleness
- Archive policies and topic maps
- Paragraph-level provenance with Markdown footnotes

## Installation

### Option 1: curl (recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/mixgreen/llm-wiki-toolchain/main/install.sh | bash
```

### Option 2: npx

```bash
npx llm-wiki-toolchain
```

Both options will:
1. Download the skill files
2. Detect installed AI agents (Claude Code, Gemini CLI, Codex CLI, OpenClaw, Hermes)
3. Let you select which agents to install into
4. Add loader notes to each agent's configuration file

### Option 3: Manual

```bash
git clone https://github.com/mixgreen/llm-wiki-toolchain.git ~/.claude/skills/llm-wiki-toolchain
```

Then add a loader note to your agent's instruction file (see table below).

## Agent configuration

| Agent | Install path | Instruction file |
|-------|-------------|-----------------|
| Claude Code | `~/.claude/skills/llm-wiki-toolchain/` | `CLAUDE.md` (project or `~/.claude/CLAUDE.md`) |
| Gemini CLI | `~/.gemini/skills/llm-wiki-toolchain/` | `GEMINI.md` (project or global) |
| Codex CLI | `~/.codex/skills/llm-wiki-toolchain/` | `AGENTS.md` (project or `~/.codex/AGENTS.md`) |
| OpenClaw | `~/.openclaw/skills/llm-wiki-toolchain/` | `OPENCLAW.md` (project or global) |
| Hermes Agent | `~/.hermes/skills/note-taking/llm-wiki-toolchain/` | Auto-discovered |

Loader note format (add to your instruction file):

```markdown
## Agent skills — LLM Wiki Toolchain

When working with Obsidian LLM Wiki knowledge bases, load and follow:
`<install-path>/SKILL.md`.

Resolve linked files relative to that directory:
- scripts/init.py
- scripts/lint.py
- templates/
- references/
```

## Quick start

```bash
# Initialize a new wiki
python3 <install-path>/scripts/init.py ~/Documents/MyVault "research-wiki" --topic "AI Research"

# Run lint
python3 <install-path>/scripts/lint.py ~/Documents/MyVault/research-wiki
```

For full workflow documentation (ingestion, querying, seeding, archive management), see `SKILL.md`.

## Update

```bash
# If installed via git clone:
cd <install-path> && git pull

# If installed via curl/npx:
re-run the installer
```

## Structure

```
├── SKILL.md              # Full workflow documentation (read by agents)
├── install.sh            # Interactive installer
├── bin/install.js        # npx entry point (delegates to install.sh)
├── scripts/
│   ├── init.py           # Wiki initialization
│   └── lint.py           # Automated health checks
├── templates/            # Page and structure templates
└── references/           # Design decisions and patterns
```

## License

MIT
