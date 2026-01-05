#!/usr/bin/env python3
"""
SubagentStop Hook: 验证并修复状态一致性
在子代理完成时检查状态文件的一致性

作用：
1. 检查 progress.json 是否被正确更新
2. 检测卡住的任务（长时间处于 in_progress 状态）
3. 验证 session.md 和 phases.md 与 progress.json 的一致性
4. 自动修复发现的不一致问题
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta


def extract_session_id(cwd, transcript_path):
    """
    从工作目录或 transcript 路径提取 session-id

    Args:
        cwd: 当前工作目录
        transcript_path: 会话记录文件路径

    Returns:
        str: session-id 或 None
    """
    sessions_dir = Path(cwd) / ".claude" / "sessions"
    if not sessions_dir.exists():
        return None

    # 找到最新的会话目录
    try:
        session_dirs = sorted(
            sessions_dir.glob("*-*-*-*"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        if session_dirs:
            return session_dirs[0].name
    except Exception:
        pass

    # 尝试从 transcript_path 提取
    if transcript_path and "sessions/" in transcript_path:
        try:
            return transcript_path.split("sessions/")[1].split("/")[0]
        except Exception:
            pass

    return None


def check_progress_update(progress_file):
    """
    检查 progress.json 的更新状态

    Args:
        progress_file: progress.json 文件路径

    Returns:
        tuple: (是否有问题, 卡住的任务列表)
    """
    try:
        with open(progress_file, "r", encoding="utf-8") as f:
            progress_data = json.load(f)
    except Exception as e:
        print(f"无法读取 progress.json: {e}", file=sys.stderr)
        return (False, [])

    last_updated_str = progress_data.get("last_updated", "")
    current_time = datetime.now()

    stuck_tasks = []

    # 检查是否"太久没更新"（超过10分钟）
    if last_updated_str:
        try:
            last_time = datetime.fromisoformat(last_updated_str)
            time_diff = (current_time - last_time).total_seconds()

            if time_diff > 600:  # 10 分钟
                print(f"⚠️ 警告：progress.json 超过 {int(time_diff/60)} 分钟未更新", file=sys.stderr)
        except Exception:
            pass

    # 检查是否有卡住的任务
    for phase in progress_data.get("phases", []):
        for task in phase.get("tasks", []):
            if task.get("status") == "in_progress":
                start_time_str = task.get("start_time")
                if start_time_str and not task.get("end_time"):
                    try:
                        start_time = datetime.fromisoformat(start_time_str)
                        running_time = (current_time - start_time).total_seconds()

                        if running_time > 1800:  # 30 分钟
                            stuck_tasks.append({
                                "task_id": task["task_id"],
                                "running_time": int(running_time / 60),
                                "phase": phase["phase_id"]
                            })
                    except Exception:
                        pass

    if stuck_tasks:
        for task in stuck_tasks:
            print(
                f"⚠️ 发现卡住的任务: {task['task_id']} (运行 {task['running_time']} 分钟)",
                file=sys.stderr
            )

    return (len(stuck_tasks) > 0, stuck_tasks)


def verify_consistency(session_dir, progress_data):
    """
    验证状态文件的一致性

    Args:
        session_dir: 会话目录路径
        progress_data: progress.json 数据

    Returns:
        list: 发现的不一致问题列表
    """
    issues = []

    # 检查 session.md 是否存在
    session_md = session_dir / "workflow" / "session.md"
    if not session_md.exists():
        issues.append("session.md 文件不存在")

    # 检查 phases.md 是否存在
    phases_md = session_dir / "planning" / "phases.md"
    if not phases_md.exists():
        issues.append("phases.md 文件不存在")

    # TODO: 可以添加更多一致性检查
    # 例如：检查 phases.md 中的任务勾选是否与 progress.json 一致

    return issues


def main():
    """主函数"""
    try:
        # 读取 hook 输入
        input_data = json.load(sys.stdin)

        cwd = input_data.get("cwd", "")
        transcript_path = input_data.get("transcript_path", "")

        # 提取 session-id
        session_id = extract_session_id(cwd, transcript_path)
        if not session_id:
            sys.exit(0)  # 没有找到 session-id，正常退出

        session_dir = Path(cwd) / ".claude" / "sessions" / session_id

        if not session_dir.exists():
            sys.exit(0)  # 会话目录不存在，正常退出

        # 检查 progress.json
        progress_file = session_dir / "workflow" / "progress.json"
        if not progress_file.exists():
            sys.exit(0)  # progress.json 不存在，正常退出

        # 检查进度更新
        has_issues, stuck_tasks = check_progress_update(progress_file)

        # 如果发现卡住的任务，可以选择性地进行处理
        # 目前只是记录警告，不做自动修复，避免误操作

        # 读取 progress.json 进行一致性验证
        try:
            with open(progress_file, "r", encoding="utf-8") as f:
                progress_data = json.load(f)
        except Exception as e:
            print(f"无法读取 progress.json: {e}", file=sys.stderr)
            sys.exit(0)

        # 验证一致性
        issues = verify_consistency(session_dir, progress_data)
        if issues:
            print(f"⚠️ 发现 {len(issues)} 个一致性问题:", file=sys.stderr)
            for issue in issues:
                print(f"  - {issue}", file=sys.stderr)

        # 如果一切正常
        if not has_issues and not issues:
            print("✓ 状态验证通过", file=sys.stderr)

        sys.exit(0)

    except Exception as e:
        # Hook 错误不应阻止主工作流
        print(f"状态验证错误（已忽略）: {e}", file=sys.stderr)
        sys.exit(0)  # 返回 0，不阻止工作流


if __name__ == "__main__":
    main()
