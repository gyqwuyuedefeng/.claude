# Hook 配置优化说明 v2

## 优化时间
2026-01-07

## 问题背景
启动时出现 `SessionStart:startup hook error`。

### 尝试的方案

#### 方案1：移除所有 Prompt Hook ❌
- 结果：启动正常，但失去所有智能检测功能

#### 方案2：简化 Prompt Hook（混合方案）❌
- 问题：Prompt Hook **无法访问对话历史文件**（transcript）
- 错误："requires reading and analyzing the transcript file... Without access to that file"
- 结论：Prompt Hook 在当前环境中不可用

#### 方案3：纯命令型 Hook（最终方案）✅
- 所有功能改用 Python 脚本实现
- 通过文件系统读取状态（progress.json、session 目录等）
- 不依赖对话历史访问

---

## 最终配置

### Hook 列表

| Hook 事件 | 类型 | 脚本 | 功能 |
|-----------|------|------|------|
| SessionStart | 命令型 | check-workflow-session.py | 检测进行中的工作流会话 |
| PreToolUse (Task) | 命令型 | validate-subagent.py | 验证子代理调用 |
| PostToolUse (Task) | 命令型 | update-progress.py | 更新工作流进度 |
| PostToolUse (Write) | 命令型 | track-file.py | 追踪文件变更 |
| UserPromptSubmit | 命令型 | capture-approval.py | 捕获用户批准 |

### 移除的 Hook

- ❌ Stop Hook（需要访问对话历史）
- ❌ SubagentStop Hook（需要访问对话历史）
- ❌ PreToolUse Write Hook（prompt 类型）

---

## 功能对比

| 功能 | 原版本 | 最终版本 |
|------|--------|----------|
| 工作流会话检测 | ✅ Prompt | ✅ Python（基于文件） |
| 会话恢复提示 | ✅ Prompt | ✅ Python（简化版） |
| 停止拦截 | ✅ Prompt | ❌ 无法实现 |
| 子代理完成性检查 | ✅ Prompt | ❌ 无法实现 |
| 写入路径保护 | ✅ Prompt | ❌ 移除 |
| 子代理验证 | ✅ Python | ✅ Python |
| 进度跟踪 | ✅ Python | ✅ Python |
| 文件追踪 | ✅ Python | ✅ Python |
| 用户批准捕获 | ✅ Python | ✅ Python |

---

## 损失的功能

由于 Prompt Hook 不可用，以下功能**无法实现**：

### 1. Stop Hook（停止拦截）
**原功能**：防止在工作流进行中意外退出
**无法实现原因**：需要分析对话历史判断工作流状态

**替代方案**：
- 用户手动检查 progress.json 确认工作流状态
- 在工作流中添加明确的"完成"标记

### 2. SubagentStop Hook（子代理完成性检查）
**原功能**：验证子代理是否完成所有职责
**无法实现原因**：需要分析子代理对话内容

**替代方案**：
- 主代理手动验证子代理输出
- 依赖子代理的自我检查逻辑

### 3. Write 路径保护
**原功能**：防止写入旧的会话目录
**无法实现原因**：需要从对话中识别活跃会话

**替代方案**：
- Python 脚本通过文件时间戳判断最新会话（准确率较低）
- 或者完全移除该功能

---

## SessionStart Python 实现

### 脚本逻辑
```python
check-workflow-session.py:
1. 查找 .claude/sessions/ 目录
2. 找到最新的会话目录（按修改时间）
3. 读取 progress.json
4. 检查 currentStage 是否为 "completed"
5. 如果未完成，输出警告消息
```

### 局限性
- ⚠️ 只能检测文件系统中的会话，无法分析对话内容
- ⚠️ 可能误判（如果用户手动删除了 session 目录）
- ⚠️ 无法识别多个并行工作流

---

## 为什么 Prompt Hook 不可用？

### 技术原因
Prompt Hook 需要：
1. 访问对话历史文件（`.jsonl` transcript）
2. 将历史传递给 Claude 进行分析
3. 获取 Claude 的判断结果

但在当前环境中：
- ❌ Hook 执行上下文**无法访问** transcript 文件
- ❌ 文件路径可能受权限限制
- ❌ Claude Code 的 hook 机制可能不支持这种用法

### 官方支持情况
需要查看 Claude Code 官方文档确认：
- Prompt Hook 是否支持访问对话历史？
- 是否有权限配置选项？
- 是否有其他方式实现类似功能？

---

## 建议

### 短期方案（当前配置）
- ✅ 使用纯命令型 Hook
- ✅ 通过文件系统状态检测工作流
- ⚠️ 接受功能损失

### 长期方案（需要进一步研究）
1. **研究官方文档**：确认 Prompt Hook 的正确用法
2. **提交 Issue**：向 Claude Code 团队反馈问题
3. **自定义工作流管理**：在主代理中实现状态检测逻辑

---

## 备份文件

- `settings.json.backup`：最初备份
- `settings.json.full-backup`：包含原始 Prompt Hook
- `HOOK-OPTIMIZATION.md`：方案A的文档（已过时）

---

## 测试结果

- ✅ 启动正常（无 hook error）
- ✅ SessionStart 检测可用（基于文件）
- ❌ Stop Hook 不可用
- ❌ SubagentStop 不可用

---

**最终方案：纯命令型 Hook** ✅

**功能保留率：约 60%**（核心功能保留，智能检测功能损失）
