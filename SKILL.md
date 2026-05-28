---
name: llm-wiki-toolchain
description: 在 Obsidian 中创建和维护 LLM Wiki 仓库——摄入来源、查询知识、质量检查、管理索引与日志。基于 Karpathy 的 LLM Wiki 模式。
---

# LLM Wiki 工具链

在 Obsidian vault 中创建和维护 LLM Wiki 的完整工具链。基于 LLM Wiki 模式。

## 核心架构

三层结构，位于 wiki 目录内：

```
<wiki-root>/
├── raw/                      # 不可变的原始文档（论文、文章、笔记、源码、附件）
├── wiki/                     # LLM 生成的 markdown 页面
│   ├── entities/             # 实体：人物、组织、产品、离子种类等
│   ├── concepts/             # 概念：理论、框架、方法、技术等
│   ├── topics/               # 主题：来源摘要、综述、领域概览
│   ├── comparisons/          # 横向对比分析：A vs B、方案比较、技术取舍
│   └── queries/              # 值得留存的查询结果、综合回答、临时研究结论
├── _archive/                 # 归档页面：过时、重复、被替代页面；默认 lint 忽略
├── _meta/
│   └── topic-map.md          # 人类友好的主题地图：按领域、问题、路线组织页面
├── index.md                  # 所有当前 wiki 页面的目录索引
├── log.md                    # 当前年份活动日志（按年份优先、500 条兜底轮转）
└── SCHEMA.md                 # 约定、页面格式、工作流（wiki 的"章程"）
```

> 设计评审结论见 `references/llm-wiki-upgrade-decisions.md`。本 skill 是用户日常使用和演进的主入口；`llm-wiki` 仅作为上游参考。

## 何时使用

- 在用户的 Obsidian vault 中搭建新的研究/学习 wiki
- 向已有 wiki 摄入新来源（论文、文章、书籍章节）
- 通过综合 wiki 知识来回答问题
- 对 wiki 进行健康检查：发现矛盾、孤页、缺失

本 skill 依赖 `obsidian` skill 提供底层 vault CRUD 操作，使用时一并加载。

## 会话开始时的强制对齐

当用户已经有一个现成 wiki 时，任何 ingest / query / lint 之前都先做三步对齐：

1. 读 `SCHEMA.md`，确认本仓库的域、标签、质量字段与工作流约定。
2. 读 `index.md`，确认当前页面清单与命名。
3. 读最近 20-30 条 `log.md`，避免重复工作与误判最近变更。

对于 100+ 页的大型 wiki，在创建新页面前再补一次全库 `search_files` 扫描相关主题。

## 初始化：创建新 LLM Wiki

运行 init 脚本搭建 wiki（可放在 Obsidian vault 内或 vault 外的独立目录——先与用户确认位置）：

```bash
python3 <SKILL_DIR>/scripts/init.py "<vault路径>" "<wiki名称>" [--topic "主题简述"]
```

> `<SKILL_DIR>` 是本 skill 的安装目录。安装脚本会将实际路径写入各 agent 的指令文件中。

init 脚本会：
1. 创建目录结构（raw/、wiki/entities、wiki/concepts、wiki/topics、wiki/comparisons、wiki/queries、_archive、_meta）
2. 从模板播种 `index.md`、`log.md`、`SCHEMA.md`、`_meta/topic-map.md`
3. 输出创建报告

初始化后，和用户一起审阅并定制 `SCHEMA.md`。SCHEMA.md 是最重要的文件——它定义了确保所有后续摄入和查询一致性的约定。

## 播种：搭建知识骨架

当用户想在摄入来源之前先搭建知识结构时使用。这是 ingest 之前的中间步骤——先建骨架，后填内容。

### 何时播种

- 用户说"先把大纲搭起来""搭骨架""建种子页面"或类似表达
- 领域明确但还没有具体来源材料
- 用户想先看到知识全景再决定从哪里深入

### 播种内容

两层次页面结构：

