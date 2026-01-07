#!/usr/bin/env python3
"""
捕获用户对计划的批准
"""
import json
import sys
import re
from pathlib import Path

def is_plan_approval(user_input: str) -> bool:
    """
    判断用户输入是否为计划批准
    使用更复杂的匹配逻辑，避免误判
    """
    # 明确的批准短语（高置信度）
    explicit_approvals = [
        "批准", "批准计划", "确认计划", "同意计划",
        "approve", "approve the plan", "confirmed", "confirm the plan"
    ]

    for phrase in explicit_approvals:
        if phrase in user_input:
            return True

    # 模糊匹配（中等置信度）- 需要同时包含批准词和计划关键词
    approval_words = ["同意", "yes", "ok", "继续", "确认"]
    plan_keywords = ["计划", "plan", "方案"]

    has_approval = any(word in user_input for word in approval_words)
    has_plan_keyword = any(keyword in user_input for keyword in plan_keywords)

    if has_approval and has_plan_keyword:
        return True

    return False

def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(1)

    prompt = input_data.get("prompt", "")
    prompt_lower = prompt.lower().strip()

    # 判断是否为计划批准
    is_approval = is_plan_approval(prompt_lower)

    if is_approval:
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
