# 会话模板

> 这是一个会话目录结构的模板
>
> 实际使用时，复制此目录并重命名为：`{序号}-{描述}-{时间}/`

## 目录说明

- `analysis/` - 存放分析阶段的报告
- `planning/` - 存放计划阶段的文档
- `execution/` - 存放执行阶段的产物
- `workflow/` - 存放工作流元数据和日志

## 使用方法

```bash
# 复制模板创建新会话
cp -r .claude/sessions/.template .claude/sessions/001-功能描述-20251231-0930

# 或者由 workflow-orchestrator 自动创建
```

---

查看 `../README.md` 了解更多详情。
