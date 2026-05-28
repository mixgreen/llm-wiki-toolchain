# llm-wiki-toolchain

Hermes Agent skill for creating and maintaining Obsidian-based LLM Wiki knowledge bases.

This skill extends Karpathy's LLM Wiki pattern with a practical toolchain:

- wiki initialization templates
- raw source integrity checks with sha256
- entity / concept / topic / comparison / query page structure
- focused lint after ingest
- archive policy
- topic maps
- paragraph-level provenance using Markdown footnotes
- Chinese-first conventions for the author's Obsidian workflows

## Quick install

Clone this repository into the skill/tooling directory used by your agent:

```bash
git clone https://github.com/mixgreen/llm-wiki-toolchain.git
```

Then point your agent at the cloned `SKILL.md` and supporting files.

Detailed install notes for Claude Code, Gemini CLI, Codex CLI, and Hermes Agent are below.

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

## Notes

This repository is a skill package, not a standalone Python package. It is intended to be consumed by agent systems that can read instruction files plus supporting scripts/templates.

The exact global instruction file differs between agent CLIs and user setups. If your local Claude/Gemini/Codex configuration uses a different instruction path, keep the clone command and adapt only the loader note path.
