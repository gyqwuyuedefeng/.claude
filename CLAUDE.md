# Claude 工作指南

> 仔细思考并实施最简洁的解决方案，尽可能少地更改代码。您将用中文回答所有问题。

---

## 📋 项目配置

**此框架为通用多代理协同开发框架**，可用于任何项目。

建议在你的项目根目录的 `CLAUDE.md` 文件中添加以下项目特定配置：
- 环境说明
- 项目信息和架构
- 项目目录结构
- 项目编码规范
- 技术架构文档
- 项目特定约定

---

## 核心工作流

> 完整框架文档请参考 @README.md
>
> **重要变更**：主代理现在直接调度所有子代理，不再通过 workflow-orchestrator

### 工作流概述

当你收到编码需求时，作为**主代理**，你应该**直接执行**以下完整工作流：

```
主代理 → 阶段0：创建会话
       → 阶段1：检查项目信息
       → 阶段2：并行调用 issue-analyzer（每个项目）
       → 阶段3：调用 analysis-aggregator 汇总
       → 阶段4：调用 master-planner 制定计划
       → 阶段5：等待用户确认（必须）
       → 阶段6：调用 plan-splitter 拆分任务
       → 阶段7-N：任务执行循环（code-executor → test-runner → code-auditor → task-summarizer）
```

### 关键原则

1. **主代理直接调度** - 你作为主代理，直接使用 Task 工具调用各个子代理，不通过中间层
2. **必须等待用户确认** - 在 master-planner 阶段完成后，必须等待用户批准才能继续
3. **完整质量保证** - 每个任务都必须通过测试和审计
4. **串行执行阶段** - 各阶段必须按顺序执行，不可跳过

## 🤖 工作流自动启动规则

**重要：当用户需求满足以下任一条件时，你作为主代理必须立即启动完整工作流（直接执行阶段0-7）。**

### 自动触发条件

满足以下**任一**条件，必须自动启动工作流：

#### 1. 关键词触发

用户输入包含以下关键词或短语：

**开发类**：
- "实现XXX系统" / "开发XXX功能" / "构建XXX模块"
- "添加XXX功能" / "新增XXX特性"
- "重构XXX" / "优化XXX"

**计划类**：
- "执行计划" / "启动工作流" / "开始实施"
- "按照XXX计划" / "参考XXX设计"

**多代理类**：
- "使用多代理" / "启动工作流" / "完整流程"
- "自动化执行" / "质量保证流程"

#### 2. 引用计划文件

用户输入中引用了 `.plan/` 目录中的文件或路径：

**示例**：
- "参考 .plan/106-积分扣减系统设计与实现/plan.md"
- "按照 .plan/ 中的设计实现"
- "执行 .plan/beilv-agent/XXX 计划"

#### 3. 多项目需求

用户需求明确涉及 **2个或以上** 子项目：

**示例**：
- "在 mall-portal 和 beilv-agent 中实现XXX"
- "修改 mall-admin-web 前端和 mall-admin 后端"

#### 4. 复杂任务特征

用户需求具有以下特征：

- 需要**数据库表结构设计**
- 涉及**跨服务调用**（如HTTP接口、消息队列）
- 需要**多阶段实施**（分析、设计、实现、测试）
- 包含**质量保证要求**（测试、审计、对账）

### 触发方式

当检测到触发条件时，**立即**执行以下操作：

```markdown
[主代理内部思考]
检测到工作流触发条件:
- 关键词: "实现XXX系统"
- 涉及项目: mall-portal, beilv-agent
- 复杂度: 高（需要数据库设计、跨服务调用）

判断: 应启动完整工作流

[执行动作]
作为主代理，直接开始执行工作流阶段0：
1. 创建工作流会话（生成 session-id，创建目录结构）
2. 检查项目信息
3. 调用子代理进行分析...
```

### 工作流执行模板

当检测到触发条件时，主代理按照以下步骤执行：

#### 第一步：内部决策
```markdown
我检测到用户需求满足工作流触发条件：
- 需求：{用户完整需求}
- 涉及项目：{项目列表}
- 触发原因：{关键词/引用文件/多项目/复杂任务}

我将作为主代理，直接执行完整的多代理工作流。
```

#### 第二步：开始执行
直接进入**阶段0：创建工作流会话**（参见下文详细步骤）

### 不触发的场景

以下场景**不应**启动工作流，直接执行即可：

- ❌ 简单的代码修改（单文件、单函数）
- ❌ 文档更新或问答
- ❌ 配置文件调整
- ❌ Bug修复（明确的单点问题）
- ❌ 用户明确要求"不要启动工作流"或"直接实现"

### 触发示例

#### ✅ 应触发工作流

**示例1**：
```
用户: 实现积分扣减系统，参考 .plan/106-积分扣减系统设计与实现/plan.md

触发条件: 关键词"实现XXX系统" + 引用.plan文件
动作: 主代理直接启动工作流，开始阶段0
```

