# StreamScribe 新功能快速上手指南

## 🎯 新功能概览

本次更新添加了以下新功能：

1. ✨ **两个新AI模型**：large-v3-turbo（速度优秀）和 belle-whisper-v3-zh-punct（质量优秀）
2. 📝 **SRT格式开关**：可选择输出SRT字幕或TXT纯文本
3. 🔧 **工具路径优化**：从 tools_path.txt 集中读取工具路径
4. 🚀 **移除batch参数**：提升稳定性

---

## 📋 使用步骤

### 1️⃣ 选择AI模型

启动程序后，在设置面板中：

```
AI模型: [下拉菜单]
├── tiny
├── base
├── small
├── medium
├── large-v2
├── large-v3
├── large-v3-turbo ⚡ (新增 - 速度优秀)
└── belle-whisper-v3-zh-punct ✨ (新增 - 质量优秀)
```

**推荐选择**：
- 🏃 **快速转录**：选择 `large-v3-turbo`（显存1.2GB，耗时23秒）
- 🎯 **高质量中文**：选择 `belle-whisper-v3-zh-punct`（显存2.7GB，耗时55秒）

### 2️⃣ 设置输出格式

在设置面板中找到：

```
☑️ 输出SRT格式  (默认勾选)
```

- **勾选**：输出 `.srt` 字幕文件（带时间戳）
- **不勾选**：输出 `.txt` 纯文本文件

### 3️⃣ 开始转录

1. 输入视频URL或选择本地文件
2. 点击"开始处理"
3. 等待转录完成

---

## ⚙️ 配置工具路径（可选）

如果需要自定义工具路径，编辑 `tools/tools_path.txt`：

```
第1行: whisper-ctranslate2.exe 的完整路径
第2行: yt-dlp.exe 的完整路径
第3行: BBDown.exe 的完整路径
```

**示例**：
```
J:\venvs\fast_whisper_env\Scripts\whisper-ctranslate2.exe
J:\app\yt-dlp\yt-dlp.exe
J:\app\BBDown\BBDown.exe
```

保存后重启程序即可生效。

---

## 🔍 模型对比

| 模型 | 速度 | 准确度 | 显存 | 耗时* | 适用场景 |
|------|------|--------|------|-------|----------|
| large-v3-turbo | ⚡⚡⚡⚡⚡ | ⭐⭐⭐⭐ | 1.2GB | 23秒 | 快速转录、实时处理 |
| belle-whisper-v3-zh-punct | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | 2.7GB | 55秒 | 高质量中文、标点准确 |
| large-v3 | ⚡⚡ | ⭐⭐⭐⭐⭐ | 高 | 慢 | 最高质量 |

*耗时基于测试音频文件

---

## 📝 输出格式对比

### SRT格式（勾选）
```srt
1
00:00:00,000 --> 00:00:05,000
这是第一句话。

2
00:00:05,000 --> 00:00:10,000
这是第二句话。
```

**优点**：
- ✅ 包含时间戳
- ✅ 可用于视频字幕
- ✅ 支持字幕编辑软件

### TXT格式（不勾选）
```txt
这是第一句话。
这是第二句话。
```

**优点**：
- ✅ 纯文本，易于阅读
- ✅ 文件更小
- ✅ 适合文字整理

---

## ❓ 常见问题

### Q1: belle模型提示找不到？
**A**: 确保模型已下载到以下路径：
```
J:\Users\ccd\Desktop\projects\asr\Belle-whisper-large-models\Belle-whisper-v3-zh-punct-ct2
```

### Q2: 工具路径读取失败？
**A**: 检查 `tools/tools_path.txt` 文件：
- 确保文件存在
- 确保每行路径正确
- 确保文件编码为UTF-8

### Q3: 转录速度变慢了？
**A**: 这是正常的。移除batch参数后：
- ✅ 稳定性大幅提升
- ✅ 内存占用更可控
- ⚠️ 速度略有下降（可接受）

### Q4: 如何恢复旧配置？
**A**: 
1. 删除或重命名 `tools/tools_path.txt`
2. 程序会自动使用 `config.ini` 中的配置

---

## 🧪 测试新功能

运行测试脚本验证功能：

```bash
python test_new_features.py
```

测试内容：
- ✅ 工具路径读取
- ✅ 新模型支持
- ✅ SRT格式配置
- ✅ batch参数移除

---

## 📚 更多信息

详细技术文档请查看：
- `docs/NEW_FEATURES_SUMMARY.md` - 完整功能说明
- `config.ini` - 配置文件示例
- `tools/tools_path.txt` - 工具路径配置

---

## 💡 使用建议

1. **首次使用**：建议先用 `large-v3-turbo` 测试，速度快
2. **重要内容**：使用 `belle-whisper-v3-zh-punct`，质量更好
3. **视频字幕**：勾选SRT格式
4. **文字整理**：不勾选SRT格式，使用TXT

---

**祝使用愉快！** 🎉

