# Capability Tracking Wiki Pattern

When an LLM Wiki tracks capabilities (like Hermes能力阶梯), structure it with **overview + detail pages** rather than one monolithic page.

## Pattern

For capability-showcase wikis, keep the base `entities / concepts / topics` split but refine it into ability-oriented subdirectories:

```
wiki/
├── entities/
│   ├── tools/                 ← L1 tools / libraries / built-in tools
│   ├── skills/                ← L2 Hermes skills
│   ├── infra/                 ← L0 system/runtime/storage infrastructure
│   └── instances/             ← L4 real user-facing outcomes / wiki instances
├── concepts/
│   ├── capabilities/          ← abstract capability concepts
│   ├── dependency-chains/      ← reusable dependency patterns
│   ├── principles/             ← design principles and conventions
│   └── maturity-models/        ← status/maturity criteria
└── topics/
    ├── capability-maps/        ← Hub: Mermaid dependency graph + inventory tables
    ├── capability-details/     ← Detail page for each L3 capability
    ├── decisions/              ← decision records
    ├── demos/                  ← evidence pages showing real tasks
    ├── evaluations/            ← maturity evaluations
    ├── timelines/              ← growth timeline
    └── roadmap/                ← future capability roadmap
```

Minimum page set for a mature L3 capability:
- `[[能力全景图]]` hub page
- `[[<能力A>（能力详情）]]` capability card
- at least one `Demo：...` evidence page
- one `评估：...能力成熟度` evaluation page
- links to instances under `entities/instances/`

## Overview Page (能力全景图)

Stays lean. Contents:
- Mermaid dependency graph (covers ALL capabilities in one visual)
- Summary inventory tables (L3/L2/L1/L0, one row per item with status)
- Links to each capability's detail page
- Links to decision records
- 待建设能力 list

## Detail Page Template

Each L3 capability gets its own page. Sections:

```markdown
# <能力名>（能力详情）

> 层级：L3 | 状态：🟢/🟡/🔴 | 概览：[[能力全景图]]

## 能力描述
一句话 + 核心操作列表

## <工作流名称> Mermaid 图
flowchart TD of the capability's workflow

## 依赖栈
ASCII tree showing L3 → L2 → L1 → L0

## 当前实例
Table of instances this capability has created

## 关键决策
Table of decision records relevant to this capability

## 相关实体
- [[entity]] links

## 相关概念
- [[concept]] links
```

## Index Integration

Add a "能力详情" subsection under Topics:

```markdown
## 主题
### 全景图
- [[能力全景图]]

### 能力详情
- [[<能力A>（能力详情）]]
```

## When to Split

**Split** when:
- The overview page exceeds ~150 lines
- A capability has its own workflow diagram
- A capability has its own set of decision records / instances
- You expect more capabilities to join at the same layer

**Don't split** when there's only 1-2 capabilities and each has minimal detail.

## Current Instance

This pattern is applied in [[Hermes能力阶梯]] wiki. First detail page: [[LLM Wiki 管理（能力详情）]].
