#!/usr/bin/env python3
"""
工作流强制执行器 - 确保严格遵循 CLAUDE.md 中的多代理工作流约束

Hook类型:
- session_start: 会话开始时注入核心约束
- prompt_check: 用户提交提示时检测是否应触发工作流
- tool_gate: 工具使用前的检查（防止绕过工作流）
- response_check: 响应完成后检查是否应启动工作流
"""

import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional

class WorkflowEnforcer:
    """工作流强制执行器"""

    # 触发关键词模式
    TRIGGER_PATTERNS = {
        "开发类": [
            r"实现.*系统",
            r"开发.*功能",
            r"构建.*模块",
            r"添加.*功能",
            r"新增.*特性",
            r"重构.*",
            r"优化.*",
        ],
        "计划类": [
            r"执行计划",
            r"启动工作流",
            r"开始实施",
            r"按照.*计划",
            r"参考.*设计",
        ],
        "多代理类": [
            r"使用多代理",
            r"启动工作流",
            r"完整流程",
            r"自动化执行",
            r"质量保证流程",
        ],
    }

    # 多项目关键词（用户需要在此配置自己的项目列表）
    # 示例：PROJECT_KEYWORDS = ["frontend", "backend", "api"]
    # 留空则禁用多项目检测
    PROJECT_KEYWORDS = [
        # TODO: 在此配置你的项目名称列表
    ]

    # 复杂任务特征
    COMPLEXITY_PATTERNS = [
        r"数据库.*设计",
        r"表结构",
        r"接口.*调用",
        r"多阶段",
        r"测试.*审计",
        r"质量保证",
    ]

    @staticmethod
    def session_start() -> str:
        """会话开始时注入核心约束"""
        return """
⚠️ **工作流提醒** ⚠️

你现在正在使用 Claude Code 多代理协同开发框架。

**核心约束（必须遵守）**：

1. **检测工作流触发条件**：
   - 关键词：实现/开发/构建/添加/新增/重构/优化 XXX系统/功能/模块
   - 引用计划：`.plan/` 目录中的文件
   - 多项目：涉及 2 个或以上子项目
   - 复杂任务：数据库设计、跨服务调用、多阶段实施、质量保证

2. **触发时必须**：
   - 立即使用 Task 工具调用 `workflow-orchestrator` 子代理
   - 不要直接实现，不要跳过工作流

3. **不触发的场景**：
   - 简单的代码修改（单文件、单函数）
   - 文档更新或问答
   - 配置文件调整
   - Bug修复（明确的单点问题）
   - 用户明确要求"不要启动工作流"或"直接实现"

**请在处理每个用户请求前，先检查是否满足触发条件！**
"""

    @staticmethod
    def check_workflow_trigger(user_prompt: str) -> Optional[str]:
        """检测用户提示是否应触发工作流"""
        reasons = []

        # 1. 检查关键词
        for category, patterns in WorkflowEnforcer.TRIGGER_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, user_prompt):
                    reasons.append(f"- 检测到{category}关键词: '{pattern}'")
                    break

        # 2. 检查是否引用 .plan/ 文件
        if re.search(r'\.plan/', user_prompt):
            reasons.append("- 引用了 .plan/ 目录中的文件")

        # 3. 检查多项目需求
        project_count = sum(1 for keyword in WorkflowEnforcer.PROJECT_KEYWORDS
                           if keyword in user_prompt)
        if project_count >= 2:
            reasons.append(f"- 涉及 {project_count} 个项目（多项目需求）")

        # 4. 检查复杂任务特征
        for pattern in WorkflowEnforcer.COMPLEXITY_PATTERNS:
            if re.search(pattern, user_prompt):
                reasons.append(f"- 检测到复杂任务特征: '{pattern}'")
                break

        # 5. 检查用户是否明确拒绝工作流
        reject_patterns = [
            r"不要启动工作流",
            r"直接实现",
            r"不需要完整流程",
            r"跳过工作流",
        ]
        for pattern in reject_patterns:
            if re.search(pattern, user_prompt):
                return None  # 用户明确拒绝

        # 如果有触发原因，返回提醒
        if reasons:
            return f"""
🚨 **检测到工作流触发条件** 🚨

{chr(10).join(reasons)}

**必须执行的操作**：
使用 Task 工具调用 `workflow-orchestrator` 子代理，不要直接实现！

示例调用：
```
Task(
    subagent_type="workflow-orchestrator",
    description="[简短描述]",
    prompt=\"\"\"
请启动完整的多代理工作流，实现以下需求：

## 用户需求
{user_prompt}

## 涉及项目
[根据需求识别的项目列表]
\"\"\"
)
```

**如果你不确定是否应该启动工作流，请询问用户！**
"""

        return None

    @staticmethod
    def tool_gate(tool_name: str, tool_input: Dict) -> Optional[str]:
        """工具使用前的检查"""
        # 如果是直接写代码但没有通过工作流，发出警告
        if tool_name in ["Write", "Edit"]:
            file_path = tool_input.get("file_path", "")

            # 检查是否是业务代码（而非配置文件）
            if any(ext in file_path for ext in [".py", ".java", ".ts", ".tsx", ".js", ".jsx"]):
                # TODO: 可以添加逻辑检查当前是否在工作流会话中
                # 如果不在工作流会话中且修改业务代码，发出警告
                pass

        return None

    @staticmethod
    def response_check() -> Optional[str]:
        """响应完成后的检查"""
        # 可以在这里添加逻辑，检查是否应该启动工作流但没有启动
        return None

def main():
    """主入口"""
    if len(sys.argv) < 2:
        print("Usage: workflow_enforcer.py <hook_type>", file=sys.stderr)
        sys.exit(1)

    hook_type = sys.argv[1]

    try:
        # 读取 stdin 的 JSON 数据
        input_data = {}
        if not sys.stdin.isatty():
            try:
                input_data = json.load(sys.stdin)
            except json.JSONDecodeError:
                pass

        enforcer = WorkflowEnforcer()
        output = None

        if hook_type == "session_start":
            output = enforcer.session_start()

        elif hook_type == "prompt_check":
            user_prompt = input_data.get("user_prompt", "")
            if user_prompt:
                output = enforcer.check_workflow_trigger(user_prompt)

        elif hook_type == "tool_gate":
            tool_name = input_data.get("tool_name", "")
            tool_input = input_data.get("tool_input", {})
            output = enforcer.tool_gate(tool_name, tool_input)

        elif hook_type == "response_check":
            output = enforcer.response_check()

        if output:
            print(output)
            # 对于 prompt_check，如果检测到触发条件，返回退出码 1
            # 这会将输出作为反馈注入到对话中
            if hook_type == "prompt_check":
                sys.exit(0)  # 正常退出，但输出会被注入

    except Exception as e:
        print(f"Hook执行错误: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
