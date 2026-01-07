#!/usr/bin/env python3
"""
项目代码分析工具

递归扫描项目目录,提取代码结构信息,支持:
- Python (使用 ast 模块)
- JavaScript/TypeScript (使用正则表达式)
- Java (使用正则表达式)
- Vue (提取 <script> 标签)

输出 JSON 格式,供 project-info-builder 子代理使用
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime

# 导入解析器
from parsers.python_parser import PythonParser
from parsers.javascript_parser import JavaScriptParser
from parsers.java_parser import JavaParser
from parsers.vue_parser import VueParser


class ProjectScanner:
    """项目目录扫描器"""

    # 默认排除的目录
    DEFAULT_EXCLUDE = {
        'node_modules', '.git', 'dist', 'build', 'target',
        '__pycache__', '.venv', 'venv', '.idea', '.vscode',
        'coverage', 'logs', 'tmp', 'temp', '.next', '.nuxt',
        'out', '.cache', '.pytest_cache', '.mypy_cache'
    }

    # 支持的代码文件扩展名
    CODE_EXTENSIONS = {
        '.py', '.js', '.ts', '.tsx', '.jsx',
        '.java', '.vue', '.go', '.rs', '.cpp', '.c', '.h'
    }

    def __init__(self, project_path: Path, exclude_dirs: Set[str] = None, max_depth: int = 10):
        self.project_path = project_path.resolve()
        self.exclude_dirs = exclude_dirs if exclude_dirs is not None else self.DEFAULT_EXCLUDE
        self.max_depth = max_depth

    def scan(self, verbose: bool = False) -> Dict:
        """
        扫描项目目录结构

        Returns:
            {
                'structure': {...},  # 目录树结构
                'files': [...],      # 代码文件列表
                'stats': {...}       # 统计信息
            }
        """
        files = []
        stats = {
            'total_files': 0,
            'code_files': 0,
            'by_extension': {}
        }

        if verbose:
            print(f"扫描项目: {self.project_path}", file=sys.stderr)

        # 遍历所有文件
        for item in self.project_path.rglob('*'):
            # 跳过排除的目录
            if any(excluded in item.parts for excluded in self.exclude_dirs):
                continue

            # 检查目录深度
            try:
                depth = len(item.relative_to(self.project_path).parts)
                if depth > self.max_depth:
                    continue
            except ValueError:
                continue

            if item.is_file():
                stats['total_files'] += 1
                ext = item.suffix.lower()

                # 统计文件扩展名
                if ext:
                    stats['by_extension'][ext] = stats['by_extension'].get(ext, 0) + 1

                # 检测是否是代码文件
                if ext in self.CODE_EXTENSIONS:
                    stats['code_files'] += 1
                    relative_path = str(item.relative_to(self.project_path))
                    files.append({
                        'path': relative_path,
                        'ext': ext,
                        'size': item.stat().st_size
                    })

                    if verbose and stats['code_files'] % 100 == 0:
                        print(f"  已扫描 {stats['code_files']} 个代码文件...", file=sys.stderr)

        # 构建目录树结构
        structure = self._build_tree(files)

        if verbose:
            print(f"扫描完成: {stats['total_files']} 个文件, {stats['code_files']} 个代码文件", file=sys.stderr)

        return {
            'structure': structure,
            'files': files,
            'stats': stats
        }

    def _build_tree(self, files: List[Dict]) -> Dict:
        """根据文件列表构建目录树"""
        tree = {}

        for file_info in files:
            path_parts = Path(file_info['path']).parts
            current = tree

            # 构建目录层级
            for part in path_parts[:-1]:
                if part not in current:
                    current[part] = {'type': 'directory', 'children': {}}
                current = current[part]['children']

            # 添加文件
            filename = path_parts[-1]
            current[filename] = {'type': 'file', 'ext': file_info['ext']}

        return tree


class ProjectAnalyzer:
    """项目代码分析器,整合所有解析器"""

    # 解析器映射
    PARSERS = {
        '.py': PythonParser,
        '.js': JavaScriptParser,
        '.ts': JavaScriptParser,
        '.tsx': JavaScriptParser,
        '.jsx': JavaScriptParser,
        '.java': JavaParser,
        '.vue': VueParser
    }

    def __init__(self, project_path: Path, exclude_dirs: Set[str] = None, max_depth: int = 10, verbose: bool = False):
        self.project_path = project_path
        self.scanner = ProjectScanner(project_path, exclude_dirs, max_depth)
        self.verbose = verbose

    def analyze(self) -> Dict:
        """
        分析项目代码结构

        Returns:
            完整的项目分析结果 (JSON 格式)
        """
        start_time = time.time()

        if self.verbose:
            print(f"\n=== 开始分析项目 ===", file=sys.stderr)
            print(f"项目路径: {self.project_path}", file=sys.stderr)

        # 1. 扫描目录
        if self.verbose:
            print(f"\n[1/3] 扫描目录结构...", file=sys.stderr)
        scan_result = self.scanner.scan(self.verbose)

        # 2. 推断项目类型和技术栈
        if self.verbose:
            print(f"\n[2/3] 分析技术栈...", file=sys.stderr)
        project_type, tech_stack = self._infer_tech_stack(scan_result['stats'])

        # 3. 解析代码文件
        if self.verbose:
            print(f"\n[3/3] 解析代码文件...", file=sys.stderr)
        parsed_files = []
        parse_errors = []

        for idx, file_info in enumerate(scan_result['files']):
            ext = file_info['ext']
            if ext in self.PARSERS:
                parser_class = self.PARSERS[ext]
                file_path = self.project_path / file_info['path']

                try:
                    parsed = parser_class.parse_file(file_path)
                    parsed_files.append({
                        'path': file_info['path'],
                        **parsed
                    })

                    if self.verbose and (idx + 1) % 50 == 0:
                        print(f"  已解析 {idx + 1}/{len(scan_result['files'])} 个文件...", file=sys.stderr)

                except Exception as e:
                    error_msg = f"{file_info['path']}: {str(e)}"
                    parse_errors.append(error_msg)
                    if self.verbose:
                        print(f"  警告: {error_msg}", file=sys.stderr)

        # 计算耗时
        duration_ms = int((time.time() - start_time) * 1000)

        if self.verbose:
            print(f"\n=== 分析完成 ===", file=sys.stderr)
            print(f"耗时: {duration_ms}ms", file=sys.stderr)
            print(f"解析成功: {len(parsed_files)}/{len(scan_result['files'])} 个文件", file=sys.stderr)
            if parse_errors:
                print(f"解析错误: {len(parse_errors)} 个文件", file=sys.stderr)

        # 组装结果
        result = {
            'project_name': self.project_path.name,
            'project_path': str(self.project_path),
            'project_type': project_type,
            'tech_stack': tech_stack,
            'file_stats': scan_result['stats'],
            'structure': scan_result['structure'],
            'files': parsed_files,
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'analyzer_version': '1.0.0',
                'scan_duration_ms': duration_ms,
                'parse_errors': parse_errors[:10] if parse_errors else []  # 最多保留10个错误
            }
        }

        return result

    def _infer_tech_stack(self, stats: Dict) -> tuple:
        """根据文件统计推断项目类型和技术栈"""
        by_ext = stats.get('by_extension', {})

        tech_stack = []
        project_type = 'unknown'

        # Python 项目
        if '.py' in by_ext:
            tech_stack.append('Python')
            project_type = 'backend'

        # JavaScript/TypeScript 项目
        if any(ext in by_ext for ext in ['.js', '.ts', '.jsx', '.tsx']):
            if '.ts' in by_ext or '.tsx' in by_ext:
                tech_stack.append('TypeScript')
            else:
                tech_stack.append('JavaScript')

            # 检测前端框架
            if '.vue' in by_ext:
                tech_stack.append('Vue')
                project_type = 'frontend'
            elif '.tsx' in by_ext or '.jsx' in by_ext:
                tech_stack.append('React')
                project_type = 'frontend'
            else:
                project_type = 'frontend' if project_type == 'unknown' else 'fullstack'

        # Java 项目
        if '.java' in by_ext:
            tech_stack.append('Java')
            project_type = 'backend' if project_type == 'unknown' else 'fullstack'

        # 其他语言
        if '.go' in by_ext:
            tech_stack.append('Go')
            project_type = 'backend'
        if '.rs' in by_ext:
            tech_stack.append('Rust')
            project_type = 'backend'

        return project_type, tech_stack


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description='分析项目代码结构，提取函数、类等信息',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--project-path',
        required=True,
        help='项目根目录路径'
    )
    parser.add_argument(
        '--output-format',
        default='json',
        choices=['json'],
        help='输出格式 (默认: json)'
    )
    parser.add_argument(
        '--exclude-dirs',
        help='额外排除的目录，逗号分隔 (如: temp,cache)'
    )
    parser.add_argument(
        '--max-depth',
        type=int,
        default=10,
        help='最大目录深度 (默认: 10)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='显示详细日志'
    )

    args = parser.parse_args()

    # 验证路径
    project_path = Path(args.project_path).resolve()
    if not project_path.exists():
        print(f"错误: 路径不存在 {project_path}", file=sys.stderr)
        sys.exit(1)

    if not project_path.is_dir():
        print(f"错误: 路径不是目录 {project_path}", file=sys.stderr)
        sys.exit(1)

    # 解析排除目录
    exclude_dirs = ProjectScanner.DEFAULT_EXCLUDE.copy()
    if args.exclude_dirs:
        for dir_name in args.exclude_dirs.split(','):
            exclude_dirs.add(dir_name.strip())

    # 分析项目
    try:
        analyzer = ProjectAnalyzer(
            project_path,
            exclude_dirs=exclude_dirs,
            max_depth=args.max_depth,
            verbose=args.verbose
        )
        result = analyzer.analyze()

        # 输出 JSON
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0)

    except KeyboardInterrupt:
        print("\n\n中断: 用户取消", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n错误: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
