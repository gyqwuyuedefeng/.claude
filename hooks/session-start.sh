#!/bin/bash

# 查找最近的工作流会话
LATEST_SESSION=$(ls -1dt .claude/sessions/[0-9]* 2>/dev/null | head -1)

if [ -z "$LATEST_SESSION" ]; then
  # 无进行中的工作流
  exit 0
fi

PROGRESS_FILE="$LATEST_SESSION/workflow/progress.json"

if [ ! -f "$PROGRESS_FILE" ]; then
  exit 0
fi

# 读取当前阶段
STAGE=$(jq -r '.workflow_stage' "$PROGRESS_FILE")
SESSION_ID=$(jq -r '.session_id' "$PROGRESS_FILE")

# 生成上下文注入
CONTEXT="
⚠️ **工作流状态恢复** ⚠️

检测到进行中的工作流会话：$SESSION_ID

当前阶段：$STAGE
会话目录：$LATEST_SESSION

**必须遵守的约束**：
1. 你必须继续执行该工作流，不能重新开始
2. 你必须使用已存在的会话目录，不能创建新的会话
3. 你必须严格按照 progress.json 中的阶段执行
4. 你必须在继续前验证所有前置条件已满足

**当前阶段检查清单**：
$(jq -r '.checklist | to_entries | map("- [\(if .value then "x" else " " end)] \(.key)") | join("\n")' "$PROGRESS_FILE")

**下一步行动**：
$(case "$STAGE" in
  "init")
    echo "你需要调用 workflow-orchestrator 开始分析阶段"
    ;;
  "analysis")
    echo "你需要完成所有项目的分析并调用 analysis-aggregator 汇总"
    ;;
  "planning")
    echo "你需要调用 master-planner 制定计划并等待用户确认"
    ;;
  "execution")
    echo "你需要继续执行 progress.json 中的任务"
    ;;
  "completed")
    echo "工作流已完成，你可以向用户报告结果"
    ;;
  *)
    echo "未知阶段，请检查 progress.json"
    ;;
esac)

请在执行任何操作前，先确认当前状态！
"

echo "$CONTEXT"
exit 0
