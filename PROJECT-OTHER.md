# Mall 项目配置文件
# 用于管理 mall 目录下所有子项目的 Git 配置

version: "1.0"
updated: "2026-01-09"

# 项目列表
projects:
  # 核心服务
  - name: beilv-agent
    path: /mnt/d/software/beilv-agent/mall/beilv-agent
    main_branch: runninghub
    type: backend
    description: 后端主服务
    remote: git@github.com:gyq-xrateverse/beilv-agent.git

  - name: beilv-agent-web
    path: /mnt/d/software/beilv-agent/mall/beilv-agent-web
    main_branch: main
    type: frontend
    description: 前端管理界面
    remote: git@github.com:xrateverse/beilv-agent-web.git

  # 部署和基础设施
  - name: beilv-agent-deploy
    path: /mnt/d/software/beilv-agent/mall/beilv-agent-deploy
    main_branch: main  # 假设为 main,如有差异请修改
    type: devops
    description: 部署配置和基础设施

  # 商城相关项目
  - name: mall-admin-web
    path: /mnt/d/software/beilv-agent/mall/mall-admin-web
    main_branch: master  # 假设为 main,如有差异请修改
    type: frontend
    description: 商城管理后台

  # API 服务
  - name: new-api
    path: /mnt/d/software/beilv-agent/mall/new-api
    main_branch: main  # 假设为 main,如有差异请修改
    type: backend
    description: 新版API服务

  # 电商系统后端
  - name: mall
    path: /mnt/d/software/beilv-agent/mall/mall
    main_branch: master  # 当前使用 Spring Boot 3.2+JDK 17 版本
    type: backend
    description: 完整的电商系统后端服务，基于 SpringBoot+MyBatis
    remote: git@github.com:xrateverse/mall.git

# 分支命名规则
branch_naming:
  prefix: session
  format: "{prefix}/{session_id}"
  # 例如: session/001-前端Logo更新-20260109-1017

# 错误处理策略
error_handling:
  on_branch_exists: stop     # stop: 报错并停止 | skip: 跳过该项目 | force: 强制删除并重建
  on_dirty_workspace: stop   # stop: 报错并停止 | stash: 自动暂存 | skip: 跳过该项目
  on_not_main_branch: switch # switch: 自动切换到主分支 | stop: 报错并停止 | skip: 在当前分支创建

# 可选配置
options:
  dry_run: false            # true: 只输出操作计划,不实际执行
  auto_push: false          # true: 创建分支后自动推送到远程
  verbose: true             # true: 输出详细日志
  skip_pull: false          # true: 切换到主分支后不拉取最新代码

# 注意事项
# 1. 如果项目的主分支不是 main,请手动修改 main_branch 字段
# 2. 可以在项目中添加 enabled: false 来临时禁用某个项目
# 3. 执行前请确保工作区干净,避免丢失未提交的更改
# 4. 如需自定义分支命名,修改 branch_naming.format
