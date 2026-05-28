# Seeding Example: 计算机系统知识库

本文件记录 `计算机系统知识库` (2026-05-13) 播种会话的关键决策，作为未来同类领域 wiki 播种的参考。

## 领域分类法（9 个核心知识域）

| 领域 | SCHEMA domain tag | 概览页 |
|------|-------------------|--------|
| 计算机体系结构 | `architecture` | 计算机体系结构概览 |
| 操作系统 | `os` | 操作系统概览 |
| 计算机网络 | `network` | 计算机网络概览 |
| 数据库系统 | `database` | 数据库系统概览 |
| 分布式系统 | `distributed` | 分布式系统概览 |
| 软件工程 | `se` | 软件工程概览 |
| 架构设计 | `design` | 架构设计概览 |
| 性能工程 | `performance` | 性能工程概览 |
| 安全工程 | `security` | 安全工程概览 |

## 9+8 拆分逻辑

- **9 个领域概览页**（`wiki/topics/`）：每个域的入口页，定义子领域、关键概念、待深入问题
- **8 个核心概念页**（`wiki/concepts/`）：被多域引用的跨域基础概念

按被引频率排序：
1. [[分布式事务]] — 被 7 个页面引用（最高频断链）
2. [[性能建模]] — 3 refs
3. [[负载均衡]], [[ATAM]], [[设计模式]] — 各 2 refs

其余 40+ 个断链为各域专属概念（如 [[虚拟内存]]、[[TCP/IP 协议栈]]、[[加密基础]]），属于第二梯队建设目标。

## 标签规范（SCHEMA.md 中定义）

实体分类：`person`, `organization`, `product`, `standard`, `language`
概念域标签：`architecture`, `os`, `network`, `database`, `distributed`, `se`, `design`, `performance`, `security`
主题类型：`source-summary`, `comparison`, `case-study`, `exam`, `synthesis`, `domain-overview`
页面状态：`draft`, `reviewed`, `stable`

## 概览页模板（本次使用）

```yaml
tags: [topic, domain-overview, <domain>]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: draft
```

章节结构：
- **TL;DR**：一句话定义这个域
- **概述**：1 段核心观点
- **核心子领域**：5 个子领域，每个附一句话说明
- **关键概念**：逗号分隔的 [[wikilinks]]（前向声明）
- **待深入问题**：2-3 个开放性问题
- **来源**：待摄入

## 概念页模板（本次使用）

```yaml
tags: [concept, <domain1>, <domain2>]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: draft
```

章节结构：
- **TL;DR**：一句话定义
- **定义**：2-3 段精确描述
- **重要性**：为什么架构师需要理解
- **核心机制**：关键技术细节
- **反面观点 / 局限性**：批判性视角
- **相关概念**：逗号分隔的 [[wikilinks]]
- **来源**：待摄入

## 播种后的 lint 处理

- 孤页（领域概览页无入链）：正常，标记为预期现象，不立即修复
- 断链（前向声明未建概念）：正常，作为建设优先级清单使用
- 索引中的模板占位符（`[[Entity Name]]` 等）：必须移除，否则 lint 报冗余
