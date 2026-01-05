#!/usr/bin/env python3
"""
PostToolUse Hook: 统一同步所有状态文件
监听 progress.json 写入，同步到 session.md 和 phases.md

作用：
1. 当任何代理写入 progress.json 时自动触发
2. 读取最新的任务状态
3. 同步更新到 session.md（工作流日志）
4. 同步更新到 phases.md（任务勾选）
5. 使用文件锁保证并发安全
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import fcntl


def update_session_md(session_md, task_info, timestamp):
    """
    更新 session.md 文件

    Args:
        session_md: session.md 文件路径
        task_info: 任务信息字典
        timestamp: 时间戳字符串

    Returns:
        bool: 是否更新成功
    """
    lock_file = session_md.parent / ".session.md.lock"

    try:
        # 获取文件锁
        lock_fd = open(lock_file, 'w')
        fcntl.flock(lock_fd, fcntl.LOCK_EX)

        try:
            status = task_info.get("status", "unknown")
            task_id = task_info.get("task_id", "unknown")

            # 根据不同状态生成不同的更新记录
            if status == "in_progress":
                update_line = f"\n- [{timestamp}] 🔄 任务 {task_id} 开始执行"
            elif status == "completed":
                test_status = task_info.get("test_status", "unknown")
                audit_status = task_info.get("audit_status", "unknown")
                update_line = f"\n- [{timestamp}] ✅ 任务 {task_id} 已完成 (测试:{test_status} 审计:{audit_status})"
            elif status == "failed":
                update_line = f"\n- [{timestamp}] ❌ 任务 {task_id} 执行失败"
            else:
                update_line = f"\n- [{timestamp}] 📝 任务 {task_id} 状态: {status}"

            # 追加到文件
            with open(session_md, "a", encoding="utf-8") as f:
                f.write(update_line + "\n")

            return True

        finally:
            # 释放文件锁
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            lock_fd.close()

    except Exception as e:
        print(f"更新 session.md 失败: {e}", file=sys.stderr)
        return False


def update_phases_md(phases_md, task_info, timestamp):
    """
    更新 phases.md 中的任务勾选状态

    Args:
        phases_md: phases.md 文件路径
        task_info: 任务信息字典
        timestamp: 时间戳字符串

    Returns:
        bool: 是否更新成功
    """
    try:
        # 读取 phases.md
        with open(phases_md, "r", encoding="utf-8") as f:
            content = f.read()

        task_id = task_info.get("task_id", "")
        status = task_info.get("status", "")

        # 如果任务完成，勾选对应的任务
        if status == "completed" and task_id in content:
            # 查找 "- [ ] **Task X.Y" 并替换为 "- [x] **Task X.Y"
            # 支持多种可能的格式
            old_patterns = [
                f"- [ ] **Task",
                f"- [ ] **{task_id}",
            ]

            new_content = content
            updated = False

            for pattern in old_patterns:
                if pattern in content:
                    # 找到对应的任务行，进行勾选
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if pattern in line and (task_id in line or f"Task" in line):
                            # 尝试匹配任务ID
                            if task_id in line or any(task_id.split('-')[-1] in line for _ in [task_id]):
                                lines[i] = line.replace('- [ ]', '- [x]', 1)
                                updated = True
                                break

                    if updated:
                        new_content = '\n'.join(lines)
                        break

            if updated:
                # 写回文件
                with open(phases_md, "w", encoding="utf-8") as f:
                    f.write(new_content)
                return True

        return False

    except Exception as e:
        print(f"更新 phases.md 失败: {e}", file=sys.stderr)
        return False


def main():
    """主函数"""
    try:
        # 读取 hook 输入（从 stdin）
        input_data = json.load(sys.stdin)

        tool_input = input_data.get("tool_input", {})
        tool_response = input_data.get("tool_response", {})
        cwd = input_data.get("cwd", "")

        # 只处理 progress.json 的写入
        file_path = tool_input.get("file_path", "")
        if "progress.json" not in file_path:
            sys.exit(0)  # 不是 progress.json，正常退出

        # 检查是否写入成功
        if not tool_response.get("success"):
            sys.exit(0)  # 写入失败，正常退出

        # 提取 session-id
        if "sessions/" not in file_path:
            sys.exit(0)  # 不在 sessions 目录下，正常退出

        session_id = file_path.split("sessions/")[1].split("/")[0]

        # 读取更新后的 progress.json
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                progress_data = json.load(f)
        except Exception as e:
            print(f"无法读取 progress.json: {e}", file=sys.stderr)
            sys.exit(0)

        # 提取当前任务信息
        current_task = progress_data.get("current_task", "")
        current_phase = progress_data.get("current_phase", "")

        if not current_task or not current_phase:
            sys.exit(0)  # 没有当前任务，正常退出

        # 查找当前任务的详细信息
        task_info = None
        for phase in progress_data.get("phases", []):
            if phase["phase_id"] == current_phase:
                for task in phase.get("tasks", []):
                    if task["task_id"] == current_task:
                        task_info = task
                        break
                if task_info:
                    break

        if not task_info:
            sys.exit(0)  # 找不到任务信息，正常退出

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. 更新 session.md
        session_md = Path(cwd) / ".claude" / "sessions" / session_id / "workflow" / "session.md"
        if session_md.exists():
            if update_session_md(session_md, task_info, timestamp):
                print(f"✓ session.md 已更新: {current_task} - {task_info.get('status')}", file=sys.stderr)

        # 2. 更新 phases.md（如果任务完成）
        phases_md = Path(cwd) / ".claude" / "sessions" / session_id / "planning" / "phases.md"
        if phases_md.exists():
            if update_phases_md(phases_md, task_info, timestamp):
                print(f"✓ phases.md 已勾选任务: {current_task}", file=sys.stderr)

        # 3. 验证一致性
        print(f"✓ 状态同步完成: {current_task} - {task_info.get('status')}", file=sys.stderr)

        sys.exit(0)

    except Exception as e:
        # Hook 错误不应阻止主工作流
        print(f"状态同步错误（已忽略）: {e}", file=sys.stderr)
        sys.exit(0)  # 返回 0，不阻止工作流


if __name__ == "__main__":
    main()