**第一层：领域概览页（`wiki/topics/`）**
- 每个核心知识域一个入口页面
- 章节：TL;DR、概述、核心子领域、关键概念（用 [[wikilink]] 前向声明）、待深入问题
- 类型标签：`tags: [topic, domain-overview, <domain>]`
- 子领域以列表形式列出，每个附一句话说明
- 关键概念用 [[wikilink]] 链接到 concepts/ 下已存在或待建的页面

**第二层：核心概念页（`wiki/concepts/`）**
- 跨域基础概念（被多个概览页引用的优先）
- 章节：TL;DR、定义、重要性、核心机制、反面观点/局限性、相关概念
- 所有页面标记 `status: draft`

### 页面创建阈值

- **创建页面**：某实体/概念在 2+ 个来源中出现，或它对单一来源是核心内容。
- **追加到已有页面**：来源只是补充说明、局部修正或边缘提及。
- **不要建页**：偶发提及、细枝末节、明显超出当前 wiki 域的内容。
- **拆分页**：页面明显变长、已经不再能快速扫读时，拆成更细子页并互相链接。

### 播种方法

用 `execute_code` + Python 批量创建页面，效率远高于逐个 write_file。示例：

```python
# 用 execute_code 运行，循环 write_file 创建所有页面
pages = {
    "页面名1": {"tags": [...], "tldr": "...", "content_fields": {...}},
    "页面名2": ...,
}
for name, data in pages.items():
    content = f"""---
tags: [...]
---
# {name}
> {data['tldr']}
..."""
    write_file(f"{base}/wiki/topics/{name}.md", content)
```

### 播种后的 lint 预期

首次播种后 lint 会有两类"预期"问题，不需立即修复：

- **孤页**：所有领域概览页因为彼此未交叉链接，会被标记为孤页。这是正常的——它们作为顶层入口，入链将随着概念页补充自然形成
- **断链**：概览页中的"关键概念"列表用 [[wikilink]] 前向声明了尚未创建的概念页。这些断链是建设清单，不是 bug

播种后向用户呈现：
- 创建了多少页面
- 哪些概念被最多页面引用（从 lint 的断链频率可推断——引用最多的优先建）
- 下一步选择：挑领域纵向深入 vs 补充高频被引概念 vs 开始摄入来源

### 播种注意事项

> 完整示例见 `references/seeding-cs-domain-example.md`——9 领域分类法、页面模板、标签规范、播种后 lint 处理。

- **先定制 SCHEMA.md。** 领域标签、实体分类、概念域等定义好了再播种，避免后续大批量改标签
- **控制页面数量。** 首次播种 15-25 页为宜（9+8 是已验证的合理规模）。太多页面会让用户不知所措，且每页只有 1-2 句话没有价值
- **不要批量创建实体页。** 实体页（人物、组织、产品）需要来源支撑细节才有意义。播种阶段只建概念和领域概览
- **所有页面标记 draft。** 播种阶段的内容是 LLM 凭常识写的，未经来源验证，不要标记为 reviewed/stable
- **使用 write_file 而非 patch。** 播种是全新创建，用 write_file 最可靠

### 词汇与标签纪律

- 先定义 wiki 的标签 taxonomy，再开始大规模写页。
- 每个页面上的 tag 都应该能在 SCHEMA.md 的 taxonomy 中找到。
- 如果需要新 tag，先补 taxonomy，再使用它。
- 在大型 wiki 中，tag audit 应作为 lint 的固定检查项。

## 摄入：处理新来源

toolchain 支持两种摄入模式：

| 模式 | 默认性 | 适用场景 |
|------|--------|----------|
| **单来源摄入** | 默认 | 重要论文、核心文档、需要用户判断重点的资料 |
| **批量摄入** | 用户明确说"批量/一批/这些文件/整个目录"时启用 | 同类资料、目录归档、源码资料、历史资料导入 |

