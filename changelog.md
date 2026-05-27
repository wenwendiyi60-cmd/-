# 更新日志

所有口令版本的变更记录按时间倒序排列。

格式规范：
- `[新增]` 新功能或新规则
- `[修改]` 对现有内容的调整
- `[修复]` 修正错误行为
- `[归档]` 将旧版本移入 archive

---

## 单一全能版 v2.2：F4.5 高危加强分支 — 2026-05-27

- [修改] `prompts/active/liuyao-v0.7-rc1-single.md` 升级 v2.2：新增 **F4.5 高危加强分支**（仅高危触发），把 A4 双向防错（防误升安全 / 防误压已亡）、A5 病重吞药拦截、高危双面取象（甲乙双写）、死亡门槛三项、药证复核**全部前置内嵌**；F5 加高危归层口径；F6a 加安全层 / 死亡终态象层细则；F7 加高危白话"可写 / 禁写"清单；总纪律加"病重≠无药、鬼旺≠救不过来"；自检简码加 F4.5 / 高危加强位；默认输出顺序拆普通题 / 高危题两套
- [修改] `tests/test-002-minimal-safety.md` 增补 F4.5 防误压验收点（病重 / 鬼旺不得直接判救不过来、不得吞掉尚在 Y1）
- 普通题仍走轻量前台；高危深度只在 F4.5 触发时加上来——一版同时扛住"防判平安"与"防判已亡"两个方向

---

## 合并为单一执行版（普通题轻 / 高危自动加深） — 2026-05-27

> 用户要求"一版就够"。把多个投喂版收敛为一个。

- [新增] `prompts/active/liuyao-v0.7-rc1-single.md`：唯一需要粘贴给 AI 的版本。普通题保持轻；F6a 高危分支内嵌 A4 双向防错（防误升安全 / 防误压已亡）+ A5 病重吞药拦句 + 死亡门槛三项 + 双面取象并列建模——高危自动加深，不用换版、不用展开审计
- [移除] 收编进单一版的冗余投喂件：`prompts/active/liuyao-v0.7-rc1-daily-minimal.md`、`templates/liuyao-f0-f7-minimal-template.md`、`templates/liuyao-high-risk-template.md`
- [修改] `tests/test-002-minimal-safety.md` 与回归 harness `--exec-prompt` 默认指向单一版
- 定位区分：`single.md`=粘了就用的口令；`execution-prompt.md` / 审计册 / 派生器 / harness = 工程底稿与校验工具，平时不碰

---

## v2.1 全套对齐：S1（世爻）升为标准代号 — 2026-05-27

把"世/用分离"从日常版推广到全套,S1 成为跨文件标准代号。

- [修改] 完整执行版 `liuyao-v0.7-rc1-execution-prompt.md`：命名表加 `S1=世爻（≠U1）`；F2 加 `S1 世爻` 输出位 + "世用分离检查"(S1是哪爻/U1是哪爻/是否兼用) + 禁止 C1 偷换 R1；F3 加 `S1 气势`；F4 加 `S1↔U1`、`S1↔R1`、`R1/LD1/C1↔S1`
- [修改] 审计册：命名沿用加 S1；G1 定位范围加 S1 + 世用分离检查；G2 合冲复核范围加 S1（含 S1↔U1、S1↔R1）；D2c 加"世用分离检查"字段
- [修改] 派生器 `derive.py`：保留 `is_shi`，hexagram 输出新增 `shi_pos` 与 `S1`(世爻 pos/branch/element/six_relative) 直达字段；单测加 S1 断言（6/6 通过）
- [修改] 日常极简版升级 `v2.1`，与完整版命名体系全套对齐
- 校验：无 S2-S11 旧步骤名残留，S1 不撞名；回归 harness 行为不变

---

## 日常极简执行版（可直接粘贴的系统提示词） — 2026-05-27

- [新增] `prompts/active/liuyao-v0.7-rc1-daily-minimal.md`：写成引擎口令、可整段粘贴的日常极简版（轻），与完整执行版（严）并存。安全红线逐项核对齐全
- [修正] 集成时改正 F2 两处定义偏离主口令命名表的写法：`U1` 由"求测者/主体"改回"主用神（≠求测者/世爻）"、`C1` 由"条件/资源/过程位"改回"承接线"——避免诱导取用神为世爻、并与 derived.json / 审计册口径一致
- 与 `templates/liuyao-f0-f7-minimal-template.md`（填空工作表）分工：active 里的是"粘了就用"的口令，templates 里的是"照着填"的盘面工作表

