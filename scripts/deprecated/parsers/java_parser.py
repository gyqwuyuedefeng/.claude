"""
Java 代码解析器

使用正则表达式匹配代码结构,提取:
- 类定义 (class)
- 接口定义 (interface)
- 方法定义
- 注解 (annotation)
"""

import re
import sys
from pathlib import Path
from typing import Dict, List


class JavaParser:
    """Java 代码解析器,使用正则表达式匹配"""

    # 正则模式
    CLASS_PATTERN = re.compile(
        r'(?:public\s+)?(?:abstract\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?',
        re.MULTILINE
    )
    INTERFACE_PATTERN = re.compile(
        r'(?:public\s+)?interface\s+(\w+)(?:\s+extends\s+([^{]+))?',
        re.MULTILINE
    )
    METHOD_PATTERN = re.compile(
        r'(?:public|private|protected)\s+(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?(\w+(?:<[^>]+>)?)\s+(\w+)\s*\(([^)]*)\)',
        re.MULTILINE
    )
    ANNOTATION_PATTERN = re.compile(
        r'@(\w+)(?:\([^)]*\))?',
        re.MULTILINE
    )

    @staticmethod
    def parse_file(file_path: Path) -> Dict:
        """
        解析 Java 文件

        Args:
            file_path: Java 文件路径

        Returns:
            包含类、接口、方法信息的字典
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            classes = []
            interfaces = []

            # 提取类
            for match in JavaParser.CLASS_PATTERN.finditer(content):
                class_name = match.group(1)
                extends = match.group(2) if match.lastindex >= 2 else None
                implements = match.group(3).strip() if match.lastindex >= 3 and match.group(3) else None

                # 提取类内方法
                class_start = match.end()
                class_end = JavaParser._find_block_end(content, class_start)
                class_body = content[class_start:class_end] if class_end else ""

                methods = []
                for method_match in JavaParser.METHOD_PATTERN.finditer(class_body):
                    # 提取方法前的注解
                    method_start = method_match.start()
                    annotations = []
                    for anno_match in JavaParser.ANNOTATION_PATTERN.finditer(class_body[:method_start]):
                        annotations.append(anno_match.group(1))

                    methods.append({
                        'name': method_match.group(2),
                        'return_type': method_match.group(1),
                        'params': method_match.group(3),
                        'annotations': annotations[-3:] if annotations else []  # 最近3个注解
                    })

                classes.append({
                    'name': class_name,
                    'extends': extends,
                    'implements': implements,
                    'line': content[:match.start()].count('\n') + 1,
                    'methods': methods
                })

            # 提取接口
            for match in JavaParser.INTERFACE_PATTERN.finditer(content):
                interfaces.append({
                    'name': match.group(1),
                    'extends': match.group(2).strip() if match.lastindex >= 2 and match.group(2) else None,
                    'line': content[:match.start()].count('\n') + 1
                })

            return {
                'language': 'java',
                'classes': classes,
                'interfaces': interfaces
            }

        except Exception as e:
            return {
                'language': 'java',
                'error': f'解析错误: {e}',
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
            if char == '"':
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
        print("用法: python java_parser.py <file_path>")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"错误: 文件不存在 {file_path}")
        sys.exit(1)

    result = JavaParser.parse_file(file_path)

    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