批量摄入规则：
1. 先读所有来源，整体识别实体、概念和更新范围。
2. 写入前先输出摄入计划：raw 文件列表、预计新增页面、预计更新页面、风险页面。
3. 如果预计触及超过 10 个 wiki 页面，必须确认范围。
4. 最后统一更新 `index.md` 和 `log.md`，避免重复写导航。

当用户要向 wiki 添加单个新来源时，按以下步骤操作：

0. **预扫描（Pre-scan）。** 读完来源后，提取所有候选实体/概念，对每个候选执行 `search_files` 全库搜索，生成摄入计划表格：

   ```
   | 实体/概念     | 状态       | 匹配页面           | 操作     |
   |---------------|-----------|-------------------|---------|
   | MS门          | 已存在     | ms-gate.md        | 更新     |
   | 量子纠错       | 已存在     | quantum-ec.md     | 更新     |
   | 某某新算法     | 未找到     | —                 | 新建     |
   | 某人名         | 模糊匹配   | 某某.md?          | 确认     |
   ```

   用 clarify() 展示表格，让用户确认或调整后批量执行。这一步是为了避免重复创建已有页面（a 问题）和漏更新应该更新的页面（b 问题）。

1. **读取来源。** 如果来源在 raw/ 中，优先用 pymupdf（`python3 -c "import pymupdf; ..."`）提取 PDF 文本，用 read_file 读取 markdown。如果是 URL，用 web_extract 或 browser。如果是图片，用 vision_analyze。如果 pymupdf 不可用，退而用 `pdftotext`。

   **raw/ 完整性要求：** 所有写入 `raw/` 的原始资料必须记录 `sha256`。raw/ 是不可变来源层，不应被直接覆盖或静默修改。重新摄入同一来源时，应重算哈希；若哈希不同，标记为来源漂移并让用户决定是否新建版本或更新 wiki 页面。

2. **与用户讨论。** 预扫描确认后，用 clarify() 呈现关键要点。询问：
   - 哪些内容需要重点强调？
   - 有哪些已有页面需要更新？
   - 有哪些新的实体/概念需要单独建页？

3. **创建来源摘要页。** 使用页面模板，写入 `wiki/topics/<来源标题>.md`。先加载模板：`skill_view(name='llm-wiki-toolchain', file_path='templates/page-templates/source-summary.md')`。

4. **更新实体页。** 对来源中提到的每个实体：
   - 如果实体页已存在，读取后添加引用此来源的章节，用 [[wikilink]] 链回来源摘要
   - 如果不存在，用实体模板创建新页面

5. **更新概念页。** 与实体同理。从来源中提取关键概念并整合。

6. **添加交叉引用。** 确保 [[wikilinks]] 双向流通——来源 → 实体/概念，实体/概念 → 来源。

7. **更新 index.md。** 为所有新创建的页面按类别追加条目。更新被修改页面的摘要。

8. **追加 log.md。** 使用格式：
   ```
   ## [YYYY-MM-DD] ingest | 来源标题
   - 新建：[[页面1]]、[[页面2]]
   - 更新：[[页面3]]、[[页面4]]
   - 关键新增：简述
   ```

9. **自动 lint（策略 A：静默通过，有问题才报告）。** ingest 完成后立即运行 lint，但只报告**本次 ingest 引入的新问题**，不翻旧账。具体做法：
   - 记录本次 ingest 新建和更新的页面列表
   - 运行 lint.py 后，只输出涉及这些页面的问题（断链、frontmatter 缺失、过时候选页等）
   - 如果所有本次涉及的页面都通过，静默——不打断用户
   - 如果发现问题，输出警告列表并建议修复

   实现方式：lint.py 增加 `--pages "page1,page2,..."` 参数，只检查指定页面的问题。ingest 流程在步骤 9 调用 `lint.py <wiki-root> --pages <本次涉及的页面>`。

## 查询：搜索与综合

当用户就 wiki 内容提问时：

1. **先读 index.md** 定位相关页面。