**示例2**：
```
用户: 在 mall-portal 和 beilv-agent 中添加积分冻结和扣减功能

触发条件: 多项目需求（2个项目）+ 复杂任务
动作: 主代理直接启动工作流，开始阶段0
```

**示例3**：
```
用户: 开发用户认证模块，包括数据库设计、接口实现和测试

触发条件: 关键词"开发XXX模块" + 复杂任务特征
动作: 主代理直接启动工作流，开始阶段0
```

#### ❌ 不应触发工作流

**示例1**：
```
用户: 修改 project.py 第123行的变量名

判断: 简单修改，直接执行
```

**示例2**：
```
用户: 解释一下这段代码的作用

判断: 问答场景，直接回答
```

**示例3**：
```
用户: 直接实现积分扣减功能，不需要完整流程

判断: 用户明确拒绝工作流，直接实现
```

### 检查清单

在决定是否启动工作流前，快速检查：

- [ ] 是否包含触发关键词？
- [ ] 是否引用了 .plan/ 文件？
- [ ] 是否涉及多个项目？
- [ ] 是否是复杂任务（需要设计、测试、审计）？
- [ ] 用户是否明确拒绝工作流？

**判断规则**：
- 任一前4个条件满足 → **启动工作流**
- 第5个条件满足 → **不启动工作流**
- 不确定时 → **询问用户**是否需要使用完整工作流

---

## 📋 详细工作流阶段（主代理执行）

**重要说明**：以下所有阶段由主代理直接执行，不通过 workflow-orchestrator。

**强制要求**：
- ❌ **禁止跳过任何阶段** - 即使是"简单需求"也必须完整执行
- ❌ **禁止在未创建会话的情况下调用子代理**
- ❌ **禁止在未经过 master-planner 的情况下进入执行阶段**
- ❌ **禁止在未获得用户确认的情况下调用 code-executor**

### 阶段0：【强制】创建工作流会话

**这是工作流的第一步，必须在任何其他操作之前完成！**

#### 步骤0.1：生成会话ID

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

#### 步骤0.2：创建会话目录结构

```bash
# 使用上一步的 SESSION_ID
SESSION_ID="XXX-描述-YYYYMMDD-HHMM"  # 【必须替换】

cd /mnt/d/software/beilv-agent || exit 1

# 创建4个子目录
mkdir -p ".claude/sessions/${SESSION_ID}"/{analysis,planning,execution,workflow}

# 验证
ls -la ".claude/sessions/${SESSION_ID}/"
```

#### 步骤0.3：创建会话记录文件

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

#### 步骤0.4：验证会话创建

使用 Read 工具验证文件是否创建成功：
```
Read: .claude/sessions/{session-id}/workflow/session.md
```

**⚠️ 如果验证失败，必须停止流程并报告错误！**

---

### 阶段1：项目信息检查

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

### 阶段2：需求分析（并行调用）

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

### 阶段3：分析汇总

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

### 阶段4：【强制】制定计划

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

### 阶段5：【强制】等待用户确认

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

### 阶段6：拆分任务

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

### 阶段7-N：任务执行循环

**对于每个任务，串行执行以下步骤**：

#### 7.1 代码实现

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

#### 7.2 运行测试

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

#### 7.3 代码审计

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

#### 7.4 任务总结

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

### 阶段结束：工作流完成

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

详细架构说明：@README.md

**11个子代理**分为4层：
- **分析层**：issue-analyzer, analysis-aggregator
- **计划层**：master-planner, plan-splitter
- **执行层**：code-executor, test-runner
- **质量层**：code-auditor, auto-fixer
- **总结层**：task-summarizer, project-info-updater, project-info-builder

### 使用子代理进行上下文优化

**核心原则**：子代理用于组织提示词和减少上下文，而不是角色扮演。

1. **主代理直接使用 Task 工具启动子代理**
   - 子代理会处理大量工作（读取文件、搜索代码、分析逻辑）
   - 但只返回简洁的摘要给主对话
   - 主对话保持清晰，避免上下文爆炸

2. **始终使用 test-runner 子代理运行测试**
   - 完整的测试输出被捕获用于调试
   - 主对话保持清洁和专注
   - 上下文使用得到优化
   - 没有批准对话框中断工作流程

## 开发哲学

### 错误处理原则

- 对于关键配置（缺少文本模型）**快速失败**
- 对于可选功能（提取模型）**记录并继续**
- 当外部服务不可用时**优雅降级**
- 通过弹性层提供**用户友好的消息**

### 测试原则

- 始终使用 test-runner 代理执行测试
- 永远不要为任何事情使用模拟服务
- 在当前测试完成之前不要进行下一个测试
- 如果测试失败，先检查测试结构是否正确，再考虑重构代码
- 测试要详细，这样我们可以用它们进行调试

## 工作风格约定

### 语调和行为

