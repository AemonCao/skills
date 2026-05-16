---
name: git-commit-zh
description: Draft Chinese Git commit messages that combine Gitmoji with Conventional Commits. Use when Codex needs to inspect `git status`, `git diff`, or `git diff --cached`, summarize repository changes, and prepare or execute a Git commit in Chinese with a correct type, optional scope, and breaking-change footer.
---

# Git Commit Zh

## Overview

为当前仓库生成可直接使用的中文 Git 提交信息。
先检查实际改动，再输出符合 `Gitmoji + Conventional Commits` 的提交标题；只有在用户明确要求时才实际执行 `git commit`。

## Workflow

1. 运行 `git status --short`，确认工作区和暂存区状态。
2. 如果存在已暂存改动，优先查看 `git diff --cached --stat` 和 `git diff --cached`。
3. 如果没有已暂存改动，再查看 `git diff --stat` 和 `git diff`。
4. 判断这些改动是否属于一个单一提交意图；如果混入多个不相关修改，优先建议拆分提交。
5. 为该提交选择一个主 `type` 和一个最贴切的 Gitmoji。
6. 输出最终提交标题；如果用户明确要求执行提交，再给出或执行对应的 `git commit` 命令。

## Commit Format

使用以下格式：

`<gitmoji> <type>(<scope>): <subject>`

遵守以下规则：

- `type` 必须使用小写 Conventional Commits 类型，例如 `feat`、`fix`、`refactor`、`docs`、`test`、`perf`、`style`、`build`、`ci`、`chore`、`revert`。
- `scope` 仅在模块边界清晰时使用，优先选择简短 ASCII 标识，例如 `chat`、`auth`、`prompt`、`build`。
- `subject` 必须使用简体中文，动词开头，简洁具体，不带句号。
- 优先使用实际 emoji；如果终端编码不稳定，再退回到 Gitmoji 代码形式，例如 `:sparkles:`。
- 如果存在破坏性变更，使用 `!` 并添加 `BREAKING CHANGE:` footer，关键字保持英文，说明可以使用中文。

示例：

```text
✨ feat(prompt): 支持中文诊前提示词模板
🐛 fix(chat): 修复会话中断后无法恢复的问题
♻️ refactor(ai): 拆分提示词构建逻辑
🚨 feat(api)!: 调整会话鉴权参数
```

## Type And Gitmoji Mapping

- `✨ feat`: 新功能、新能力、新接口。
- `🐛 fix`: 缺陷修复、错误处理修正、行为纠偏。
- `♻️ refactor`: 不改变外部行为的重构、拆分、抽象、整理。
- `📝 docs`: 文档、注释、说明更新。
- `✅ test`: 测试补充、测试修复、断言调整。
- `⚡️ perf`: 性能优化、耗时或内存改进。
- `🎨 style`: 代码格式、结构整理、命名微调，不影响运行逻辑。
- `💄 style`: UI 样式、视觉呈现、界面细节调整。
- `📦️ build`: 构建配置、依赖、打包产物相关调整。
- `👷 ci`: CI/CD 流程、流水线、自动化发布配置。
- `🔧 chore`: 杂项维护、工具配置、非产品行为变更。
- `⏪️ revert`: 回滚历史提交。

如果多个类型都能解释同一组改动，优先选择最能描述用户可感知结果的那个类型。

## Writing Rules

- 避免空泛标题，例如 `修复问题`、`更新代码`、`调整细节`。
- 在标题中点明受影响模块、能力或场景。
- 以“将要合入的内容”为准描述提交；如果暂存区和工作区不同，以暂存区为准。
- 用户只要求“写 commit”时，只输出消息，不擅自执行提交。
- 用户明确要求“提交”时，只提交与当前意图一致的文件；不要顺手暂存无关改动。
- 如果当前改动明显包含多个独立意图，先建议拆分，再分别起草提交信息。

## Body And Footer

只有在以下情况才添加正文或 footer：

- 仅看标题无法说明原因或影响范围。
- 需要说明迁移步骤、兼容性变化或注意事项。
- 存在破坏性变更，需要 `BREAKING CHANGE:` footer。

示例：

```text
🚨 feat(api)!: 调整会话鉴权参数

BREAKING CHANGE: 创建会话时必须传入 tenantId
```

## Output Template

默认同时给出“提交标题”和“提交命令”两种输出：

```text
提交标题：
✨ feat(prompt): 支持中文诊前提示词模板

提交命令：
git commit -m "✨ feat(prompt): 支持中文诊前提示词模板"
```

如果需要正文，使用多段 `-m`：

```text
git commit -m "♻️ refactor(ai): 拆分会话提示词构建逻辑" -m "抽离模板选择与消息组装，减少 useConversationAi 中的条件分支复杂度。"
```
