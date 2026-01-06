# Hooks 系统使用指南

## 快速开始

### 1. 验证安装

检查以下文件是否存在：

```bash
# 检查 hooks 配置
ls -la .claude/settings.json

# 检查 hook 脚本
ls -la .claude/hooks/workflow_enforcer.py

# 检查说明文档
ls -la .claude/hooks/README.md
```

### 2. 测试 Hooks

运行以下命令测试各个 hook 是否正常工作：

```bash
# 测试会话开始提醒
python3 .claude/hooks/workflow_enforcer.py session_start

# 测试工作流触发检测（应该输出警告）
echo '{"user_prompt":"实现用户认证系统"}' | python3 .claude/hooks/workflow_enforcer.py prompt_check

# 测试简单任务（不应输出）
echo '{"user_prompt":"修改变量名"}' | python3 .claude/hooks/workflow_enforcer.py prompt_check

# 测试用户拒绝工作流（不应输出）
echo '{"user_prompt":"实现XXX功能，不要启动工作流"}' | python3 .claude/hooks/workflow_enforcer.py prompt_check
```

### 3. 启用 Hooks

Hooks 会在下次启动 Claude Code 会话时自动生效。无需手动操作。

### 4. 验证 Hooks 是否生效

重新启动 Claude Code 会话后，你应该在对话开始时看到：

```
⚠️ **工作流提醒** ⚠️

你现在正在使用 Claude Code 多代理协同开发框架。
...
```

当你输入满足触发条件的需求时（例如："实现用户认证系统"），你应该看到：

```
🚨 **检测到工作流触发条件** 🚨
...
```

---

## 触发条件详解

### ✅ 会触发工作流的情况

#### 1. 关键词触发

**开发类关键词**：
- "实现XXX系统"
- "开发XXX功能"
- "构建XXX模块"
- "添加XXX功能"
- "新增XXX特性"
- "重构XXX"
- "优化XXX"

**示例**：
```
✅ "实现用户认证系统"
✅ "开发积分扣减功能"
✅ "构建订单管理模块"
✅ "添加支付功能"
```

**计划类关键词**：
- "执行计划"
- "启动工作流"
- "开始实施"
- "按照XXX计划"
- "参考XXX设计"

**示例**：
```
✅ "执行积分扣减计划"
✅ "按照设计文档实现"
```

**多代理类关键词**：
- "使用多代理"
- "启动工作流"
- "完整流程"
- "自动化执行"
- "质量保证流程"

**示例**：
```
✅ "使用多代理实现这个功能"
✅ "启动完整工作流"
```

#### 2. 引用计划文件

**示例**：
```
✅ "参考 .plan/106-积分扣减系统设计与实现/plan.md"
✅ "按照 .plan/ 中的设计实现"
```

#### 3. 多项目需求

涉及 **2个或以上** 子项目：
- {project-3}
- {project-2}
- {project-4}
- {project-5}

**示例**：
```
✅ "在 {project-3} 和 {project-2} 中实现XXX"
✅ "修改 {project-4} 前端和 {project-5} 后端"
```

#### 4. 复杂任务特征

**示例**：
```
✅ "设计数据库表结构并实现"
✅ "实现跨服务接口调用"
✅ "包括分析、设计、实现、测试各阶段"
✅ "需要完整的质量保证流程"
```

---

### ❌ 不会触发工作流的情况

#### 1. 简单的代码修改

**示例**：
```
❌ "修改 project.py 第123行的变量名"
❌ "给这个函数添加注释"
❌ "格式化代码"
```

#### 2. 文档更新或问答

**示例**：
```
❌ "更新 README 文档"
❌ "解释一下这段代码的作用"
❌ "这个函数是干什么的？"
```

#### 3. 配置文件调整

**示例**：
```
❌ "修改 settings.json 配置"
❌ "调整端口号为 8080"
```

#### 4. Bug修复（明确的单点问题）

**示例**：
```
❌ "修复登录按钮点击无响应的bug"
❌ "解决空指针异常"
```

#### 5. 用户明确拒绝工作流

**拒绝关键词**：
- "不要启动工作流"
- "直接实现"
- "不需要完整流程"
- "跳过工作流"

**示例**：
```
❌ "实现用户认证功能，但是不要启动工作流，直接实现"
❌ "添加这个功能，跳过工作流"
```

---

## 工作流程示例

### 示例 1：正确使用工作流

**用户输入**：
```
实现积分扣减系统，参考 .plan/106-积分扣减系统设计与实现/plan.md
```

**Hook 输出**：
```
🚨 **检测到工作流触发条件** 🚨

- 检测到开发类关键词: '实现.*系统'
- 检测到计划类关键词: '参考.*设计'
- 引用了 .plan/ 目录中的文件

**必须执行的操作**：
使用 Task 工具调用 `workflow-orchestrator` 子代理，不要直接实现！
```

**Claude 应该做的**：
```python
Task(
    subagent_type="workflow-orchestrator",
    description="启动积分扣减系统工作流",
    prompt="""
请启动完整的多代理工作流，实现以下需求：

## 用户需求
实现积分扣减系统，参考 .plan/106-积分扣减系统设计与实现/plan.md

## 涉及项目
{project-2}, {project-3}
"""
)
```

---

### 示例 2：简单任务不触发

**用户输入**：
```
修改 project.py 第123行的变量名为 user_id
```

