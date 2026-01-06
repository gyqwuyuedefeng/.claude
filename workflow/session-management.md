# 会话目录管理规范

> 版本：1.0.0
> 创建时间：2026-01-04
> 用途：规范多代理系统中的会话目录管理

## 概述

本规范定义了 workflow-orchestrator 和所有子代理如何管理会话目录，确保：
- 所有产物保存在同一个会话目录下
- session-id 正确传递和使用
- 避免创建多个会话目录
- 文件路径一致性

## 核心原则

### 1. 唯一会话目录

每个工作流**只有一个**会话目录：
```
<项目根目录>/.claude/sessions/{session-id}/
```

**格式规范**：
- `session-id` 格式：`NNN-描述-YYYYMMDD-HHMM`
- 示例：`001-积分扣减系统-20260104-1618`

### 2. 职责分工

**workflow-orchestrator（创建者）**：
- **创建**唯一的会话目录
- **生成** session-id
- **传递** session-id 给所有子代理

**所有其他子代理（使用者）**：
- **接收** session-id（从 prompt 中提取）
- **验证**会话目录存在
- **使用**指定的会话目录（不创建新目录）

### 3. 显式传递

session-id 必须通过 **prompt 显式传递**：
- 不依赖环境变量
- 不依赖隐式约定
- 所有调用都明确传递

## 目录结构

### 标准结构

```
.claude/sessions/{session-id}/
├── analysis/           # 分析阶段产物
│   ├── {project1}-analysis.md
│   ├── {project2}-analysis.md
│   └── summary.md
├── planning/           # 计划阶段产物
│   ├── overall-plan.md
│   ├── changes.md
│   └── phases.md
├── execution/          # 执行阶段产物
│   ├── phaseXX-{阶段描述}/
│   │   ├── taskYY-{任务描述}/
│   │   │   ├── task.md
│   │   │   ├── reports/
│   │   │   │   ├── task-report.md
│   │   │   │   └── test-result.md
│   │   │   └── audit/
│   │   │       └── audit-{timestamp}.md
│   │   └── README.md
│   └── README.md
└── workflow/           # 工作流元数据
    ├── session.md
    └── progress.json
```

### 子目录职责

| 子目录 | 负责代理 | 文件类型 |
|--------|---------|---------|
| `analysis/` | issue-analyzer, analysis-aggregator | 分析报告 |
| `planning/` | master-planner, plan-splitter | 计划文档 |
| `execution/` | code-executor, test-runner, code-auditor | 执行产物 |
| `workflow/` | workflow-orchestrator, task-summarizer | 工作流状态 |

## workflow-orchestrator 规范

### 会话创建流程

#### 1. 生成 session-id

```bash
# 1. 获取当前最新序号
LAST_NUM=$(ls -1d <项目根目录>/.claude/sessions/[0-9]* 2>/dev/null | \
  sed 's/.*\/\([0-9]\{3\}\)-.*/\1/' | sort -n | tail -1)

# 2. 计算新序号
if [ -z "$LAST_NUM" ]; then
  NEW_NUM="001"
else
  NEW_NUM=$(printf "%03d" $((10#$LAST_NUM + 1)))
fi

# 3. 生成时间戳
TIMESTAMP=$(date +%Y%m%d-%H%M)

# 4. 从用户需求提取描述
DESC="积分扣减系统"  # 根据实际需求修改

# 5. 生成完整会话ID
SESSION_ID="${NEW_NUM}-${DESC}-${TIMESTAMP}"
echo "会话ID: $SESSION_ID"
```

#### 2. 创建目录结构

```bash
# 创建完整目录结构
mkdir -p "<项目根目录>/.claude/sessions/${SESSION_ID}"/{analysis,planning,execution,workflow}

# 验证目录是否创建成功
ls -la "<项目根目录>/.claude/sessions/${SESSION_ID}/"
```

#### 3. 创建会话记录文件

使用 Write 工具创建 `.claude/sessions/{session-id}/workflow/session.md`。

### 调用子代理时的 prompt 模板

**通用模板**：
```markdown
**[会话信息]**
- 会话ID: {session_id}
- 会话目录: <项目根目录>/.claude/sessions/{session_id}/

**[任务具体参数]**
... (根据子代理的需求提供)

**[输出要求]**
请将结果保存到：{session_dir}/{subdir}/{filename}

**重要**：请使用上述指定的会话目录，不要创建新的会话目录。
```

**具体示例**：

