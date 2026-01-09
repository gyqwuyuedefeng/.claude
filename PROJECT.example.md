# PROJECT.example.md - 项目配置模板
#
# 🎯 使用说明:
# 1. 复制此文件为 PROJECT.md:
#    cp PROJECT.example.md PROJECT.md
# 2. 修改 projects 列表中的项目路径、名称、主分支
# 3. 调整 error_handling 和 options 配置
# 4. 验证 YAML 格式:
#    python3 -c "import yaml; yaml.safe_load(open('PROJECT.md'))"
#
# ⚠️ 注意事项:
# - 所有路径必须使用绝对路径
# - main_branch 必须与实际 git 仓库的默认分支一致
# - 可以使用 enabled: false 临时禁用某个项目
# - 建议将 PROJECT.md 加入 .gitignore（如果每个开发者路径不同）
#
# 📦 此框架为通用多代理协同开发框架，可用于任何项目
# 更新时间: 2026-01-09

version: "1.0"
updated: "2026-01-09"

# ============================================================================
# 项目列表配置
# ============================================================================
# 定义所有需要管理的 Git 项目

projects:
  # 示例项目 1 - 后端服务
  - name: example-backend          # 项目名称（必填）- 用于在会话中识别项目
    path: /path/to/your/backend    # 项目绝对路径（必填）- 必须是 git 仓库根目录
    main_branch: main              # 主分支名称（必填）- 可能是 main/master/develop
    type: backend                  # 项目类型（可选）- backend/frontend/devops/mobile
    description: 示例后端服务       # 项目描述（可选）- 便于团队理解
    remote: git@github.com:user/repo.git  # 远程仓库（可选）- 用于文档记录
    enabled: true                  # 是否启用（可选，默认true）- false 则跳过此项目

  # 示例项目 2 - 前端应用
  - name: example-frontend
    path: /path/to/your/frontend
    main_branch: main
    type: frontend
    description: 示例前端应用

  # 示例项目 3 - 移动端应用
  - name: example-mobile
    path: /path/to/your/mobile
    main_branch: develop           # 注意：某些项目可能使用 develop 作为主分支
    type: mobile
    description: 示例移动端应用

  # 示例项目 4 - 部署配置（可禁用）
  - name: example-deploy
    path: /path/to/your/deploy
    main_branch: main
    type: devops
    description: 部署配置和脚本
    enabled: false                 # 临时禁用此项目

# ============================================================================
# 分支命名规则
# ============================================================================
# 定义自动创建的分支命名格式

branch_naming:
  prefix: session              # 分支前缀，可改为 feature、task、hotfix 等
  format: "{prefix}/{session_id}"  # 格式模板，支持变量: {prefix}, {session_id}
  #
  # 生成示例:
  # - 会话ID: 001-用户认证-20260109-1234
  # - 分支名: session/001-用户认证-20260109-1234
  #
  # 其他格式示例:
  # - "{prefix}-{session_id}"  → session-001-用户认证-20260109-1234
  # - "work/{session_id}"      → work/001-用户认证-20260109-1234

# ============================================================================
# 错误处理策略
# ============================================================================
# 定义遇到各种错误情况时的处理方式（根据团队规范调整）

error_handling:
  # 分支已存在时的处理方式
  on_branch_exists: stop
  # - stop: 报错并停止（推荐，防止意外覆盖）
  # - skip: 跳过该项目，继续处理其他项目
  # - force: 强制删除旧分支并重建（危险，慎用）

  # 工作区有未提交更改时的处理方式
  on_dirty_workspace: stop
  # - stop: 报错并停止（推荐，避免丢失代码）
  # - stash: 自动暂存更改（需谨慎，可能影响工作状态）
  # - skip: 跳过该项目，继续处理其他项目

  # 当前不在主分支时的处理方式
  on_not_main_branch: switch
  # - switch: 自动切换到主分支（推荐）
  # - stop: 报错并停止
  # - skip: 在当前分支基础上创建新分支

# ============================================================================
# 可选配置
# ============================================================================
# 高级功能配置选项

options:
  dry_run: false              # true: 仅预览操作，不实际执行（用于测试）
  auto_push: false            # true: 创建分支后自动推送到远程
  verbose: true               # true: 输出详细日志
  skip_pull: false            # true: 切换到主分支后不拉取最新代码

# ============================================================================
# 使用示例
# ============================================================================
#
# 1. 初次配置:
#    cp PROJECT.example.md PROJECT.md
#    # 编辑 PROJECT.md，填入实际项目信息
#
# 2. 验证配置:
#    python3 -c "import yaml; yaml.safe_load(open('PROJECT.md'))"
#
# 3. 测试分支创建:
#    # 创建测试会话，查看是否自动创建分支
#
# 4. 迁移到其他项目:
#    # 复制整个 .claude/ 目录到新项目
#    # 修改 PROJECT.md 中的项目路径
#
# ============================================================================
# 字段说明总结
# ============================================================================
#
# projects[].name          项目唯一标识名称
# projects[].path          项目绝对路径（必须是git仓库）
# projects[].main_branch   主分支名称（main/master/develop等）
# projects[].type          项目类型标签
# projects[].description   项目描述
# projects[].remote        远程仓库URL
# projects[].enabled       是否启用（true/false）
#
# branch_naming.prefix     分支名称前缀
# branch_naming.format     分支命名格式模板
#
# error_handling.*         各种错误情况的处理策略
# options.*                功能开关配置
#
# ============================================================================