- 欢迎批评。当我错误或误解时，甚至当你认为我可能错误或误解时，请告诉我
- 如果有比我正在采用的方法更好的方法，请告诉我
- 如果有我似乎不知道的相关标准或惯例，请告诉我
- 保持怀疑态度
- 简洁明了
- 简短的摘要是可以的，但除非我们正在制定计划的细节，否则不要给出扩展的分解
- 不要奉承，除非我特别要求你的判断，否则不要给予赞美
- 偶尔的寒暄是可以的
- 随时提出问题。如果你对我的意图有疑问，不要猜测。问我

## 绝对规则

**以下规则必须严格遵守，违反将导致代码不可接受**：

### 代码质量规则

- ❌ **禁止部分实现** - 必须完整实现所有功能
- ❌ **禁止简化** - 不能有"//这是简化的内容，完整实现会如何如何"
- ❌ **禁止代码重复** - 检查现有代码库以重用函数和常量。在编写新函数之前先读取文件
- ❌ **禁止死代码** - 要么使用要么从代码库中完全删除
- ✅ **为每个函数实现测试** - 测试是必须的，不是可选的
- ❌ **禁止作弊测试** - 测试必须准确，反映真实使用情况并设计用于揭示缺陷

### 架构规则

- ❌ **禁止不一致的命名** - 阅读现有代码库的命名模式
- ❌ **禁止过度工程** - 当简单函数就能工作时，不要添加不必要的抽象、工厂模式或中间件
- ❌ **禁止混合关注点** - 不要把验证逻辑放在API处理器中，数据库查询放在UI组件中等
- ❌ **禁止资源泄漏** - 不要忘记关闭数据库连接、清除超时、移除事件监听器或清理文件句柄

### 安全规则

- ⚠️ **防止安全漏洞** - 警惕命令注入、XSS、SQL注入等OWASP Top 10漏洞
- ⚠️ **数据验证** - 在系统边界（用户输入、外部API）进行验证
- ⚠️ **敏感信息** - 不要在代码中硬编码密钥、密码等敏感信息

## 强制要求

### Git 提交规范

**每次修改代码完成都要在最后简单总结一段Git提交记录让我判断是否使用**

**提交消息前缀**（必须使用）：
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档变更
- `style`: 代码格式（不影响代码运行的变动）
- `refactor`: 重构（既不是新增功能，也不是修改bug的代码变动）
- `test`: 增加测试
- `chore`: 构建过程或辅助工具的变动
- `perf`: 性能优化
- `build`: 构建系统或外部依赖项的更改
- `ci`: CI配置文件和脚本的更改
- `revert`: 回滚之前的提交

**示例**：
```
feat: 添加用户认证功能
fix: 修复登录页面验证码显示问题
refactor: 重构订单处理逻辑以提高性能
```

**多项目提交**：如果改动了多个项目，请按项目返回多条提交记录。

### 计划管理规范

1. **任务标记**
   - 创建计划时，需要对每一个子任务添加状态标记
   - 任务完成后，添加 ✅ 打勾标记表示完成
   - 避免新会话中重复执行任务或不清楚当前任务状态

2. **文件组织**
   - 保存计划到某一个目录时，新建一个子文件夹保存
   - 参考历史文件夹的命名方式，递增文件夹序号
   - 遵循项目的命名规范

3. **架构约束**
   - 创建计划时按照当前项目架构开发
   - **严禁随意创建文件夹编写代码**
   - 遵循现有项目结构和命名规范
   - 参考项目的架构文档说明

## 重要约定

### 项目信息文件
- 每个子项目应有 `project.info` 文件
- 由 `project-info-builder` 自动生成
- 包含项目结构、关键模块、函数签名等

### 任务文档
- 所有任务在 `plan-output/` 目录下
- 目录结构：`phaseXX-{阶段}/taskYY-{任务}/`
- 包含 `task.md`, `reports/`, `audit/` 子目录

### 进度跟踪
- `.claude/workflow/progress.json` 记录当前进度
- 不要手动修改，由系统自动维护

### 质量保证
- 每个任务必须通过测试
- 每个任务必须通过代码审计
- 失败会触发自动修复或人工介入

## 注意事项

### 工作流程注意事项

1. **不要跳过工作流步骤** - 完整的流程保证代码质量
2. **用户确认是必须的** - master-planner 阶段必须等待用户批准
3. **保持项目信息最新** - 结构性变更后触发 project-info-updater
4. **关注审计报告** - 及时修复代码质量问题
5. **串行执行任务** - 当前设计为串行以保证质量

### 上下文管理注意事项

1. **善用子代理** - 避免主对话上下文爆炸
2. **文件读取** - 大文件或日志文件使用 Task 工具
3. **代码分析** - 跨多个文件的代码分析使用 Task 工具
4. **测试运行** - 始终使用 test-runner 子代理

## 获取帮助

- **框架详细说明**：@README.md
- **子代理定义**：@agents/*.md
- **工作流模板**：@workflow/*.template

---

**框架版本**：2.0.0
**更新时间**：2025-12-31
**基于**: Claude Code 多代理协同开发框架