**调用 issue-analyzer**：
```
Task(
  subagent_type="issue-analyzer",
  description="分析mall-portal项目",
  prompt=f"""
**[会话信息]**
- 会话ID: 001-积分扣减系统-20260104-1618
- 会话目录: <项目根目录>/.claude/sessions/001-积分扣减系统-20260104-1618/

**[项目信息]**
- 项目路径: <项目根目录>/mall/mall-portal
- 项目名称: mall-portal

**[用户需求]**
实现积分扣减系统...

**[任务要求]**
请分析该项目并将分析报告保存到以下位置：
<项目根目录>/.claude/sessions/001-积分扣减系统-20260104-1618/analysis/mall-portal-analysis.md

**重要**：请使用上述指定的会话目录，不要创建新的会话目录。
  """
)
```

**调用 analysis-aggregator**：
```
Task(
  subagent_type="analysis-aggregator",
  description="汇总所有项目分析结果",
  prompt=f"""
**[会话信息]**
- 会话ID: 001-积分扣减系统-20260104-1618
- 会话目录: <项目根目录>/.claude/sessions/001-积分扣减系统-20260104-1618/

**[分析文件]**
- <项目根目录>/.claude/sessions/001-积分扣减系统-20260104-1618/analysis/mall-portal-analysis.md
- <项目根目录>/.claude/sessions/001-积分扣减系统-20260104-1618/analysis/beilv-agent-analysis.md

**[用户需求]**
实现积分扣减系统...

**[任务要求]**
请汇总所有项目的分析报告，并将汇总结果保存到：
<项目根目录>/.claude/sessions/001-积分扣减系统-20260104-1618/analysis/summary.md

**重要**：请使用上述指定的会话目录。
  """
)
```

## 子代理规范

### 输入参数章节（必须）

每个子代理定义文件必须包含"输入参数"章节：

```markdown
## 输入参数

你将通过 prompt 接收以下参数（由 workflow-orchestrator 或上级代理传递）：

**[会话信息]**
- `session-id`: 工作流会话的唯一标识（格式：NNN-描述-YYYYMMDD-HHMM）
- `session-dir`: 会话目录的完整路径

**[任务具体参数]**
- ... (根据子代理的职责定义)

**⚠️ 重要约定**：
- 你**不应该**自己创建会话目录
- 你**必须**使用传入的 `session-id`
- 所有输出文件必须保存到指定的会话目录
- 如果会话目录不存在，**报错并停止**
```

### 步骤0：验证会话目录（必须）

每个子代理的工作流程必须以"步骤0：验证会话目录"开始：

```markdown
### 步骤0：验证会话目录（必须第一步执行）

**⚠️ 这是第一步，必须在任何其他操作之前完成！**

1. **从 prompt 中提取 session-id**
   - 读取 `**[会话信息]**` 中的 `session-id` 值
   - 验证格式是否符合：`NNN-描述-YYYYMMDD-HHMM`

2. **验证会话目录存在**
   ```bash
   # 使用 Bash 工具验证
   ls -la <项目根目录>/.claude/sessions/{session-id}/
   ```

3. **验证相关子目录存在**
   ```bash
   ls -la <项目根目录>/.claude/sessions/{session-id}/{子目录}/
   ```
   （根据代理职责验证 analysis/, planning/, execution/, 或 workflow/）

4. **如果任一验证失败，报错并停止**

**验证通过标准**：
- ✅ 会话目录存在
- ✅ 相关子目录存在
- ✅ 可以写入文件到该目录

**如果验证失败**：
```markdown
❌ 错误：会话目录验证失败

原因：上级代理没有正确创建会话目录或传递 session-id
会话ID：{session-id}
预期路径：<项目根目录>/.claude/sessions/{session-id}/

请检查：
1. workflow-orchestrator 是否正确执行了步骤0
2. session-id 是否正确传递
3. 会话目录是否已创建

**流程终止**
```
```

### 文件保存规范

**使用实际 session-id，不是占位符**：

❌ **错误示例**：
```python
# 不要使用占位符
file_path = f".claude/sessions/{{session-id}}/analysis/report.md"
```

✅ **正确示例**：
```python
# 从 prompt 中提取实际的 session-id
session_id = "001-积分扣减系统-20260104-1618"  # 从 prompt 提取
file_path = f"<项目根目录>/.claude/sessions/{session_id}/analysis/report.md"
```

### 输出规范章节

每个子代理定义文件的"输出规范"必须强调使用实际 session-id：

