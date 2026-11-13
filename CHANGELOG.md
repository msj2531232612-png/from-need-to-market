# 更新记录

## 0.2.0 — 2026-11-12

### 新增

- Claude 插件清单（`.claude-plugin/plugin.json` 和 `marketplace.json`）。仓库现在既是 Claude 插件，也仍可作为 Codex 项目级 Skill 安装。
- 五份成果文件的模板（`skills/from-need-to-market/assets/templates/`），随 Skill 一起安装。
- 成果校验脚本 `validate_research_output.py`：检查文件、调研状态、卡片顺序与编号、引用、证据追溯、行动字段、链接和残留占位符。
- 两个脚本的单元测试（`tests/`）和 GitHub Actions 检查。
- 触发评测查询集 `evals/trigger-queries.json`。
- `.gitignore`，默认不提交 `outputs/`。

### 变更

- 重写 `SKILL.md`：触发描述限定为 B2B 软件并加入英文说法；调用方式不再绑定 Codex；规定成果语言跟随用户；调研状态固定为四个取值；首轮必须先做不含品牌的查询，地区未指定时覆盖中英文；续做记录改为带日期的追加条目，新增“进行中”状态。
- 调研手册说明了先做不含品牌查询的原因，查询记录增加“路径”一栏。
- 目录脚本在 `--output-dir` 与 `--topic`、`--base-dir`、`--date` 同时出现时在 stderr 提示后者被忽略。
- 示例：总入口改用固定的调研状态；A01–A03 补上状态字段；`04-action-results.md` 改为带日期的记录；证据台账注明 Q01–Q12 是从品牌开始的历史查询。
- README 增加 Claude 安装方式，去掉与示例重复的卡片正文；发布步骤移到 `docs/publishing.md`。

### 未变

- 示例中的查询、来源和结论没有新增或重查。
- 许可证仍未选定。

## 0.1.0 — 2026-11-12

- 首次发布：Skill、调研手册、目录脚本、WhatsApp 询盘转报价示例和评测记录。
