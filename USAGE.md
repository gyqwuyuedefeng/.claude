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

# 3. 完成！框架已可用
```

### 方法2：选择性复制

```bash
# 只复制需要的文件
cp /path/to/source-project/.claude/CLAUDE.md /path/to/new-project/.claude/
cp /path/to/source-project/.claude/README.md /path/to/new-project/.claude/
cp -r /path/to/source-project/.claude/agents /path/to/new-project/.claude/
cp -r /path/to/source-project/.claude/workflow /path/to/new-project/.claude/

# 完成！
```

## 🔧 版本控制配置

### 提交到版本控制

建议将整个 `.claude` 目录提交到版本控制：

```bash
# 添加并提交 .claude 目录
git add .claude/
git commit -m "feat: 添加 Claude Code 多代理框架"
```

**注意事项**：
- ✅ 所有通用文件都应提交
- ✅ sessions/ 目录会被自动忽略（运行时生成）
- ✅ 框架的配置在 `.claude/.gitignore` 中已正确设置

## 📚 文档说明

### CLAUDE.md - 工作指南
- 通用的 Claude Code 工作规范
- 包含开发哲学、编码规则、工作流程
- **不需要修改**，直接使用

### README.md - 框架文档
- 多代理协同系统的详细说明
- 包含架构图、工作流程、使用示例
- **不需要修改**，作为参考文档

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

2. **开始使用**
   - Claude Code 启动时会自动加载 `CLAUDE.md`
   - 建议在项目根目录的 `CLAUDE.md` 中添加项目特定配置
   - 所有规范和配置即刻生效！

## ❓ 常见问题

### Q: 如何更新框架到最新版本？

A: 复制通用文件到你的项目：
```bash
cp /path/to/latest/.claude/CLAUDE.md .claude/
cp /path/to/latest/.claude/README.md .claude/
cp -r /path/to/latest/.claude/agents .claude/
cp -r /path/to/latest/.claude/workflow .claude/
```

### Q: 可以自定义子代理吗？

A: 可以！在 `agents/` 目录下添加你的自定义代理定义文件即可。

### Q: 如何添加项目特定配置？

A: 在你的项目根目录的 `CLAUDE.md` 中添加项目信息、编码规范等配置。

## 📖 更多信息

- **框架详细文档**：查看 `README.md`
- **工作指南**：查看 `CLAUDE.md`
- **子代理说明**：查看 `agents/` 目录下的各个文件

---

**框架版本**：2.0.0
**更新时间**：2025-12-31
**维护者**：Claude Code 多代理框架团队
