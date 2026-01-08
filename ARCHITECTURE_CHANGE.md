# 架构重构说明

> **重构日期**：2026-01-08
> **变更类型**：架构优化 - 从二层调度改为主代理直接调度

---

## 变更概述

将多代理协同框架从**二层调度架构**（主代理 → workflow-orchestrator → 其他子代理）改为**主代理直接调度架构**（主代理 → 所有子代理）。

---

## 变更原因

### 问题诊断

原有架构存在以下问题：

1. **子代理嵌套调用不稳定** workflow-orchestrator 作为子代理，应该调用其他子代理（issue-analyzer、master-planner 等）
   - 但实际执行时，workflow-orchestrator 没有正确调用后续子代理
   - 即使提示词写得非常详细（609行），LLM 仍然"自作主张"地简化了流程

2. **上下文传递问题**
   - 子代理调用子代理时，上下文可能不完整
   - session-id 等关键信息传递困难

3. **调试困难**
   - 嵌套调用链路复杂
   - 问题定位困难

4. **遵循率低**
   - 子代理的提示词约束力较弱
   - 主代理的 CLAUDE.md 指令约束力最强

### 用户反馈

用户发现 workflow-orchestrator 没有按预期执行完整流程，只执行了 4 个 Bash 工具调用就返回了，没有调用任何其他子代理。

---

## 新架构设计

### 架构图

**旧架构（二层调度）**：
```
主代理 → workflow-orchestrator 子代理 → issue-analyzer
                                      → analysis-aggregator
                                      → master-planner
                                      → plan-splitter
                                      → code-executor
                                      → ...
```

**新架构（直接调度）**：
```
主代理 → 阶段0：创建会话
       → 阶段1：检查项目信息 → project-info-builder（如需要）
       → 阶段2：并行调用 issue-analyzer（每个项目）
       → 阶段3：调用 analysis-aggregator
       → 阶段4：调用 master-planner
       → 阶段5：等待用户确认（必须）
       → 阶段6：调用 plan-splitter
       → 阶段7-N：任务执行循环
                  → code-executor
                  → test-runner
                  → code-auditor
                  → task-summarizer
```

### 关键变更

1. **主代理直接执行所有阶段**
   - 阶段0（创建会话）由主代理使用 Bash 工具执行
   - 后续阶段由主代理直接调用相应的子代理
   - 不再通过 workflow-orchestrator 中间层

2. **所有工作流逻辑写入 CLAUDE.md**
   - 详细的阶段说明（阶段0-N）
   - 每个阶段的具体执行步骤
   - 子代理调用模板
   - 强制要求和验证步骤

3. **子代理数量减少**
   - 从 12 个子代理减少到 11 个
   - 移除 workflow-orchestrator
   - 其他子代理保持不变

---

## 文件变更清单

### 修改的文件

1. **`.claude/CLAUDE.md`** - 主要变更
   - ✅ 更新"核心工作流"部分
   - ✅ 更新"工作流自动启动规则"部分
   - ✅ 添加"详细工作流阶段（主代理执行）"章节（约400行）
   - ✅ 更新"多代理系统"部分（从12个子代理改为11个）
   - ✅ 移除所有对 workflow-orchestrator 的调用引用

### 备份的文件

2. **`.claude/agents/workflow-orchestrator.md.backup`** - 备份
   - 原 workflow-orchestrator.md 重命名为 .backup
   - 保留历史记录，方便回滚

---

## 详细变更内容

### 1. CLAUDE.md - 核心工作流部分

**旧版本**：
```markdown
当你收到编码需求时，应该：

1. **启动工作流编排**
   - 使用 Task 工具调用 `workflow-orchestrator` 子代理
   - 工作流会自动完成：项目信息检查 → 需求分析 → ...
```

**新版本**：
```markdown
当你收到编码需求时，作为**主代理**，你应该**直接执行**以下完整工作流：

主代理 → 阶段0：创建会话
       → 阶段1：检查项目信息
       → 阶段2：并行调用 issue-analyzer（每个项目）
       → ...

### 关键原则

1. **主代理直接调度** - 你作为主代理，直接使用 Task 工具调用各个子代理，不通过中间层
2. **必须等待用户确认** - 在 master-planner 阶段完成后，必须等待用户批准才能继续
3. **完整质量保证** - 每个任务都必须通过测试和审计
4. **串行执行阶段** - 各阶段必须按顺序执行，不可跳过
```

### 2. CLAUDE.md - 工作流自动启动规则

