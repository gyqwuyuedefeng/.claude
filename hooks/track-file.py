#!/usr/bin/env python3
"""
追踪关键文件的生成，更新 progress.json
"""
import json
import sys
from pathlib import Path

def track_file(tool_input, tool_response):
    """追踪文件写入"""
    file_path = tool_input.get("file_path", "")

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

    checklist = progress.get("checklist", {})

    # 检查关键文件
    if "session.md" in file_path:
        checklist["session_md_exists"] = True
    elif "summary.md" in file_path and "analysis" in file_path:
        checklist["analysis_completed"] = True
    elif "overall-plan.md" in file_path:
        checklist["planning_started"] = True
    elif "phases.md" in file_path:
        checklist["tasks_created"] = True

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

    track_file(tool_input, tool_response)

    sys.exit(0)

if __name__ == "__main__":
    main()
