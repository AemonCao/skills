---
name: git-commit-zh
description: Draft Chinese Git commit messages that combine Gitmoji with Conventional Commits, including concise bodies for changes with meaningful causes, impacts, compatibility concerns, operational notes, or verification details. Use when Codex needs to inspect `git status`, `git diff`, or `git diff --cached`, summarize repository changes, and prepare or execute a Git commit in Chinese with a correct type, optional scope, and breaking-change footer.
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

Gitmoji 不规定 Conventional Commit 的 `type`；先按改动意图选择 `type`，再从下列完整目录选择最贴切的 Gitmoji。常用搭配包括：`✨ feat`、`🐛 fix`、`♻️ refactor`、`📝 docs`、`✅ test`、`⚡️ perf`、`🎨 style`、`💄 style`、`📦️ build`、`👷 ci`、`🔧 chore`、`⏪️ revert`。

以下目录与 `https://gitmoji.dev/api/gitmojis` 同步（2026-07-27，共 75 个）：

- `🎨 :art:`：改善代码结构或格式。
- `⚡️ :zap:`：改善性能。
- `🔥 :fire:`：删除代码或文件。
- `🐛 :bug:`：修复缺陷。
- `🚑️ :ambulance:`：紧急修复严重问题。
- `✨ :sparkles:`：引入新功能。
- `📝 :memo:`：新增或更新文档。
- `🚀 :rocket:`：部署内容。
- `💄 :lipstick:`：新增或更新 UI 与样式文件。
- `🎉 :tada:`：启动项目。
- `✅ :white_check_mark:`：新增、更新或通过测试。
- `🔒️ :lock:`：修复安全或隐私问题。
- `🔐 :closed_lock_with_key:`：新增或更新密钥。
- `🔖 :bookmark:`：发布或版本标签。
- `🚨 :rotating_light:`：修复编译器或 linter 警告。
- `🚧 :construction:`：进行中的工作。
- `💚 :green_heart:`：修复 CI 构建。
- `⬇️ :arrow_down:`：降级依赖。
- `⬆️ :arrow_up:`：升级依赖。
- `📌 :pushpin:`：锁定依赖至特定版本。
- `👷 :construction_worker:`：新增或更新 CI 构建系统。
- `📈 :chart_with_upwards_trend:`：新增或更新分析、埋点代码。
- `♻️ :recycle:`：重构代码。
- `➕ :heavy_plus_sign:`：新增依赖。
- `➖ :heavy_minus_sign:`：移除依赖。
- `🔧 :wrench:`：新增或更新配置文件。
- `🔨 :hammer:`：新增或更新开发脚本。
- `🌐 :globe_with_meridians:`：国际化与本地化。
- `✏️ :pencil2:`：修正错别字。
- `💩 :poop:`：写入待改进的糟糕代码。
- `⏪️ :rewind:`：回滚改动。
- `🔀 :twisted_rightwards_arrows:`：合并分支。
- `📦️ :package:`：新增或更新编译产物或包。
- `👽️ :alien:`：因外部 API 变更而更新代码。
- `🚚 :truck:`：移动或重命名资源，例如文件、路径、路由。
- `📄 :page_facing_up:`：新增或更新许可证。
- `💥 :boom:`：引入破坏性变更。
- `🍱 :bento:`：新增或更新资源文件。
- `♿️ :wheelchair:`：改善无障碍支持。
- `💡 :bulb:`：新增或更新源代码注释。
- `🍻 :beers:`：醉酒编程。
- `💬 :speech_balloon:`：新增或更新文本与字面量。
- `🗃️ :card_file_box:`：进行数据库相关改动。
- `🔊 :loud_sound:`：新增或更新日志。
- `🔇 :mute:`：移除日志。
- `👥 :busts_in_silhouette:`：新增或更新贡献者。
- `🚸 :children_crossing:`：改善用户体验或易用性。
- `🏗️ :building_construction:`：进行架构改动。
- `📱 :iphone:`：处理响应式设计。
- `🤡 :clown_face:`：模拟对象或行为。
- `🥚 :egg:`：新增或更新彩蛋。
- `🙈 :see_no_evil:`：新增或更新 `.gitignore` 文件。
- `📸 :camera_flash:`：新增或更新快照。
- `⚗️ :alembic:`：进行实验。
- `🔍️ :mag:`：改善 SEO。
- `🏷️ :label:`：新增或更新类型。
- `🌱 :seedling:`：新增或更新种子文件。
- `🚩 :triangular_flag_on_post:`：新增、更新或移除功能开关。
- `🥅 :goal_net:`：捕获错误。
- `💫 :dizzy:`：新增或更新动画与过渡效果。
- `🗑️ :wastebasket:`：废弃待清理的代码。
- `🛂 :passport_control:`：处理授权、角色与权限相关代码。
- `🩹 :adhesive_bandage:`：简单修复非关键问题。
- `🧐 :monocle_face:`：数据探索或检查。
- `⚰️ :coffin:`：删除死代码。
- `🧪 :test_tube:`：新增失败测试。
- `👔 :necktie:`：新增或更新业务逻辑。
- `🩺 :stethoscope:`：新增或更新健康检查。
- `🧱 :bricks:`：基础设施相关改动。
- `🧑‍💻 :technologist:`：改善开发者体验。
- `💸 :money_with_wings:`：新增赞助或资金相关基础设施。
- `🧵 :thread:`：新增或更新多线程、并发相关代码。
- `🦺 :safety_vest:`：新增或更新校验相关代码。
- `✈️ :airplane:`：改善离线支持。
- `🦖 :t-rex:`：新增向后兼容代码。

