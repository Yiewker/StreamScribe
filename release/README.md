# StreamScribe

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

StreamScribe 是一个通用的视频流文稿提取工具，能够智能地为视频生成纯文本格式的文稿。

## 🎯 项目特色

- **🎬 多平台支持**: 支持 YouTube、Bilibili 等主流视频平台
- **🤖 智能转录**: 优先使用字幕，无字幕时自动调用 Whisper AI 转录
- **🖥️ 现代界面**: 基于 CustomTkinter 的美观用户界面
- **⚙️ 高度可配置**: 通过配置文件灵活管理所有设置
- **📊 实时反馈**: 详细的进度显示和状态反馈

## 功能特性

- **多平台支持**: 模块化设计，当前支持 YouTube，未来可轻松扩展到 Bilibili 等其他平台
- **智能转录**: 自动检测并优先使用 CC 字幕；若无字幕，则调用本地 Whisper 模型进行 AI 转录
- **图形界面**: 基于 CustomTkinter 的现代化用户界面
- **可配置化**: 通过 `config.ini` 文件管理所有设置
- **状态反馈**: 实时显示任务进度和结果

## 系统要求

- Python 3.8+
- Windows 操作系统
- yt-dlp (外部工具)
- whisper-ctranslate2 (在独立虚拟环境中)

## 安装和配置

1. **克隆项目**:
   ```bash
   git clone https://github.com/yiewker/StreamScribe.git
   cd StreamScribe
   ```

2. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```

3. **配置设置**:
   编辑 `config.ini` 文件，确保以下路径正确：
   - `yt_dlp_path`: yt-dlp 可执行文件路径
   - `whisper_venv_path`: Whisper 虚拟环境路径
   - `output_dir`: 输出文件目录
   - `proxy`: 网络代理设置（如需要）

## 使用方法

1. 运行应用程序：
   ```bash
   python main.py
   ```

2. 在界面中输入视频链接（当前支持 YouTube）

3. 点击"开始"按钮开始处理

4. 等待处理完成，文稿将保存到配置的输出目录

## 项目架构

```
StreamScribe/
├── main.py              # GUI主程序入口
├── ui.py                # UI界面布局
├── config.ini           # 配置文件
├── requirements.txt     # 项目依赖
├── README.md           # 项目说明
└── core/               # 核心后端逻辑包
    ├── __init__.py
    ├── manager.py       # 任务管理器
    ├── config.py        # 配置模块
    ├── transcriber.py   # AI转录模块
    ├── utils.py         # 工具函数模块
    └── platform/        # 平台相关逻辑子包
        ├── __init__.py
        ├── youtube.py   # YouTube平台处理器
        └── (bilibili.py) # 未来扩展
```

## 扩展新平台

要添加新的视频平台支持：

1. 在 `core/platform/` 目录下创建新的平台处理器文件
2. 实现与 `youtube.py` 相同的接口
3. 在 `core/manager.py` 中添加平台识别逻辑

## 📸 界面预览

![StreamScribe 界面](docs/screenshot.png)

## 🔧 技术栈

- **前端**: CustomTkinter (现代化 GUI 框架)
- **后端**: Python 3.8+
- **AI 转录**: Whisper (OpenAI)
- **视频处理**: yt-dlp, BBDown
- **配置管理**: ConfigParser

## 📝 更新日志

### v1.0.0 (2024-12-21)
- 🎉 首次发布
- ✅ 支持 YouTube 和 Bilibili 平台
- ✅ 集成 Whisper AI 转录
- ✅ 现代化用户界面
- ✅ 完整的配置系统

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 👨‍💻 作者

- **yiewker** - [GitHub](https://github.com/yiewker)

## 🙏 致谢

- [OpenAI Whisper](https://github.com/openai/whisper) - AI 转录技术
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - 视频下载工具
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - 现代化 GUI 框架

## 📞 支持

如果您遇到问题或有建议，请：

- 📋 [提交 Issue](https://github.com/yiewker/StreamScribe/issues)
- 💬 [参与讨论](https://github.com/yiewker/StreamScribe/discussions)
- ⭐ 如果这个项目对您有帮助，请给个 Star！
