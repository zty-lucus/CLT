# -*- coding: utf-8 -*-
"""
测试运行脚本
用于运行B分支代码的所有测试
"""
import pytest
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    # 运行所有测试
    exit_code = pytest.main([
        'tests/',
        '-v',
        '--tb=short',
        '-x'  # 遇到第一个失败就停止
    ])

    sys.exit(exit_code)
