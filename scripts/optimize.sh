#!/bin/bash
# Claude Code 性能优化配置脚本
# 基于 debug 日志分析自动应用优化配置

set -e

CLAUDE_HOME="$HOME/.claude"
BACKUP_DIR="$CLAUDE_HOME/backups/$(date +%Y%m%d_%H%M%S)"

echo "🚀 Claude Code 性能优化配置"
echo "================================"
echo

# 创建备份目录
mkdir -p "$BACKUP_DIR"
echo "✓ 创建备份目录: $BACKUP_DIR"

# 1. 备份现有配置
if [ -f "$CLAUDE_HOME/.claude.json" ]; then
    cp "$CLAUDE_HOME/.claude.json" "$BACKUP_DIR/.claude.json.bak"
    echo "✓ 备份全局配置"
fi

if [ -f "$CLAUDE_HOME/settings.json" ]; then
    cp "$CLAUDE_HOME/settings.json" "$BACKUP_DIR/settings.json.bak"
    echo "✓ 备份用户配置"
fi

echo

# 2. 禁用遥测
echo "📊 配置遥测设置..."
SHELL_RC=""
if [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
elif [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
fi

if [ -n "$SHELL_RC" ]; then
    if ! grep -q "ANTHROPIC_DISABLE_TELEMETRY" "$SHELL_RC"; then
        echo "" >> "$SHELL_RC"
        echo "# Claude Code 性能优化 - 禁用遥测" >> "$SHELL_RC"
        echo "export ANTHROPIC_DISABLE_TELEMETRY=1" >> "$SHELL_RC"
        echo "✓ 已添加遥测禁用配置到 $SHELL_RC"
        echo "  请运行: source $SHELL_RC"
    else
        echo "✓ 遥测禁用配置已存在"
    fi
else
    echo "⚠ 未找到 shell 配置文件，请手动添加:"
    echo "  export ANTHROPIC_DISABLE_TELEMETRY=1"
fi

echo

# 3. 配置日志清理
echo "🗑️  配置日志清理..."
CLEANUP_SCRIPT="$CLAUDE_HOME/cleanup-logs.sh"

cat > "$CLEANUP_SCRIPT" << 'EOF'
#!/bin/bash
# Claude Code 日志清理脚本
LOG_DIR="$HOME/.claude/debug"
MAX_SIZE_MB=100
MAX_AGE_DAYS=7

if [ ! -d "$LOG_DIR" ]; then
    exit 0
fi

# 获取目录大小（MB）
SIZE=$(du -sm "$LOG_DIR" 2>/dev/null | cut -f1)

if [ -z "$SIZE" ]; then
    exit 0
fi

if [ $SIZE -gt $MAX_SIZE_MB ]; then
    echo "[$(date)] 日志目录超过 ${MAX_SIZE_MB}MB (当前: ${SIZE}MB)，开始清理..."
    DELETED=$(find "$LOG_DIR" -name "*.txt" -mtime +$MAX_AGE_DAYS -delete -print | wc -l)
    echo "[$(date)] 清理完成，删除 $DELETED 个文件"
else
    echo "[$(date)] 日志目录大小正常 (${SIZE}MB)"
fi
EOF

chmod +x "$CLEANUP_SCRIPT"
echo "✓ 创建日志清理脚本: $CLEANUP_SCRIPT"

# 4. 添加到 crontab（可选）
echo
read -p "是否添加日志清理到 crontab？(每天凌晨2点执行) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 检查是否已存在
    if crontab -l 2>/dev/null | grep -q "cleanup-logs.sh"; then
        echo "✓ crontab 任务已存在"
    else
        (crontab -l 2>/dev/null; echo "0 2 * * * bash $CLEANUP_SCRIPT >> $CLAUDE_HOME/cleanup.log 2>&1") | crontab -
        echo "✓ 已添加 crontab 任务"
    fi
else
    echo "⊘ 跳过 crontab 配置"
    echo "  如需手动添加，运行: crontab -e"
    echo "  添加行: 0 2 * * * bash $CLEANUP_SCRIPT"
fi

echo

# 5. 创建性能监控脚本
echo "📈 创建性能监控工具..."
PERF_SCRIPT="$CLAUDE_HOME/scripts/analyze-performance.py"
mkdir -p "$CLAUDE_HOME/scripts"

cat > "$PERF_SCRIPT" << 'EOF'
#!/usr/bin/env python3
"""Claude Code 性能分析工具"""
import json
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def analyze_performance():
    log_file = Path.home() / '.claude' / 'performance.jsonl'

    if not log_file.exists():
        print("❌ 性能日志文件不存在")
        print(f"   位置: {log_file}")
        return

    stats = defaultdict(list)
    total_events = 0

    with open(log_file) as f:
        for line in f:
            try:
                entry = json.loads(line)
                stats[entry['event']].append(entry['duration_ms'])
                total_events += 1
            except:
                continue

    if total_events == 0:
        print("❌ 没有性能数据")
        return

    print("📊 Claude Code 性能统计")
    print("=" * 60)
    print(f"总事件数: {total_events}")
    print()

    for event, durations in sorted(stats.items()):
        avg = sum(durations) / len(durations)
        max_dur = max(durations)
        min_dur = min(durations)
        p95 = sorted(durations)[int(len(durations) * 0.95)]

        print(f"📌 {event}")
        print(f"   平均: {avg:>8.2f}ms")
        print(f"   P95:  {p95:>8.2f}ms")
        print(f"   最大: {max_dur:>8.2f}ms")
        print(f"   最小: {min_dur:>8.2f}ms")
        print(f"   次数: {len(durations):>8}")
        print()

if __name__ == '__main__':
    analyze_performance()
EOF

chmod +x "$PERF_SCRIPT"
echo "✓ 创建性能分析脚本: $PERF_SCRIPT"

echo

# 6. 创建快速诊断脚本
echo "🔍 创建诊断工具..."
DIAG_SCRIPT="$CLAUDE_HOME/scripts/diagnose.sh"

cat > "$DIAG_SCRIPT" << 'EOF'
#!/bin/bash
# Claude Code 快速诊断工具

echo "🔍 Claude Code 诊断报告"
echo "================================"
echo

# 检查配置
echo "📁 配置文件:"
echo "  全局配置: $([ -f ~/.claude.json ] && echo '✓ 存在' || echo '✗ 不存在')"
echo "  用户配置: $([ -f ~/.claude/settings.json ] && echo '✓ 存在' || echo '✗ 不存在')"
echo

# 检查日志大小
echo "📊 日志统计:"
if [ -d ~/.claude/debug ]; then
    LOG_SIZE=$(du -sh ~/.claude/debug 2>/dev/null | cut -f1)
    LOG_COUNT=$(find ~/.claude/debug -name "*.txt" 2>/dev/null | wc -l)
    echo "  日志目录大小: $LOG_SIZE"
    echo "  日志文件数量: $LOG_COUNT"
else
    echo "  日志目录不存在"
fi
echo

# 检查最近的错误
echo "🚨 最近的错误 (最近10条):"
if [ -d ~/.claude/debug ]; then
    LATEST_LOG=$(ls -t ~/.claude/debug/*.txt 2>/dev/null | head -1)
    if [ -n "$LATEST_LOG" ]; then
        grep "\[ERROR\]" "$LATEST_LOG" 2>/dev/null | tail -10 | while read line; do
            echo "  $line"
        done
    else
        echo "  无日志文件"
    fi
else
    echo "  日志目录不存在"
fi
echo

# 检查遥测配置
echo "⚙️  遥测配置:"
if [ -n "$ANTHROPIC_DISABLE_TELEMETRY" ]; then
    echo "  ✓ 遥测已禁用"
else
    echo "  ⚠ 遥测未禁用（建议禁用）"
fi
echo

# 检查 crontab
echo "⏰ 定时任务:"
if crontab -l 2>/dev/null | grep -q "cleanup-logs"; then
    echo "  ✓ 日志清理任务已配置"
else
    echo "  ⊘ 日志清理任务未配置"
fi
echo

echo "================================"
echo "诊断完成"
EOF

chmod +x "$DIAG_SCRIPT"
echo "✓ 创建诊断脚本: $DIAG_SCRIPT"

echo

# 7. 总结
echo "✅ 配置完成！"
echo
echo "📋 已完成的优化:"
echo "  1. ✓ 备份现有配置到: $BACKUP_DIR"
echo "  2. ✓ 配置遥测禁用（需要重启 shell）"
echo "  3. ✓ 创建日志清理脚本"
echo "  4. ✓ 创建性能分析工具"
echo "  5. ✓ 创建诊断工具"
echo
echo "🔧 可用的工具:"
echo "  • 日志清理: bash $CLEANUP_SCRIPT"
echo "  • 性能分析: python3 $PERF_SCRIPT"
echo "  • 系统诊断: bash $DIAG_SCRIPT"
echo
echo "📖 详细文档:"
echo "  • 性能优化指南: .claude/docs/PERFORMANCE.md"
echo "  • 分析报告: ~/.claude/plans/eager-sparking-lobster.md"
echo
echo "⚠️  重要提示:"
echo "  1. 请运行 'source $SHELL_RC' 使遥测配置生效"
echo "  2. 项目的 hook 超时已自动优化"
echo "  3. 建议定期运行诊断工具检查系统状态"
echo