---

## 极简模板 + 高风险模板 + 安全边界回归 — 2026-05-27

**只压执行负担、不压安全负担的两个实战模板**

- [新增] `templates/liuyao-f0-f7-minimal-template.md`：极简前台执行模板。压候选池/取用理由/逐爻细气势/双面甲乙；保住 F5 病药四问、F6a 双层外放、现实处置旁注、过程证/终局证分离、缺项回问、安危红线。末附"集成补遗"(derived.json 优先 / F6 不引入新爻 / CHECK_JSON 按需补)
- [新增] `templates/liuyao-high-risk-template.md`：安危/抢救/失踪/病危专用模板，一键保留全部红线，F4 强制点名医护/救应/承接线，F6a 不可删
- [新增] `tests/test-002-minimal-safety.md`：极简模板安全边界行为测试
- [新增] `tests/regression/` 用例 `MIN-SAFE`（cases/expected/sample_runs）：可执行版,验证极简模板不丢"现实处置旁注 / 死亡终态象层 / 医护接入≠救回"。离线跑批通过
- [审计] 两模板经逐项核对：压缩的全是执行/可选项，安全红线无一丢失

---

## 执行层工程化（盘面派生器 + 回归 harness + 程序化约束） — 2026-05-27

**把执行从"模型自我表演"改成"工具先算、模型只解释、回归能验"**

- [新增] `tools/liuyao_calc/`（包：ganzhi / relations / najia / derive / schema / cli）：读人工盘 YAML → 校验人工值与规则表 → 输出 derived.json（旬空/纳甲/六亲/世应/动变/本变卦/五行/月日生克/六合六冲/空亡/VV）。人工值与表算冲突直接 fail。第一版不碰旺衰档/病药/应期裁量
- [新增] `tests/fixtures/liuyao_cases/`：master_dishuishi（母盘地水师）、sample_basic（水雷屯）、conflict_palace（冲突演示）
- [新增] `tests/test_derive.py`：派生器单测，6/6 通过（PR1 验收）
- [新增] `tests/regression/`：新回归 harness（cases + expected + run_regression.py）。每用例两层断言——正文 must_contain/must_not_contain + F7 末尾 CHECK_JSON 结构字段比对；输出 per-case 与 overall 失败率（PR2 验收）。sample_runs 离线演示：overall 50%（T1-A 50% 抓到漂移、T1-C 100% 抓到违规、MASTER 0%）
- [修改] 执行册新增 §二十三 程序化约束四条：strict_step 默认分步、derived.json 优先、F6 不得引入新爻、F7 输出 CHECK_JSON；更新工具引用（liuyao_paipan→liuyao_calc、新 harness 路径）
- [修改] 审计册更新回归工具引用至 `tests/regression/` 与 `tools/liuyao_calc`
- [移除] 替换被取代的临时件：`tools/liuyao_paipan.py`、`tools/run_regression.py`、`tests/regression_cases.json`、`tests/sample_outputs/`

---

## v0.7-RC1-final（最终可投喂版 · T1 写实） — 2026-05-27

**审计册 T1 对照写实 + 回归用例落地**

- [修改] `rules/liuyao-v0.7-rc1-audit-regression-manual.md` §十五 T1：T1-A~E 期望从一句话扩为写实（用神状态档 / 安全层 / 死亡终态象层 / 附记 / 病药归层 / Y1 到病 / Y1 落验 + 说明），新增"用神状态档判定要求"四分支，并补三条"不得偷换"拦句（用神得救≠平安倾向、用神显形≠用神可确认、死亡终态象未坐实≠安全）
- [修改] `tests/regression_cases.json`：T1-A~E 期望从占位补成写实断言，与手册 §十五 一一对应
- [新增] `tests/sample_outputs/T1-B.txt`、`T1-D.txt`、`T1-E.txt`：补全跑批覆盖；当前 6 用例离线打分 5 PASS / 1 FAIL（T1-C 为故意违规演示，被正确判失败），失败率 17%
- 执行册无实质变化（与审修定稿版一致），不重复改动

---

## v0.7-RC1-final（审修定稿 + 执行层工程） — 2026-05-27

