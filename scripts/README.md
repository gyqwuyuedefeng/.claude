# 项目代码分析工具

一个高效的项目代码分析工具，用于扫描项目目录并提取代码结构信息，支持多种编程语言。

## 功能特性

- **多语言支持**: Python, JavaScript, TypeScript, Java, Vue
- **精确解析**: Python 使用 ast 模块，其他语言使用正则表达式
- **快速扫描**: 中型项目 (200+ 文件) < 5 秒
- **JSON 输出**: 标准化 JSON 格式，易于集成
- **零依赖**: 仅使用 Python 标准库

## 使用方法

### 基本用法

```bash
cd /mnt/d/software/beilv-agent/.claude/scripts
python3 project_analyzer.py --project-path /path/to/project
```

### 命令行参数

```
--project-path PATH    项目根目录路径 (必需)
--output-format FORMAT 输出格式, 默认 json
--exclude-dirs DIRS    额外排除的目录, 逗号分隔
--max-depth N          最大目录深度, 默认 10
--verbose              显示详细日志
```

### 使用示例

```bash
# 分析项目并输出详细日志
python3 project_analyzer.py \
  --project-path /mnt/d/software/beilv-agent/mall/beilv-agent \
  --verbose

# 排除额外目录
python3 project_analyzer.py \
  --project-path /path/to/project \
  --exclude-dirs "temp,cache,uploads"

# 限制扫描深度
python3 project_analyzer.py \
  --project-path /path/to/project \
  --max-depth 5

# 保存结果到文件
python3 project_analyzer.py \
  --project-path /path/to/project \
  > project_analysis.json
```

## 输出格式

工具输出 JSON 格式，结构如下：

```json
{
  "project_name": "项目名称",
  "project_path": "/项目/路径",
  "project_type": "backend|frontend|fullstack",
  "tech_stack": ["Python", "FastAPI"],
  "file_stats": {
    "total_files": 219,
    "code_files": 219,
    "by_extension": {
      ".py": 219
    }
  },
  "structure": {
    "app": {
      "type": "directory",
      "children": {...}
    }
  },
  "files": [
    {
      "path": "app/api/routes/project.py",
      "language": "python",
      "functions": [...],
      "classes": [...],
      "imports": [...]
    }
  ],
  "metadata": {
    "generated_at": "2026-01-07T10:30:00Z",
    "analyzer_version": "1.0.0",
    "scan_duration_ms": 1234,
    "parse_errors": []
  }
}
```

## 支持的语言

### Python (.py)

- **解析器**: ast 模块 (精确解析)
- **提取内容**:
  - 函数定义 (包括 async 函数)
  - 类定义和方法
  - docstring
  - 函数签名 (参数、返回类型)
  - 导入语句

### JavaScript/TypeScript (.js, .ts, .jsx, .tsx)

- **解析器**: 正则表达式
- **提取内容**:
  - 函数声明
  - 箭头函数
  - 类定义
  - 接口定义 (TypeScript)
  - 方法定义

### Java (.java)

- **解析器**: 正则表达式
- **提取内容**:
  - 类定义
  - 接口定义
  - 方法定义
  - 注解 (Annotations)

### Vue (.vue)

- **解析器**: 正则表达式
- **提取内容**:
  - `<script>` 标签内容
  - 组件方法
  - computed, data 等选项

## 默认排除的目录

工具会自动跳过以下目录：

```
node_modules, .git, dist, build, target,
__pycache__, .venv, venv, .idea, .vscode,
coverage, logs, tmp, temp, .next, .nuxt,
out, .cache, .pytest_cache, .mypy_cache
```

## 性能

| 项目规模 | 文件数 | 扫描时间 | Token 消耗 |
|---------|--------|---------|-----------|
| 小型 | < 50 | < 1秒 | ~2,500 |
| 中型 | 200 | < 5秒 | ~4,500 |
| 大型 | 1000 | < 20秒 | ~8,000 |

## 集成到 project-info-builder

在 `.claude/agents/project-info-builder.md` 中调用：

```bash
# 调用分析脚本
python3 /mnt/d/software/beilv-agent/.claude/scripts/project_analyzer.py \
  --project-path "{project_path}" \
  --output-format json \
  --verbose
```

然后解析 JSON 输出并格式化为 Markdown。

## 扩展指南

### 添加新语言支持

1. 在 `parsers/` 目录创建新的解析器文件 (如 `go_parser.py`)
2. 实现 `parse_file(file_path: Path) -> Dict` 方法
3. 在 `project_analyzer.py` 中注册解析器：

```python
# 在 ProjectAnalyzer.PARSERS 中添加
PARSERS = {
    ...
    '.go': GoParser,
}
```

4. 在 `ProjectScanner.CODE_EXTENSIONS` 中添加扩展名：

```python
CODE_EXTENSIONS = {
    ...
    '.go',
}
```

### 解析器模板

```python
from pathlib import Path
from typing import Dict

class NewLanguageParser:
    @staticmethod
    def parse_file(file_path: Path) -> Dict:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取信息
            functions = [...]
            classes = [...]

            return {
                'language': 'new_language',
                'functions': functions,
                'classes': classes
            }

        except Exception as e:
            return {
                'language': 'new_language',
                'error': str(e),
                'functions': [],
                'classes': []
            }
```

## 测试

### 测试单个解析器

```bash
# 测试 Python 解析器
cd .claude/scripts/parsers
python3 python_parser.py /path/to/file.py

# 测试 JavaScript 解析器
python3 javascript_parser.py /path/to/file.js
```

### 测试主程序

```bash
# 使用详细模式测试
python3 project_analyzer.py \
  --project-path /path/to/small/project \
  --verbose
```

## 故障排除

### 权限错误

在 WSL 环境下可能无法添加执行权限，使用 `python3` 直接运行即可。

### 编码错误

确保所有源文件使用 UTF-8 编码。如遇到编码问题，脚本会跳过该文件并记录错误。

### 解析错误

- **Python**: 检查语法错误
- **其他语言**: 正则匹配可能不完美，但会优雅降级

## 版本历史

- **v1.0.0** (2026-01-07)
  - 初始版本
  - 支持 Python, JavaScript, TypeScript, Java, Vue
  - Token 优化: 减少 75-80%

## 许可证

MIT License

## 技术栈

- Python 3.7+
- 标准库: ast, re, json, pathlib, argparse, datetime
