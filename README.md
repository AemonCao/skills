# Skills

[中文说明](README.zh-CN.md)

This repository contains local Codex skills used to extend task-specific workflows.

## Available Skills

- `git-commit-zh`: drafts and creates Chinese Git commit messages using Gitmoji and Conventional Commits.
- `git-daily-report`: generates concise Chinese daily reports from Git history and current changes.
- `grill-me`: stress-tests plans or designs through focused, sequential questioning.
- `markdown-normalizer`: converts plain or loosely formatted text into clean Markdown without changing the substance.

## Structure

Each skill lives in its own directory and defines its behavior in a `SKILL.md` file.

```text
skills/
  git-commit-zh/
    SKILL.md
  git-daily-report/
    SKILL.md
  grill-me/
    SKILL.md
  markdown-normalizer/
    SKILL.md
```

## Maintenance

When adding or updating a skill:

1. Keep the skill instructions focused on one workflow.
2. Include clear trigger conditions in the frontmatter description.
3. Prefer concrete steps and output formats over broad guidance.
4. Update this README when the set of available skills changes.