**旧版本**：
```markdown
**重要：当用户需求满足以下任一条件时，你必须立即使用 Task 工具调用 `workflow-orchestrator` 子代理启动完整工作流。**

### 调用模板

Task(
    subagent_type="workflow-orchestrator",
    description="{从用户需求提取的简短描述（3-5个字）}",
    prompt=f"""...
    """
)
```

**新版本**：
```markdown
**重要：当用户需求满足以下任一条件时，你作为主代理必须立即启动完整工作流（直接执行阶段0-7）。**

### 工作流执行模板

当检测到触发条件时，主代理按照以下步骤执行：

#### 第一步：内部决策
我检测到用户需求满足工作流触发条件：
- 需求：{用户完整需求}
- 涉及项目：{项目列表}
- 触发原因：{关键词/引用文件/多项目/复杂任务}

我将作为主代理，直接执行完整的多代理工作流。

#### 第二步：开始执行
直接进入**阶段0：创建工作流会话**（参见下文详细步骤）
```

### 3. CLAUDE.md - 新增详细工作流阶段

新增章节："📋 详细工作流阶段（主代理执行）"，包含：

- **阶段0**：创建工作流会话（必须第一步执行）
  - 步骤0.1：生成会话ID
  - 步骤0.2：创建会话目录结构
  - 步骤0.3：创建会话记录文件
  - 步骤0.4：验证会话创建

- **阶段1**：项目信息检查

- **阶段2**：需求分析（并行调用）

- **阶段3**：分析汇总

- **阶段4**：【强制】制定计划

- **阶段5**：【强制】等待用户确认

- **阶段6**：拆分任务

- **阶段7-N**：任务执行循环
  - 7.1 代码实现
  - 7.2 运行测试
  - 7.3 代码审计
  - 7.4 任务总结

- **阶段结束**：工作流完成

每个阶段都包含：
- 详细的执行步骤
- Bash 命令或 Task 调用模板
- 验证和错误处理说明
- 强制要求标记（⚠️）

### 4. CLAUDE.md - 多代理系统

**旧版本**：
```markdown
**12个子代理**分为5层：
- **编排层**：workflow-orchestrator
- **分析层**：issue-analyzer, analysis-aggregator
- ...
```

**新版本**：
```markdown
**11个子代理**分为4层：
- **分析层**：issue-analyzer, analysis-aggregator
- **计划层**：master-planner, plan-splitter
- **执行层**：code-executor, test-runner
- **质量层**：code-auditor, auto-fixer
- **总结层**：task-summarizer, project-info-updater, project-info-builder
```

---

## 优势分析

### 1. 遵循率提升

- ✅ **CLAUDE.md 的约束力最强** - 主代理会严格遵循 CLAUDE.md 中的指令
- ✅ **详细的步骤说明** - 每个阶段都有明确的执行步骤和模板
- ✅ **强制要求标记** - 使用 ⚠️ 和 ❌ 标记关键约束，增强可见性

### 2. 上下文完整性

- ✅ **主代理始终保持全局视野** - 不会因为子代理嵌套丢失上下文
- ✅ **session-id 传递简单** - 主代理直接将 session-id 传递给各个子代理
- ✅ **状态管理清晰** - 主代理可以直接读取和更新 progress.json

### 3. 调试便利性

- ✅ **调用链路清晰** - 主代理 → 子代理，没有嵌套
- ✅ **问题定位容易** - 可以直接看到哪个子代理调用失败
- ✅ **日志追踪简单** - 不需要在多层子代理之间追踪

### 4. 灵活性提升

- ✅ **动态调整流程** - 主代理可以根据实际情况决定是否调用某个子代理
- ✅ **易于扩展** - 添加新的子代理只需在 CLAUDE.md 中添加调用步骤
- ✅ **易于维护** - 所有逻辑集中在 CLAUDE.md 中，便于理解和修改

---

## 使用方式变更

### 旧的使用方式

```markdown
用户: 实现积分扣减系统

主代理思考：检测到工作流触发条件，应调用 workflow-orchestrator

主代理执行：
Task(
    subagent_type="workflow-orchestrator",
    description="启动积分扣减系统工作流",
    prompt="..."
)

workflow-orchestrator 执行：
（应该调用 issue-analyzer, master-planner 等，但实际没有执行）
```

### 新的使用方式

