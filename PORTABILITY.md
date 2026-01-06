# .claude 目录移植性说明

> 版本：2.0.0
> 更新时间：2026-01-06
> 状态：✅ 已完成通用性改造

---

## 📋 概述

`.claude` 目录是 **Claude Code 多代理协同开发框架** 的核心配置目录。经过通用性改造后，现在可以**直接拷贝到任意项目**使用，无需修改代理文件或脚本。

### ✅ 改造完成项

- [x] 12个代理配置文件 - 所有硬编码路径已改为相对路径
- [x] 脚本文件 - 动态获取项目根目录
- [x] 钩子文件 - 无硬编码路径
- [x] 文档文件 - 使用占位符表示路径

### 🎯 核心特性

- **完全可移植** - 可直接拷贝到任意项目
- **零硬编码** - 所有路径使用相对路径或动态获取
- **简单配置** - 只需修改 `PROJECT.md` 即可使用
- **跨平台兼容** - 支持 Windows、Linux、macOS

---

## 🚀 快速开始

### 步骤1：拷贝 .claude 目录

将整个 `.claude` 目录拷贝到目标项目的根目录：

```bash
# 示例：从当前项目拷贝到新项目
cp -r /path/to/current-project/.claude /path/to/new-project/
```

### 步骤2：配置项目信息

进入新项目，修改 `PROJECT.md` 文件：

```bash
cd /path/to/new-project
```

**方式A：从模板创建**（推荐）
```bash
cp .claude/PROJECT.md.template .claude/PROJECT.md
# 然后编辑 .claude/PROJECT.md
```

**方式B：直接修改现有文件**
```bash
# 编辑 .claude/PROJECT.md，修改以下内容：
# - 项目名称
# - 项目类型
# - 技术栈
# - 项目架构
# - 目录结构
# - 编码规范
# - 数据库表前缀（如适用）
# - 端口分配（如适用）
```

### 步骤3：验证配置

确认 `.claude` 目录结构完整：

```bash
ls -la .claude/
```

应该看到以下目录和文件：
```
.claude/
├── agents/          # 12个代理配置文件
├── hooks/           # 钩子脚本
├── scripts/         # 工具脚本
├── sessions/        # 会话目录（运行时生成）
├── workflow/        # 工作流模板
├── CLAUDE.md        # 工作指南（通用）
├── PROJECT.md       # 项目配置（需修改）
├── README.md        # 框架说明（通用）
└── .gitignore       # Git忽略规则
```

### 步骤4：开始使用

在 Claude Code 中启动工作流：

```bash
# 示例：实现新功能
# Claude 会自动检测并启动 workflow-orchestrator
```

---

## 📁 目录结构说明

### 核心目录

| 目录/文件 | 用途 | 是否需要修改 |
|----------|------|-------------|
| `agents/` | 12个子代理配置文件 | ❌ 不需要 |
| `hooks/` | 工作流钩子脚本 | ❌ 不需要 |
| `scripts/` | 工具脚本（如会话验证） | ❌ 不需要 |
| `workflow/` | 工作流模板文件 | ❌ 不需要 |
| `sessions/` | 会话目录（运行时生成） | ❌ 不需要 |
| `CLAUDE.md` | 通用工作指南 | ❌ 不需要 |
| `README.md` | 框架说明文档 | ❌ 不需要 |
| `PROJECT.md` | **项目特定配置** | ✅ **必须修改** |
| `.gitignore` | Git忽略规则 | ⚠️ 可选修改 |

### 运行时生成的目录

以下目录会在工作流运行时自动创建，**不需要手动创建**：

```
.claude/sessions/
└── {序号}-{描述}-{时间}/
    ├── analysis/      # 分析报告
    ├── planning/      # 计划文档
    ├── execution/     # 执行任务
    └── workflow/      # 工作流状态
```

---

## ⚙️ 配置说明

### PROJECT.md 配置项

`PROJECT.md` 是**唯一需要修改**的文件，包含以下配置项：

#### 1. 基本信息
```markdown
**项目名称**：[你的项目名称]
**项目类型**：[单体应用 / 微服务 / Monorepo / 前后端分离]
**技术栈**：[主要技术栈]
```

#### 2. 项目架构
```markdown
项目根目录: [项目根目录路径]

子项目/模块路径：
├── [模块1名称]: [路径]
├── [模块2名称]: [路径]
└── [模块3名称]: [路径]
```

#### 3. 编码规范
```markdown
### Python 代码规范
- 格式化工具：[工具名称]
- 代码风格：[风格指南]
...

### TypeScript/React 代码规范
...
```

#### 4. 项目特定约定
```markdown
### 数据库表前缀（如适用）
- `user_*`: 用户管理
- `order_*`: 订单管理
...

### 端口分配（如适用）
- 前端: 3000
- 后端: 8080
...
```

### .gitignore 配置

`.claude/.gitignore` 默认排除以下内容：

```gitignore
# 项目特定配置（不纳入版本控制）
PROJECT.md

# 所有工作流会话（运行时生成）
sessions/
!sessions/README.md
```

**建议**：将 `.claude/.gitignore` 的内容添加到项目根目录的 `.gitignore` 中。

---

## 🔧 技术细节

### 路径处理机制

#### 代理文件中的路径

所有代理配置文件（`.claude/agents/*.md`）中的路径都使用**相对路径**：

**示例：workflow-orchestrator.md**
```bash
# 会话ID生成
LAST_NUM=$(ls -1d .claude/sessions/[0-9]* 2>/dev/null | \
  sed 's/.*\/\([0-9]\{3\}\)-.*/\1/' | sort -n | tail -1)

# 目录创建
mkdir -p ".claude/sessions/${SESSION_ID}"/{analysis,planning,execution,workflow}
```

