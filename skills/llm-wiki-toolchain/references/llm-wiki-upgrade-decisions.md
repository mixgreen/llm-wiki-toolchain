# llm-wiki 与 llm-wiki-toolchain 合并升级决策

本参考记录一次针对 `llm-wiki` 与 `llm-wiki-toolchain` 的设计评审结论。后续维护以 `llm-wiki-toolchain` 为主体，吸收 `llm-wiki` 的通用稳健性能力。

## 已定方向

1. **toolchain 为主入口**
   - `llm-wiki-toolchain` 是用户日常使用和演进的 LLM Wiki 管理 skill。
   - `llm-wiki` 作为上游参考，不作为日常 wiki 操作主入口。

2. **页面目录扩展为五类**
   - 保留：`wiki/entities/`、`wiki/concepts/`、`wiki/topics/`
   - 新增：`wiki/comparisons/`、`wiki/queries/`
   - 原因：用户的 wiki 页面数量会轻松超过 50 页，对比分析和查询归档需要独立承载。

3. **初始化默认创建主题地图**
   - 新增 `_meta/topic-map.md`。
   - `index.md` 是全量登记表；`topic-map.md` 是人类友好的导航层。
   - `topic-map.md` 只在新增领域、路线、专题综述或阅读路径时更新，不要求每页同步。

4. **raw/ 强制 sha256 完整性校验**
   - raw 原始资料视为不可变层。
   - 所有 raw 文件都应记录 `sha256`。
   - lint 应能报告：缺失 sha256、哈希不匹配、来源漂移。

5. **引入页面质量信号**
   - `status`：强制，用于页面成熟度（draft/reviewed/stable）。
   - `confidence`：推荐，用于证据强度（low/medium/high）。
   - `contested`：条件强制，页面存在争议或矛盾时必须写。
   - `contradictions`：条件强制，列出与当前页面冲突的页面。
   - 注意：`status` 与 `confidence` 含义不同；页面整理得好不代表证据强。

6. **段落级溯源使用 Markdown 脚注格式**
   - 不使用 `^[raw/...]` inline marker。
   - 使用 Obsidian/Markdown 兼容格式：
     ```markdown
     结论文本。[^source-short-name]

     ## 段落级来源
     [^source-short-name]: raw/papers/example.md，第 3 节
     ```
   - 适用：多来源概念页、主题综述页、对比页；来源摘要页通常不需要。

7. **支持双模式摄入**
   - 单来源摄入：默认模式，适合重要论文、核心文档、需要用户判断重点的资料。
   - 批量摄入：用户明确说“批量/一批/这些文件/整个目录”时启用，适合同类资料、目录归档、源码资料和历史资料导入。
   - 批量摄入前应先输出摄入计划；预计触及超过 10 个 wiki 页面时必须确认范围。

8. **加入归档机制**
   - 新增 `_archive/`。
   - 过时、重复、被替代页面移入归档，不物理删除。
   - lint 默认忽略 `_archive/`，除非显式包含。

9. **log.md 轮转机制**
   - 优先按年份轮转。
   - 单年超过 500 条记录时用 part 文件兜底。

10. **不写 ADR**
    - 本次决策直接写入 skill、模板、脚本和本参考文档。
    - 不创建 `docs/adr/`。

## 已落地文件

- `SKILL.md`
  - 五目录结构
  - `_meta/topic-map.md`
  - 双模式摄入
  - raw sha256 要求
  - focused lint 策略
  - 归档、日志轮转、段落级溯源说明

- `templates/`
  - `SCHEMA.md`：五目录、raw sha256、质量字段、段落级溯源、归档、日志轮转、lint checklist
  - `index.md`：新增 Comparisons / Queries
  - `log.md`：新增轮转规则与新目录结构
  - `topic-map.md`：新增主题地图模板
  - `page-templates/comparison.md`、`query.md`：新增页面模板
  - `concept.md`、`topic.md`、`entity.md`、`source-summary.md`：补充质量字段和段落级来源

- `scripts/init.py`
  - 创建 `wiki/comparisons/`、`wiki/queries/`、`_archive/`、`_meta/`
  - 生成 `_meta/topic-map.md`

- `scripts/lint.py`
  - 检查孤页、断链、索引一致性
  - 检查 raw sha256 完整性
  - 检查 frontmatter / status / confidence / contested / contradictions
  - 检查页面大小（默认 200 行）
  - 检查 log.md 轮转需求
  - 检查 `_meta/topic-map.md` 存在性
  - 默认忽略 `_archive/`，支持 `--include-archive`
  - 支持 `--pages` 聚焦检查本次 ingest 触及页面

- `../research/llm-wiki/SKILL.md`
  - 降级为上游参考，不再作为日常中文 wiki 工作流入口。