2. **阅读候选页面。** 深入阅读最相关的页面。

3. **综合回答。** 用 [[wikilinks]] 标注引用来源。

4. **询问是否归档。** 如果回答有价值，问："需要把这份分析归档为新的 wiki 页面吗？" 如果同意，写入 `wiki/topics/` 或 `wiki/concepts/` 并更新 index。

输出格式（询问用户偏好）：
- Markdown 页面（默认）
- 对比表格
- Marp 幻灯片
- 图表（Matplotlib）

## 检查：健康巡检

定期运行检查，保持 wiki 健康。有两种方式：

### 自动检查（推荐）

运行 lint.py 脚本，自动检测孤页、断链、索引一致性、raw 完整性、质量字段、页面大小、日志轮转和主题地图：

```bash
python3 <SKILL_DIR>/scripts/lint.py "<wiki-root>"

# 单项检查
python3 <SKILL_DIR>/scripts/lint.py "<wiki-root>" --orphans       # 仅孤页
python3 <SKILL_DIR>/scripts/lint.py "<wiki-root>" --broken        # 仅断链
python3 <SKILL_DIR>/scripts/lint.py "<wiki-root>" --index         # 仅索引一致性
python3 <SKILL_DIR>/scripts/lint.py "<wiki-root>" --raw           # 仅 raw/ sha256 完整性
python3 <SKILL_DIR>/scripts/lint.py "<wiki-root>" --quality       # 仅 frontmatter/质量字段
python3 <SKILL_DIR>/scripts/lint.py "<wiki-root>" --stale         # 仅过时候选页
python3 <SKILL_DIR>/scripts/lint.py "<wiki-root>" --tags          # 仅标签 taxonomy 审计
python3 <SKILL_DIR>/scripts/lint.py "<wiki-root>" --log           # 仅日志轮转
python3 <SKILL_DIR>/scripts/lint.py "<wiki-root>" --topic-map     # 仅主题地图存在性

# ingest 后聚焦检查本次涉及页面
python3 <SKILL_DIR>/scripts/lint.py "<wiki-root>" --pages "wiki/concepts/页面A.md,wiki/topics/页面B.md"

# 检查归档内容
python3 <SKILL_DIR>/scripts/lint.py "<wiki-root>" --include-archive

# JSON 输出（供程序消费）
python3 <SKILL_DIR>/scripts/lint.py "<wiki-root>" --json

# 退出码：0=全部通过，1=发现问题，2=错误
```

> **iCloud 死锁（`errno 11`）**：iCloud 目录中的文件可能处于 dataless 状态——stat 报告文件大小但数据未本地化。读取时抛 `OSError: [Errno 11] Resource deadlock avoided`。详见 `references/icloud-dataless-workaround.md`。遇到此错误时，先 `brctl download` 逐个拉取文件，再运行 lint。不要用 Python 重试循环——必须主动触发 `brctl download`。

### 手动深度检查

以下项目需要 LLM 的语义理解，暂未自动化：

1. **矛盾。** 扫描 wiki 页面中的矛盾声明，用 clarify() 标注。存在矛盾时，页面应使用 `contested: true` 和 `contradictions: [...]`。

2. **孤页。** 没有被其他 wiki 页面 [[wikilink]] 引用的页面。列出报告。

3. **缺失页面。** 在多处被提及但缺少独立页面的重要概念。建议创建。

4. **过时声明。** 可能被新来源取代的旧声明。查看 log.md 中近期摄入，判断是否影响旧页面。

5. **断链。** 指向不存在页面的 [[wikilinks]]。

6. **索引新鲜度。** 验证所有 wiki 页面都在 index.md 中出现且摘要准确。

7. **raw 完整性。** 检查 `raw/` 文件是否带 `sha256`，并识别哈希不匹配导致的来源漂移。

8. **质量信号。** 报告 `confidence: low`、`contested: true`、缺失必要质量字段的页面。

