---
name: send-photo-from-folder
description: 从指定文件夹随机选取图片发送给用户。当用户说"美女图片"、"看美女"、"来点图片"、"发点图片"、"随机图片"时，从 ~/Downloads/DCIM/Camera 文件夹随机选2~3张图片发送。
---

# Send Photo From Folder Skill

## 触发词
- "美女图片"、"看美女"、"来点图片"、"发点图片"、"随机图片"
- 任何想从本地文件夹看图片的请求

## 工作流程

1. **扫描文件夹**：用 Python 列出 `~/Downloads/DCIM/Camera` 下的图片（jpg、jpeg、png、heic、webp）
2. **随机选片**：`random.sample` 随机挑 2~3 张（不超过文件夹内实际数量）
3. **复制到临时目录**：图片复制到 `/tmp/openclaw/photo-send/`（飞书媒体上传白名单）
4. **发送图片**：通过 `message` 工具发送

## 核心脚本

```python
import os, random, shutil

folder = '/Users/liufeng/Downloads/DCIM/Camera'
dest = '/tmp/openclaw/photo-send'
os.makedirs(dest, exist_ok=True)

files = [f for f in os.listdir(folder)
         if f.lower().endswith(('.jpg','.jpeg','.png','.heic','.webp'))]
selected = random.sample(files, min(3, len(files)))

for f in selected:
    shutil.copy2(os.path.join(folder, f), os.path.join(dest, f))
    print(os.path.join(dest, f))
```

## 发送方式

当前会话 channel 为 `feishu`，通过 message 工具发送：

```
message(
    action="send",
    channel="feishu",
    target="ou_620abe530f4e51e0f6c22fe8f3472055",
    media="<图片绝对路径（/tmp/openclaw/photo-send/ 下）>",
    message="来啦~ 🌸"
)
```

## 注意事项

- 图片必须复制到 `/tmp/openclaw/photo-send/` 才能被飞书媒体接口访问
- macOS 没有 `shuf` 命令，用 Python 的 `random.sample`
- 如果文件夹少于2张，就发1张；只有1张就发1张
- 如果文件夹为空，回复"文件夹是空的，没找到图片~"
- 发完图片清理临时目录
