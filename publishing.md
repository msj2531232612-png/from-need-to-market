# 发布指南：通过 GitHub 网页发布

面向仓库维护者。发布前先在仓库根目录运行 `python -m unittest discover -s tests`，并更新 `CHANGELOG.md` 和 `.claude-plugin/plugin.json` 中的版本号。

1. 登录 GitHub，选择创建新仓库；由你决定仓库名称、公开/私有和初始化选项。
2. 若创建时勾选自动生成 README，先确认不要覆盖本项目现有 README。新手可选择空仓库，再上传项目文件。
3. 在仓库主页选择 Add file → Upload files。
4. 将项目内的全部文件和文件夹一并上传，包括以点开头的 `.claude-plugin/`、`.github/` 和 `.gitignore`。部分系统默认隐藏这些项目，上传后在仓库页面确认它们存在。也可以将文件夹拖入浏览器，上传前检查目录层级。
5. 在提交说明中写清更改内容，例如“Add from-need-to-market skill and research example”。
6. 选择提交到默认分支或新建分支。确认仓库设置后完成提交。
7. 返回仓库主页，检查 README 的示例和相对链接。打开 Skill、调研手册、四份调研示例和续接记录，确认目录与链接正确。
8. 发布许可证由仓库所有者决定。本项目没有预设许可证；没有许可证的公开仓库默认保留所有权利，他人不能合法复用。希望他人使用时，在仓库页面选择 Add file → Create new file，文件名输入 `LICENSE`，再从 GitHub 提供的模板中挑选。
9. 若不希望公开客户信息，不要把访谈原文、客户消息、价目表、试用凭据或内部系统信息上传到仓库。

官方网页上传步骤见 [GitHub 文档](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository)。GitHub 网页支持一次上传多个文件，但单文件有大小限制；若页面提示文件过大，使用 Git 客户端或命令行上传。
