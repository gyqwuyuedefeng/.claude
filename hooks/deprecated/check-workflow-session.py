#!/usr/bin/env python3
"""
SessionStart Hook - 检测进行中的工作流会话
"""
import json
import sys
import os
from pathlib import Path

def check_workflow_session():
    """检查是否有进行中的工作流会话"""
    try:
        # 查找最新的 sessions 目录
        claude_dir = Path(os.environ.get('CLAUDE_PROJECT_DIR', '.')) / '.claude' / 'sessions'

        if not claude_dir.exists():
            # 没有会话目录，直接返回
            return

        # 查找最新的会话目录
        sessions = sorted(claude_dir.glob('*-*-*'), key=lambda p: p.stat().st_mtime, reverse=True)

        if not sessions:
            return

        latest_session = sessions[0]

        # 读取 progress.json
        progress_file = latest_session / 'workflow' / 'progress.json'
        if not progress_file.exists():
            return

        with open(progress_file, 'r', encoding='utf-8') as f:
            progress = json.load(f)

        # 检查是否完成
        current_stage = progress.get('currentStage', 'unknown')
        if current_stage == 'completed':
            return

        # 输出警告消息
        session_id = latest_session.name
        print(f"⚠️  检测到进行中的工作流会话：{session_id}")
        print(f"当前阶段：{current_stage}")
        print("建议：请继续执行该工作流，不要重新开始。")

    except Exception:
        # 静默失败，不影响启动
        pass

if __name__ == '__main__':
    check_workflow_session()