```markdown
用户: 实现积分扣减系统

主代理思考：检测到工作流触发条件，应直接启动工作流

主代理执行阶段0：
Bash: 生成 session-id → 001-积分扣减系统-20260108-1730
Bash: 创建会话目录结构
Bash: 创建会话记录文件
Read: 验证会话创建成功

主代理执行阶段1：
Bash: 检查 project.info

主代理执行阶段2：
Task(subagent_type="issue-analyzer", ...) # 项目1
Task(subagent_type="issue-analyzer", ...) # 项目2

主代理执行阶段3：
Task(subagent_type="analysis-aggregator", ...)

主代理执行阶段4：
Task(subagent_type="master-planner", ...)

主代理执行阶段5：
向用户展示计划，等待确认

（用户批准后）

主代理执行阶段6：
Task(subagent_type="plan-splitter", ...)

主代理执行阶段7-N：
对每个任务：
  Task(subagent_type="code-executor", ...)
  Task(subagent_type="test-runner", ...)
  Task(subagent_type="code-auditor", ...)
  Task(subagent_type="task-summarizer", ...)
```

---

## 兼容性说明

### 向后兼容

- ✅ **所有子代理定义保持不变** - issue-analyzer, master-planner 等子代理的 `.md` 文件无需修改
- ✅ **会话目录结构保持不变** - `.claude/sessions/{session-id}/` 结构不变
- ✅ **输出文件格式保持不变** - 分析报告、计划文档等文件格式不变

### 不兼容的地方

- ❌ **workflow-orchestrator 子代理不再使用** - 如果有自定义逻辑依赖 workflow-orchestrator，需要迁移到主代理
- ❌ **调用方式改变** - 不再使用 `Task(subagent_type="workflow-orchestrator")`

---

## 回滚方案

如果新架构出现问题，可以按以下步骤回滚：

1. **恢复 workflow-orchestrator.md**
   ```bash
   mv .claude/agents/workflow-orchestrator.md.backup .claude/agents/workflow-orchestrator.md
   ```

2. **恢复 CLAUDE.md**
   ```bash
   git checkout HEAD -- .claude/CLAUDE.md
   # 或者使用版本控制系统恢复到重构前的版本
   ```

3. **删除新增的章节**
   - 删除 CLAUDE.md 中的"详细工作流阶段（主代理执行）"章节

---

## 测试建议

### 测试场景

1. **简单单项目需求**
   - 测试主代理是否能正确识别不触发工作流
   - 直接实现简单修改

2. **复杂单项目需求**
   - 测试主代理是否能正确启动工作流
   - 验证阶段0（会话创建）是否正确执行
   - 验证 session-id 生成和目录创建

3. **多项目需求**
   - 测试主代理是否能并行调用多个 issue-analyzer
   - 验证 analysis-aggregator 是否正确汇总

4. **用户确认流程**
   - 测试主代理是否在 master-planner 后等待用户确认
   - 测试用户拒绝计划时的处理

5. **任务执行循环**
   - 测试 code-executor → test-runner → code-auditor → task-summarizer 循环
   - 测试测试失败和审计失败时的处理

### 验证清单

- [ ] 主代理能正确识别工作流触发条件
- [ ] 阶段0能正确创建会话目录和文件
- [ ] session-id 能正确递增
- [ ] 主代理能正确调用各个子代理
- [ ] session-id 能正确传递给子代理
- [ ] 用户确认流程工作正常
- [ ] 任务执行循环工作正常
- [ ] 所有输出文件正确生成

---

## 未来优化方向

1. **进一步简化 CLAUDE.md**
   - 将 Bash 脚本提取为独立的 shell 文件
   - 使用更简洁的调用模板

2. **增强子代理的独立性**
   - 子代理应该能够自动检测 session-id
   - 子代理应该能够自动验证输入和输出

3. **添加更多验证步骤**
   - 每个阶段结束后自动验证输出
   - 失败时自动重试或回滚

4. **改进错误处理**
   - 更详细的错误消息
   - 自动诊断常见问题

---

## 总结

这次架构重构从根本上解决了 workflow-orchestrator 子代理不稳定的问题，通过让主代理直接调度所有子代理，提升了遵循率、上下文完整性和调试便利性。

**关键成果**：
- ✅ 移除了不稳定的 workflow-orchestrator 子代理
- ✅ 将完整的工作流逻辑写入 CLAUDE.md
- ✅ 主代理直接调度所有子代理
- ✅ 保持了所有子代理的定义和功能
- ✅ 保持了会话目录结构和输出文件格式

**下一步**：
- 在实际项目中测试新架构
- 根据测试结果进一步优化
- 更新 README.md 文档（如需要）

---

**重构完成时间**：2026-01-08 17:35
**重构执行者**：Claude (主代理)
