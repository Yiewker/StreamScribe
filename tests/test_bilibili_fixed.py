"""
测试修复后的B站字幕检测功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_specific_bilibili_video():
    """测试特定的B站视频"""
    print("测试特定B站视频的字幕检测...")
    print("=" * 50)
    
    try:
        from core.platform.bilibili import BilibiliHandler
        
        handler = BilibiliHandler()
        test_url = "https://www.bilibili.com/video/BV159NbzqEK5"
        
        def status_callback(message):
            print(f"状态: {message}")
        
        print(f"测试URL: {test_url}")
        print("这个视频确认有字幕，我们来看看能否正确检测...")
        print()
        
        # 测试完整的处理流程
        result = handler.get_transcript(test_url, status_callback)
        
        print("\n" + "="*50)
        print("处理结果:")
        print(f"成功: {result['success']}")
        print(f"方法: {result.get('method', '未知')}")
        print(f"视频标题: {result.get('video_title', '未知')}")
        print(f"文稿文件: {result.get('transcript_file', '无')}")
        print(f"错误信息: {result.get('error', '无')}")
        
        if result['success'] and result['transcript_file']:
            # 检查文稿内容
            try:
                with open(result['transcript_file'], 'r', encoding='utf-8') as f:
                    content = f.read()
                
                print(f"\n文稿内容预览 (前300字符):")
                print("-" * 30)
                print(content[:300])
                print("-" * 30)
                
                if result.get('method') == 'subtitle':
                    print("✅ 成功检测并下载了现成字幕！")
                    return True
                elif result.get('method') == 'whisper':
                    print("⚠️ 使用了AI转录，可能字幕检测失败")
                    return False
                
            except Exception as e:
                print(f"❌ 读取文稿文件失败: {e}")
                return False
        else:
            print("❌ 处理失败")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_bbdown_commands_directly():
    """直接测试BBDown命令"""
    print("\n直接测试BBDown命令...")
    print("=" * 50)
    
    try:
        from core.config import get_config
        import subprocess
        
        config = get_config()
        test_url = "https://www.bilibili.com/video/BV159NbzqEK5"
        
        # 确保临时目录存在
        os.makedirs(config.temp_dir, exist_ok=True)
        
        # 测试修复后的命令格式
        commands_to_test = [
            # 获取视频信息
            [config.bbdown_path, test_url, '--only-show-info'],
            
            # 下载字幕
            [config.bbdown_path, test_url, '--sub-only', '--work-dir', config.temp_dir],
        ]
        
        for i, command in enumerate(commands_to_test, 1):
            print(f"\n--- 测试命令 {i} ---")
            print(f"命令: {' '.join(command)}")
            
            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=False,
                    timeout=120
                )
                
                print(f"返回码: {result.returncode}")
                
                # 解码输出
                stdout = ""
                stderr = ""
                for encoding in ['utf-8', 'gbk', 'cp936']:
                    try:
                        stdout = result.stdout.decode(encoding)
                        stderr = result.stderr.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                
                if stdout:
                    print("输出:")
                    print(stdout[:500] + "..." if len(stdout) > 500 else stdout)
                
                if stderr:
                    print("错误:")
                    print(stderr[:500] + "..." if len(stderr) > 500 else stderr)
                
                # 对于字幕下载命令，检查生成的文件
                if '--sub-only' in command:
                    subtitle_files = []
                    for ext in ['*.srt', '*.ass', '*.vtt', '*.xml']:
                        subtitle_files.extend(list(Path(config.temp_dir).glob(ext)))
                    
                    if subtitle_files:
                        print(f"✅ 找到字幕文件: {[f.name for f in subtitle_files]}")
                        
                        # 查看第一个字幕文件的内容
                        first_subtitle = subtitle_files[0]
                        try:
                            with open(first_subtitle, 'r', encoding='utf-8') as f:
                                content = f.read()
                            print(f"字幕内容预览 (前200字符):")
                            print(content[:200])
                            
                            # 清理文件
                            for f in subtitle_files:
                                try:
                                    f.unlink()
                                except:
                                    pass
                                    
                        except Exception as e:
                            print(f"读取字幕文件失败: {e}")
                    else:
                        print("❌ 未找到字幕文件")
                
            except subprocess.TimeoutExpired:
                print("命令超时")
            except Exception as e:
                print(f"命令执行失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_subtitle_conversion():
    """测试字幕格式转换"""
    print("\n测试字幕格式转换...")
    print("=" * 50)
    
    try:
        from core.platform.bilibili import BilibiliHandler
        
        handler = BilibiliHandler()
        
        # 创建测试SRT文件
        test_srt_content = """1
00:00:01,000 --> 00:00:03,000
这是第一句测试字幕

2
00:00:04,000 --> 00:00:06,000
这是第二句测试字幕
"""
        
        test_srt_file = "test_subtitle.srt"
        test_txt_file = "test_subtitle.txt"
        
        # 写入测试SRT文件
        with open(test_srt_file, 'w', encoding='utf-8') as f:
            f.write(test_srt_content)
        
        # 测试转换
        handler._convert_srt_to_txt(test_srt_file, test_txt_file)
        
        # 检查转换结果
        if os.path.exists(test_txt_file):
            with open(test_txt_file, 'r', encoding='utf-8') as f:
                converted_content = f.read()
            
            print("转换结果:")
            print(converted_content)
            
            # 清理测试文件
            try:
                os.remove(test_srt_file)
                os.remove(test_txt_file)
            except:
                pass
            
            if "这是第一句测试字幕" in converted_content and "这是第二句测试字幕" in converted_content:
                print("✅ 字幕转换功能正常")
                return True
            else:
                print("❌ 字幕转换结果不正确")
                return False
        else:
            print("❌ 转换后的文件不存在")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("🔧 修复后的B站字幕检测功能测试")
    print("=" * 60)
    
    tests = [
        test_subtitle_conversion,
        test_bbdown_commands_directly,
        test_specific_bilibili_video
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print(f"✅ {test.__name__} 通过")
            else:
                print(f"❌ {test.__name__} 失败")
        except Exception as e:
            print(f"❌ {test.__name__} 异常: {e}")
        
        print("\n" + "="*60)
    
    print(f"\n测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！B站字幕检测功能已修复")
        return True
    else:
        print("\n❌ 部分测试失败，需要进一步调试")
        return False


if __name__ == "__main__":
    try:
        success = main()
        input(f"\n{'测试完成' if success else '测试失败'}！按回车键退出...")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n程序异常: {e}")
        input("按回车键退出...")
        sys.exit(1)
