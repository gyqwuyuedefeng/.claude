# Hooks 智能化优化 - 测试指南

> 创建时间：2026-01-07
> 相关计划：`.plan/claude/07-Hooks智能化优化方案/plan.md`

## 已完成的修改

### ✅ 修改内容

1. **SessionStart Hook**：从 Command Hook (session-start.sh) 转换为 Prompt Hook
2. **PreToolUse Write Hook**：从 Command Hook (validate-write.py) 转换为 Prompt Hook
3. **capture-approval.py**：优化关键词匹配逻辑，提升准确性
4. **旧脚本归档**：session-start.sh 和 validate-write.py 已移至 `.claude/hooks/archived/`

### 📁 修改的文件

- ✅ `.claude/settings.json` - 更新 hooks 配置
- ✅ `.claude/hooks/capture-approval.py` - 优化批准识别逻辑
- ✅ `.claude/settings.json.backup` - 备份文件（如需回滚）

---

## 测试计划

### 测试 1：SessionStart Prompt Hook

**目的**：验证会话启动时能够自动检测进行中的工作流并恢复上下文

#### 场景 1.1：无进行中工作流（正常启动）

```bash
# 启动全新的 Claude Code 会话
claude chat
```

**预期结果**：
- ✅ 正常启动，无额外消息
- ✅ 没有工作流恢复提示

#### 场景 1.2：有进行中工作流（上下文恢复）

**前置条件**：
1. 在之前的会话中启动过工作流（调用了 workflow-orchestrator）
2. 工作流未完成（阶段不是 completed）

```bash
# 恢复之前的会话或启动新会话
claude chat --resume
# 或
claude chat
```

**预期结果**：
- ✅ 显示工作流恢复消息
- ✅ 包含以下信息：
  - 会话 ID
  - 当前阶段（init/analysis/planning/execution）
  - 4 条约束提醒
  - 下一步行动指导

**示例输出**：
```
⚠️ **工作流状态恢复** ⚠️

检测到进行中的工作流会话：001-hooks-optimization-20260107

当前阶段：planning

**必须遵守的约束**：
1. 你必须继续执行该工作流，不能重新开始
2. 你必须使用已存在的会话目录
3. 你必须严格按照阶段执行
4. 你必须在继续前验证所有前置条件已满足

**下一步行动**：
你需要调用 master-planner 制定计划并等待用户确认
```

---

### 测试 2：PreToolUse Write Prompt Hook

**目的**：防止错误地写入到旧的工作流会话目录

#### 场景 2.1：写入当前会话（允许）

**前置条件**：存在活跃的工作流会话

```bash
# 在 Claude 会话中执行
> 创建文件 .claude/sessions/002-current-session/planning/plan.md
```

**预期结果**：
- ✅ 写入操作被允许
- ✅ 文件成功创建

#### 场景 2.2：写入旧会话（拒绝）

**前置条件**：
1. 存在多个会话目录
2. 当前活跃会话是最新的（例如 002-xxx）
3. 尝试写入旧会话（例如 001-xxx）

```bash
# 在 Claude 会话中执行
> 创建文件 .claude/sessions/001-old-session/planning/plan.md
```

**预期结果**：
- ❌ 写入操作被拒绝
- ❌ 显示错误消息：
  ```
  错误：正在尝试写入旧会话目录 001-old-session，当前活跃会话为 002-current-session。这会导致数据不一致。
  ```

#### 场景 2.3：写入非会话目录（允许）

```bash
# 在 Claude 会话中执行
> 创建文件 src/main.py
```

**预期结果**：
- ✅ 写入操作被允许
- ✅ 文件成功创建

---

### 测试 3：capture-approval.py 优化

**目的**：验证改进的批准识别逻辑

#### 场景 3.1：明确的批准（应触发）

**前置条件**：工作流处于 planning 阶段

测试输入：
1. `批准`
2. `批准计划`
3. `确认计划`
4. `approve`
5. `approve the plan`

**预期结果**：
- ✅ 识别为批准
- ✅ progress.json 中 `user_approved_plan` 设置为 `true`
- ✅ 显示消息：`✅ 用户已批准计划，progress.json 已更新。`

#### 场景 3.2：模糊批准 + 计划关键词（应触发）

测试输入：
1. `同意这个计划`
2. `ok，执行这个方案`
3. `yes, go ahead with the plan`
4. `继续执行计划`

**预期结果**：
- ✅ 识别为批准
- ✅ progress.json 更新

#### 场景 3.3：误判场景（不应触发）

测试输入：
1. `我同意你的看法`（只有"同意"，没有"计划"关键词）
2. `yes`（只有批准词，没有计划关键词）
3. `ok`（只有批准词，没有计划关键词）
4. `这个方案不错`（只有"方案"，没有批准词）

