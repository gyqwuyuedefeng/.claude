#!/usr/bin/env python3
"""
子代理调用完成后，自动更新 progress.json
"""
import json
import sys
from pathlib import Path
from datetime import datetime

def update_progress(tool_input, tool_response):
    """更新工作流进度"""
    # 查找最新会话
    sessions_dir = Path(".claude/sessions")
    if not sessions_dir.exists():
        return

    sessions = sorted(sessions_dir.glob("[0-9]*"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not sessions:
        return

    progress_file = sessions[0] / "workflow" / "progress.json"
    if not progress_file.exists():
        return

    with open(progress_file) as f:
        progress = json.load(f)

    subagent_type = tool_input.get("subagent_type", "")

    # 更新子代理完成状态
    if "subagents_completed" not in progress:
        progress["subagents_completed"] = {}

    progress["subagents_completed"][subagent_type] = True
    progress["updated_at"] = datetime.now().isoformat()

    # 更新检查清单
    checklist = progress.get("checklist", {})

    if subagent_type == "workflow-orchestrator":
        checklist["session_created"] = True
    elif subagent_type == "issue-analyzer":
        checklist["analysis_started"] = True
    elif subagent_type == "analysis-aggregator":
        checklist["analysis_completed"] = True
        progress["workflow_stage"] = "planning"
    elif subagent_type == "master-planner":
        checklist["planning_started"] = True
        # 注意：user_approved_plan 需要人工确认，不在这里设置
    elif subagent_type == "plan-splitter":
        checklist["tasks_created"] = True
        progress["workflow_stage"] = "execution"

    progress["checklist"] = checklist

    # 保存
    with open(progress_file, 'w') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)

def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(1)

    tool_input = input_data.get("tool_input", {})
    tool_response = input_data.get("tool_response", {})

    update_progress(tool_input, tool_response)

    sys.exit(0)

if __name__ == "__main__":
    main()
