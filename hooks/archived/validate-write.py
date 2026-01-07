#!/usr/bin/env python3
"""
验证文件写入操作是否符合工作流规范
"""
import json
import sys
from pathlib import Path

def validate_write(tool_input):
    """验证写入操作"""
    file_path = tool_input.get("file_path", "")

    # 检查是否在正确的会话目录中写入
    if ".claude/sessions/" in file_path:
        # 查找最新会话
        sessions_dir = Path(".claude/sessions")
        if sessions_dir.exists():
            sessions = sorted(sessions_dir.glob("[0-9]*"), key=lambda p: p.stat().st_mtime, reverse=True)
            if sessions:
                latest_session = str(sessions[0])
                if latest_session not in file_path:
                    return False, f"不允许写入旧会话目录。请使用当前会话目录：{latest_session}"

    return True, None

def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"错误：无效的 JSON 输入：{e}", file=sys.stderr)
        sys.exit(1)

    tool_input = input_data.get("tool_input", {})

    valid, reason = validate_write(tool_input)

    if not valid:
        # 输出 JSON 阻止调用
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"⛔ 文件写入违规\n\n{reason}"
            }
        }
        print(json.dumps(output))
        sys.exit(0)

    # 允许写入
    sys.exit(0)

if __name__ == "__main__":
    main()
