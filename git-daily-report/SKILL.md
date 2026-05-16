---
name: git-daily-report
description: Generate Chinese daily reports from git activity. Use when Codex needs to inspect today's git commit history, staged or unstaged diffs, and untracked files, then turn them into a concise work summary using `1. 2. 3. 4.` numbering that emphasizes feature progress, fixes, and user-visible outcomes over file-level or code-level details.
---

# Git Daily Report

## Overview

为当前仓库生成中文日报。先读取当天提交和当前未提交改动，再把零散提交、diff 和文件变化合并成少量“工作主题”，输出偏功能视角的日报。

## Workflow

1. 先运行 `scripts/collect_git_daily_context.py` 收集当天上下文。默认只看当前 git 用户当天的提交，并同时带出 staged、unstaged、untracked 改动。
2. 先阅读 `Today Commits` 和 `Working Tree`，识别 2 到 4 个工作主题。
3. 如果提交标题偏技术实现、无法直接映射到功能点，补看有代表性的 diff，而不是把所有文件逐个展开。
4. 把相关提交和未提交内容合并成少量日报项，再按 `1. 2. 3. 4.` 编号输出中文日报。

常用命令：

```bash
python <skill-dir>/scripts/collect_git_daily_context.py --repo <repo-path>
python <skill-dir>/scripts/collect_git_daily_context.py --repo <repo-path> --date 2026-04-01 --timezone Asia/Shanghai
python <skill-dir>/scripts/collect_git_daily_context.py --repo <repo-path> --author all --format json
```

必要时补看的命令：

```bash
git show <commit> --stat
git show <commit> -- <path>
git diff -- <path>
git diff --cached -- <path>
```

## Writing Rules

- 优先写功能点、业务结果、用户可感知变化。
- 不要按提交、文件、组件一条条罗列；要把同一主题的改动合并表达。
- 优先写“支持了什么”“修复了什么”“完善了什么流程”，而不是“改了什么文件”“补了什么类型”。
- 只有在确实没有更高层描述时，才写代码层面的工作，例如重构、测试补充、构建配置调整。
- 对未提交内容不要写成已经完成。使用“继续完善”“正在补充”“补齐中”“待联调”这类措辞。
- 默认压缩为 2 到 4 条。如果主题超过 4 个，合并相邻主题；如果少于 4 个，不要为了凑数虚构内容。
- 除非用户明确要求，否则不要在最终日报里保留文件路径、commit hash、git 命令或 `staged`、`unstaged` 这类术语。

## Heuristics

- `feat`、新页面、新入口、新流程、新查询、新集成，优先改写成“新增能力”或“补齐流程”。
- `fix`、错误处理、回归修复，优先改写成“修复问题”“提升稳定性”“减少异常”。
- 多个低层提交如果共同服务同一个场景，按场景汇总，不按技术动作拆开。
- 新增未跟踪文件如果同时伴随页面或路由修改，通常意味着一个新功能或新界面的一部分；先看页面 diff 再写日报。
- 只有测试、构建、配置类改动时，才写成“补充验证”“完善工程配置”“提升开发效率”等工程项。

## Good And Bad

坏例子：

```text
1. 修改 patients 页面并新增 ThePatientCard 组件
2. 调整 AI 类型定义和测试断言
```

好例子：

```text
1. 支持患者列表的查询、切换以及新增删除流程，并补齐独立页面路由
2. 修复 AI 提示词响应链路中的类型问题，减少预问诊相关异常
```

## Output Template

```text
1. ...
2. ...
3. ...
4. ...
```

如果当天只有 2 到 3 个主题，就只输出 2 到 3 条，不要编造第 4 条。

## Script Notes

- `scripts/collect_git_daily_context.py` 默认收集：
  - 当前 git 用户当天的提交
  - 当前 staged 改动
  - 当前 unstaged 改动
  - 当前 untracked 文件
- 脚本会给出 working tree 的 patch 预览，但会截断。预览不够时，再手动查看实际 diff。
- 多人共用同一台机器或仓库时，优先显式传入 `--author <email>` 或 `--author all`。

## Resources

- `scripts/collect_git_daily_context.py`: 收集当天提交、当前工作区状态、变更文件和 patch 预览，供日报总结使用。