**定稿两份口令 + 加确定性排盘与回归跑批工具**

> 在拆分版基础上，按多轮审修把两份口令做到内部自洽、命名干净、安危语义全程降格；并新增执行层降错工具：确定性排盘 + 可执行回归跑批。

- [修改] `prompts/active/liuyao-v0.7-rc1-execution-prompt.md`：替换为审修定稿版（修 `S10/S2.5` 残留命名；`已激活专题/红线` 取代悬空"治理"；F6a 加 `用神状态档` 输出；补 `VV`/`人象合一` 定义与概率档 `不足` 门槛；F4 增 `轻量归身三问`；F6a-2 死亡门槛对 `动化鬼` 加"无引拔/未解除"限定）
- [修改] `rules/liuyao-v0.7-rc1-audit-regression-manual.md`：替换为审修定稿版（`动化鬼` 限定向 A5/E-W002/母盘/通过标准/发布/禁增六处传播；T1 小盘期望补 `用神状态档`；G4 加"不替代前台 F4"说明）
- [新增] `tools/liuyao_paipan.py`：确定性排盘（旬空/纳甲/六亲/世应/旺衰/合冲/动变），把机械计算从模型口算里拿走（执行层降错杠杆 2）；自带 selftest
- [新增] `tools/run_regression.py` + `tests/regression_cases.json`：T1-T3 与双向防错母盘的可执行跑批打分骨架，`--runs N` 抓概率性、输出失败率（杠杆 4）；`call_model` 留 API 接入点
- [新增] `tests/sample_outputs/`：T1-A（PASS）、T1-C（FAIL 演示）、MASTER（PASS）样例输出

---

## v0.7-RC1-final — 2026-05-27

**病药主轴重排版：拆分执行分册与审计分册**

> 将原《六爻大世界 v0.7-RC1-final》单体超长口令拆分落地，实时跑卦与后台审计分离，按“最小改名 + 强化 S2.5 + 高风险分步握手 + EV 回引审计 + 安危语义降格”五条锁死。

- [新增] `prompts/active/liuyao-v0.7-rc1-execution-prompt.md`：实时执行分册（F0–F7 主链、病药四问、安全红线、命名表、输出格式、最小自检）
- [新增] `rules/liuyao-v0.7-rc1-audit-regression-manual.md`：审计与回归分册（G1–G6、A1–A5、D2a/b/c、T1–T3、E-W001/E-W002、v0.7.1 候选补丁、双向防错母盘）
- [修改] 主链由 S1–S11 压缩为 F0–F7，后台审计默认不在前台展开
- [修改] 命名去冲突（最小必要）：法源层级 L1–L5→LV1–LV5、落地线 L1→LD1、应期精度 L0–L3→EP0–EP3、证据 E1–E3→EV1–EV3、R2.1 六闸→G1–G6；保留 R1 结果线命名，新增 `R1 只表示结果线、R2/R2.1 只表示版本` 硬规则
- [修改] 伏神 / 化爻 / 变卦关键爻 ID 由 F1/H1/V1 改为 伏1/化1/变1，避免与 F0–F7 步骤前缀冲突
- [修改] S2.5 结果本体锁定保留为强制三问，不得降为 yes/no 勾选
- [新增] 高风险题型在 F2、F5 后新增握手确认点
- [新增] 审计字段“已执行”须绑定 EV 编号并回引本次输出原文，禁止空审计
- [修复] 安危语义降格：`死亡终态层 / 已亡坐实`→`死亡终态象层 / 死亡终态象强（现实须确认）`，不作现实死亡事实断言
- [新增] L5 调用边界明确化：默认不参与实时裁决，仅在用户明确启用观察运行 / 复盘 / 错题审查 / 回归测试时展开

---

## v1.0.0 — 2026-04-07

**初始版本**

- [新增] 创建仓库基本结构
- [新增] `prompts/active/v1.0-liuyao-core.md`：第一个六爻核心口令
- [新增] `rules/core-rules.md`：六爻分析核心规则文档
- [新增] `templates/prompt-template.md`：新口令模板
- [新增] `templates/case-template.md`：新案例模板
- [新增] `cases/case-001-example.md`：示例预测案例
- [新增] `tests/test-001-anti-hallucination.md`：防幻觉测试用例

---

<!-- 在此处继续追加新版本记录，最新版本在最上方 -->