**Hook 输出**：
- 无输出（不满足触发条件）

**Claude 应该做的**：
- 直接读取文件并修改变量名

---

### 示例 3：用户拒绝工作流

**用户输入**：
```
实现用户登录功能，直接实现，不需要完整工作流
```

**Hook 输出**：
- 无输出（检测到用户明确拒绝）

**Claude 应该做的**：
- 按照用户要求直接实现登录功能

---

## 自定义配置

### 修改触发关键词

编辑 `.claude/hooks/workflow_enforcer.py`，修改以下部分：

```python
# 触发关键词模式
TRIGGER_PATTERNS = {
    "开发类": [
        r"实现.*系统",
        r"开发.*功能",
        # 添加你的自定义模式
    ],
    # ...
}
```

### 添加项目关键词

```python
# 多项目关键词
PROJECT_KEYWORDS = [
    "{project-3}",
    "{project-2}",
    # 添加你的项目名称
]
```

### 修改复杂任务特征

```python
# 复杂任务特征
COMPLEXITY_PATTERNS = [
    r"数据库.*设计",
    r"表结构",
    # 添加你的自定义模式
]
```

### 修改拒绝关键词

在 `check_workflow_trigger` 方法中修改：

```python
reject_patterns = [
    r"不要启动工作流",
    r"直接实现",
    # 添加你的自定义模式
]
```

---

## 调试和故障排除

### 1. Hooks 没有生效

**检查步骤**：

```bash
# 1. 确认 settings.json 存在
cat .claude/settings.json

# 2. 确认 Python 可以执行
python3 --version

# 3. 手动测试 hook 脚本
python3 .claude/hooks/workflow_enforcer.py session_start
```

### 2. 启用调试日志

编辑 `.claude/hooks/workflow_enforcer.py`，在文件开头添加：

```python
import logging

# 配置日志
logging.basicConfig(
    filename="/tmp/workflow_enforcer.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
```

在关键位置添加日志：

```python
logger.debug(f"检测用户输入: {user_prompt}")
logger.info(f"触发条件: {reasons}")
```

查看日志：

```bash
tail -f /tmp/workflow_enforcer.log
```

### 3. Hook 执行超时

如果 hook 执行时间超过设置的超时时间（默认 5 秒），会被强制终止。

**解决方法**：
- 优化 hook 脚本，减少执行时间
- 或在 `settings.json` 中增加超时时间：

```json
{
  "type": "command",
  "command": "...",
  "timeout": 10  // 增加到 10 秒
}
```

### 4. Hook 输出没有显示

确保 hook 脚本的输出被正确打印到 stdout：

```python
print(output)  # 输出到 stdout
print(f"错误: {e}", file=sys.stderr)  # 错误输出到 stderr
```

---

## 禁用 Hooks

如果你想临时禁用 hooks，有以下几种方式：

### 方法 1：重命名 settings.json

```bash
mv .claude/settings.json .claude/settings.json.disabled
```

### 方法 2：编辑 settings.json

将整个 `hooks` 对象注释掉：

```json
{
  "comment_hooks": {
    "SessionStart": [...]
  }
}
```

### 方法 3：删除特定 hook

在 `settings.json` 中删除不需要的 hook 事件。

---

## 更新 Hooks

### 更新 Hook 脚本

直接编辑 `.claude/hooks/workflow_enforcer.py` 文件即可。更改会在下次 Claude Code 调用 hook 时生效。

### 更新 Hook 配置

编辑 `.claude/settings.json`，更改会在下次启动会话时生效。

---

## 常见问题

### Q1: Hooks 会影响 Claude Code 的性能吗？

A: 影响很小。Hooks 设计为快速执行（通常 < 100ms），且设置了超时保护（5秒）。

### Q2: Hook 能强制 Claude 必须调用工作流吗？

A: 不能。Hooks 只能提供**提醒和反馈**，不能强制 Claude 的行为。但通过持续、明确的提醒，可以显著提高遵循率。

### Q3: 如果 Hook 脚本有 bug 会怎样？

A: Hook 执行错误会被捕获，不会影响 Claude Code 的正常运行。错误信息会输出到 stderr。

### Q4: Hooks 支持哪些事件？

A: 当前实现的 hook 事件：
- SessionStart：会话开始
- UserPromptSubmit：用户提示提交
- PreToolUse：工具使用前
- Stop：响应完成

完整的 hook 事件列表请参考 Claude Code 官方文档。

### Q5: 可以用其他语言编写 Hook 脚本吗？

A: 可以。Hook 可以是任何可执行的 shell 命令，包括 Bash、Python、Node.js 等。只需确保命令在系统中可用即可。

---

## 参考资源

- **官方文档**：Claude Code Hooks 参考文档
- **项目文档**：
  - `.claude/CLAUDE.md` - 工作流规则定义
  - `.claude/hooks/README.md` - Hooks 系统详细说明
  - `.claude/README.md` - 多代理框架说明

---

## 反馈和改进

如果你发现：
- Hook 误报（不应触发却触发了）
- Hook 漏报（应触发却没触发）
- 其他问题或改进建议

请：
1. 记录具体的用户输入和预期行为
2. 编辑 `.claude/hooks/workflow_enforcer.py` 调整检测逻辑
3. 或联系项目维护者

---

**版本**：1.0.0
**更新时间**：2026-01-05
