#!/usr/bin/env python3
"""
验证子代理调用是否符合工作流流程
"""
import json
import sys
import os
from pathlib import Path

def load_progress():
    """加载最新的工作流进度"""
    sessions_dir = Path(".claude/sessions")
    if not sessions_dir.exists():
        return None

    # 查找最新会话
    sessions = sorted(sessions_dir.glob("[0-9]*"), key=os.path.getmtime, reverse=True)
    if not sessions:
        return None

    progress_file = sessions[0] / "workflow" / "progress.json"
    if not progress_file.exists():
        return None

    with open(progress_file) as f:
        return json.load(f)

def infer_workflow_stage(progress):
    """当 workflow_stage 缺失时，自动推断工作流阶段"""

    # 规则1：有 phases 和 tasks → execution 阶段
    if "phases" in progress and progress.get("phases"):
        print("ℹ️  自动推断工作流阶段：execution（检测到phases和tasks）", file=sys.stderr)
        return "execution"

    # 规则2：有 overall_plan → planning 阶段
    if "overall_plan" in progress:
        print("ℹ️  自动推断工作流阶段：planning（检测到overall_plan）", file=sys.stderr)
        return "planning"

    # 规则3：有 session_id 但无其他内容 → init 阶段
    if "session_id" in progress:
        print("ℹ️  自动推断工作流阶段：init（仅有session_id）", file=sys.stderr)
        return "init"

    # 规则4：完全空白 → 允许启动新会话
    return ""

def validate_subagent_call(tool_input, progress):
    """验证子代理调用是否符合当前阶段"""
    if not progress:
        # 无工作流状态，可能是首次调用
        return True, None

    prompt = tool_input.get("prompt", "")
    subagent_type = tool_input.get("subagent_type", "")
    stage = progress.get("workflow_stage", "")
    checklist = progress.get("checklist", {})

    # 【新增】当 stage 为空但 progress 有内容时，自动推断阶段
    if not stage and progress:
        stage = infer_workflow_stage(progress)

    # 定义终态：允许在这些状态下启动新会话
    TERMINAL_STAGES = [
        "completed",                      # 正常完成
        "failed",                         # 失败
        "testing_completed_with_issues",  # 测试完成但有问题
        "cancelled",                      # 用户取消
        ""                                # 空字符串表示未初始化
    ]

    # 特殊处理：允许在终态下启动新的 workflow-orchestrator
    # 这样用户可以在上一个会话完成后启动全新的独立会话
    if subagent_type == "workflow-orchestrator" and stage in TERMINAL_STAGES:
        return True, None

    # 定义阶段-子代理映射
    STAGE_AGENTS = {
        "init": ["workflow-orchestrator"],
        "analysis": ["project-info-builder", "issue-analyzer", "analysis-aggregator"],
        "planning": ["master-planner", "plan-splitter"],
        "execution": ["code-executor", "test-runner", "code-auditor", "auto-fixer", "Explore", "task-summarizer"],
        "summary": ["task-summarizer", "project-info-updater"]
    }

    allowed_agents = STAGE_AGENTS.get(stage, [])

    if subagent_type not in allowed_agents:
        return False, f"当前阶段 '{stage}' 不允许调用 '{subagent_type}' 子代理。允许的子代理：{', '.join(allowed_agents) if allowed_agents else '无'}\n\n提示：如果您想开启新会话，请等待当前会话完成。"

    # 检查前置条件
    if subagent_type == "analysis-aggregator":
        if not checklist.get("analysis_started"):
            return False, "必须先完成所有项目的 issue-analyzer 分析，才能调用 analysis-aggregator"

    if subagent_type == "master-planner":
        if not checklist.get("analysis_completed"):
            return False, "必须先完成分析汇总（analysis-aggregator），才能调用 master-planner"

    if subagent_type == "plan-splitter":
        if not checklist.get("user_approved_plan"):
            return False, "必须等待用户批准计划后，才能调用 plan-splitter 拆分任务"

    if subagent_type == "code-executor":
        if not checklist.get("tasks_created"):
            return False, "必须先由 plan-splitter 创建任务，才能调用 code-executor"

    return True, None

def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"错误：无效的 JSON 输入：{e}", file=sys.stderr)
        sys.exit(1)

    tool_input = input_data.get("tool_input", {})
    progress = load_progress()

    valid, reason = validate_subagent_call(tool_input, progress)

    if not valid:
        # 输出 JSON 阻止调用
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"⛔ 工作流流程违规\n\n{reason}\n\n请先完成前置步骤！"
            }
        }
        print(json.dumps(output))
        sys.exit(0)

    # 允许调用
    sys.exit(0)

if __name__ == "__main__":
    main()
