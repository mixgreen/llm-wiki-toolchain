# 官方 llm-wiki 能力沉淀清单

本参考记录从官方 `llm-wiki` v2.1.0 对照 `llm-wiki-toolchain` 后，适合沉淀进 toolchain 的治理能力。官方版可视为上游基线；toolchain 是用户日常中文 Obsidian LLM Wiki 的主入口。

## 已立刻沉淀的能力

1. **会话开始强制对齐**
   - 对已有 wiki 做 ingest / query / lint 前，先读 `SCHEMA.md`、`index.md`、最近 20-30 条 `log.md`。
   - 对 100+ 页大型 wiki，创建新页前额外全库 `search_files` 预搜索相关主题。

2. **页面创建阈值**
   - 建页：实体/概念出现在 2+ 个来源，或是单来源核心内容。
   - 更新已有页：边缘补充、局部修正、已有主题的新证据。
   - 不建页：偶发提及、细枝末节、明显超出当前 wiki 域。
   - 拆分页：页面变长到不再能快速扫读时，拆成子页并互链。

3. **标签 taxonomy 纪律**
   - 大规模写页前先在 `SCHEMA.md` 定义 tag taxonomy。
   - 使用新 tag 前先补 taxonomy。
   - 大型 wiki 把 tag audit 作为固定 lint 项。

4. **lint: 过时候选页**
   - `lint.py --stale` 检查 `updated` 超过默认 90 天的页面。
   - 输出 `stale_pages` / `stale_count`。

5. **lint: 标签审计**
   - `lint.py --tags` 从 `SCHEMA.md` 的 `Tag Taxonomy` 段落提取允许 tag。
   - 检查页面 frontmatter `tags` 是否在 taxonomy 中。
   - 输出 `tag_audit` / `tag_audit_count`。

## 不建议直接照搬的官方规则

- **lowercase-hyphen-no-spaces 文件名规则**：更适合英文 wiki。用户的中文 Obsidian 页面需要中文文件名和精确 wikilink 匹配，不应强制改为英文 slug。
- **inline provenance marker `^[raw/...]`**：toolchain 已决策使用 Markdown 脚注，更适合 Obsidian 和长期维护。

## 后续可观察但暂不强制的能力

- Obsidian headless / sync 运维说明：有价值，但偏部署场景；除非用户明确需要跨设备或服务器同步，否则不放入主流程。
- 更复杂的 stale 检查：官方提到“比最新相关来源落后 >90 天”，当前先实现简单 `updated` 阈值；未来可结合 raw/source mention 图谱升级。

## 维护注意

- 更新 `SKILL.md` 时，保持主文档是高层流程；会话细节和对照结论放入 `references/`。
- 修改脚本后必须至少运行：
  - `python3 -m py_compile scripts/lint.py`
  - `python3 scripts/lint.py <某个现有wiki> --json`，确认新增 key 正常出现。
