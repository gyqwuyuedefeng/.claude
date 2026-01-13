# 性能优化工具使用指南

## 快速开始

### 1. 运行自动优化脚本

```bash
cd /mnt/d/software/beilv-agent
bash .claude/scripts/optimize.sh
```

这个脚本会自动：
- 备份现有配置
- 配置遥测禁用
- 创建日志清理脚本
- 安装性能监控工具
- 创建诊断工具

### 2. 手动应用优化

如果自动脚本无法运行，可以手动执行以下步骤：

#### 禁用遥测（最重要）

在 `~/.bashrc` 或 `~/.zshrc` 中添加：

```bash
export ANTHROPIC_DISABLE_TELEMETRY=1
```

然后重新加载配置：

```bash
source ~/.bashrc  # 或 source ~/.zshrc
```

#### 配置日志清理

创建清理脚本 `~/.claude/cleanup-logs.sh`:

```bash
#!/bin/bash
LOG_DIR="$HOME/.claude/debug"
MAX_SIZE_MB=100

SIZE=$(du -sm "$LOG_DIR" 2>/dev/null | cut -f1)
if [ $SIZE -gt $MAX_SIZE_MB ]; then
    find "$LOG_DIR" -name "*.txt" -mtime +7 -delete
fi
```

添加到 crontab（每天凌晨2点执行）:

```bash
crontab -e
# 添加以下行
0 2 * * * bash ~/.claude/cleanup-logs.sh
```

## 可用工具

### 诊断工具

检查系统状态和配置：

```bash
bash .claude/scripts/diagnose.sh
```

输出示例：
```
🔍 Claude Code 诊断报告
================================

📁 配置文件:
  全局配置: ✓ 存在
  用户配置: ✓ 存在

📊 日志统计:
  日志目录大小: 2.3M
  日志文件数量: 5

🚨 最近的错误 (最近10条):
  [ERROR] 1P event logging: 29 events failed to export
  ...

⚙️  遥测配置:
  ✓ 遥测已禁用

⏰ 定时任务:
  ✓ 日志清理任务已配置
```

### 性能分析工具

分析性能日志（需要先收集性能数据）：

```bash
python3 ~/.claude/scripts/analyze-performance.py
```

### 日志清理工具

手动清理日志：

```bash
bash ~/.claude/cleanup-logs.sh
```

## 验证优化效果

### 1. 检查遥测是否禁用

```bash
echo $ANTHROPIC_DISABLE_TELEMETRY
# 应该输出: 1
```

### 2. 检查 hook 超时配置

```bash
cat .claude/settings.json | grep timeout
```

应该看到：
```json
"timeout": 15,  // validate-subagent
"timeout": 10,  // update-progress, track-file, capture-approval
"timeout": 90,  // create-branch-from-session
```

### 3. 运行诊断

```bash
bash .claude/scripts/diagnose.sh
```

## 预期改进效果

实施优化后，你应该看到：

1. **错误日志减少 50%+**
   - 遥测错误（873次）将消失
   - 超时错误显著减少

2. **日志更清晰**
   - 噪音减少，更容易定位问题
   - 日志大小可控

3. **性能提升**
   - Hook 执行更稳定
   - 减少因超时导致的重试

## 监控和维护

### 定期检查

建议每周运行一次诊断：

```bash
bash .claude/scripts/diagnose.sh
```

### 查看日志大小

```bash
du -sh ~/.claude/debug
```

### 手动清理旧日志

```bash
# 删除7天前的日志
find ~/.claude/debug -name "*.txt" -mtime +7 -delete
```

## 故障排除

### 问题：遥测错误仍然出现

**解决方案**:
1. 确认环境变量已设置: `echo $ANTHROPIC_DISABLE_TELEMETRY`
2. 重启 Claude Code CLI
3. 如果仍然出现，这些错误不影响功能，可以忽略

### 问题：Hook 超时

**解决方案**:
1. 检查 `.claude/settings.json` 中的超时配置
2. 根据实际情况增加超时时间
3. 检查 hook 脚本是否有性能问题

### 问题：日志目录过大

**解决方案**:
1. 运行清理脚本: `bash ~/.claude/cleanup-logs.sh`
2. 手动删除旧日志: `find ~/.claude/debug -name "*.txt" -mtime +30 -delete`
3. 配置 crontab 自动清理

## 参考文档

- [性能优化指南](./PERFORMANCE.md) - 详细的优化说明
- [分析报告](~/.claude/plans/eager-sparking-lobster.md) - 完整的日志分析报告

## 支持

如果遇到问题：
1. 运行诊断工具获取系统状态
2. 查看最新的 debug 日志
3. 检查 hook 脚本的输出

## 更新日志

- 2026-01-13: 初始版本
  - 优化 hook 超时配置
  - 创建自动化优化脚本
  - 添加诊断和监控工具