9. **过时候选页。** 报告 `updated` 距今超过阈值（默认 90 天）的页面，提醒是否需要复核。

10. **标签审计。** 对照 SCHEMA.md 的 Tag Taxonomy，报告未定义却被使用的 tag。

11. **归档排除。** 默认忽略 `_archive/`；只有用户明确要求时检查归档内容。

12. **日志轮转。** 检查 `log.md` 是否跨年或超过 500 条记录。

以结构化列表形式报告发现，附建议。

## 索引管理

`index.md` 是导航中枢。格式：

```markdown
# LLM Wiki 索引 — <主题>

> 最后更新：YYYY-MM-DD

## 实体
- [[实体名称]] — 一句话摘要（最后更新 YYYY-MM-DD，N 个来源）

## 概念
- [[概念名称]] — 一句话摘要（最后更新 YYYY-MM-DD）

## 主题
- [[主题页面]] — 一句话摘要（YYYY-MM-DD）

## 对比
- [[对比页面]] — 比较对象和结论摘要（YYYY-MM-DD）

## 查询
- [[查询页面]] — 可复用综合回答摘要（YYYY-MM-DD）
```

每次摄入后更新。任何查询都先从 index 开始定位相关页面。

## 日志管理

`log.md` 仅追加。每条记录有可解析的标题：

```markdown
## [YYYY-MM-DD] <操作> | <描述>
```

可解析命令：
```bash
grep "^## \[" log.md | tail -5   # 最近5条
grep "^## \[2026-05" log.md       # 2026年5月全部记录
```

### 日志轮转

- `log.md` 默认保存当前年份活动。
- 每年第一次写入时，如果 `log.md` 中已有上一年记录，轮转为 `log-YYYY.md`。
- 如果当前年超过 500 条记录，轮转为 `log-YYYY-partN.md` 后继续写新的 `log.md`。
- lint 应报告需要轮转但尚未轮转的日志。

## 归档管理

当页面过时、重复、命名不准、被更准确页面替代，或不再作为当前知识入口时，不要物理删除，使用 `_archive/` 归档。

规则：
- 普通过时页面：移入 `_archive/<原路径>/`
- 重复页面：合并内容后归档重复页
- 被替代页面：在 frontmatter 中写 `superseded_by`
- raw/ 原始资料：不归档、不删除；raw/ 是不可变来源层
- 归档页面默认从 `index.md` 移除
- lint 默认忽略 `_archive/`，除非用户显式要求检查归档

归档 frontmatter 示例：

```yaml
archived: true
archived_at: YYYY-MM-DD
archived_reason: "被 [[新页面名]] 取代"
superseded_by: [[新页面名]]
```

归档后要更新指向旧页面的链接：如果旧页面有明确替代页，入链改向新页面；如果旧页面仅作为历史记录保留，可保留链接但注明 archived。

## 页面模板

所有模板位于 `templates/page-templates/`。创建页面前先用 skill_view 加载对应模板。

### 实体页（`entity.md`）
- 前置元数据：tags、created、updated、source_count
- 章节：概述、关键事实、关联关系、来源
- 为 Obsidian Dataview 兼容，必须包含 YAML frontmatter

### 概念页（`concept.md`）
- 前置元数据：tags、created、updated、status（draft/reviewed/stable）
- 推荐元数据：confidence（low/medium/high）
- 条件元数据：contested、contradictions（存在争议或矛盾时必须写）
- 章节：定义、重要性、证据、反面观点、相关概念

### 主题页（`topic.md`）
- 前置元数据：tags、created、updated、status（draft/reviewed/stable）
- 推荐元数据：confidence（low/medium/high）
- 条件元数据：contested、contradictions（存在争议或矛盾时必须写）
- 章节：概述、关键要点、分析、未解决问题、来源

### 对比页（`comparison.md`）
- 建议位置：`wiki/comparisons/`
- 用途：横向比较技术、方案、概念或决策选项
- 章节：比较对象、比较维度、表格分析、结论、未解决问题、来源
- 多来源对比页强烈建议使用段落级溯源

