# 详细工作流阶段（主代理执行）

**重要说明**：以下所有阶段由主代理直接执行。

**强制要求**：
- ❌ **禁止跳过任何阶段** - 工作流一旦启动，必须完整执行所有阶段
- ❌ **禁止在未创建会话的情况下调用子代理**
- ❌ **禁止在未经过 master-planner 的情况下进入执行阶段**
- ❌ **禁止在未获得用户确认的情况下调用 code-executor**

**启动前提**：用户在 Plan Mode 中选择了"完整工作流"选项。

---

## 阶段0：【强制】创建工作流会话

**这是工作流的第一步，必须在任何其他操作之前完成！**

### 步骤0.1：生成会话ID

使用 Bash 工具执行以下脚本：

```bash
# 确保在项目根目录执行
cd /mnt/d/software/beilv-agent || { echo "错误：无法切换到项目根目录"; exit 1; }

# 确保 sessions 目录存在
mkdir -p .claude/sessions

# 获取当前最新序号
LAST_NUM=$(ls -1d .claude/sessions/[0-9][0-9][0-9]-* 2>/dev/null | \
  sed 's/.*\/\([0-9][0-9][0-9]\)-.*/\1/' | \
  sort -n | \
  tail -1 | \
  sed 's/^0*//')

# 计算新序号
if [ -z "$LAST_NUM" ]; then
  NEW_NUM="001"
else
  LAST_NUM_DECIMAL=$((10#$LAST_NUM))
  NEW_NUM=$(printf "%03d" $((LAST_NUM_DECIMAL + 1)))
fi

# 生成时间戳
TIMESTAMP=$(date +%Y%m%d-%H%M)

# 从用户需求提取描述（根据实际需求修改）
DESC="需求描述"  # 【必须修改】例如："积分扣减系统"、"用户认证"

# 生成会话ID
SESSION_ID="${NEW_NUM}-${DESC}-${TIMESTAMP}"

echo "会话ID: $SESSION_ID"
```

**重要**：记录输出的 SESSION_ID，后续所有步骤都要使用这个值。

### 步骤0.2：创建会话目录结构

```bash
# 使用上一步的 SESSION_ID
SESSION_ID="XXX-描述-YYYYMMDD-HHMM"  # 【必须替换】

cd /mnt/d/software/beilv-agent || exit 1

# 创建4个子目录
mkdir -p ".claude/sessions/${SESSION_ID}"/{analysis,planning,execution,workflow}

# 验证
ls -la ".claude/sessions/${SESSION_ID}/"
```

### 步骤0.3：创建会话记录文件

```bash
# 使用 cat 和 heredoc 创建会话文件
cat > ".claude/sessions/${SESSION_ID}/workflow/session.md" <<'EOF'
# 工作流会话记录

## 会话信息
- 创建时间：YYYY-MM-DD HH:MM:SS
- 会话ID：{session-id}

## 用户需求
{完整的用户需求}

## 涉及项目
1. {项目路径}

## 需求分类
- 类型：{新功能|bug修复|重构|优化}
- 复杂度：{简单|中等|复杂}

## 调度序列
- [x] 主代理 - 已完成会话创建

## 状态流转
- {时间} - 开始工作流
EOF

echo "会话文件创建成功"
```

### 步骤0.4：验证会话创建

使用 Read 工具验证文件是否创建成功：
```
Read: .claude/sessions/{session-id}/workflow/session.md
```

**⚠️ 如果验证失败，必须停止流程并报告错误！**

---

## 阶段1：项目信息检查

对每个涉及的项目：

1. **检查 project.info 文件**
   ```bash
   ls -la {项目根目录}/project.info
   ```

2. **若缺失，调用 project-info-builder**
   ```python
   Task(
       subagent_type="project-info-builder",
       description="构建{项目名}信息",
       prompt=f"""
       请为项目生成 project.info 文件：
       - 项目路径：{project_path}
       - 输出位置：{project_path}/project.info
       """
   )
   ```

