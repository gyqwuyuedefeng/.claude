"""
JavaScript/TypeScript 代码解析器

使用正则表达式匹配代码结构,提取:
- 函数声明 (function)
- 箭头函数 (=>)
- 类定义 (class)
- 接口定义 (interface, TypeScript)
- 导出语句 (export)
"""

import re
import sys
from pathlib import Path
from typing import Dict, List


class JavaScriptParser:
    """JavaScript/TypeScript 代码解析器,使用正则表达式匹配"""

    # 正则模式
    FUNCTION_PATTERN = re.compile(
        r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\((.*?)\)',
        re.MULTILINE
    )
    ARROW_PATTERN = re.compile(
        r'(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s*)?\((.*?)\)\s*=>',
        re.MULTILINE
    )
    CLASS_PATTERN = re.compile(
        r'(?:export\s+)?(?:abstract\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?',
        re.MULTILINE
    )
    INTERFACE_PATTERN = re.compile(
        r'(?:export\s+)?interface\s+(\w+)(?:\s+extends\s+([^{]+))?',
        re.MULTILINE
    )
    METHOD_PATTERN = re.compile(
        r'(?:public|private|protected)?\s*(?:async\s+)?(\w+)\s*\((.*?)\)',
        re.MULTILINE
    )

    @staticmethod
    def parse_file(file_path: Path) -> Dict:
        """
        解析 JavaScript/TypeScript 文件

        Args:
            file_path: JS/TS 文件路径

        Returns:
            包含函数、类、接口信息的字典
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            functions = []
            classes = []
            interfaces = []

            # 提取函数声明
            for match in JavaScriptParser.FUNCTION_PATTERN.finditer(content):
                functions.append({
                    'name': match.group(1),
                    'signature': match.group(0),
                    'params': match.group(2),
                    'line': content[:match.start()].count('\n') + 1,
                    'type': 'function'
                })

            # 提取箭头函数
            for match in JavaScriptParser.ARROW_PATTERN.finditer(content):
                functions.append({
                    'name': match.group(1),
                    'signature': match.group(0),
                    'params': match.group(2),
                    'line': content[:match.start()].count('\n') + 1,
                    'type': 'arrow_function'
                })

            # 提取类
            for match in JavaScriptParser.CLASS_PATTERN.finditer(content):
                class_name = match.group(1)
                extends = match.group(2) if match.lastindex >= 2 else None

                # 尝试提取类方法
                class_start = match.end()
                class_end = JavaScriptParser._find_block_end(content, class_start)
                class_body = content[class_start:class_end] if class_end else ""

                methods = []
                for method_match in JavaScriptParser.METHOD_PATTERN.finditer(class_body):
                    methods.append({
                        'name': method_match.group(1),
                        'params': method_match.group(2)
                    })

                classes.append({
                    'name': class_name,
                    'extends': extends,
                    'line': content[:match.start()].count('\n') + 1,
                    'methods': methods
                })

            # 提取接口 (TypeScript)
            for match in JavaScriptParser.INTERFACE_PATTERN.finditer(content):
                interfaces.append({
                    'name': match.group(1),
                    'extends': match.group(2).strip() if match.lastindex >= 2 and match.group(2) else None,
                    'line': content[:match.start()].count('\n') + 1
                })

            return {
                'language': 'javascript',
                'functions': functions,
                'classes': classes,
                'interfaces': interfaces
            }

        except Exception as e:
            return {
                'language': 'javascript',
                'error': f'解析错误: {e}',
                'functions': [],
                'classes': [],
                'interfaces': []
            }

    @staticmethod
    def _find_block_end(content: str, start: int) -> int:
        """查找代码块的结束位置 (匹配大括号)"""
        brace_count = 0
        in_string = False
        escape = False

        for i in range(start, len(content)):
            char = content[i]

            # 跳过字符串内容
            if char == '"' or char == "'":
                if not escape:
                    in_string = not in_string
                escape = False
            elif char == '\\':
                escape = True
            else:
                escape = False

            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        return i

        return len(content)


# 用于命令行测试
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python javascript_parser.py <file_path>")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"错误: 文件不存在 {file_path}")
        sys.exit(1)

    result = JavaScriptParser.parse_file(file_path)

    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
