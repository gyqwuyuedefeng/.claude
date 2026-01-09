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

> **重要变更**：主代理现在直接调度所有子代理

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

**核心原则：默认启动完整工作流，除非明确满足"简单任务"条件且用户说明直接修改**

### 默认行为

**对于所有编码相关需求，必须启动完整的多代理工作流**

这确保了：
- 完整的需求分析
- 用户确认的计划
- 测试和审计保证
- 可追溯的实施记录

### 简单任务例外（需同时满足2个条件）

只有**同时满足**以下两个条件，才可以跳过工作流：

#### 条件1：任务属于以下5类之一

1. **单行/少量代码修改**
   - 示例：修改变量名、修正拼写错误、调整常量值
   - 限制：不超过3行代码，单个文件

2. **纯配置调整**
   - 示例：修改配置文件参数、调整环境变量
   - 限制：不影响业务逻辑

3. **文档编辑**
   - 示例：更新 README、添加注释、修改文档
   - 限制：纯文档类文件（.md, .txt）

4. **问答场景**
   - 示例：解释代码、回答技术问题
   - 限制：不涉及代码修改

5. **样式/资源替换**
   - 示例：替换图片、修改CSS颜色、调整布局
   - 限制：纯视觉修改，不涉及逻辑

#### 条件2：用户明确说明"简单任务直接修改"

用户输入必须包含以下任一短语：
- "直接修改"
- "简单任务"
- "不需要工作流"
- "快速修改"
- "立即执行"

**重要**：仅满足条件1但用户未说明，仍然**必须启动工作流**

### 判断流程

```
用户输入
  ↓
是否属于5类简单任务之一？
  ├─ NO → 启动工作流（必须）
  └─ YES → 用户是否明确说明"直接修改"？
      ├─ NO → 启动工作流（默认安全）
      └─ YES → 直接执行（例外情况）
```

### 触发示例

#### ✅ 必须启动工作流

**示例1**：
```
用户: 使用 logo.svg 作为前端系统的 logo 和网页图标

判断:
- 涉及多个文件修改
- 未明确说明"简单任务"
结论: 启动工作流
```

**示例2**：
```
用户: 添加一个新的API接口

判断:
- 不属于5类简单任务
结论: 启动工作流
```

**示例3**：
```
用户: 修改登录页面的布局

判断:
- 可能涉及多个组件，影响范围不明确
- 未明确说明"简单任务"
结论: 启动工作流（默认安全）
```

**示例4**：
```
用户: 实现积分扣减系统，参考 .plan/106-积分扣减系统设计与实现/plan.md

判断:
- 复杂任务，涉及多个阶段
结论: 启动工作流
```

**示例5**：
```
用户: 在 mall-portal 和 beilv-agent 中添加积分冻结和扣减功能

判断:
- 涉及多个项目
结论: 启动工作流
```

**示例6**：
```
用户: 开发用户认证模块，包括数据库设计、接口实现和测试

判断:
- 复杂任务，需要完整流程
结论: 启动工作流
```

#### ✅ 可以直接执行

**示例1**：
```
用户: 把第123行的变量名从 foo 改成 bar，简单任务直接修改

判断:
- 属于"单行代码修改"
- 用户明确说明"简单任务直接修改"
结论: 直接执行
```

**示例2**：
```
用户: 快速修改一下 README 的拼写错误

判断:
- 属于"文档编辑"
- 用户使用了"快速修改"关键词
结论: 直接执行
```

**示例3**：
```
用户: 解释一下这段代码的作用

判断:
- 属于"问答场景"
- 不涉及代码修改
结论: 直接回答（不需要工作流）
```

### 检查清单

在决定是否启动工作流前，快速检查：

- [ ] 任务是否属于5类简单任务之一？（单行代码、配置、文档、问答、样式）
- [ ] 用户是否明确说明"直接修改"或"简单任务"？
- [ ] 是否涉及多个文件或组件？
- [ ] 是否可能影响业务逻辑？

**判断规则**：
- 前2项都满足 → **可以直接执行**
- 任一项不满足 → **必须启动工作流**
- 不确定时 → **必须启动工作流**（默认安全）

### 特殊情况处理

#### 1. 用户说"这个很简单"但未明确要求直接修改
→ **启动工作流**（"简单"是主观判断，需要规范流程）

#### 2. 任务看起来简单，但涉及多个文件
→ **启动工作流**（影响范围不明确）

#### 3. 用户说"直接改"但任务复杂
→ **询问用户确认**，建议启动工作流

#### 4. 不确定是否简单
→ **启动工作流**（宁可过度保护，不可质量风险）

### 工作流执行模板

当判断需要启动工作流时，主代理按照以下步骤执行：

#### 第一步：内部决策
```markdown
我检测到需要启动完整工作流：
- 需求：{用户完整需求}
- 涉及项目：{项目列表}
- 判断原因：{不满足简单任务条件 / 用户未明确说明 / 影响范围不明确}

我将作为主代理，直接执行完整的多代理工作流。
```

#### 第二步：开始执行
直接进入**阶段0：创建工作流会话**（参见下文详细步骤）

---

## 📋 详细工作流阶段（主代理执行）

**重要说明**：以下所有阶段由主代理直接执行，不通过 workflow-orchestrator。

**强制要求**：
- ❌ **禁止跳过任何阶段** - 工作流一旦启动，必须完整执行所有阶段
- ❌ **禁止在未创建会话的情况下调用子代理**
- ❌ **禁止在未经过 master-planner 的情况下进入执行阶段**
- ❌ **禁止在未获得用户确认的情况下调用 code-executor**

**注意**：根据"工作流自动启动规则"，只有同时满足"简单任务"定义且用户明确说明的情况下，才可以不启动工作流。

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

---

**框架版本**：2.0.0
**更新时间**：2026-01-09
**架构**：主代理直接调度，11个子代理协同
