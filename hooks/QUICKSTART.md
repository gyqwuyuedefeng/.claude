# Hooks 系统快速开始

## ✅ 系统已就绪

所有 hooks 已成功配置并通过测试！

```
通过: 17 个测试
失败: 0 个测试
状态: ✓ 就绪
```

## 🚀 立即启用

### 方法 1：重启 Claude Code 会话（推荐）

1. 退出当前 Claude Code 会话
2. 重新启动 Claude Code
3. Hooks 将自动加载

### 方法 2：无需重启（如果支持）

某些 Claude Code 版本支持动态重载配置，可以尝试：
- 运行 `/reload` 命令（如果可用）
- 或手动重新加载项目

## 📋 验证 Hooks 是否生效

### 步骤 1：检查会话开始提醒

重启会话后，你应该看到：

```
⚠️ **工作流提醒** ⚠️

你现在正在使用 Claude Code 多代理协同开发框架。

**核心约束（必须遵守）**：
...
```

### 步骤 2：测试触发检测

输入以下测试需求：

```
实现用户认证系统
```

你应该看到：

```
🚨 **检测到工作流触发条件** 🚨

- 检测到开发类关键词: '实现.*系统'

**必须执行的操作**：
使用 Task 工具调用 `workflow-orchestrator` 子代理，不要直接实现！
```

### 步骤 3：测试不触发场景

输入以下测试需求：

```
修改 project.py 第123行的变量名
```

应该**不会**看到任何警告，Claude 会直接处理。

## 📚 完整文档

- **使用指南**：`.claude/hooks/USAGE.md`
- **系统说明**：`.claude/hooks/README.md`
- **实施总结**：`.claude/hooks/IMPLEMENTATION_SUMMARY.md`

## 🔧 如何自定义

### 添加自定义触发关键词

编辑 `.claude/hooks/workflow_enforcer.py`：

```python
TRIGGER_PATTERNS = {
    "开发类": [
        r"实现.*系统",
        r"开发.*功能",
        r"你的自定义模式",  # 添加这里
    ],
    # ...
}
```

### 添加项目关键词

```python
PROJECT_KEYWORDS = [
    "{project-3}",
    "{project-2}",
    "你的项目名",  # 添加这里
]
```

## 🐛 故障排除

### Hooks 没有生效？

1. **检查配置文件**：
   ```bash
   cat .claude/settings.json
   ```

2. **手动测试 hook**：
   ```bash
   python3 .claude/hooks/workflow_enforcer.py session_start
   ```

3. **运行验证脚本**：
   ```bash
   python3 .claude/hooks/verify.py
   ```

### 需要调试？

启用日志：编辑 `.claude/hooks/workflow_enforcer.py`

```python
import logging
logging.basicConfig(
    filename="/tmp/workflow_enforcer.log",
    level=logging.DEBUG
)
```

查看日志：
```bash
tail -f /tmp/workflow_enforcer.log
```

## 📊 预期效果

### Before（没有 Hooks）

```
用户: 实现积分扣减系统

Claude: 好的，我来直接实现...
[跳过工作流，直接写代码]
```

### After（有 Hooks）

```
用户: 实现积分扣减系统

Hook: 🚨 检测到工作流触发条件！
      必须使用 workflow-orchestrator！

Claude: 检测到工作流触发条件，我将调用 workflow-orchestrator...
        Task(subagent_type="workflow-orchestrator", ...)
        [正确启动完整工作流]
```

## ⚠️ 重要提醒

### Hooks 的作用

✅ **提供持续、明确的提醒**
✅ **自动检测触发条件**
✅ **提供调用模板**

❌ **不能强制 Claude 的行为**
❌ **不能100%阻止错误操作**

### 最佳实践

1. **定期查看 CLAUDE.md**：确保理解工作流规则
2. **遇到警告时停下思考**：是否真的应该启动工作流
3. **及时反馈**：如果发现误报或漏报，调整检测逻辑

## 🎯 下一步

现在你可以：

1. **重启 Claude Code 会话**测试 hooks
2. **尝试输入触发需求**验证检测
3. **开始使用完整工作流**提高代码质量

## 📞 获取帮助

- 查看 `USAGE.md` 了解详细使用方法
- 查看 `README.md` 了解系统架构
- 查看 `IMPLEMENTATION_SUMMARY.md` 了解实施细节

---

**Hooks 系统版本**：1.0.0
**状态**：✓ 已就绪，所有测试通过
**最后验证**：2026-01-05
