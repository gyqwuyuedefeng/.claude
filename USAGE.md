# Claude Code 多代理框架使用指南

> 本目录包含 Claude Code 多代理协同开发框架的通用配置
>
> **框架版本**：2.0.0

## 📁 目录结构

```
.claude/
├── .gitignore                      # Git忽略规则
├── USAGE.md                        # 本文件 - 使用说明
├── CLAUDE.md                       # ✅ 通用工作指南
├── PROJECT.md                      # ❌ 项目特定配置（不纳入版本控制）
├── PROJECT.md.template             # ✅ 项目配置模板
├── README.md                       # ✅ 多代理框架详细文档
├── agents/                         # ✅ 子代理定义（12个）
│   ├── workflow-orchestrator.md
│   ├── issue-analyzer.md
│   ├── analysis-aggregator.md
│   ├── master-planner.md
│   ├── plan-splitter.md
│   ├── code-executor.md
│   ├── test-runner.md
│   ├── code-auditor.md
│   ├── auto-fixer.md
│   ├── task-summarizer.md
│   ├── project-info-builder.md
│   └── project-info-updater.md
├── sessions/                       # ❌ 工作流会话（运行时生成，不纳入版本控制）
│   ├── .template/                  # ✅ 会话模板
│   └── {序号}-{描述}-{时间}/        # ❌ 具体会话目录
│       ├── analysis/               # 分析阶段产物
│       ├── planning/               # 计划阶段产物
│       ├── execution/              # 执行阶段产物
│       └── workflow/               # 工作流元数据
└── workflow/                       # ✅ 工作流模板
    ├── workflow-session.md.template
    └── progress.json.template
```

**标识说明**：
- ✅ 通用文件 - 可以直接复制到其他项目
- ❌ 项目特定文件 - 需要根据项目修改

## 🚀 在新项目中使用

### 方法1：完整复制（推荐）

```bash
# 1. 复制整个 .claude 目录到新项目
cp -r /path/to/beilv-agent/.claude /path/to/new-project/

# 2. 进入新项目的 .claude 目录
cd /path/to/new-project/.claude

# 3. 复制模板创建项目配置
cp PROJECT.md.template PROJECT.md

# 4. 编辑 PROJECT.md 填写项目信息
vim PROJECT.md  # 或使用其他编辑器

# 5. 完成！
```

### 方法2：选择性复制

```bash
# 只复制需要的文件
cp /path/to/beilv-agent/.claude/CLAUDE.md /path/to/new-project/.claude/
cp /path/to/beilv-agent/.claude/README.md /path/to/new-project/.claude/
cp -r /path/to/beilv-agent/.claude/agents /path/to/new-project/.claude/
cp -r /path/to/beilv-agent/.claude/workflow /path/to/new-project/.claude/
cp /path/to/beilv-agent/.claude/PROJECT.md.template /path/to/new-project/.claude/

# 创建项目配置
cd /path/to/new-project/.claude
cp PROJECT.md.template PROJECT.md
vim PROJECT.md
```

## 📝 配置 PROJECT.md

`PROJECT.md` 是唯一需要根据项目修改的文件。它包含：

1. **环境说明** - 开发环境特点和限制
2. **项目信息** - 项目名称、类型、技术栈
3. **项目架构** - 目录结构和子项目
4. **编码规范** - 项目特定的代码规范
5. **技术文档** - 相关文档引用
6. **项目约定** - 命名规范、端口分配等

参考 `PROJECT.md.template` 中的说明和示例进行填写。

## 🔧 版本控制配置

### 在原项目中（beilv-agent）

**不要提交** `PROJECT.md` 到版本控制：
- ✅ `PROJECT.md` 已在 `.gitignore` 中
- ✅ 提交 `PROJECT.md.template` 作为模板
- ✅ 提交所有其他通用文件

### 在新项目中

根据需求决定：

**选项1：不提交项目配置**（推荐给开源项目）
```bash
# 保留 .gitignore，让每个开发者创建自己的 PROJECT.md
git add .claude/
# PROJECT.md 会被自动忽略
```

**选项2：提交项目配置**（推荐给团队项目）
```bash
# 修改 .gitignore，移除 PROJECT.md
sed -i '/PROJECT.md/d' .claude/.gitignore

# 然后提交所有文件
git add .claude/
git commit -m "feat: 添加 Claude Code 多代理框架配置"
```

## 📚 文档说明

### CLAUDE.md - 工作指南
- 通用的 Claude Code 工作规范
- 包含开发哲学、编码规则、工作流程
- **不需要修改**，直接使用

### README.md - 框架文档
- 多代理协同系统的详细说明
- 包含架构图、工作流程、使用示例
- **不需要修改**，作为参考文档

### PROJECT.md - 项目配置
- **唯一需要修改**的文件
- 包含项目特定的信息和规范
- 使用 `PROJECT.md.template` 作为起点

### agents/ - 子代理定义
- 12个专职子代理的定义
- 每个代理负责特定职责
- **不需要修改**，按需使用

### workflow/ - 工作流模板
- 工作流会话记录模板
- 进度跟踪JSON模板
- **不需要修改**，框架会自动使用

## 🎯 快速开始

1. **复制框架到新项目**
   ```bash
   cp -r .claude /path/to/new-project/
   ```

2. **创建项目配置**
   ```bash
   cd /path/to/new-project/.claude
   cp PROJECT.md.template PROJECT.md
   ```

3. **编辑项目信息**
   ```bash
   # 修改 PROJECT.md：
   # - 项目名称
   # - 项目架构
   # - 编码规范
   # - 技术文档引用
   ```

4. **开始使用**
   - Claude Code 启动时会自动加载 `CLAUDE.md`
   - `CLAUDE.md` 会通过 `@PROJECT.md` 引用你的项目配置
   - 所有规范和配置即刻生效！

## ❓ 常见问题

### Q: 如何更新框架到最新版本？

A: 复制通用文件到你的项目，**不要覆盖** `PROJECT.md`：
```bash
cp /path/to/latest/.claude/CLAUDE.md .claude/
cp /path/to/latest/.claude/README.md .claude/
cp -r /path/to/latest/.claude/agents .claude/
cp -r /path/to/latest/.claude/workflow .claude/
# 保留你的 PROJECT.md 不变
```

### Q: 可以自定义子代理吗？

A: 可以！在 `agents/` 目录下添加你的自定义代理定义文件即可。

### Q: `PROJECT.md` 应该提交到版本控制吗？

A: 取决于你的场景：
- **团队项目**：提交，让团队统一配置
- **开源项目**：不提交，让贡献者自定义
- **个人项目**：随意

### Q: 如何禁用某些规则？

A: 直接编辑你的 `PROJECT.md`，添加项目特定的规则覆盖。

## 📖 更多信息

- **框架详细文档**：查看 `README.md`
- **工作指南**：查看 `CLAUDE.md`
- **子代理说明**：查看 `agents/` 目录下的各个文件

---

**框架版本**：2.0.0
**更新时间**：2025-12-31
**维护者**：Claude Code 多代理框架团队
