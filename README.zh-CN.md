# llm-wiki-toolchain

基于 Obsidian 的 LLM Wiki 知识库管理系统。

本工具链帮助你维护结构化的知识库，提供以下能力：

- 原始来源完整性校验（SHA-256 哈希）
- 分类页面结构：实体（entities）、概念（concepts）、主题（topics）、对比（comparisons）、查询（queries）
- 摄入后针对性 lint 检查
- 归档策略与主题导航图（topic map）
- 段落级溯源（使用 Markdown 脚注）
- 中文优先的 Obsidian 工作流约定

## 安装

### 方式一：curl 一键安装（推荐）

```bash
curl -fsSL https://raw.githubusercontent.com/mixgreen/llm-wiki-toolchain/main/install.sh | bash
```

安装流程：

1. 自动下载工具链
2. 检测本机已安装的 AI agent（Claude Code、Gemini CLI、Codex CLI、OpenClaw、Hermes Agent）
3. 交互式勾选要安装到哪些 agent
4. 自动在对应 agent 的配置文件中添加 loader note

### 方式二：npm / npx 安装

```bash
npx llm-wiki-toolchain
```

或先全局安装：

```bash
npm install -g llm-wiki-toolchain
llm-wiki-toolchain
```

交互流程与 curl 版本一致。

### 方式三：手动安装

克隆仓库后手动复制到目标 agent 的 skill 目录：

```bash
git clone https://github.com/mixgreen/llm-wiki-toolchain.git
```

然后参考下方各 agent 的手动安装说明。

## 各 Agent 手动安装指南

### Claude Code

推荐安装位置：

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/mixgreen/llm-wiki-toolchain.git ~/.claude/skills/llm-wiki-toolchain
```

在 `CLAUDE.md`（项目根目录或 `~/.claude/CLAUDE.md`）中添加 loader note：

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

### Gemini CLI

推荐安装位置：

```bash
mkdir -p ~/.gemini/skills
git clone https://github.com/mixgreen/llm-wiki-toolchain.git ~/.gemini/skills/llm-wiki-toolchain
```

在 `GEMINI.md`（项目根目录或全局配置文件）中添加 loader note：

```markdown
## Agent skills

When the task involves an LLM Wiki, Obsidian knowledge base, source ingest, wiki lint, or wiki querying, read and follow:
`~/.gemini/skills/llm-wiki-toolchain/SKILL.md`.

Resolve relative paths from `~/.gemini/skills/llm-wiki-toolchain/`.
```

### Codex CLI

推荐安装位置：

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/mixgreen/llm-wiki-toolchain.git ~/.codex/skills/llm-wiki-toolchain
```

在 `AGENTS.md`（项目根目录或 `~/.codex/AGENTS.md`）中添加 loader note：

```markdown
## Agent skills

When working on LLM Wiki / Obsidian knowledge-base tasks, use this skill:
`~/.codex/skills/llm-wiki-toolchain/SKILL.md`.

Read the skill before acting. Supporting scripts and templates are relative to:
`~/.codex/skills/llm-wiki-toolchain/`.
```

### OpenClaw

推荐安装位置：

```bash
mkdir -p ~/.openclaw/skills
git clone https://github.com/mixgreen/llm-wiki-toolchain.git ~/.openclaw/skills/llm-wiki-toolchain
```

在 `OPENCLAW.md`（项目根目录或全局配置）中添加 loader note：

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

### Hermes Agent

直接克隆到 profile 的 skills 目录：

```bash
mkdir -p ~/.hermes/skills/note-taking
git clone https://github.com/mixgreen/llm-wiki-toolchain.git ~/.hermes/skills/note-taking/llm-wiki-toolchain
```

新会话中自动可用，通过以下方式加载：

```text
skill_view(name='llm-wiki-toolchain')
```

如果使用命名 profile，改用对应路径：

```bash
mkdir -p ~/.hermes/profiles/<profile名>/skills/note-taking
git clone https://github.com/mixgreen/llm-wiki-toolchain.git ~/.hermes/profiles/<profile名>/skills/note-taking/llm-wiki-toolchain
```

## 初始化新 Wiki

```bash
python3 scripts/init.py "<vault或父目录路径>" "<wiki名称>" --topic "<主题描述>"
```

示例：

```bash
python3 ~/.hermes/skills/note-taking/llm-wiki-toolchain/scripts/init.py \
  "$HOME/Documents" "My LLM Wiki" --topic "AI research notes"
```

## 运行 Lint

```bash
python3 scripts/lint.py "<wiki根目录>"
python3 scripts/lint.py "<wiki根目录>" --json
python3 scripts/lint.py "<wiki根目录>" --pages "wiki/concepts/PageA.md,wiki/topics/PageB.md"
python3 scripts/lint.py "<wiki根目录>" --stale
python3 scripts/lint.py "<wiki根目录>" --tags
```

参数说明：

| 参数 | 作用 |
|------|------|
| 无参数 | 基础 lint：检查 frontmatter、结构完整性 |
| `--json` | 以 JSON 格式输出报告 |
| `--pages` | 只检查指定的页面（逗号分隔） |
| `--stale` | 检查陈旧页面（长时间未更新） |
| `--tags` | 审计标签分类（tag taxonomy）一致性 |

## 更新

拉取最新版本：

```bash
cd ~/.hermes/skills/note-taking/llm-wiki-toolchain  # 或你选择的安装路径
git pull
```

## 目录结构

```text
.
├── SKILL.md                   # 主 skill 指令文档
├── scripts/
│   ├── init.py                # Wiki 初始化脚本
│   └── lint.py                # Lint 检查脚本
├── templates/
│   ├── SCHEMA.md              # 结构与规范模板
│   ├── index.md               # 全量索引模板
│   ├── log.md                 # 变更日志模板
│   ├── topic-map.md           # 主题导航图模板
│   └── page-templates/        # 各类页面模板
└── references/                # 参考资料
```

## 配置文件速查表

各 agent 的安装路径与指令文件对照：

| Agent | 安装路径 | 指令文件 |
|-------|---------|---------|
| Claude Code | `~/.claude/skills/llm-wiki-toolchain/` | `CLAUDE.md`（项目根目录或 `~/.claude/CLAUDE.md`） |
| Gemini CLI | `~/.gemini/skills/llm-wiki-toolchain/` | `GEMINI.md`（项目根目录或全局配置） |
| Codex CLI | `~/.codex/skills/llm-wiki-toolchain/` | `AGENTS.md`（项目根目录或 `~/.codex/AGENTS.md`） |
| OpenClaw | `~/.openclaw/skills/llm-wiki-toolchain/` | `OPENCLAW.md`（项目根目录或全局配置） |
| Hermes Agent | `~/.hermes/skills/note-taking/llm-wiki-toolchain/` | 自动发现；用 `skill_view(name='llm-wiki-toolchain')` 加载 |

## 说明

本仓库是一个 **skill 包**，不是独立的 Python 包。它被设计为由 AI agent 系统消费——agent 读取指令文件（`SKILL.md`）并按需调用配套的脚本和模板。

不同 agent CLI 的全局指令文件路径各不相同。如果你本地的 Claude / Gemini / Codex 使用了不同的指令路径，保留 clone 命令不变，只修改 loader note 中的路径即可。

---

**English version**: [README.md](./README.md)
