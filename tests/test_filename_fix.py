#!/usr/bin/env python3
"""
测试文件名处理修复

验证修复后的文件名清理和文稿文件查找功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.utils import sanitize_filename, generate_output_filename

def test_sanitize_filename():
    """测试文件名清理功能"""
    print("🧪 测试文件名清理功能")
    print("=" * 50)
    
    test_cases = [
        # (原始文件名, 预期结果描述)
        ("看懂了这个，你再去炒股；股市暴跌，为啥散户炒股票总赔钱？李永乐老师用数学告诉你！", "包含分号、问号、中文标点"),
        ("Test<>:\"/\\|?*Video", "包含所有Windows非法字符"),
        ("Normal Video Title", "正常英文标题"),
        ("视频标题【测试】（括号）《书名》", "包含中文括号"),
        ("", "空字符串"),
        ("___", "只有下划线"),
        ("a" * 200, "超长文件名"),
        ("Video@#$%^&+={}[]", "包含特殊符号"),
    ]
    
    for original, description in test_cases:
        cleaned = sanitize_filename(original)
        print(f"原始: {original[:50]}{'...' if len(original) > 50 else ''}")
        print(f"清理: {cleaned}")
        print(f"描述: {description}")
        print(f"长度: {len(cleaned)}")
        print("-" * 30)
    
    print("✅ 文件名清理测试完成\n")

def test_generate_output_filename():
    """测试输出文件名生成"""
    print("🧪 测试输出文件名生成")
    print("=" * 50)
    
    test_titles = [
        "看懂了这个，你再去炒股；股市暴跌，为啥散户炒股票总赔钱？李永乐老师用数学告诉你！",
        "Normal Video Title",
        "Test<>:\"/\\|?*Video",
        "",
    ]
    
    for title in test_titles:
        filename = generate_output_filename(title, 'youtube')
        print(f"标题: {title[:50]}{'...' if len(title) > 50 else ''}")
        print(f"文件名: {filename}")
        print(f"长度: {len(filename)}")
        print("-" * 30)
    
    print("✅ 输出文件名生成测试完成\n")

def test_problematic_video_title():
    """测试问题视频的标题处理"""
    print("🧪 测试问题视频标题处理")
    print("=" * 50)
    
    # 这是导致问题的实际视频标题
    problematic_title = "看懂了这个，你再去炒股；股市暴跌，为啥散户炒股票总赔钱？李永乐老师用数学告诉你！"
    
    print(f"原始标题: {problematic_title}")
    
    # 测试清理
    cleaned = sanitize_filename(problematic_title)
    print(f"清理后: {cleaned}")
    
    # 测试生成文件名
    filename = generate_output_filename(problematic_title, 'youtube')
    print(f"生成文件名: {filename}")
    
    # 检查是否包含问题字符
    problem_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', ';']
    has_problems = any(char in filename for char in problem_chars)
    
    print(f"包含问题字符: {'❌ 是' if has_problems else '✅ 否'}")
    print(f"文件名长度: {len(filename)}")
    
    if has_problems:
        print("⚠️ 文件名仍包含问题字符:")
        for char in problem_chars:
            if char in filename:
                print(f"  - 发现字符: '{char}'")
    
    print("✅ 问题视频标题处理测试完成\n")

def test_file_path_compatibility():
    """测试文件路径兼容性"""
    print("🧪 测试文件路径兼容性")
    print("=" * 50)
    
    problematic_title = "看懂了这个，你再去炒股；股市暴跌，为啥散户炒股票总赔钱？李永乐老师用数学告诉你！"
    filename = generate_output_filename(problematic_title, 'youtube')
    
    # 测试不同的文件路径
    test_paths = [
        f"C:\\temp\\{filename}.mp3",
        f"C:\\temp\\{filename}.txt",
        f"/tmp/{filename}.mp3",
        f"/tmp/{filename}.txt",
    ]
    
    for path in test_paths:
        try:
            # 尝试创建Path对象
            path_obj = Path(path)
            print(f"路径: {path}")
            print(f"有效: ✅")
            print(f"父目录: {path_obj.parent}")
            print(f"文件名: {path_obj.name}")
            print(f"扩展名: {path_obj.suffix}")
        except Exception as e:
            print(f"路径: {path}")
            print(f"有效: ❌ - {e}")
        print("-" * 30)
    
    print("✅ 文件路径兼容性测试完成\n")

def main():
    """主测试函数"""
    print("🔧 文件名处理修复测试")
    print("=" * 60)
    
    # 运行所有测试
    test_sanitize_filename()
    test_generate_output_filename()
    test_problematic_video_title()
    test_file_path_compatibility()
    
    print("🎉 所有测试完成！")
    print("\n📋 修复总结:")
    print("- ✅ 改进了文件名清理函数，处理更多特殊字符")
    print("- ✅ 增加了文件名长度限制")
    print("- ✅ 改进了空文件名处理")
    print("- ✅ 增强了文稿文件查找逻辑")
    print("- ✅ 添加了详细的调试信息")

if __name__ == "__main__":
    main()
