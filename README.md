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

## Usage in Hermes

Place this directory under your Hermes skills directory, for example:

```bash
~/.hermes/skills/note-taking/llm-wiki-toolchain/
```

Then load it from Hermes with:

```text
skill_view(name='llm-wiki-toolchain')
```

## Initialize a new wiki

```bash
python3 scripts/init.py "<vault-or-parent-path>" "<wiki-name>" --topic "<topic>"
```

## Run lint

```bash
python3 scripts/lint.py "<wiki-root>"
python3 scripts/lint.py "<wiki-root>" --json
python3 scripts/lint.py "<wiki-root>" --pages "wiki/concepts/PageA.md,wiki/topics/PageB.md"
```

## Notes

This repository is a skill package, not a standalone Python package. It is intended to be consumed by Hermes Agent's skill system.
