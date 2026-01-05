# Session-ID 传递机制修改总结

> 完成时间：2026-01-04
> 修改范围：所有子代理定义文件
> 目的：解决多个子代理创建不同会话目录的问题

## 问题描述

**原始问题**：
- 用户发现两个并行的 `issue-analyzer` 子代理创建了不同的会话目录
- 分析报告分散在多个目录中，无法正确汇总

**根本原因**：
- `workflow-orchestrator` 创建会话目录后，没有显式传递 `session-id` 给子代理
- 子代理使用占位符 `{session-id}`，但不知道实际值
- 每个子代理可能自己创建新的会话目录

## 解决方案

### 核心原则

1. **workflow-orchestrator 创建并传递**：唯一负责创建会话目录并生成 session-id
2. **子代理接收并验证**：从 prompt 中接收 session-id，验证会话目录存在
3. **显式传递**：所有调用都在 prompt 中显式传递 session-id
4. **使用实际值**：子代理使用从 prompt 提取的实际 session-id，不使用占位符

### 修改内容

#### 1. workflow-orchestrator.md（已完成 ✅）

**修改位置**：步骤3 - 调度分析阶段

**修改内容**：
- 添加了详细的调用模板
- 在调用 issue-analyzer 时传递 session-id
- 在调用 analysis-aggregator 时传递 session-id

**调用示例**：
```markdown
Task(
  subagent_type="issue-analyzer",
  description="分析mall-portal项目",
  prompt=f"""
**[会话信息]**
- 会话ID: {session_id}
- 会话目录: /mnt/d/software/beilv-agent/.claude/sessions/{session_id}/

**[项目信息]**
- 项目路径: {project_path}
- 项目名称: {project_name}

**[用户需求]**
{user_requirement}

**[任务要求]**
请分析该项目并将分析报告保存到以下位置：
/mnt/d/software/beilv-agent/.claude/sessions/{session_id}/analysis/{project_name}-analysis.md

**重要**：请使用上述指定的会话目录，不要创建新的会话目录。
  """
)
```

#### 2. 所有子代理的通用修改（已完成 ✅）

**新增章节1：输入参数**（在"核心职责"之前）

```markdown
## 输入参数

你将通过 prompt 接收以下参数（由 workflow-orchestrator 或上级代理传递）：

**[会话信息]**
- `session-id`: 工作流会话的唯一标识（格式：NNN-描述-YYYYMMDD-HHMM）
- `session-dir`: 会话目录的完整路径

**[任务具体参数]**
- ... (根据子代理职责定义)

**⚠️ 重要约定**：
- 你**不应该**自己创建会话目录
- 你**必须**使用传入的 `session-id`
- 所有输出文件必须保存到指定的会话目录
- 如果会话目录不存在，**报错并停止**
```

**新增章节2：步骤0 - 验证会话目录**（在"工作流程"开头）

