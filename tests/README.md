# StreamScribe 测试文件

这个目录包含了 StreamScribe 项目的所有测试文件。

## 测试文件说明

### 核心功能测试
- `test_core.py` - 核心功能测试（推荐首先运行）
- `test_complete_system.py` - 完整系统测试
- `test_fixed_system.py` - 修复后的系统测试

### 模块测试
- `test_model_selection.py` - 模型选择和量化映射测试
- `test_command_printing.py` - 命令打印功能测试
- `test_optimized_whisper.py` - 优化后的 Whisper 性能测试

### Whisper 相关测试
- `test_whisper_ctranslate2.py` - whisper-ctranslate2 功能测试
- `test_whisper_direct.py` - 直接 Whisper 测试
- `test_whisper_only.py` - 仅 Whisper 测试
- `test_whisper_import.py` - Whisper 导入测试
- `test_faster_whisper.py` - faster_whisper 测试

### 字幕相关测试
- `test_subtitle.py` - 字幕检测测试
- `test_subtitle_fixed.py` - 修复后的字幕检测测试
- `test_simple.py` - 简单功能测试

### 调试和设置
- `debug_whisper.py` - Whisper 环境调试
- `setup_whisper.py` - Whisper 环境设置
- `setup_whisper.bat` - Whisper 环境设置批处理

## 运行测试

### 方法1: 使用批处理文件（推荐）
```bash
# 在项目根目录双击或运行
test.bat
```

### 方法2: 直接运行 Python
```bash
# 在项目根目录运行
python tests/test_core.py
```

### 方法3: 运行特定测试
```bash
# 测试模型选择功能
python tests/test_model_selection.py

# 测试完整系统
python tests/test_complete_system.py

# 测试 Whisper 功能
python tests/test_whisper_ctranslate2.py
```

## 测试顺序建议

1. **首先运行**: `test_core.py` - 验证基本功能
2. **然后运行**: `test_model_selection.py` - 验证模型选择
3. **最后运行**: `test_complete_system.py` - 完整功能测试

## 注意事项

- 大部分测试需要网络连接（访问 YouTube）
- Whisper 相关测试需要正确配置虚拟环境
- 某些测试可能需要较长时间（AI 转录）
- 测试过程中会在控制台显示详细的命令和状态信息
