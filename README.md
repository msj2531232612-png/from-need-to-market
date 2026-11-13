# from-need-to-market

把一句模糊的 B2B 软件需求，调研成可搜索的细分市场、已有产品和替代做法、带来源的证据，以及拿到就能执行的验证方案。可作为 Claude 插件或 Codex Agent Skill 使用。

> **English summary.** An agent skill that turns a one-line B2B software need into candidate markets, existing products and workarounds, sourced evidence, and a concrete validation plan, saved as four linked Markdown files that a later session can pick up. The skill text is written in Chinese; it responds in the language you ask in.

## 适用场景

- 只有一段用户痛点或产品想法，需要拆成几个可检索的市场方向。
- 需要知道哪些现有产品覆盖了目标工作步骤，以及它们的地区、系统和试用条件。
- 需要把公开证据、待核实事项和下一步行动放在同一套可追溯的成果里。

聚焦中英文 B2B 软件。调研结果用于筛选假设，不代表市场规模、客户需求强度或产品实际效果已经得到验证。

## 你会得到什么

每次完整调研在 `outputs/日期-主题/` 下生成四份互相链接的文件：

| 文件 | 内容 |
|---|---|
| `00-start-here.md` | 结论、调研状态、最接近的市场和产品、建议先做的一件事 |
| `01-market-cards.md` | 六类成果卡：需求 R、市场 M、产品 P、证据 E、优先验证 V、调研覆盖 C |
| `02-evidence-log.md` | 实际执行的查询、查阅的来源、每个来源能支持和不能支持的判断 |
| `03-action-plan.md` | 编号行动 A01…、验收条件和可复制到新会话的交接指令 |

继续执行行动时会追加第五份 `04-action-results.md`，按日期记录每次进展。重复运行会新建带序号的目录，旧结果保留。

完整示例见 [WhatsApp 询盘转报价](examples/whatsapp-quotation/00-start-here.md)。

## 安装

### Claude Code

```text
/plugin marketplace add msj2531232612-png/from-need-to-market
/plugin install from-need-to-market@from-need-to-market
```

### Claude 应用

把仓库打包成 `from-need-to-market.plugin`（一个 zip 文件，根目录包含 `.claude-plugin/` 和 `skills/`），在应用的插件设置中上传。具体入口以应用当前界面为准。

### Codex

把 `skills/from-need-to-market/` 整个文件夹复制到项目的 `.agents/skills/` 下，或复制到 `$HOME/.agents/skills/` 供所有项目使用。

逐步说明见[入门指南](docs/getting-started.md)。

## 使用

直接描述需求即可，也可以显式调用（Claude 中是 `/from-need-to-market`，Codex 中是 `$from-need-to-market`）：

```text
我想帮外贸业务员少做重复工作。请找对应的市场、已有产品，并保存完整成果和下一步方案。
```

补充目标国家、行业、实际使用者和现有 CRM/ERP 会让结果更贴近业务。没有这些信息时，Skill 会标明假设后继续。你也可以要求只在聊天中交付、只要某一类卡片，或者离线运行（只生成假设和待执行的查询）。

在新会话继续：把成果目录和 `03-action-plan.md` 末尾的交接指令一起交给新会话，或直接说“请读取这个成果目录，执行下一步并记录结果”。

## 目录结构

```text
.claude-plugin/            Claude 插件清单
skills/from-need-to-market/
├── SKILL.md               执行流程、六类成果卡、文件交付和续做规则
├── references/            调研手册：搜索路径、来源核验、冲突处理
├── assets/templates/      五份成果文件的模板
└── scripts/               创建成果目录、校验成果目录
examples/whatsapp-quotation/   一套联网调研成果和续做记录示例
evals/                     行为测试用例、触发查询集和验证记录
tests/                     两个脚本的单元测试
docs/                      入门指南、发布步骤
```

## 开发与检查

需要 Python 3.8 或更高版本，无第三方依赖。Windows 上加 `-X utf8`。

```text
python -m unittest discover -s tests
python skills/from-need-to-market/scripts/validate_research_output.py examples/whatsapp-quotation
```

哪些行为已经实测、哪些还没有，见[评测记录](evals/cases.md)。版本变化见[更新记录](CHANGELOG.md)。

## 许可证

本仓库尚未选定许可证。在添加许可证之前，默认保留所有权利，他人不能合法地复制或修改。

## 参考

- [Agent Skills 格式规范](https://agentskills.io/specification)
- [Codex Skills 文档](https://developers.openai.com/codex/skills)
- [OpenAI：系统化测试 Agent Skills](https://developers.openai.com/blog/eval-skills)
