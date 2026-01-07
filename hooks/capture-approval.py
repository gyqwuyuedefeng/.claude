#!/usr/bin/env python3
"""
捕获用户对计划的批准
"""
import json
import sys
import re
from pathlib import Path

def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(1)

    prompt = input_data.get("prompt", "").lower()

    # 检测批准关键词
    approval_keywords = ["批准", "确认", "同意", "approve", "yes", "ok", "继续"]

    if any(keyword in prompt for keyword in approval_keywords):
        # 查找最新会话
        sessions_dir = Path(".claude/sessions")
        if sessions_dir.exists():
            sessions = sorted(sessions_dir.glob("[0-9]*"), key=lambda p: p.stat().st_mtime, reverse=True)
            if sessions:
                progress_file = sessions[0] / "workflow" / "progress.json"
                if progress_file.exists():
                    with open(progress_file) as f:
                        progress = json.load(f)

                    # 如果当前在 planning 阶段，标记为已批准
                    if progress.get("workflow_stage") == "planning":
                        progress["checklist"]["user_approved_plan"] = True

                        with open(progress_file, 'w') as f:
                            json.dump(progress, f, indent=2, ensure_ascii=False)

                        # 添加上下文
                        context = "\n✅ 用户已批准计划，progress.json 已更新。你现在可以调用 plan-splitter 拆分任务。\n"
                        print(context)

    sys.exit(0)

if __name__ == "__main__":
    main()
