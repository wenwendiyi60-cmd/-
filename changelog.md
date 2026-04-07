# 更新日志

所有口令版本的变更记录，按时间倒序排列。

格式：`[新增]` 新内容 · `[修改]` 调整现有内容 · `[修复]` 纠正错误行为 · `[删除]` 移除内容 · `[归档]` 移入 archive

---

## v2.0.0 — 2026-04-07

**第二次提交：重构为真实工作系统**

### 口令

- [新增] `prompts/active/断卦引擎-2.0-Lite-Lock.md`：实战口令，含阶段1锁盘、阶段2固定分析顺序、核心裁决链（旺衰力度 + 双面取象 + 证据分层 + 四问裁决）、严格反脑补铁律
- [新增] `prompts/active/final-mother-version.md`：总母版占位，记录扩展开发方向
- [新增] `prompts/active/paipan-format.md`：独立排盘格式口令，只排盘不断卦
- [删除] `prompts/active/v1.0-liuyao-core.md`：通用版口令，已替换

### 规则

- [新增] `rules/anti-hallucination.md`：防脑补铁律，禁止造动爻/旬空/变卦/剧情/应期
- [新增] `rules/stage-protocol.md`：五阶段执行协议（锁盘→用神→旺衰→双面→四问→断语）
- [新增] `rules/audit-checklist.md`：口令发布前全项检查清单
- [新增] `rules/timing-governance.md`：应期分析边界与合规推算规则
- [新增] `rules/terminology.md`：系统术语定义表（六亲/用神速查/分析链术语）
- [删除] `rules/core-rules.md`：通用规则，已拆分为以上专项文件

### 测试

- [新增] `tests/test-missing-moving-lines.md`：动爻缺失时的行为回归测试
- [新增] `tests/test-missing-xunkong.md`：旬空缺失时的行为回归测试
- [新增] `tests/test-static-no-biangua.md`：无动爻时禁止生成变卦的回归测试
- [新增] `tests/test-no-analysis-before-stage1.md`：阶段1未完成前禁止分析的回归测试
- [新增] `tests/test-process-vs-outcome-evidence.md`：过程证据不得替代结论证据的回归测试
- [删除] `tests/test-001-anti-hallucination.md`：已被以上专项测试替代

### 其他

- [删除] `index.html`、`style.css`：网站文件与本项目无关，已清除
- [修改] `README.md`：重写为六爻口令工程仓库说明

---

## v1.0.0 — 2026-04-07

**第一次提交：仓库骨架**

- [新增] 基本目录结构（prompts/rules/cases/tests/templates）
- [新增] `prompts/active/v1.0-liuyao-core.md`：初始通用口令
- [新增] `rules/core-rules.md`：通用规则文档
- [新增] `cases/case-001-example.md`：示例案例
- [新增] `tests/test-001-anti-hallucination.md`：初始防幻觉测试
- [新增] `templates/prompt-template.md`、`templates/case-template.md`

---

<!-- 新版本记录添加在顶部 -->