**工作原理**：
- Claude Code 的工作目录默认在项目根目录
- 相对路径 `.claude/sessions/` 会自动解析为 `<项目根目录>/.claude/sessions/`
- 无需手动指定项目根目录

#### 脚本中的路径

脚本文件（如 `.claude/scripts/validate-session.sh`）使用**动态路径获取**：

```bash
# 动态获取项目根目录（脚本在 .claude/scripts/ 下）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SESSION_DIR="$PROJECT_ROOT/.claude/sessions"
```

**工作原理**：
- 脚本首先获取自身所在目录
- 通过相对路径计算项目根目录
- 从项目根目录构建完整路径

### 跨平台兼容性

| 平台 | 路径分隔符 | 兼容性 | 说明 |
|------|----------|--------|------|
| Linux | `/` | ✅ 完全兼容 | 原生支持 |
| macOS | `/` | ✅ 完全兼容 | 原生支持 |
| Windows | `\` 或 `/` | ✅ 完全兼容 | Bash 脚本需在 WSL/Git Bash 中运行 |

**Windows 用户注意**：
- 如果使用 WSL，完全兼容
- 如果使用 Git Bash，完全兼容
- 如果使用 PowerShell，需要安装 WSL 或 Git Bash

---

## 📝 使用示例

### 示例1：拷贝到 Node.js 项目

```bash
# 1. 拷贝 .claude 目录
cp -r /path/to/source/.claude /path/to/nodejs-project/

# 2. 进入新项目
cd /path/to/nodejs-project

# 3. 创建 PROJECT.md
cp .claude/PROJECT.md.template .claude/PROJECT.md

# 4. 编辑 PROJECT.md
nano .claude/PROJECT.md
```

**PROJECT.md 配置示例**：
```markdown
**项目名称**：My Node.js App
**项目类型**：单体应用
**技术栈**：Node.js + Express + MongoDB

## 项目架构
项目根目录: /path/to/nodejs-project

主要目录：
├── src/          # 源代码
├── tests/        # 测试文件
├── config/       # 配置文件
└── public/       # 静态资源
```

### 示例2：拷贝到 Python 项目

```bash
# 1. 拷贝 .claude 目录
cp -r /path/to/source/.claude /path/to/python-project/

# 2. 进入新项目
cd /path/to/python-project

# 3. 修改 PROJECT.md
```

**PROJECT.md 配置示例**：
```markdown
**项目名称**：My Python API
**项目类型**：微服务
**技术栈**：Python + FastAPI + PostgreSQL

## 编码规范
### Python 代码规范
- 使用 Black 格式化（88字符行宽）
- 使用 isort 管理导入
- 遵循 PEP 8 规范
```

### 示例3：拷贝到 Monorepo 项目

```bash
# 1. 拷贝 .claude 目录
cp -r /path/to/source/.claude /path/to/monorepo/

# 2. 修改 PROJECT.md
```

**PROJECT.md 配置示例**：
```markdown
**项目名称**：My Monorepo
**项目类型**：Monorepo
**技术栈**：TypeScript + React + Node.js

## 项目架构
项目根目录: /path/to/monorepo

子项目路径：
├── packages/frontend: packages/frontend
├── packages/backend: packages/backend
├── packages/shared: packages/shared
└── packages/mobile: packages/mobile
```

---

## ❓ 常见问题

### Q1: 拷贝后会话目录创建失败？

**原因**：Claude Code 的工作目录不在项目根目录。

**解决方案**：
```bash
# 确认当前工作目录
pwd

# 应该在项目根目录，如果不是，请切换
cd /path/to/your-project
```

### Q2: 脚本执行失败？

**原因**：脚本没有执行权限。

**解决方案**：
```bash
# 添加执行权限
chmod +x .claude/scripts/*.sh
chmod +x .claude/hooks/*.py
```

### Q3: 代理文件中的路径不正确？

**原因**：可能是旧版本的 `.claude` 目录，未完成通用性改造。

**解决方案**：
```bash
# 验证是否有硬编码路径
grep -r "/mnt/d/software/beilv-agent" .claude/agents/

# 如果有结果，说明是旧版本，需要重新拷贝最新版本
```

### Q4: PROJECT.md 应该纳入版本控制吗？

**建议**：
- **团队项目**：纳入版本控制（删除 `.claude/.gitignore` 中的 `PROJECT.md` 规则）
- **个人项目**：不纳入版本控制（保持默认配置）

### Q5: 如何验证改造是否成功？

**验证方法**：
```bash
# 1. 检查是否有硬编码路径
grep -r "/mnt/d/software/beilv-agent" .claude/

# 2. 如果没有输出，说明改造成功
# 3. 如果有输出，说明还有硬编码路径需要修复
```

---

## 🔄 版本历史

### v2.0.0 (2026-01-06)
- ✅ 完成通用性改造
- ✅ 所有代理文件使用相对路径
- ✅ 脚本文件动态获取项目根目录
- ✅ 创建移植性说明文档

### v1.0.0 (2025-12-31)
- 初始版本
- 包含硬编码路径（不可移植）

---

## 📞 获取帮助

如有问题或建议，请参考：

- **框架说明**：`.claude/README.md`
- **工作指南**：`.claude/CLAUDE.md`
- **项目配置模板**：`.claude/PROJECT.md.template`

---

## 📄 许可证

MIT License

---

**祝您使用愉快！** 🎉
