---
name: git-push-workspace
description: "将 OpenClaw workspace 目录 git push 到 GitHub。触发词：上载claw配置、push配置、推送配置。"
---

# Git Push Workspace Skill

将 `~/.openclaw/workspace/` 目录推送到 GitHub 远程仓库。

## 仓库信息

- 远程地址：`git@github.com:uit890/openclaw-workspace.git`
- 分支：`master`
- 工作目录：`/Users/liufeng/.openclaw/workspace/`

## 执行命令

```bash
cd /Users/liufeng/.openclaw/workspace && git add -A && git commit -m "<提交信息>" && git push
```

## 触发词

- "上载claw配置"
- "push配置"
- "推送配置"

## 注意事项

- 推送前会自动 `git add -A` 暂存所有变更
- 如果没有变更（nothing to commit），直接 push
- 如果 GitHub 推送被拒绝（rejected），需要先 pull 再 push
