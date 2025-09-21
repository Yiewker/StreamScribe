"""
调试B站字幕检测问题
"""

import sys
import os
import subprocess
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_bbdown_info():
    """测试BBDown获取视频信息"""
    print("测试BBDown获取视频信息...")
    print("=" * 50)
    
    try:
        from core.config import get_config
        
        config = get_config()
        test_url = "https://www.bilibili.com/video/BV159NbzqEK5"
        
        # 测试BBDown --info命令
        command = [
            config.bbdown_path,
            '--info',
            test_url
        ]
        
        print(f"执行命令: {' '.join(command)}")
        print()
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=False,
            timeout=60
        )
        
        print(f"返回码: {result.returncode}")
        
        # 尝试解码输出
        stdout = ""
        stderr = ""
        for encoding in ['utf-8', 'gbk', 'cp936']:
            try:
                stdout = result.stdout.decode(encoding)
                stderr = result.stderr.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        
        print("标准输出:")
        print(stdout)
        print("\n标准错误:")
        print(stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_bbdown_subtitle_check():
    """测试BBDown字幕检查"""
    print("\n测试BBDown字幕检查...")
    print("=" * 50)
    
    try:
        from core.config import get_config
        
        config = get_config()
        test_url = "https://www.bilibili.com/video/BV159NbzqEK5"
        
        # 确保临时目录存在
        os.makedirs(config.temp_dir, exist_ok=True)
        
        # 测试不同的字幕下载命令
        commands_to_test = [
            # 原始命令
            [config.bbdown_path, '--sub-only', '--work-dir', config.temp_dir, test_url],
            
            # 尝试其他参数
            [config.bbdown_path, '--subtitle-only', '--work-dir', config.temp_dir, test_url],
            
            # 检查可用的字幕
            [config.bbdown_path, '--check-subtitle', test_url],
            
            # 列出所有可用内容
            [config.bbdown_path, '--list', test_url],
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
                
                # 检查是否有字幕文件生成
                subtitle_files = list(Path(config.temp_dir).glob("*.srt"))
                subtitle_files.extend(list(Path(config.temp_dir).glob("*.ass")))
                subtitle_files.extend(list(Path(config.temp_dir).glob("*.vtt")))
                
                if subtitle_files:
                    print(f"找到字幕文件: {[f.name for f in subtitle_files]}")
                    
                    # 清理文件
                    for f in subtitle_files:
                        try:
                            f.unlink()
                        except:
                            pass
                else:
                    print("未找到字幕文件")
                
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


def test_bbdown_help():
    """测试BBDown帮助信息，查看正确的参数"""
    print("\n测试BBDown帮助信息...")
    print("=" * 50)
    
    try:
        from core.config import get_config
        
        config = get_config()
        
        # 获取帮助信息
        command = [config.bbdown_path, '--help']
        
        print(f"执行命令: {' '.join(command)}")
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=False,
            timeout=30
        )
        
        # 解码输出
        stdout = ""
        for encoding in ['utf-8', 'gbk', 'cp936']:
            try:
                stdout = result.stdout.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        
        print("BBDown 帮助信息:")
        print(stdout)
        
        # 查找字幕相关的参数
        subtitle_lines = []
        for line in stdout.split('\n'):
            if any(keyword in line.lower() for keyword in ['sub', 'caption', '字幕']):
                subtitle_lines.append(line.strip())
        
        if subtitle_lines:
            print("\n字幕相关参数:")
            for line in subtitle_lines:
                print(f"  {line}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_current_bilibili_handler():
    """测试当前的B站处理器"""
    print("\n测试当前B站处理器...")
    print("=" * 50)
    
    try:
        from core.platform.bilibili import BilibiliHandler
        
        handler = BilibiliHandler()
        test_url = "https://www.bilibili.com/video/BV159NbzqEK5"
        
        def status_callback(message):
            print(f"状态: {message}")
        
        print(f"测试URL: {test_url}")
        print()
        
        # 测试获取视频信息
        print("--- 获取视频信息 ---")
        video_info = handler._get_video_info(test_url)
        print(f"视频信息: {video_info}")
        
        # 测试字幕下载
        print("\n--- 尝试下载字幕 ---")
        subtitle_file = handler._try_download_subtitle(test_url, video_info)
        print(f"字幕文件: {subtitle_file}")
        
        if subtitle_file and os.path.exists(subtitle_file):
            print("✅ 成功下载字幕")
            with open(subtitle_file, 'r', encoding='utf-8') as f:
                content = f.read()[:200]
                print(f"字幕内容预览: {content}...")
        else:
            print("❌ 未能下载字幕")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("🔧 B站字幕检测调试")
    print("=" * 60)
    
    tests = [
        test_bbdown_help,
        test_bbdown_info,
        test_bbdown_subtitle_check,
        test_current_bilibili_handler
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"测试 {test.__name__} 异常: {e}")
        
        print("\n" + "="*60)
    
    print("\n调试完成！")
    print("请查看上面的输出，找出字幕检测失败的原因。")


if __name__ == "__main__":
    try:
        main()
        input("\n按回车键退出...")
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n程序异常: {e}")
        input("按回车键退出...")
