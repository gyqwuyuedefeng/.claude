# Hooks 功能测试指南

## 已完成的配置

✅ **1. Hooks 脚本已创建**：
- `.claude/hooks/sync-all-state.py` - 监听 progress.json 写入，同步到 session.md 和 phases.md
- `.claude/hooks/verify-and-fix-state.py` - 验证状态一致性，自动修复

✅ **2. 脚本语法验证通过**：
- Python 语法检查：通过
- 执行权限：已设置（WSL 环境下默认具有）

✅ **3. Claude Code 配置已更新**：
- `.claude/settings.json` 已添加 PostToolUse 和 SubagentStop hooks
- JSON 格式验证：通过

## Hooks 工作原理

### PostToolUse Hook（sync-all-state.py）

**触发时机**：当任何代理使用 Write 或 Edit 工具修改文件时

**处理流程**：
1. 检查是否是 progress.json 文件被修改
2. 如果是，读取最新的任务状态
3. 使用文件锁安全地更新 session.md
4. 如果任务完成，同步勾选 phases.md 中的任务
5. 输出同步结果到 stderr（在 verbose 模式下可见）

**示例输出**：
```
✓ session.md 已更新: phase01-task01 - completed
✓ phases.md 已勾选任务: phase01-task01
✓ 状态同步完成: phase01-task01 - completed
```

### SubagentStop Hook（verify-and-fix-state.py）

**触发时机**：当任何子代理完成工作时

**处理流程**：
1. 检查 progress.json 的最后更新时间
2. 如果超过 10 分钟未更新，发出警告
3. 检测是否有卡住的任务（运行超过 30 分钟）
4. 验证 session.md 和 phases.md 是否存在
5. 输出验证结果

**示例输出**：
```
✓ 状态验证通过
```

或：
```
⚠️ 警告：progress.json 超过 15 分钟未更新
⚠️ 发现卡住的任务: phase01-task02 (运行 45 分钟)
```

## 如何验证 Hooks 正常工作

### 方法 1：检查下次工作流执行

当您下次使用工作流时（例如运行 `workflow-orchestrator` 或 `code-executor`）：

1. **开启 verbose 模式**（如果 Claude Code 支持）
2. **观察 stderr 输出**，查找 hooks 的输出信息
3. **检查 session.md 文件**，查看是否有新的进度更新记录

**期望看到**：
- 在 code-executor 更新 progress.json 后，session.md 会自动添加新的时间戳记录
- 在任务完成后，phases.md 中对应的任务会被自动勾选

### 方法 2：手动测试（开发环境）

如果您想立即测试 hooks：

```bash
# 1. 创建一个测试 session 目录（或使用现有的）
cd .claude/sessions/001-积分扣减系统-20260105-0920/

# 2. 手动触发 sync-all-state.py
# 模拟 PostToolUse hook 的输入
cat <<'EOF' | python3 ../../hooks/sync-all-state.py
{
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/mnt/d/software/beilv-agent/.claude/sessions/001-积分扣减系统-20260105-0920/workflow/progress.json"
  },
  "tool_response": {
    "success": true
  },
  "cwd": "/mnt/d/software/beilv-agent"
}
EOF

# 3. 检查 session.md 是否有更新
tail -20 workflow/session.md

# 4. 手动触发 verify-and-fix-state.py
cat <<'EOF' | python3 ../../hooks/verify-and-fix-state.py
{
  "cwd": "/mnt/d/software/beilv-agent",
  "transcript_path": "/mnt/d/software/beilv-agent/.claude/sessions/001-积分扣减系统-20260105-0920/transcript.jsonl"
}
EOF
```

### 方法 3：检查实时工作流

在下次工作流执行时，您可以：

**执行前**：
```bash
# 记录 session.md 的当前状态
tail -10 .claude/sessions/001-积分扣减系统-20260105-0920/workflow/session.md > /tmp/before.txt
```

**执行工作流**（例如启动一个新任务）

**执行后**：
```bash
# 比较 session.md 的变化
tail -10 .claude/sessions/001-积分扣减系统-20260105-0920/workflow/session.md > /tmp/after.txt
diff /tmp/before.txt /tmp/after.txt
```

**期望看到**：新增的进度更新记录，格式如：
```markdown
- [2026-01-05 12:30:45] 🔄 任务 phase01-task01 开始执行
- [2026-01-05 12:35:20] ✅ 任务 phase01-task01 已完成 (测试:passed 审计:passed)
```

## 故障排查

### 如果 hooks 没有执行

**检查项**：

1. **Claude Code 版本**：确保您的 Claude Code 支持 hooks 功能
   ```bash
   # 检查 Claude Code 版本
   claude --version
   ```

2. **Hooks 配置**：确认 `.claude/settings.json` 中的 hooks 配置正确
   ```bash
   cat .claude/settings.json | grep -A 10 "PostToolUse"
   ```

3. **脚本权限**：确认脚本可以被 Python 执行
   ```bash
   python3 .claude/hooks/sync-all-state.py --help 2>&1 | head -5
   ```

4. **路径问题**：确认 `$CLAUDE_PROJECT_DIR` 环境变量指向正确的项目目录

### 如果 hooks 执行但没有更新 session.md

**可能原因**：

1. **文件路径不匹配**：检查 progress.json 的完整路径是否包含 "sessions/"
2. **JSON 格式问题**：检查 progress.json 是否是有效的 JSON
3. **权限问题**：检查是否有写入 session.md 的权限

**调试方法**：
```bash
# 查看 hook 的详细输出（需要在 verbose 模式下）
# 或者临时修改脚本，将 print() 输出重定向到文件：
# 在脚本顶部添加：
# import sys
# sys.stderr = open('/tmp/hook-debug.log', 'a')
```

## 文件锁机制

Hooks 使用 `fcntl.flock()` 文件锁来避免并发冲突：

```python
lock_file = session_md.parent / ".session.md.lock"
lock_fd = open(lock_file, 'w')
fcntl.flock(lock_fd, fcntl.LOCK_EX)  # 获取排他锁

try:
    # 执行文件更新操作
    ...
finally:
    fcntl.flock(lock_fd, fcntl.LOCK_UN)  # 释放锁
    lock_fd.close()
```

这确保了即使多个代理同时工作，session.md 的更新也是安全的。

## 性能影响

- **PostToolUse Hook**：每次 Write/Edit 操作后触发，但只处理 progress.json 相关的写入
- **SubagentStop Hook**：每次子代理完成时触发，执行轻量级的验证检查
- **超时设置**：两个 hooks 的超时都设置为 10 秒，足够完成所有操作
- **失败处理**：即使 hooks 执行失败（返回 exit code 0），也不会阻止主工作流

**预期开销**：每个 hook 执行时间 < 100ms（正常情况下）

## 下一步

现在 Hooks 系统已经配置完成。下次运行工作流时，您将自动获得：

✅ **实时的 session.md 更新**
✅ **自动的 phases.md 任务勾选**
✅ **状态一致性验证**
✅ **卡住任务的自动检测**

无需任何手动干预！

---

**创建时间**：2026-01-05
**版本**：1.0.0
