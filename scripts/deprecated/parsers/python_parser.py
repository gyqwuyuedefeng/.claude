"""
Python 代码解析器

使用 Python ast 模块精确解析代码，提取:
- 函数定义 (包括 async 函数)
- 类定义和方法
- docstring
- 函数签名 (参数、返回类型)
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List, Optional


class PythonParser:
    """Python 代码解析器,使用 ast 模块解析代码结构"""

    @staticmethod
    def parse_file(file_path: Path) -> Dict:
        """
        解析 Python 文件，提取函数和类

        Args:
            file_path: Python 文件路径

        Returns:
            包含函数和类信息的字典，格式:
            {
                'language': 'python',
                'functions': [...],
                'classes': [...],
                'imports': [...]
            }
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()

            # 解析 AST
            tree = ast.parse(source, filename=str(file_path))

            functions = []
            classes = []
            imports = []

            # 遍历顶层节点
            for node in ast.iter_child_nodes(tree):
                # 提取函数定义
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_info = PythonParser._extract_function(node, source)
                    functions.append(func_info)

                # 提取类定义
                elif isinstance(node, ast.ClassDef):
                    class_info = PythonParser._extract_class(node, source)
                    classes.append(class_info)

                # 提取导入语句
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    import_info = PythonParser._extract_import(node)
                    imports.append(import_info)

            return {
                'language': 'python',
                'functions': functions,
                'classes': classes,
                'imports': imports
            }

        except SyntaxError as e:
            return {
                'language': 'python',
                'error': f'语法错误: {e}',
                'functions': [],
                'classes': [],
                'imports': []
            }
        except Exception as e:
            return {
                'language': 'python',
                'error': f'解析错误: {e}',
                'functions': [],
                'classes': [],
                'imports': []
            }

    @staticmethod
    def _extract_function(node: ast.FunctionDef, source: str) -> Dict:
        """提取函数信息"""
        # 提取参数
        args = []
        if node.args:
            for arg in node.args.args:
                arg_name = arg.arg
                # 提取类型注解
                arg_type = None
                if arg.annotation:
                    try:
                        arg_type = ast.unparse(arg.annotation)
                    except:
                        arg_type = None
                args.append({
                    'name': arg_name,
                    'type': arg_type
                })

        # 提取返回类型
        return_type = None
        if node.returns:
            try:
                return_type = ast.unparse(node.returns)
            except:
                return_type = None

        # 提取函数签名
        try:
            # 只提取签名部分，不包含函数体
            signature_lines = source.split('\n')[node.lineno - 1:node.lineno + 5]
            signature = ''
            for line in signature_lines:
                signature += line.strip() + ' '
                if ':' in line and not line.strip().startswith('#'):
                    break
            signature = signature.strip()
        except:
            signature = f"{'async ' if isinstance(node, ast.AsyncFunctionDef) else ''}def {node.name}(...)"

        return {
            'name': node.name,
            'signature': signature,
            'docstring': ast.get_docstring(node),
            'line': node.lineno,
            'is_async': isinstance(node, ast.AsyncFunctionDef),
            'args': args,
            'return_type': return_type
        }

    @staticmethod
    def _extract_class(node: ast.ClassDef, source: str) -> Dict:
        """提取类信息"""
        methods = []

        # 遍历类内部节点,提取方法
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_info = PythonParser._extract_function(item, source)
                methods.append(method_info)

        # 提取基类
        bases = []
        for base in node.bases:
            try:
                bases.append(ast.unparse(base))
            except:
                pass

        return {
            'name': node.name,
            'docstring': ast.get_docstring(node),
            'line': node.lineno,
            'bases': bases,
            'methods': methods
        }

    @staticmethod
    def _extract_import(node) -> Dict:
        """提取导入语句"""
        if isinstance(node, ast.Import):
            return {
                'type': 'import',
                'modules': [alias.name for alias in node.names]
            }
        elif isinstance(node, ast.ImportFrom):
            return {
                'type': 'from',
                'module': node.module or '',
                'names': [alias.name for alias in node.names]
            }
        return {}


# 用于命令行测试
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python python_parser.py <file_path>")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"错误: 文件不存在 {file_path}")
        sys.exit(1)

    result = PythonParser.parse_file(file_path)

    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
