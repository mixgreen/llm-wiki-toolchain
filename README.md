# llm-wiki-toolchain

> [English](./docs/README.en.md)

用 AI agent 在 Obsidian 中构建和维护结构化知识库。

基于 [Karpathy 的 LLM Wiki 模式](https://x.com/karpathy/status/1881417542127472796)，将"读论文 → 提取知识 → 交叉引用 → 持续维护"的流程工具化，让 LLM agent 成为你的知识管理助手。

## 它能做什么

```
用户提供来源（论文/文章/笔记）
        ↓
Agent 读取 → 提取实体和概念 → 创建/更新 wiki 页面
        ↓
自动交叉引用、更新索引、追加日志
        ↓
定期 lint 检查：孤页、断链、过时内容、标签一致性
```

**核心能力：**

- **摄入** — 单来源精读或批量导入，自动建立交叉引用
- **查询** — 综合 wiki 知识回答问题，有价值的回答归档为新页面
- **检查** — 13 项自动化 lint（孤页、断链、索引一致性、标签审计、过时检测等）
- **播种** — 在摄入来源前先搭建知识骨架
- **归档** — 过时页面不删除，移入 `_archive/` 保留历史

## 安装

### Claude Code（推荐）

在 `~/.claude/settings.json` 的 `extraKnownMarketplaces` 中添加：

```json
{
  "extraKnownMarketplaces": {
    "llm-wiki-toolchain": {
      "source": {
        "source": "github",
        "repo": "mixgreen/llm-wiki-toolchain"
      }
    }
  }
}
```

然后在 Claude Code 中运行 `/install llm-wiki-toolchain` 即可。

### 其他 Agent（curl 一键安装）

```bash
curl -fsSL https://raw.githubusercontent.com/mixgreen/llm-wiki-toolchain/main/install.sh | bash
```

交互式选择要安装到哪些 agent（Gemini CLI、Codex CLI、OpenClaw、Hermes）。

<details>
<summary>手动安装</summary>

```bash
git clone https://github.com/mixgreen/llm-wiki-toolchain.git
```

将 `skills/llm-wiki-toolchain/` 目录复制到目标 agent 的 skill 路径，然后在指令文件中添加 loader note（格式见下方"Agent 配置"）。

</details>

安装器会自动检测本机的 AI agent 并写入配置：

| Agent | 安装路径 | 指令文件 |
|-------|---------|---------|
| Claude Code | `~/.claude/skills/llm-wiki-toolchain/` | `CLAUDE.md` |
| Gemini CLI | `~/.gemini/skills/llm-wiki-toolchain/` | `GEMINI.md` |
| Codex CLI | `~/.codex/skills/llm-wiki-toolchain/` | `AGENTS.md` |
| OpenClaw | `~/.openclaw/skills/llm-wiki-toolchain/` | `OPENCLAW.md` |
| Hermes Agent | `~/.hermes/skills/note-taking/llm-wiki-toolchain/` | 自动发现 |

## 快速开始

### 1. 初始化 wiki

```bash
python3 <安装路径>/scripts/init.py ~/Documents/MyVault "量子计算" --topic "量子计算与量子纠错"
```

生成的目录结构：

```
量子计算/
├── raw/                  # 不可变原始文档（论文、笔记）
├── wiki/
│   ├── entities/         # 人物、组织、产品
│   ├── concepts/         # 理论、框架、方法
│   ├── topics/           # 来源摘要、领域概览
│   ├── comparisons/      # 横向对比分析
│   └── queries/          # 值得留存的查询结果
├── _archive/             # 归档页面
├── _meta/topic-map.md    # 主题导航图
├── index.md              # 全量索引
├── log.md                # 活动日志
└── SCHEMA.md             # 约定与规范
```

### 2. 运行 lint

```bash
python3 <安装路径>/scripts/lint.py ~/Documents/MyVault/量子计算

# 常用选项
python3 ... --json              # JSON 输出
python3 ... --orphans           # 仅检查孤页
python3 ... --tags              # 标签审计
python3 ... --stale             # 过时页面（>90天未更新）
python3 ... --pages "a.md,b.md" # 只检查指定页面
```

### 3. 开始使用

安装完成后，在 agent 会话中直接说：

- "帮我摄入这篇论文到 wiki"
- "wiki 里关于 XX 的内容有哪些？"
- "跑一下 lint 看看 wiki 健康状况"
- "帮我搭建一个关于 YY 的知识骨架"

Agent 会自动加载 `SKILL.md` 中的完整工作流指令。

## Agent 配置

安装器自动写入的 loader note 格式：

```markdown
## Agent skills — LLM Wiki Toolchain

When working with Obsidian LLM Wiki knowledge bases, load and follow:
`<安装路径>/SKILL.md`.

Resolve linked files relative to that directory:
- scripts/init.py
- scripts/lint.py
- templates/
- references/
```

## 更新

```bash
# git clone 安装：
cd <安装路径> && git pull

# curl/npx 安装：
重新运行安装器即可
```

## 项目结构

```
├── .claude-plugin/plugin.json    # Claude Code plugin 清单
├── skills/llm-wiki-toolchain/
│   ├── SKILL.md                  # 完整工作流文档（agent 运行时读取）
│   ├── scripts/
│   │   ├── init.py               # Wiki 初始化
│   │   └── lint.py               # 自动化健康检查（13 项）
│   ├── templates/                # 页面和结构模板
│   │   └── page-templates/       # entity / concept / topic / comparison / query
│   └── references/               # 设计决策、模式参考、踩坑记录
├── install.sh                    # 交互式安装脚本（非 Claude Code agent 用）
└── README.md
```

## 许可证

MIT
