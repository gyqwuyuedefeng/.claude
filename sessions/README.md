# Sessions 目录说明

> 本目录存放所有工作流会话的运行时文件

## 📋 目录结构

每个会话是一次完整的工作流执行，包含从分析到执行的所有产物。

```
.claude/sessions/
└── {序号}-{描述}-{时间}/
    ├── analysis/              # 分析阶段产物
    ├── planning/              # 计划阶段产物
    ├── execution/             # 执行阶段产物
    └── workflow/              # 工作流元数据
```

## 🏷️ 会话命名规范

**格式**：`{序号}-{描述}-{时间}/`

- **序号**：3位数字，从 001 开始递增
- **描述**：简短的功能描述，使用中划线连接
- **时间**：格式为 `YYYYMMDD-HHMM`

**示例**：
```
001-用户认证功能-20251231-0930/
002-支付宝集成-20251231-1430/
003-修复登录bug-20251231-1600/
004-性能优化-20260101-0900/
```

## 📂 会话内部结构

### 1. analysis/ - 分析阶段产物

**目的**：深度分析需求，定位关键模块和风险

**文件结构**：
```
analysis/
├── {project1}-analysis.md      # 项目1的分析报告
├── {project2}-analysis.md      # 项目2的分析报告（如涉及多个项目）
└── summary.md                   # 汇总所有项目的分析摘要
```

**文件内容**：
- 定位的关键模块和文件
- 评估的影响范围
- 识别的风险点
- 跨项目依赖关系

**生成者**：`issue-analyzer` → `analysis-aggregator`

---

### 2. planning/ - 计划阶段产物

**目的**：制定整体实施计划，拆分阶段和任务

**文件结构**：
```
planning/
├── overall-plan.md              # 整体实施计划（需用户确认）
├── phases.md                    # 阶段和任务索引
└── changes.md                   # 计划变更记录（如有修改）
```

**文件内容**：
- 实施阶段划分
- 每个阶段的任务列表
- 风险点和假设条件
- 人工确认项

**生成者**：`master-planner` → `plan-splitter`

**关键流程**：必须等待用户确认后才能继续

---

### 3. execution/ - 执行阶段产物

**目的**：按计划执行任务，记录执行过程和结果

**文件结构**：
```
execution/
├── phase01-{阶段名称}/
│   ├── README.md                          # 阶段说明
│   ├── task01-{任务名称}/
│   │   ├── task.md                       # 任务详细说明
│   │   ├── reports/
│   │   │   ├── task-report.md           # 任务执行报告
│   │   │   └── test-result.md           # 测试结果
│   │   └── audit/
│   │       ├── audit-20251231-1430.md   # 审计报告
│   │       └── audit-20251231-1450.md   # 重新审计（如有）
│   └── task02-{任务名称}/
│       └── ...
│
├── phase02-{阶段名称}/
└── phase03-{阶段名称}/
```

**文件内容**：
- **task.md**：任务需求、验收标准、实现步骤
- **task-report.md**：代码实现总结、改动说明
- **test-result.md**：测试运行结果、通过率
- **audit-*.md**：代码质量审计报告

**生成者**：
- `plan-splitter` → 创建目录和 task.md
- `code-executor` → 生成 task-report.md
- `test-runner` → 生成 test-result.md
- `code-auditor` → 生成 audit-*.md

**执行流程**：
```
task.md (任务说明)
    ↓
code-executor (实现代码)
    ↓
test-runner (运行测试)
    ↓
code-auditor (审计代码)
    ↓
auto-fixer (自动修复) 或 人工修复
    ↓
task-summarizer (总结并进入下一任务)
```

---

### 4. workflow/ - 工作流元数据

**目的**：记录整个工作流的会话日志和进度

**文件结构**：
```
workflow/
├── session.md                   # 整个工作流的会话记录
├── progress.json                # 全局进度跟踪
└── logs/                        # 各种日志文件
    ├── error.log
    ├── debug.log
    └── execution.log
```

**文件内容**：
- **session.md**：完整的工作流执行记录
- **progress.json**：当前进度、已完成/进行中/待执行的任务
- **logs/**：详细的执行日志

**生成者**：
- `workflow-orchestrator` → 创建 session.md
- `plan-splitter` → 初始化 progress.json
- `task-summarizer` → 更新 progress.json

**progress.json 示例**：
```json
{
  "session_id": "001-用户认证功能-20251231-0930",
  "status": "in_progress",
  "current_phase": "phase02-后端API开发",
  "current_task": "task03-实现登录接口",
  "start_time": "2025-12-31T09:30:00",
  "phases": [
    {
      "id": "phase01",
      "name": "数据库设计",
      "status": "completed",
      "tasks": [
        {"id": "task01", "name": "创建用户表", "status": "completed"},
        {"id": "task02", "name": "创建认证表", "status": "completed"}
      ]
    },
    {
      "id": "phase02",
      "name": "后端API开发",
      "status": "in_progress",
      "tasks": [
        {"id": "task03", "name": "实现登录接口", "status": "in_progress"},
        {"id": "task04", "name": "实现注册接口", "status": "pending"}
      ]
    }
  ]
}
```

---

## 🔄 工作流生命周期

一个完整的会话经历以下阶段：

### 1️⃣ 创建会话
```bash
# 自动创建会话目录
.claude/sessions/001-用户认证功能-20251231-0930/
```

### 2️⃣ 分析阶段
```
生成 analysis/ 下的文件
```

### 3️⃣ 计划阶段
```
生成 planning/ 下的文件
等待用户确认
```

### 4️⃣ 执行阶段
```
在 execution/ 下逐个执行任务
每个任务生成对应的产物
```

### 5️⃣ 完成
```
所有任务完成后，会话状态变为 completed
```

---

## 📊 会话状态

| 状态 | 说明 |
|------|------|
| `pending` | 刚创建，等待开始 |
| `analyzing` | 分析阶段 |
| `planning` | 计划阶段 |
| `awaiting_approval` | 等待用户确认计划 |
| `executing` | 执行阶段 |
| `completed` | 已完成 |
| `failed` | 失败（需人工介入） |

---

## 🗂️ 版本控制

**不要**将 `.claude/sessions/` 目录提交到版本控制！

原因：
1. 这些是运行时生成的项目特定文件
2. 每个开发者的会话不同
3. 文件量可能很大

`.claude/sessions/` 已在 `.gitignore` 中被忽略。

---

## 🔍 查找会话

### 按时间查找
```bash
ls -t sessions/  # 按时间倒序
```

### 按描述查找
```bash
ls sessions/ | grep "用户认证"
```

### 查看最新会话
```bash
ls -t sessions/ | head -1
```

---

## 🧹 清理旧会话

建议定期清理已完成的旧会话：

```bash
# 列出30天前的会话
find sessions/ -type d -mtime +30

# 删除30天前的会话
find sessions/ -type d -mtime +30 -exec rm -rf {} \;
```

或者手动归档：
```bash
# 创建归档目录
mkdir -p .claude/sessions/archive/2025

# 移动旧会话
mv sessions/001-* sessions/archive/2025/
```

---

**创建时间**：2025-12-31
**维护者**：Claude Code 多代理框架