**预期结果**：
- ❌ 不识别为批准
- ❌ progress.json 不更新
- ✅ 避免了误判

---

## 手动测试步骤

### 准备工作

1. 确认修改已应用：
   ```bash
   cat .claude/settings.json | grep -A 5 "SessionStart"
   cat .claude/settings.json | grep -A 5 "matcher.*Write"
   ```

2. 验证旧脚本已归档：
   ```bash
   ls .claude/hooks/archived/
   # 应该看到：session-start.sh, validate-write.py
   ```

### 执行测试

#### 测试 SessionStart Hook

1. **测试场景 1.1（无工作流）**：
   ```bash
   # 启动新的 Claude 会话
   claude chat
   # 发送消息："你好"
   # 检查：没有工作流恢复消息
   ```

2. **测试场景 1.2（有工作流）**：
   ```bash
   # 在一个会话中启动工作流
   claude chat
   # 发送消息："启动 workflow-orchestrator 测试"
   # 退出会话

   # 重新启动会话
   claude chat --resume
   # 检查：应该显示工作流恢复消息
   ```

#### 测试 PreToolUse Write Hook

1. **测试场景 2.1（写入当前会话）**：
   ```bash
   # 在有工作流的会话中
   > 请创建文件 .claude/sessions/{当前会话ID}/test.txt
   # 检查：文件应该成功创建
   ```

2. **测试场景 2.2（写入旧会话）**：
   ```bash
   # 创建第二个会话
   # 尝试写入第一个会话的目录
   > 请创建文件 .claude/sessions/{旧会话ID}/test.txt
   # 检查：应该被拒绝并显示错误消息
   ```

#### 测试 capture-approval.py

1. **测试场景 3.1（明确批准）**：
   ```bash
   # 在 planning 阶段
   > 批准
   # 检查 progress.json：
   cat .claude/sessions/{会话ID}/workflow/progress.json | grep user_approved_plan
   # 应该显示：true
   ```

2. **测试场景 3.3（误判）**：
   ```bash
   # 在 planning 阶段
   > 我同意你的看法
   # 检查 progress.json：
   cat .claude/sessions/{会话ID}/workflow/progress.json | grep user_approved_plan
   # 应该显示：false（未改变）
   ```

---

## 回滚方案

如果测试发现问题，可以快速回滚：

```bash
# 恢复旧配置
cp .claude/settings.json.backup .claude/settings.json

# 恢复旧脚本
mv .claude/hooks/archived/session-start.sh .claude/hooks/
mv .claude/hooks/archived/validate-write.py .claude/hooks/

# 恢复旧的 capture-approval.py（如果需要）
git checkout .claude/hooks/capture-approval.py
```

---

## 验收标准

### ✅ 功能验收

- [ ] SessionStart Hook 能正确检测进行中的工作流
- [ ] SessionStart Hook 在无工作流时不输出消息
- [ ] PreToolUse Write Hook 能阻止写入旧会话目录
- [ ] PreToolUse Write Hook 允许写入当前会话和非会话目录
- [ ] capture-approval.py 能识别明确的批准短语
- [ ] capture-approval.py 能识别模糊批准+计划关键词
- [ ] capture-approval.py 不会误判普通对话

### ✅ 质量验收

- [x] JSON 格式验证通过
- [x] 旧脚本已正确归档
- [x] 配置文件已备份
- [x] 测试文档已创建

---

## 已知限制

1. **SessionStart Hook**：依赖对话历史识别工作流，如果对话历史被清除可能无法恢复上下文
2. **PreToolUse Write Hook**：只检查 `.claude/sessions/` 路径，其他路径不做验证
3. **capture-approval.py**：仍然基于关键词匹配，虽然已优化但不是完全的语义理解

---

## 后续优化建议

### 可选改进（未在本次实施）

1. **validate-subagent.py**：可以考虑转换为 Prompt Hook，使用 AI 判断子代理调用是否合规
2. **混合方案**：需要写文件的 hooks 可以采用 Command + Prompt 混合方案
3. **更智能的批准识别**：使用内嵌 Prompt Hook 进行语义分析

### 不建议修改

- ❌ **update-progress.py**：保持 Command Hook（核心自动化）
- ❌ **track-file.py**：保持 Command Hook（核心自动化）

---

## 联系人

如有问题，请参考：
- 计划文档：`.plan/claude/07-Hooks智能化优化方案/plan.md`
- 原始 Stop Hook 优化：`.plan/claude/06-Stop-Hook修复方案/`

---

**测试愉快！** 🎉
