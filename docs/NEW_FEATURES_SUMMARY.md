# StreamScribe 新功能总结

## 更新日期
2025-11-03

## 新增功能

### 1. 新增两个AI模型选项

#### large-v3-turbo（速度优秀）
- **量化类型**: int8_float16
- **显存占用**: 1.2GB
- **处理速度**: 23秒（测试文件）
- **特点**: 速度优秀，适合快速转录需求
- **命令示例**:
  ```bash
  whisper-ctranslate2.exe audio.flac --model large-v3-turbo --output_format srt --output_dir ./output --compute_type int8_float16 --vad_filter True --language zh
  ```

#### belle-whisper-v3-zh-punct（质量优秀）
- **量化类型**: int8_float16
- **显存占用**: 2.7GB
- **处理速度**: 55秒（测试文件）
- **特点**: 质量优秀，中文标点符号处理更好
- **模型路径**: `J:\Users\ccd\Desktop\projects\asr\Belle-whisper-large-models\Belle-whisper-v3-zh-punct-ct2`
- **命令示例**:
  ```bash
  whisper-ctranslate2.exe audio.flac --model_directory "J:\Users\ccd\Desktop\projects\asr\Belle-whisper-large-models\Belle-whisper-v3-zh-punct-ct2" --output_format srt --output_dir ./output --compute_type int8_float16 --vad_filter True --language zh
  ```

### 2. SRT输出格式勾选框

- **位置**: 设置面板中，强制转录模式下方
- **默认状态**: 勾选（输出SRT格式）
- **功能**: 
  - 勾选时：输出SRT字幕格式（带时间戳）
  - 不勾选时：输出TXT纯文本格式
- **配置保存**: 自动保存到config.ini的`[whisper]`节中的`output_format_srt`选项

### 3. 工具路径读取优化

#### 新的读取方式
- **优先级**: tools/tools_path.txt > config.ini
- **文件格式**: tools/tools_path.txt（每行一个路径）
  ```
  第1行: whisper-ctranslate2.exe的完整路径
  第2行: yt-dlp.exe的完整路径
  第3行: BBDown.exe的完整路径
  ```

#### 示例文件内容
```
J:\venvs\fast_whisper_env\Scripts\whisper-ctranslate2.exe
J:\app\yt-dlp\yt-dlp.exe
J:\app\BBDown\BBDown.exe
```

#### 优势
- 集中管理工具路径
- 无需修改配置文件
- 更容易维护和更新

### 4. 移除batch参数

#### 移除原因
- batch参数的副作用远大于收益
- 可能导致内存问题和不稳定
- 简化配置，提高可靠性

#### 移除的配置项
- `whisper_batched`: 是否启用批处理推理
- `whisper_batch_size`: 批处理大小

#### 影响
- 转录速度可能略有下降，但稳定性大幅提升
- 内存占用更加可控
- 减少了配置复杂度

## 代码修改详情

### 修改的文件

1. **core/config.py**
   - 添加 `_load_tools_paths()` 方法读取tools_path.txt
   - 修改 `yt_dlp_path`、`bbdown_path`、`whisper_venv_path` 属性以优先使用tools_path.txt
   - 添加 `get_model_directory()` 方法支持自定义模型目录
   - 更新 `get_compute_type_for_model()` 添加新模型的量化类型
   - 更新 `get_available_models()` 添加新模型
   - 添加 `whisper_output_format_srt` 属性和 `set_output_format_srt()` 方法
   - 移除 `whisper_batched` 和 `whisper_batch_size` 属性

2. **core/transcriber.py**
   - 修改 `_build_whisper_command()` 方法：
     - 优先从tools_path.txt读取whisper可执行文件路径
     - 支持使用 `--model_directory` 参数（用于belle模型）
     - 根据 `output_format_srt` 配置决定输出格式
     - 移除batch相关参数

3. **ui_compact.py**（紧凑版UI）
   - 模型下拉菜单添加新模型选项
   - 添加SRT输出格式勾选框
   - 添加 `on_output_srt_changed()` 回调函数
   - 更新 `get_model_info()` 添加新模型信息

4. **ui.py**（标准版UI）
   - 模型下拉菜单添加新模型选项
   - 添加SRT输出格式勾选框
   - 添加 `on_output_srt_changed()` 回调函数
   - 更新 `get_model_info()` 添加新模型信息

## 使用说明

### 选择模型

1. 启动StreamScribe
2. 在设置面板中找到"AI模型"下拉菜单
3. 选择合适的模型：
   - **large-v3-turbo**: 需要快速转录时使用
   - **belle-whisper-v3-zh-punct**: 需要高质量中文转录时使用

### 设置输出格式

1. 在设置面板中找到"输出SRT格式"勾选框
2. 勾选：输出带时间戳的SRT字幕文件
3. 不勾选：输出纯文本TXT文件

### 配置工具路径

1. 编辑 `tools/tools_path.txt` 文件
2. 按顺序填写三个工具的完整路径
3. 保存文件后重启程序

## 测试

运行测试脚本验证新功能：
```bash
python test_new_features.py
```

测试内容：
- ✅ 从tools_path.txt读取工具路径
- ✅ 新模型支持和量化类型
- ✅ SRT格式配置
- ✅ batch参数已移除

## 注意事项

1. **belle模型路径**: 确保belle模型已下载到指定路径，否则选择该模型会失败
2. **工具路径**: 如果tools_path.txt不存在或读取失败，会回退到config.ini中的配置
3. **配置保存**: SRT格式设置会自动保存到config.ini，下次启动时保持
4. **性能**: 移除batch参数后，转录速度可能略有下降，但稳定性提升

## 兼容性

- 向后兼容：旧的配置文件仍然可用
- 如果tools_path.txt不存在，会使用config.ini中的路径
- 如果config.ini中没有output_format_srt配置，默认为True（输出SRT）

