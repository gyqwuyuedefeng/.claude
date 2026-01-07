"""
Vue 组件解析器

提取 Vue 单文件组件的代码结构:
- <script> 标签内容
- 组件选项 (data, methods, computed, etc.)
- TypeScript 类型定义
"""

import re
import sys
from pathlib import Path
from typing import Dict, List


class VueParser:
    """Vue 组件解析器,提取 <script> 标签并解析"""

    # 正则模式
    SCRIPT_TAG = re.compile(r'<script[^>]*>(.*?)</script>', re.DOTALL)
    EXPORT_DEFAULT = re.compile(r'export\s+default\s*{', re.DOTALL)
    METHOD_PATTERN = re.compile(r'(\w+)\s*\(([^)]*)\)\s*{', re.MULTILINE)
    COMPUTED_PATTERN = re.compile(r'computed:\s*{', re.DOTALL)
    DATA_PATTERN = re.compile(r'data\s*\(\)\s*{', re.DOTALL)

    @staticmethod
    def parse_file(file_path: Path) -> Dict:
        """
        解析 Vue 文件

        Args:
            file_path: Vue 文件路径

        Returns:
            包含组件信息的字典
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取 <script> 标签内容
            script_match = VueParser.SCRIPT_TAG.search(content)
            if not script_match:
                return {
                    'language': 'vue',
                    'has_script': False,
                    'methods': [],
                    'computed': []
                }

            script_content = script_match.group(1)

            # 检测是否有 export default
            has_export_default = VueParser.EXPORT_DEFAULT.search(script_content) is not None

            # 提取方法
            methods = []
            for match in VueParser.METHOD_PATTERN.finditer(script_content):
                method_name = match.group(1)
                # 跳过保留字和非方法定义
                if method_name not in ['if', 'else', 'for', 'while', 'function', 'const', 'let', 'var']:
                    methods.append({
                        'name': method_name,
                        'params': match.group(2)
                    })

            # 检测是否有 computed, data 等选项
            has_computed = VueParser.COMPUTED_PATTERN.search(script_content) is not None
            has_data = VueParser.DATA_PATTERN.search(script_content) is not None

            return {
                'language': 'vue',
                'has_script': True,
                'has_export_default': has_export_default,
                'has_computed': has_computed,
                'has_data': has_data,
                'methods': methods
            }

        except Exception as e:
            return {
                'language': 'vue',
                'error': f'解析错误: {e}',
                'has_script': False,
                'methods': []
            }


# 用于命令行测试
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python vue_parser.py <file_path>")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"错误: 文件不存在 {file_path}")
        sys.exit(1)

    result = VueParser.parse_file(file_path)

    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
