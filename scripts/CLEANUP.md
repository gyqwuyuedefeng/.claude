# Scripts 目录 - 清理指南

> 更新时间：2025-01-07

## 🎯 清理目标

将旧方案的废弃文件归档到 `deprecated/` 目录，保留有用文件。

---

## 📋 当前状态

### 已归档文件 ✅
- ✅ `project_analyzer.py` (11KB) - 已移至 `deprecated/`
- ✅ `project.info` (1.2MB) - 已移至 `deprecated/`（测试文件）

### 待归档文件 ⏳
- ⏳ `parsers/` 目录 - 因权限问题暂未移动

### 保留文件 ✅
- ✅ `validate-session.sh` - 会话验证脚本（仍然有用）
- ✅ `README.md` - 说明文档（需要更新）
- ✅ `DEPRECATED.md` - 废弃说明（本文件）

---

## 🛠️ 手动清理命令

如果自动归档失败，请手动执行以下命令：

```bash
# 进入 scripts 目录
cd /mnt/d/software/beilv-agent/.claude/scripts/

# 方法1：复制后删除（推荐）
cp -r parsers/ deprecated/
rm -rf parsers/

# 或者方法2：强制移动
sudo mv parsers/ deprecated/ 2>/dev/null || cp -r parsers/ deprecated/ && rm -rf parsers/

# 验证清理结果
ls -la
ls -la deprecated/
```

---

## 📊 清理后的目录结构

```
.claude/scripts/
├── README.md                      # 说明文档（需更新）
├── DEPRECATED.md                  # 废弃说明（本文件）
├── CLEANUP.md                     # 清理指南（本文件）
├── validate-session.sh            # ✅ 保留：会话验证脚本
└── deprecated/                    # 归档目录
    ├── project_analyzer.py        # 🗑️ 废弃：旧的 Python 分析脚本
    ├── project.info               # 🗑️ 废弃：旧的测试输出（1.2MB）
    └── parsers/                   # 🗑️ 废弃：代码解析器
        ├── __init__.py
        ├── python_parser.py
        ├── javascript_parser.py
        ├── java_parser.py
        └── vue_parser.py
```

---

## ✅ 验证清理结果

清理完成后，执行以下命令验证：

```bash
# 1. 检查 scripts 目录（应该只有 4 个项目）
ls -la /mnt/d/software/beilv-agent/.claude/scripts/
# 预期输出：
# README.md
# DEPRECATED.md
# CLEANUP.md
# validate-session.sh
# deprecated/

# 2. 检查 deprecated 目录（应该有 3 个项目）
ls -la /mnt/d/software/beilv-agent/.claude/scripts/deprecated/
# 预期输出：
# project_analyzer.py
# project.info
# parsers/

# 3. 统计文件大小
du -sh /mnt/d/software/beilv-agent/.claude/scripts/deprecated/
# 预期输出：~1.3MB（主要是 project.info）
```

---

## 🗑️ 彻底删除归档文件（可选）

**警告**：执行前请确认新方案运行正常！

```bash
# 确认新方案正常运行后，可以彻底删除归档文件
cd /mnt/d/software/beilv-agent/.claude/scripts/

# 删除归档目录（慎重！）
rm -rf deprecated/

# 验证删除
ls -la
# 预期输出：只剩下 README.md, DEPRECATED.md, CLEANUP.md, validate-session.sh
```

---

## 📝 新方案说明

### 旧方案（已废弃）

```python
# 使用 Python 脚本全量扫描
python3 project_analyzer.py --project-path /path/to/project
# 生成 1.2MB 的 JSON 文件
```

**问题**：
- ❌ 文件太大（1.2MB）
- ❌ 难以阅读（纯 JSON）
- ❌ Token 消耗高

---

### 新方案（推荐）

```bash
# 使用 tree 命令 + LLM 推断
tree -L 4 -I 'node_modules|.git|dist|build|__pycache__' /path/to/project
# 生成 < 10KB 的 Markdown 树状结构
```

**优势**：
- ✅ 文件小巧（< 10KB）
- ✅ 直观易读（树状 + 注释）
- ✅ Token 消耗低
- ✅ 按需访问（需要时再读取文件）

---

## 🔗 相关文档

- 新方案文档：`../.claude/agents/project-info-builder.md`
- 更新策略：`../.claude/agents/project-info-updater.md`
- 废弃说明：`./DEPRECATED.md`

---

*最后更新：2025-01-07*
