# 入门指南：安装与试用

这份指南面向第一次安装 Agent Skill 的用户。Skill 本质上是一个带有 SKILL.md 的文件夹；Codex 会在项目目录的 .agents/skills 中发现项目级 Skill。本指南说明如何安装和运行。维护者发布新版本的步骤见[发布指南](publishing.md)。

## 一、安装

### 在 Claude 中安装

Claude Code 中依次输入：

~~~~text
/plugin marketplace add msj2531232612-png/from-need-to-market
/plugin install from-need-to-market@from-need-to-market
~~~~

在 Claude 应用中，把打包好的 `from-need-to-market.plugin` 文件通过插件设置上传。具体入口以应用当前界面为准。

### 本地安装到 Codex 项目

1. 下载本仓库 ZIP 并解压，或把仓库克隆到本地。
2. 打开需要使用 Skill 的项目文件夹。
3. 在项目根目录建立 `.agents/skills/`。
4. 将本仓库 `skills/from-need-to-market/` 整个文件夹复制到 `.agents/skills/` 下，包括 `SKILL.md`、`references/`、`assets/` 和 `scripts/`。
5. 在 Codex 中打开目标项目。Skill 更新通常会自动发现；若没有出现，重启 Codex。
6. 如果希望在多个项目使用，将 Skill 文件夹放在个人目录 $HOME/.agents/skills/from-need-to-market/。不要把个人路径提交到公开仓库。

最终结构应为：

~~~~text
your-project/
└── .agents/
    └── skills/
        └── from-need-to-market/
            ├── SKILL.md
            ├── assets/
            │   └── templates/
            ├── references/
            │   └── research-playbook.md
            └── scripts/
                ├── create_research_directory.py
                └── validate_research_output.py
~~~~

## 二、运行一次调研

在新任务或对话中直接描述需求，或显式调用（Codex 用 `$from-need-to-market`，Claude 用 `/from-need-to-market`）：

~~~~text
$from-need-to-market 我想帮外贸业务员少做重复工作。请找对应的市场、已有产品，并保存完整成果和下一步方案。
~~~~

要得到更贴近业务的结果，请补充目标国家、行业、实际使用者、现有 CRM/ERP、报价或审批限制。没有这些信息时，Skill 会标明假设并在能进行有用比较的情况下继续调研。

完整运行默认在当前工作区的 outputs/ 下新建日期与主题目录，包含：

- 00-start-here.md：结论与文件导航。
- 01-market-cards.md：完整 R、M、P、E、V、C 卡。
- 02-evidence-log.md：实际查询、来源和证据边界。
- 03-action-plan.md：可执行步骤和交接指令。

运行后先检查总入口中的结论，再从 V01 按编号查看成果卡与来源。执行时从 A01 开始，按前置条件准备输入，在行动方案注明的验收条件下记录结果。真实客户数据、账号、授权和付费操作必须由你提供或安排；不要将敏感原始资料直接放入公开查询或未经审查的第三方产品。

如要求离线，Skill 仍会生成四份文件，并标注哪些内容是假设、已有材料和待执行查询。重复运行会另建带序号的目录。只想看聊天时，可以在请求里写「只在聊天中交付」。

### 换窗口执行下一步

1. 打开 `03-action-plan.md`，把末尾的交接指令和实际成果目录一起提供给新会话。
2. 要求执行下一步时，新会话会读行动方案及已有的 `04-action-results.md`，按最新记录继续。如果缺少授权、样本或试用权限，先处理可完成的部分，再列出缺少的材料。
3. 第一次续接会按需创建 `04-action-results.md`。以后续接时在同一份文件末尾追加带日期的记录，每条写明行动编号、状态、证据、产出和下一步。初次调研的四份文件可用于回查。
4. 只想了解下一步时，直接问「请告诉我下一步要做什么」。查看示例可打开[行动执行记录](../examples/whatsapp-quotation/04-action-results.md)。

### 自己检查一份成果

想确认某个成果目录的编号、引用和链接是否完整，可以运行校验脚本（Windows 上加 `-X utf8`）：

~~~~text
python skills/from-need-to-market/scripts/validate_research_output.py outputs/你的成果目录
~~~~

脚本列出“错误”和“提醒”。它只检查结构，来源是否可靠、结论是否成立仍需要你自己判断。

## 参考

- [Agent Skills 格式规范](https://agentskills.io/specification)
- [Codex Skills 文档](https://developers.openai.com/codex/skills)
- [OpenAI Skill 评测指南](https://developers.openai.com/blog/eval-skills)

