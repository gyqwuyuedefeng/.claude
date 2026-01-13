# 性能优化指南

本文档基于 debug 日志分析，提供工作流性能优化建议。

## 已实施的改进

### 1. Hook 超时优化 ✅

已将所有 hook 的超时时间增加，避免因超时导致的失败：

- `validate-subagent.py`: 10s → 15s
- `update-progress.py`: 5s → 10s
- `track-file.py`: 5s → 10s
- `create-branch-from-session.sh`: 60s → 90s
- `capture-approval.py`: 5s → 10s

## 需要用户配置的优化

### 2. 禁用遥测（强烈推荐）

**问题**: 遥测事件导出失败占总错误的 46%（873次），严重污染日志。

**解决方案**: 设置环境变量禁用遥测

```bash
# 在 ~/.bashrc 或 ~/.zshrc 中添加
export ANTHROPIC_DISABLE_TELEMETRY=1

# 或者在启动 claude-code 时
ANTHROPIC_DISABLE_TELEMETRY=1 claude-code
```

**注意**: 这是 Claude Code CLI 的内部功能，目前没有官方配置选项。如果上述方法无效，可以忽略日志中的遥测错误，它们不影响实际功能。

### 3. 增加 API 超时时间

**问题**: 5秒超时导致部分请求失败。

**解决方案**: 目前 Claude Code CLI 没有提供配置 API 超时的选项。这是内部硬编码的值。

**临时方案**:
- 确保网络连接稳定
- 使用更快的 API 端点
- 如果使用代理，优化代理配置

### 4. 优化插件市场配置

**问题**: SSH 认证失败导致插件市场刷新失败。

**解决方案**: 在全局配置中禁用自动更新

编辑 `/home/gyq/.claude.json`，添加或修改：

```json
{
  "autoUpdates": false,
  "officialMarketplaceAutoInstallAttempted": true
}
```

## 工作流优化建议

### 5. 减少 API 调用频率

**当前状态**: 4小时1200次调用，平均12秒一次

**优化策略**:

1. **批量操作**: 合并多个小的文件读取/搜索操作
2. **缓存结果**: 避免重复查询相同的信息
3. **减少子代理嵌套**: 尽量在主代理中完成简单任务

### 6. 日志管理

**当前状态**: 4小时生成 2.3MB 日志

**优化方案**:

1. **定期清理**:
```bash
# 清理30天前的日志
find ~/.claude/debug -name "*.txt" -mtime +30 -delete
```

2. **日志轮转脚本**:
```bash
#!/bin/bash
# 保存为 ~/.claude/cleanup-logs.sh
LOG_DIR="$HOME/.claude/debug"
MAX_SIZE_MB=100

# 获取目录大小
SIZE=$(du -sm "$LOG_DIR" | cut -f1)

if [ $SIZE -gt $MAX_SIZE_MB ]; then
    echo "日志目录超过 ${MAX_SIZE_MB}MB，开始清理..."
    find "$LOG_DIR" -name "*.txt" -mtime +7 -delete
    echo "清理完成"
fi
```

3. **添加到 crontab**:
```bash
# 每天凌晨2点执行
0 2 * * * bash ~/.claude/cleanup-logs.sh
```

### 7. 子代理日志追踪

**问题**: 日志中缺少子代理执行的详细信息

**建议**: 在子代理脚本中添加结构化日志

示例（Python）:
```python
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(f"{os.environ['HOME']}/.claude/debug/subagent-{os.getpid()}.log"),
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger('issue-analyzer')
logger.info("子代理启动")
```

## 性能监控

### 8. 添加性能指标收集

创建 `~/.claude/hooks/performance-monitor.py`:

```python
#!/usr/bin/env python3
import json
import time
import os
from pathlib import Path

def log_performance(event_type, duration_ms, metadata=None):
    log_file = Path.home() / '.claude' / 'performance.jsonl'

    entry = {
        'timestamp': time.time(),
        'event': event_type,
        'duration_ms': duration_ms,
        'metadata': metadata or {}
    }

    with open(log_file, 'a') as f:
        f.write(json.dumps(entry) + '\n')

# 使用示例
# log_performance('api_call', 1234, {'model': 'sonnet', 'tokens': 100})
```

### 9. 性能分析脚本

创建 `~/.claude/scripts/analyze-performance.py`:

```python
#!/usr/bin/env python3
import json
from pathlib import Path
from collections import defaultdict

def analyze_performance():
    log_file = Path.home() / '.claude' / 'performance.jsonl'

    if not log_file.exists():
        print("性能日志文件不存在")
        return

    stats = defaultdict(list)

    with open(log_file) as f:
        for line in f:
            entry = json.loads(line)
            stats[entry['event']].append(entry['duration_ms'])

    print("性能统计:")
    print("-" * 50)

    for event, durations in stats.items():
        avg = sum(durations) / len(durations)
        max_dur = max(durations)
        min_dur = min(durations)

        print(f"{event}:")
        print(f"  平均: {avg:.2f}ms")
        print(f"  最大: {max_dur:.2f}ms")
        print(f"  最小: {min_dur:.2f}ms")
        print(f"  次数: {len(durations)}")
        print()

if __name__ == '__main__':
    analyze_performance()
```

## 网络优化

### 10. 使用更快的 API 端点

当前配置使用: `https://2api.letshappy.fun`

**建议**:
- 测试不同端点的延迟
- 选择地理位置最近的端点
- 考虑使用 CDN 加速

**测试脚本**:
```bash
#!/bin/bash
# 测试 API 端点延迟
ENDPOINTS=(
    "https://2api.letshappy.fun"
    "https://api.anthropic.com"
    # 添加其他端点
)

for endpoint in "${ENDPOINTS[@]}"; do
    echo "测试: $endpoint"
    time curl -s -o /dev/null -w "时间: %{time_total}s\n" "$endpoint/v1/messages" \
        -H "x-api-key: test" \
        -H "anthropic-version: 2023-06-01" \
        -d '{"model":"claude-3-haiku-20240307","max_tokens":1,"messages":[{"role":"user","content":"hi"}]}' \
        2>&1 | grep "时间"
    echo
done
```

## 总结

### 立即可执行的改进（已完成）
- ✅ 增加 hook 超时时间

### 需要用户配置（推荐）
- 🔴 禁用遥测（最高优先级）
- 🟡 禁用自动更新
- 🟡 设置日志清理计划

### 长期优化（可选）
- 🟢 添加性能监控
- 🟢 优化网络配置
- 🟢 改进子代理日志

## 预期效果

实施这些优化后，预期可以：

1. **减少错误日志 50%+**: 禁用遥测后，873次错误将消失
2. **降低超时失败**: hook 超时增加后，超时失败率降低
3. **改善日志可读性**: 减少噪音，更容易定位真正的问题
4. **提升整体性能**: 通过监控和优化，持续改进

## 参考

- 完整分析报告: `/home/gyq/.claude/plans/eager-sparking-lobster.md`
- Debug 日志: `/home/gyq/.claude/debug/cf6d7d10-802d-412c-99c1-cc00a220e207.txt`