---

## 阶段2：需求分析（并行调用）

**为每个项目并行调用 issue-analyzer**：

```python
# 对于项目1
Task(
    subagent_type="issue-analyzer",
    description="分析项目1",
    prompt=f"""
**[会话信息]**
- 会话ID: {session_id}
- 会话目录: .claude/sessions/{session_id}/

**[项目信息]**
- 项目路径: {project1_path}
- 项目名称: {project1_name}

**[用户需求]**
{user_requirement}

**[任务要求]**
请分析该项目并将分析报告保存到：
.claude/sessions/{session_id}/analysis/{project1_name}-analysis.md
    """
)

# 对于项目2（如果有）
Task(
    subagent_type="issue-analyzer",
    description="分析项目2",
    prompt=f"""
... 类似的 prompt ...
    """
)
```

**重要**：使用单个消息发起多个 Task 调用，实现并行执行。

---

## 阶段3：分析汇总

**调用 analysis-aggregator 汇总所有分析结果**：

```python
Task(
    subagent_type="analysis-aggregator",
    description="汇总所有分析结果",
    prompt=f"""
**[会话信息]**
- 会话ID: {session_id}
- 会话目录: .claude/sessions/{session_id}/

**[分析文件]**
- .claude/sessions/{session_id}/analysis/{project1_name}-analysis.md
- .claude/sessions/{session_id}/analysis/{project2_name}-analysis.md

**[用户需求]**
{user_requirement}

**[任务要求]**
请汇总所有项目的分析报告，并保存到：
.claude/sessions/{session_id}/analysis/summary.md
    """
)
```

**验证汇总报告**：
```
Read: .claude/sessions/{session-id}/analysis/summary.md
```

---

## 阶段4：【强制】制定计划

**所有需求都必须经过计划阶段**：

```python
Task(
    subagent_type="master-planner",
    description="制定整体实施计划",
    prompt=f"""
**[会话信息]**
- 会话ID: {session_id}
- 会话目录: .claude/sessions/{session_id}/

**[分析汇总]**
{从 analysis/summary.md 读取的内容}

**[用户需求]**
{user_requirement}

**[任务要求]**
请根据分析汇总制定整体实施计划，并保存到：
.claude/sessions/{session_id}/planning/overall-plan.md

**重要**：
1. 计划必须包含阶段划分、任务分解、风险识别
2. 计划必须列出需要用户确认的关键决策点
3. 计划完成后等待用户确认批准
    """
)
```

**读取计划**：
```
Read: .claude/sessions/{session-id}/planning/overall-plan.md
```

---

## 阶段5：【强制】等待用户确认

**主代理必须向用户展示计划并等待确认**：

```markdown
## 计划已完成

我已经完成了整体实施计划，详情如下：

{计划摘要}

完整计划文件：`.claude/sessions/{session-id}/planning/overall-plan.md`

**请您审阅计划并告诉我：**
1. ✅ 批准计划 - 我将继续执行
2. 🔄 修改计划 - 请告诉我需要修改的地方
3. ❌ 拒绝计划 - 我将停止工作流

请问您的决定是？
```

**⚠️ 只有在用户明确批准后，才能继续执行阶段6！**

---

## 阶段6：拆分任务

**用户批准后，调用 plan-splitter**：

```python
Task(
    subagent_type="plan-splitter",
    description="拆分任务",
    prompt=f"""
**[会话信息]**
- 会话ID: {session_id}
- 会话目录: .claude/sessions/{session_id}/

**[整体计划]**
{从 planning/overall-plan.md 读取的内容}

**[任务要求]**
请将整体计划拆分为可执行的子任务：
1. 创建任务目录结构
2. 生成详细任务文档
3. 创建阶段索引：.claude/sessions/{session_id}/planning/phases.md
4. 初始化进度跟踪：.claude/sessions/{session_id}/workflow/progress.json
    """
)
```