```markdown
### 步骤0：验证会话目录（必须第一步执行）

**⚠️ 这是第一步，必须在任何其他操作之前完成！**

1. **从 prompt 中提取 session-id**
   - 读取 `**[会话信息]**` 中的 `session-id` 值
   - 验证格式是否符合：`NNN-描述-YYYYMMDD-HHMM`

2. **验证会话目录存在**
   ```bash
   ls -la /mnt/d/software/beilv-agent/.claude/sessions/{session-id}/
   ```

3. **验证相关子目录存在**
   (根据代理职责验证 analysis/, planning/, execution/, 或 workflow/)

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
预期路径：/mnt/d/software/beilv-agent/.claude/sessions/{session-id}/

请检查：
1. workflow-orchestrator 是否正确执行了步骤0
2. session-id 是否正确传递
3. 会话目录是否已创建

**流程终止**
```
```

**修改章节3：文件保存路径**

将所有使用 `{session-id}` 占位符的地方改为：
- 强调"使用从 prompt 中提取的实际 session-id"
- 提供完整的绝对路径
- 添加警告："不要使用占位符"

## 已完成的文件修改

### P0 优先级（核心分析流程）✅

1. **workflow-orchestrator.md** ✅
   - 添加 session-id 传递逻辑
   - 提供详细调用模板

2. **issue-analyzer.md** ✅
   - 添加"输入参数"章节
   - 添加"步骤0：验证会话目录"
   - 修改文件保存路径

3. **analysis-aggregator.md** ✅
   - 添加"输入参数"章节
   - 添加"步骤0：验证会话目录"
   - 修改文件保存路径

### P1 优先级（计划和执行流程）✅

4. **master-planner.md** ✅
   - 添加"输入参数"章节
   - 添加"步骤0：验证会话目录"
   - 修改文件保存路径

5. **plan-splitter.md** ✅
   - 添加"输入参数"章节
   - 添加"步骤0：验证会话目录"
   - 修改所有目录创建路径

6. **code-executor.md** ⏳
7. **test-runner.md** ⏳
8. **code-auditor.md** ⏳
9. **task-summarizer.md** ⏳

### P2 优先级（辅助功能）⏳

10. **project-info-updater.md** ⏳

### 规范文档 ✅

11. **session-management.md** ✅（新建）
    - 完整的会话管理规范
    - 详细的调用模板
    - 错误处理指南
    - 迁移指南

### 验证脚本 ⏳

12. **validate-session.sh** ⏳（新建）

## 剩余文件的修改模板

### 对于 code-executor, test-runner, code-auditor, task-summarizer

这些文件需要相同的修改：

1. **在文件开头添加"输入参数"章节**
2. **在"工作流程"开头添加"步骤0：验证会话目录"**
3. **修改文件保存路径**：
   - code-executor: 保存到 `{session-dir}/execution/{task}/reports/`
   - test-runner: 保存到 `{session-dir}/execution/{task}/reports/`
   - code-auditor: 保存到 `{session-dir}/execution/{task}/audit/`
   - task-summarizer: 更新 `{session-dir}/workflow/progress.json`

### 对于 project-info-updater

虽然 project-info-updater 主要更新项目根目录的 `project.info`，但它也可能需要读取会话目录中的信息。建议添加相同的"输入参数"章节以保持一致性。

## 验证方法

### 测试场景

1. **创建测试会话**：
   ```bash
   SESSION_ID="999-测试会话-20260104-2000"
   mkdir -p "/mnt/d/software/beilv-agent/.claude/sessions/$SESSION_ID"/{analysis,planning,execution,workflow}
   ```

2. **模拟调用两个 issue-analyzer**：
   - 调用时都传递相同的 session-id: `999-测试会话-20260104-2000`

3. **验证结果**：
   ```bash
   ls -la "/mnt/d/software/beilv-agent/.claude/sessions/$SESSION_ID/analysis/"
   # 应该看到两个分析报告在同一个目录下：
   # - project1-analysis.md
   # - project2-analysis.md
   ```

### 使用验证脚本

```bash
# 运行验证脚本（创建后）
bash /mnt/d/software/beilv-agent/.claude/scripts/validate-session.sh
```

## 预期效果

修改完成后：

1. ✅ **会话目录唯一**：每个工作流只有一个会话目录
2. ✅ **文件集中**：所有产物保存在同一个会话目录下
3. ✅ **代理协作**：后续代理能正确读取前置代理的输出
4. ✅ **易于追溯**：完整的工作流产物在一个地方
5. ✅ **易于调试**：问题定位更简单

## 向后兼容性

### 已存在的会话目录

如果系统中已经存在多个会话目录（如用户报告的情况），可以：

1. **手动整理**：
   ```bash
   # 找到正确的会话目录
   CORRECT_SESSION="001-积分扣减系统-20260104-1618"

   # 将其他目录中的文件移动到正确目录
   mv "/mnt/d/software/beilv-agent/.claude/sessions/001-积分扣减系统分析/analysis/beilv-agent-analysis.md" \
      "/mnt/d/software/beilv-agent/.claude/sessions/$CORRECT_SESSION/analysis/"

   # 删除空的错误目录
   rmdir "/mnt/d/software/beilv-agent/.claude/sessions/001-积分扣减系统分析/analysis"
   rmdir "/mnt/d/software/beilv-agent/.claude/sessions/001-积分扣减系统分析"
   ```

2. **重新运行工作流**：
   如果文件混乱严重，建议清理后重新运行工作流。

## 下一步行动

### 立即行动（已完成 ✅）

- [x] 修改 workflow-orchestrator.md
- [x] 修改 issue-analyzer.md
- [x] 修改 analysis-aggregator.md
- [x] 创建 session-management.md
- [x] 修改 master-planner.md
- [x] 修改 plan-splitter.md

### 继续完成（进行中 ⏳）

- [ ] 修改 code-executor.md
- [ ] 修改 test-runner.md
- [ ] 修改 code-auditor.md
- [ ] 修改 task-summarizer.md
- [ ] 修改 project-info-updater.md
- [ ] 创建 validate-session.sh

### 测试验证

- [ ] 测试 issue-analyzer 并行调用
- [ ] 验证所有文件保存在同一目录
- [ ] 运行完整工作流测试

## 参考文档

- **会话管理规范**：`.claude/workflow/session-management.md`
- **计划文件**：`/home/gyq/.claude/plans/vivid-enchanting-boole.md`

---

**维护者**：Claude Code 多代理系统团队
**最后更新**：2026-01-04