如果多个类型都能解释同一组改动，优先选择最能描述用户可感知结果的那个类型。

## Writing Rules

- 避免空泛标题，例如 `修复问题`、`更新代码`、`调整细节`。
- 在标题中点明受影响模块、能力或场景。
- 以“将要合入的内容”为准描述提交；如果暂存区和工作区不同，以暂存区为准。
- 用户只要求“写 commit”时，只输出消息，不擅自执行提交。
- 用户明确要求“提交”时，只提交与当前意图一致的文件；不要顺手暂存无关改动。
- 如果当前改动明显包含多个独立意图，先建议拆分，再分别起草提交信息。

## Body And Footer

先判断提交是否需要正文。简单、单一、标题已经能准确表达结果的改动可以只写标题；遇到以下任一情形时，默认必须添加正文：

- 同时影响多个模块、层级或文件类型。
- 修改用户可见行为、业务规则或数据流。
- 修复问题但根因、复现条件或影响范围无法从标题看清。
- 涉及兼容性、迁移、配置、部署、回滚或使用注意事项。
- 变更权限、事务、数据一致性、安全性或性能。
- 包含多个紧密相关、但标题难以完整概括的改动。
- 需要说明设计取舍、限制、未覆盖范围或验证方式。

正文使用自然段，优先说明变更原因或根因，再说明影响范围、行为变化、注意事项或验证结果。按实际需要写 2–5 行，不强制补齐“原因”“影响”“验证”等标签，也不要为了满足格式编造内容。

普通原因、影响、迁移步骤和验证说明写在正文；只有真正改变既有接口、配置或行为契约时，才添加 `BREAKING CHANGE:` footer，并同时在标题中使用 `!`。

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

如果需要正文，使用多段 `-m`；正文包含多个自然段时继续追加 `-m`：

```text
git commit -m "♻️ refactor(ai): 拆分会话提示词构建逻辑" -m "抽离模板选择与消息组装，减少 useConversationAi 中的条件分支复杂度。"
```

需要破坏性变更说明时，将 footer 作为独立段落追加：

```text
git commit -m "🚨 feat(api)!: 调整会话鉴权参数" -m "统一创建会话时的鉴权参数，并更新调用方校验逻辑。" -m "BREAKING CHANGE: 创建会话时必须传入 tenantId"
```