### 查询归档页（`query.md`）
- 建议位置：`wiki/queries/`
- 用途：保存值得复用的综合回答、研究结论、临时分析
- 不要归档琐碎查询；只保存未来重新推导成本高的回答

### 主题地图（`topic-map.md`）
- 位置：`_meta/topic-map.md`
- 初始化时默认创建
- 用途：按领域、问题、路线或阅读路径组织页面；不同于 `index.md` 的全量登记
- 更新时机：新增领域、路线、专题综述或用户要求整理全景图时

### 来源摘要（`source-summary.md`）
- 前置元数据：source_url、source_type、date_ingested、tags
- 章节：一句话总结、核心要点、涉及实体、涉及概念、原始笔记

## 段落级溯源

当一个页面综合多个来源时，页面末尾的来源清单不足以说明每个结论来自哪里。此时使用 Markdown 脚注格式做段落级溯源。

推荐使用场景：
- 概念页综合 3 个以上来源
- 实体页 `source_count >= 3`
- 主题综述页
- 对比页
- 严肃查询归档页

格式：

```markdown
该方法要求相位空间轨迹在门末闭合。[^source-ms-gate]

## 段落级来源

[^source-ms-gate]: raw/papers/ms-gate-1999.md，第 3 节
```

不要使用 `^[raw/...]` inline marker；Obsidian/Markdown 脚注格式更适合长期维护。

## 公式与符号规范

- **所有数学符号**（不仅是完整公式，也包括单个希腊字母、上下标、运算符）必须使用 LaTeX 语法，包裹在 `$...$` 或 `$$...$$` 中
- 不应出现裸 Unicode 数学字符：`ϕ` `χ` `ω` `α` `µ` `Ω` `∼` `≈` `∆` `∂` `∑` `²` `³` `⊗` `≥` `≤` `±` `∝` `√` `∞` 等，一律写为 `$\phi$` `$\chi$` `$\omega$` `$\alpha$` `$\mu$` `$\Omega$` `$\sim$` `$\approx$` `$\Delta$` `$\partial$` `$\sum$` `^2` `^3` `$\otimes$` `$\geq$` `$\leq$` `$\pm$` `$\propto$` `$\sqrt{}$` `$\infty$`
- 行内公式用单 `$`：`$\phi_{ij} = 2\chi_{ij}$`
- 独立公式用双 `$$`：
  ```
  $$
  f_{\text{max}} \geq \frac{1}{2^{7/4} \pi \tau \sqrt{\beta}}
  $$
  ```
- 希腊字母用 LaTeX 命令：`\phi` `\chi` `\omega` `\eta` `\tau` `\beta` `\Delta` `\Omega` `\alpha` `\mu` `\psi` `\sigma` `\zeta`
- 上下标：`\omega_p` `\alpha_{ip}` `\eta_{pi}` `f_{\text{max}}` `N^{1/4}`
- 积分求和：`\int_0^\tau` `\sum_p` `\prod_i`
- 分数：`\frac{\pi}{8}`
- 偏导：`\frac{\partial^k \alpha_{ip}}{\partial \omega_p^k}`
- 特殊符号：`\partial` `\approx` `\geq` `\leq` `\pm` `\sim` `\propto` `\otimes` `\sqrt{}` `\infty`
- 文本下标用 `\text{}`：`f_{\text{max}}` 而非 `f_{max}`

### 公式转换注意事项

> 详见 `references/formula-conversion-pitfalls.md`——自动正则替换 Unicode 符号到 LaTeX 的常见陷阱（下标分裂、命令粘连、多符号破碎）。**涉及多处符号的页面，用 write_file 手动重写，不要批量自动转换。**