**验证任务拆分**：
```
Read: .claude/sessions/{session-id}/workflow/progress.json
```

---

## 阶段7-N：任务执行循环

**对于每个任务，串行执行以下步骤**：

### 7.1 代码实现

```python
Task(
    subagent_type="code-executor",
    description="执行任务{task-id}",
    prompt=f"""
**[会话信息]**
- 会话ID: {session_id}
- 任务目录: .claude/sessions/{session_id}/execution/phase{X}/task{Y}/

**[任务文档]**
{从 task.md 读取的内容}

**[任务要求]**
请实现该任务并生成任务报告：
.claude/sessions/{session_id}/execution/phase{X}/task{Y}/reports/task-report.md
    """
)
```

### 7.2 运行测试

```python
Task(
    subagent_type="test-runner",
    description="测试任务{task-id}",
    prompt=f"""
**[任务信息]**
- 任务目录: .claude/sessions/{session_id}/execution/phase{X}/task{Y}/

**[任务要求]**
请运行相关测试并生成测试报告：
.claude/sessions/{session_id}/execution/phase{X}/task{Y}/reports/test-result.md
    """
)
```

**如果测试失败** → 返回步骤 7.1 修复代码

### 7.3 代码审计

```python
Task(
    subagent_type="code-auditor",
    description="审计任务{task-id}",
    prompt=f"""
**[任务信息]**
- 任务目录: .claude/sessions/{session_id}/execution/phase{X}/task{Y}/

**[任务要求]**
请审计该任务的代码质量并生成审计报告：
.claude/sessions/{session_id}/execution/phase{X}/task{Y}/audit/audit-{timestamp}.md
    """
)
```

**如果审计失败且可自动修复** → 调用 auto-fixer
**如果审计失败且需人工介入** → 通知用户

### 7.4 任务总结

```python
Task(
    subagent_type="task-summarizer",
    description="总结任务{task-id}",
    prompt=f"""
**[会话信息]**
- 会话ID: {session_id}
- 任务目录: .claude/sessions/{session_id}/execution/phase{X}/task{Y}/

**[任务要求]**
请总结任务成果并：
1. 更新 progress.json
2. 更新 phases.md
3. 如有结构性变更，触发 project-info-updater
4. 准备下一任务
    """
)
```

**循环条件**：如果还有待执行任务，返回步骤 7.1

---

## 阶段结束：工作流完成

**所有任务完成后，主代理输出总结**：

```markdown
## ✨ 工作流完成

我已经完成了所有任务的实现、测试和审计。

**会话信息**：
- 会话ID：{session_id}
- 会话目录：`.claude/sessions/{session_id}/`

**完成的任务**：
1. Phase 1: {阶段1描述} - {N}个任务
2. Phase 2: {阶段2描述} - {M}个任务

**输出文件**：
- 分析报告：`.claude/sessions/{session_id}/analysis/`
- 计划文档：`.claude/sessions/{session_id}/planning/`
- 执行记录：`.claude/sessions/{session_id}/execution/`

**下一步**：您可以查看上述目录中的详细文档，或者开始测试新功能。
```

---

## 多代理系统

**11个子代理**：
- **分析层**：issue-analyzer（分析项目）, analysis-aggregator（汇总分析）
- **计划层**：master-planner（制定计划）, plan-splitter（拆分任务）
- **执行层**：code-executor（代码实现）, test-runner（运行测试）
- **质量层**：code-auditor（代码审计）, auto-fixer（自动修复）
- **维护层**：task-summarizer（任务总结）, project-info-builder（构建信息）, project-info-updater（更新信息）

### 子代理使用原则

1. **主代理直接调用** - 使用 Task 工具直接启动子代理
2. **减少上下文** - 子代理处理复杂工作，只返回摘要
3. **测试独立运行** - 始终使用 test-runner 代理运行测试

---

**文档版本**：2.0.0
**更新时间**：2026-01-09
