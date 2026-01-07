# Scripts 目录说明

> 更新时间：2025-01-07
> 版本：2.0.0

## 目录状态：已废弃（部分）

### 🗑️ 废弃文件（使用新方案）

以下文件在新的优化方案中**不再需要**：

#### 1. `project_analyzer.py` (11KB)

**原用途**：
- 全量扫描项目文件
- 使用 AST 解析 Python 代码
- 使用正则表达式解析 JS/TS/Java/Vue 代码
- 生成巨大的 JSON 文件（1.2MB, 38,161行）

**废弃原因**：
- ❌ 生成文件过大（1.2MB）
- ❌ 全量扫描浪费资源
- ❌ 难以阅读和使用
- ❌ Token 消耗高

**新方案替代**：
- ✅ 使用 `tree` 命令生成树状结构
- ✅ LLM 基于目录/文件名智能推断职责
- ✅ 按需访问策略（需要时再读取文件）
- ✅ 文件大小 < 10KB

**处理建议**：
```bash
# 归档到 deprecated 目录
mkdir -p .claude/scripts/deprecated
mv .claude/scripts/project_analyzer.py .claude/scripts/deprecated/
mv .claude/scripts/parsers/ .claude/scripts/deprecated/
```

---

#### 2. `project.info` (1.2MB)

**原用途**：
- 旧方案生成的测试文件

**废弃原因**：
- ❌ 格式错误（纯 JSON，应该是 Markdown）
- ❌ 文件过大（1.2MB）
- ❌ 不符合新方案规范

**处理建议**：
```bash
# 删除旧的测试文件
rm .claude/scripts/project.info

# 或者归档
mv .claude/scripts/project.info .claude/scripts/deprecated/
```

---

#### 3. `parsers/` 目录

**原用途**：
- 包含各种语言的代码解析器

**废弃原因**：
- ❌ 配合 `project_analyzer.py` 使用
- ❌ 新方案不需要解析代码

**处理建议**：
```bash
# 归档
mv .claude/scripts/parsers/ .claude/scripts/deprecated/
```

---

### ✅ 保留文件（仍然有用）

以下文件在新方案中**仍然需要**：

#### 1. `validate-session.sh` (5.5KB)

**用途**：
- 验证工作流会话目录的完整性
- 检查必需文件和目录是否存在
- 生成验证报告

**保留原因**：
- ✅ 用于会话管理，与 project.info 生成无关
- ✅ 独立功能，仍然有用

**无需修改**

---

#### 2. `README.md` (6KB)

**用途**：
- 说明 scripts 目录的用途

**保留原因**：
- ✅ 文档文件，需要更新以反映新方案

**需要更新** - 见下方新版本

---

## 目录结构（更新后）

```
.claude/scripts/
├── README.md                      # 说明文档（已更新）
├── DEPRECATED.md                  # 废弃说明（本文件）
├── validate-session.sh            # ✅ 保留：会话验证脚本
└── deprecated/                    # 归档目录
    ├── project_analyzer.py        # 🗑️ 废弃：旧的 Python 分析脚本
    ├── project.info               # 🗑️ 废弃：旧的测试输出
    └── parsers/                   # 🗑️ 废弃：代码解析器
        ├── __init__.py
        ├── python_parser.py
        ├── javascript_parser.py
        └── ...
```

---

## 优化效果对比

| 指标 | 旧方案（Python 脚本） | 新方案（tree + LLM） |
|------|---------------------|---------------------|
| 生成文件大小 | 1.2MB | < 10KB ✅ |
| 生成时间 | ~5-10秒（全量扫描） | < 2秒（tree 命令） ✅ |
| 可读性 | 差（纯 JSON） | 优秀（树状+注释） ✅ |
| Token 消耗 | ~20,000 | ~2,000 ✅ |
| 可维护性 | 复杂（需维护解析器） | 简单（只用 tree） ✅ |

---

## 清理命令（推荐）

```bash
# 1. 创建归档目录
mkdir -p /mnt/d/software/beilv-agent/.claude/scripts/deprecated

# 2. 归档废弃文件
cd /mnt/d/software/beilv-agent/.claude/scripts/
mv project_analyzer.py deprecated/
mv project.info deprecated/
mv parsers/ deprecated/

# 3. 保留有用文件
# validate-session.sh - 保持不变
# README.md - 更新内容

# 4. （可选）彻底删除归档文件
# rm -rf deprecated/
```

---

## 新方案说明

### project-info-builder

**现在使用**：
- `tree` 命令 - 生成树状目录结构
- LLM 推断 - 基于目录/文件名推断职责
- `Write` 工具 - 生成轻量的 Markdown 文件

**不再使用**：
- ❌ Python 脚本全量扫描
- ❌ AST 解析
- ❌ 正则表达式提取函数签名
- ❌ JSON 格式输出

---

### project-info-updater

**现在使用**：
- 只关注**结构性变更**（新增/删除文件/目录）
- 重新运行 `tree` 命令
- 完全重新生成 project.info

**不再使用**：
- ❌ 增量更新 JSON
- ❌ 定位和修改具体条目
- ❌ 处理函数级别的变更

---

## 迁移指南

### 如果你的项目已使用旧方案

1. **删除旧的 project.info**
   ```bash
   cd /path/to/your/project
   rm project.info  # 或者 mv project.info project.info.old
   ```

2. **重新生成（使用新方案）**
   - 调用 `project-info-builder` 子代理
   - 会自动使用新的 tree + LLM 方案

3. **验证新文件**
   - 检查文件大小是否 < 10KB
   - 检查格式是否是 Markdown 树状结构
   - 检查是否有职责注释

---

## 常见问题

### Q1: 是否需要手动删除 deprecated/ 目录？

A: 不强制。建议先归档，测试新方案稳定后再删除。

### Q2: 旧的 project.info 数据会丢失吗？

A: 不会。新方案会重新扫描项目，生成更直观的结构。旧数据不重要，因为：
- 旧数据过于庞大（1.2MB）
- 旧数据难以使用（纯 JSON）
- 新方案生成的信息更实用

### Q3: validate-session.sh 需要更新吗？

A: 不需要。它用于会话验证，与 project.info 生成无关。

---

## 参考

- 新方案文档：`/mnt/d/software/beilv-agent/.claude/agents/project-info-builder.md`
- 更新策略：`/mnt/d/software/beilv-agent/.claude/agents/project-info-updater.md`
- 总体框架：`/mnt/d/software/beilv-agent/.claude/README.md`

---

*最后更新：2025-01-07*