- **不要用正则批量自动转换**：自动化替换极易产生下标分裂（`$\omega$_p`）、命令粘连（`\pint`）、多符号破碎（`$\partial$^k $\alpha$_ip`）等错误
- **手动重写是最可靠的方式**：对于含多处符号的页面，用 `write_file` 完整重写，逐行确认每个 `$...$` 包裹的正确性
- 多个符号如属于同一表达式，应包裹在同一个 `$...$` 中：`$\partial^k \alpha_{ip} / \partial \omega_p^k = 0$` 而非 `$\partial$^k $\alpha$_ip / $\partial$$\omega$_p^k = 0$`

## 图表规范

- 依赖关系、流程图、架构图使用 Mermaid 语法，Obsidian 原生渲染
- 依赖关系图用 `graph TD`（自上而下）或 `graph LR`（自左而右）
- 流程图用 `flowchart TD`
- 示例——能力依赖图：
  ````
  ```mermaid
  graph TD
    A[LLM Wiki 管理] --> B[llm-wiki-toolchain]
    B --> C[obsidian]
    B --> D[pymupdf]
    B --> E[search_files]
    D --> F[Hermes venv]
    E --> G[rg]
  ```
  ````
- 节点用方括号 `[文本]`，圆角用 `(文本)`
- 用 `::: ` 加样式类，用 `-->|标签|` 标注关系
- 状态可用 emoji 前缀：`A[🟢 可用]` `B[🟡 降级]` `C[🔴 淘汰]`

## 与 Obsidian 集成

- **图谱视图：** 页面间的 [[wikilinks]] 构成知识图谱。鼓励密集链接。
- **Dataview：** 前置元数据支持动态查询。例：`LIST FROM #concept WHERE source_count > 3`
- **Web Clipper：** 浏览器扩展，将网页文章直接剪切到 raw/。
- **Git：** wiki 就是 markdown 文件集合——版本控制零成本。

## 技巧与避免事项

- **一次一个来源** 优于批量摄入——让用户参与指导重点方向。
- **更新已有页面** 而不仅仅是新建。价值在于交叉引用。
- **index 是你的地图。** 任何查询前先读它。
- **好的回答要归档。** 用户要求做的对比或分析，应变成 wiki 页面。
- **SCHEMA.md 会不断演化。** 发现好用约定时，更新章程。
- **不要修改 raw/。** 原始文档不可变——LLM 只读不写。
- **vault 路径要加引号。** 路径常含空格和非 ASCII 字符。
- **配合 obsidian skill 使用。** obsidian skill 处理基础 CRUD，本 skill 提供高层 LLM Wiki 工作流。
- **能力追踪 wiki 用 overview + detail 模式。** 见 `references/capability-tracking-pattern.md`——每个 L3 能力在 `wiki/topics/` 下单开详情页，全景图保持精简。
- **Skill 升级后同步能力追踪 wiki。** 见 `references/cross-skill-capability-sync.md`——当驱动 L3 能力的 skill 被升级时，按 7 步配方将变更传播到 Hermes能力阶梯 wiki。
- **初始化前确认 wiki 位置。** 用户可能希望 wiki 不放在 Obsidian vault 内部，而是与已有 wiki 并列（如 iCloud Documents 下）。初始化前用 clarify() 确认目标路径，不要假设 wiki 一定建在 vault 内。
- **文件名与 \[\[wikilink\]\] 必须精确匹配。** Obsidian 的 wikilink 对文件名中的空格敏感——文件名 `Agent沙盒安全模型.md` 与链接 `[[Agent 沙盒安全模型]]` 会被视为不同页面。创建页面时确保文件名与后续 wikilinks 中使用的名称完全一致（空格、大小写）。lint 的「索引一致性」检查能发现此类不匹配——页面创建后立即跑 lint 验证。
- **官方 llm-wiki 能力沉淀清单。** 见 `references/official-llm-wiki-import-checklist.md`——记录从官方 `llm-wiki` v2.1.0 对照后已沉淀进 toolchain 的治理能力（会话对齐、页面创建阈值、tag taxonomy、`--stale`、`--tags`）以及不建议照搬的规则。