```markdown
## 输出规范

### 文件保存位置

**必须**使用从 prompt 中接收的 session-id：

```
<项目根目录>/.claude/sessions/{实际的session-id}/{子目录}/{文件名}
```

**⚠️ 警告**：
- 不要使用占位符 `{session-id}`
- 使用步骤0中从 prompt 提取的实际值
- 不要创建新的会话目录
```

## 错误处理

### 常见错误及处理

#### 1. 会话目录不存在

**错误**：子代理无法找到会话目录

**原因**：
- workflow-orchestrator 没有正确创建会话目录
- session-id 传递错误
- 路径拼写错误

**处理**：
```markdown
1. 验证 session-id 格式是否正确
2. 检查 workflow-orchestrator 的执行日志
3. 手动验证目录是否存在：
   ls -la <项目根目录>/.claude/sessions/{session-id}/
4. 如果目录不存在，报错并终止流程
```

#### 2. 多个会话目录

**错误**：发现多个会话目录，每个子代理创建了自己的目录

**原因**：
- 子代理没有使用传入的 session-id
- 子代理自己创建了新的 session-id

**处理**：
```markdown
1. 检查子代理定义，确认"步骤0：验证会话目录"是否执行
2. 检查子代理是否正确提取并使用传入的 session-id
3. 删除多余的会话目录，保留正确的那个
4. 重新运行工作流
```

#### 3. session-id 传递错误

**错误**：子代理收到的 session-id 与实际创建的不符

**原因**：
- workflow-orchestrator 调用时传递了错误的 session-id
- prompt 模板错误

**处理**：
```markdown
1. 检查 workflow-orchestrator 的调用代码
2. 验证 prompt 模板是否正确
3. 确认 session-id 变量的值
```

## 验证方法

### 手动验证

#### 验证会话目录结构

```bash
# 列出所有会话目录
ls -la <项目根目录>/.claude/sessions/

# 检查特定会话的目录结构
SESSION_ID="001-积分扣减系统-20260104-1618"
tree <项目根目录>/.claude/sessions/$SESSION_ID/
```

**预期结果**：
```
001-积分扣减系统-20260104-1618/
├── analysis/
│   ├── mall-portal-analysis.md
│   ├── beilv-agent-analysis.md
│   └── summary.md
├── planning/
│   └── overall-plan.md
├── execution/
└── workflow/
    └── session.md
```

#### 验证没有孤儿会话

```bash
# 查找所有会话目录
find <项目根目录>/.claude/sessions/ -maxdepth 1 -type d -name "[0-9]*"

# 应该只有一个与当前工作流相关的会话目录
```

### 自动化验证

参见 `.claude/scripts/validate-session.sh`

## 最佳实践

### 1. 一致性原则

所有子代理必须使用相同的 session-id：
- 不自己生成 session-id
- 不修改传入的 session-id
- 严格使用传入的值

### 2. 早期验证原则

在步骤0立即验证会话目录：
- 不要等到保存文件时才发现问题
- 失败快速，错误明确

### 3. 完整路径原则

始终使用绝对路径：
- 不使用相对路径
- 避免路径解析错误

### 4. 错误报告原则

验证失败时，提供详细的错误信息：
- 说明失败原因
- 提供预期路径和实际状态
- 给出检查建议

## 迁移指南

### 将现有代理迁移到新规范

#### 步骤1：添加"输入参数"章节

在"核心职责"之前添加"输入参数"章节（参见上文模板）。

#### 步骤2：添加"步骤0：验证会话目录"

在"工作流程"开头添加"步骤0：验证会话目录"（参见上文模板）。

#### 步骤3：修改文件保存逻辑

将所有文件保存路径从占位符改为使用实际 session-id：
- 搜索 `{session-id}` 占位符
- 替换为 `{实际的session-id}`（从 prompt 提取）

#### 步骤4：更新"输出规范"章节

强调使用实际 session-id，添加警告（参见上文模板）。

### 兼容性注意事项

- 已存在的会话目录可能需要手动整理
- 旧的子代理调用需要更新 prompt
- 测试所有调用链以确保 session-id 正确传递

## 参考

- 会话模板：`.claude/workflow/workflow-session.md.template`
- 验证脚本：`.claude/scripts/validate-session.sh`
- 相关子代理：
  - workflow-orchestrator.md
  - issue-analyzer.md
  - analysis-aggregator.md
  - master-planner.md
  - plan-splitter.md
  - code-executor.md
  - test-runner.md
  - code-auditor.md
  - task-summarizer.md
  - project-info-updater.md

---

**版本历史**：
- v1.0.0 (2026-01-04) - 初始版本

**维护者**：Claude Code 多代理系统团队
