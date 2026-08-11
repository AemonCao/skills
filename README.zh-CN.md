# 技能库

[English](README.md)

这个仓库用于存放本地 Codex 技能。每个技能都围绕一个明确的工作流编写，让 Codex 在处理特定任务时可以复用稳定的步骤、格式和判断标准。

## 可用技能

- `git-commit-zh`：检查 Git 改动后，生成并执行符合 `Gitmoji + Conventional Commits` 规范的中文提交。
- `git-daily-report`：根据当天提交记录、暂存区和未提交改动，整理出简洁的中文工作日报。
- `grill-me`：围绕计划或设计进行连续追问，帮助梳理依赖、分支决策和潜在风险。
- `grill-with-docs`：针对项目的领域模型和既有决策拷问计划，在术语和取舍逐步明确的过程中，同步更新 `CONTEXT.md` 和 ADR 文档。
- `markdown-normalizer`：将普通文本或格式松散的内容整理为清晰的 Markdown，并保持原意不变。
- `dbx-create-table-sql`：通过 DBX 检查 PostgreSQL 模式，并起草符合约定的 CREATE TABLE SQL。
- `handoff`：将当前对话压缩为交接文档，方便另一个 agent 接手后续工作。
- `prototype`：构建一次性原型来打磨设计方案——用终端应用验证逻辑/状态，或在单一路由上提供多个可切换的 UI 变体来探索设计。

## 目录结构

每个技能都放在独立目录中，并通过 `SKILL.md` 定义触发条件、执行流程和输出格式。

```text
skills/
  git-commit-zh/
    SKILL.md
  git-daily-report/
    SKILL.md
  grill-me/
    SKILL.md
  grill-with-docs/
    SKILL.md
    CONTEXT-FORMAT.md
    ADR-FORMAT.md
  markdown-normalizer/
    SKILL.md
  dbx-create-table-sql/
    SKILL.md
  handoff/
    SKILL.md
  prototype/
    SKILL.md
    LOGIC.md
    UI.md
```

## 维护方式

新增或更新技能时，建议遵循这些原则：

1. 让每个技能只服务一个清晰的工作流。
2. 在 frontmatter 的 `description` 中写清楚触发场景。
3. 优先提供具体步骤、检查项和输出模板，少写泛泛而谈的原则。
4. 当技能列表发生变化时，同步更新英文和中文 README。
