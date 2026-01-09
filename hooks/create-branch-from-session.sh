#!/usr/bin/env bash
# create-branch-from-session.sh
# 功能: 在会话创建后自动为涉及的项目创建 git 分支
# 用法: 由 Claude Code Hook 系统自动调用(PostToolUse: Write|Bash)

set -e
set -o pipefail

# ============================================================================
# 配置和常量
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
PROJECT_CONFIG="$PROJECT_ROOT/.claude/PROJECT.md"
SESSIONS_DIR="$PROJECT_ROOT/.claude/sessions"

# 日志函数
log_info() {
    echo "ℹ️  $*" >&2
}

log_success() {
    echo "✅ $*" >&2
}

log_warn() {
    echo "⚠️  $*" >&2
}

log_error() {
    echo "❌ $*" >&2
}

# ============================================================================
# 主要功能函数
# ============================================================================

# 从 Hook 输入中提取会话ID
extract_session_id() {
    local input="$1"

    python3 -c "
import json
import sys
import re

try:
    data = json.loads('''$input''')
    tool_name = data.get('tool_name', '')

    if tool_name == 'Write':
        file_path = data.get('tool_input', {}).get('file_path', '')
        match = re.search(r'\.claude/sessions/([^/]+)/workflow/session\.md', file_path)
        if match:
            print(match.group(1))
    elif tool_name == 'Bash':
        command = data.get('tool_input', {}).get('command', '')
        match = re.search(r'\.claude/sessions/([^/]+)', command)
        if match:
            print(match.group(1))
except:
    pass
"
}

# 等待 session.md 文件创建完成
wait_for_session_md() {
    local session_md="$1"
    local max_attempts=20
    local attempt=0

    while [[ $attempt -lt $max_attempts ]]; do
        if [[ -f "$session_md" ]] && grep -q "## 涉及项目" "$session_md" 2>/dev/null; then
            return 0
        fi
        sleep 0.5
        ((attempt++))
    done

    return 1
}

# 从 session.md 提取涉及的项目列表
# 期望格式：
#   ## 涉及项目
#   1. beilv-agent-web
#   2. beilv-agent
# 注：仅支持项目名称，不支持完整路径
extract_involved_projects() {
    local session_md="$1"

    # 提取 "## 涉及项目" 到下一个 ## 之间的内容
    # 匹配项目名称（如 beilv-agent-web）或带 mall/ 前缀的名称
    awk '/## 涉及项目/,/^## [^涉]/' "$session_md" | \
        grep -oP '(?:mall/)?[a-zA-Z][a-zA-Z0-9_-]+' | \
        sed 's|^mall/||' | \
        grep -v "涉及项目\|需求分类\|需求\|类型\|复杂度" | \
        sort -u
}

# 创建分支的 Python 脚本
create_branches_python() {
    local session_id="$1"
    local involved_projects="$2"

    python3 << 'PYTHON_SCRIPT'
import yaml
import sys
import os
import subprocess
from pathlib import Path

def main():
    # 读取环境变量
    project_config = os.environ['PROJECT_CONFIG']
    session_id = os.environ['SESSION_ID']
    involved_str = os.environ.get('INVOLVED_PROJECTS', '')

    if not involved_str:
        print("📝 未找到涉及的项目列表", file=sys.stderr)
        return 0

    involved = set(involved_str.strip().split('\n'))

    # 检查配置文件
    if not os.path.exists(project_config):
        print(f"⚠️  配置文件不存在: {project_config}", file=sys.stderr)
        return 0

    # 读取配置
    try:
        with open(project_config, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ 配置文件解析失败: {e}", file=sys.stderr)
        return 1

    projects = config.get('projects', [])
    branch_format = config['branch_naming']['format']
    error_handling = config['error_handling']

    # 生成分支名
    branch_name = branch_format.format(
        prefix=config['branch_naming']['prefix'],
        session_id=session_id
    )

    print(f"\n📌 分支创建报告", file=sys.stderr)
    print(f"会话ID: {session_id}", file=sys.stderr)
    print(f"分支名: {branch_name}", file=sys.stderr)
    print(f"", file=sys.stderr)

    results = []
    has_error = False

    for project in projects:
        project_name = project['name']

        # 检查是否被禁用
        if not project.get('enabled', True):
            continue

        # 只处理涉及的项目
        if project_name not in involved:
            continue

        project_path = project['path']
        main_branch = project['main_branch']

        try:
            # 检查路径
            if not os.path.isdir(project_path):
                results.append(f"⚠️  {project_name}: 路径不存在,跳过")
                continue

            # 切换到项目目录
            os.chdir(project_path)

            # 检查是否为 git 仓库
            if not os.path.isdir('.git'):
                results.append(f"⚠️  {project_name}: 非 Git 仓库,跳过")
                continue

            # 检查工作区状态
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True
            )
            status = result.stdout if result.returncode == 0 else ''

            if status.strip():
                if error_handling['on_dirty_workspace'] == 'stop':
                    results.append(f"❌ {project_name}: 工作区有未提交更改")
                    has_error = True
                    continue
                elif error_handling['on_dirty_workspace'] == 'stash':
                    subprocess.run(['git', 'stash'], check=True, capture_output=True)
                    results.append(f"📦 {project_name}: 已暂存未提交更改")
                else:  # skip
                    results.append(f"⚠️  {project_name}: 工作区不干净,跳过")
                    continue

            # 获取当前分支
            try:
                result = subprocess.run(
                    ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                    capture_output=True,
                    text=True
                )
                current_branch = result.stdout.strip() if result.returncode == 0 else ''
                if not current_branch:
                    raise Exception("无法获取分支名")
            except:
                results.append(f"⚠️  {project_name}: 无法获取当前分支,跳过")
                continue

            # 切换到主分支
            if current_branch != main_branch:
                if error_handling['on_not_main_branch'] == 'switch':
                    try:
                        subprocess.run(
                            ['git', 'checkout', main_branch],
                            check=True,
                            capture_output=True
                        )
                        results.append(f"🔄 {project_name}: 已切换到 {main_branch}")
                    except:
                        results.append(f"❌ {project_name}: 无法切换到主分支 {main_branch}")
                        has_error = True
                        continue
                elif error_handling['on_not_main_branch'] == 'stop':
                    results.append(f"❌ {project_name}: 当前不在主分支 {main_branch}")
                    has_error = True
                    continue

            # 检查分支是否存在
            existing = subprocess.run(
                ['git', 'rev-parse', '--verify', branch_name],
                capture_output=True
            ).returncode == 0

            if existing:
                if error_handling['on_branch_exists'] == 'stop':
                    results.append(f"❌ {project_name}: 分支已存在 {branch_name}")
                    has_error = True
                    continue
                elif error_handling['on_branch_exists'] == 'force':
                    subprocess.run(
                        ['git', 'branch', '-D', branch_name],
                        check=True,
                        capture_output=True
                    )
                    results.append(f"🗑️  {project_name}: 已删除旧分支")
                else:  # skip
                    results.append(f"⚠️  {project_name}: 分支已存在,跳过")
                    continue

            # 创建新分支
            subprocess.run(
                ['git', 'checkout', '-b', branch_name],
                check=True,
                capture_output=True
            )
            results.append(f"✅ {project_name}: 已创建分支 {branch_name}")

        except subprocess.CalledProcessError as e:
            results.append(f"❌ {project_name}: Git 操作失败 - {e}")
            has_error = True
        except Exception as e:
            results.append(f"❌ {project_name}: {str(e)}")
            has_error = True

    # 输出结果
    for result in results:
        print(result, file=sys.stderr)

    print(f"\n{'='*60}", file=sys.stderr)

    return 1 if has_error else 0

if __name__ == '__main__':
    sys.exit(main())
PYTHON_SCRIPT
}

# ============================================================================
# 主执行流程
# ============================================================================

main() {
    # 1. 读取 Hook 输入
    local input
    input=$(cat)

    # 2. 提取会话ID
    local session_id
    session_id=$(extract_session_id "$input")

    if [[ -z "$session_id" ]]; then
        # 不是会话创建事件,静默退出
        exit 0
    fi

    # 3. 幂等性检查 - 使用锁文件防止并发执行
    local lock_file="/tmp/create-branch-${session_id}.lock"
    if [[ -f "$lock_file" ]]; then
        log_info "分支创建任务已在执行中,跳过重复调用"
        exit 0
    fi

    touch "$lock_file"
    trap "rm -f $lock_file" EXIT

    # 4. 等待 session.md 创建完成
    local session_md="$SESSIONS_DIR/$session_id/workflow/session.md"

    log_info "等待会话文件创建: $session_id"

    if ! wait_for_session_md "$session_md"; then
        log_warn "会话文件创建超时或格式不完整,跳过分支创建"
        exit 0
    fi

    log_success "会话文件已就绪"

    # 5. 检查配置文件
    if [[ ! -f "$PROJECT_CONFIG" ]]; then
        log_warn "配置文件不存在: $PROJECT_CONFIG"
        log_info "请创建配置文件或参考 mall/PROJECT.md.example"
        exit 0
    fi

    # 6. 提取涉及的项目
    local involved_projects
    involved_projects=$(extract_involved_projects "$session_md")

    if [[ -z "$involved_projects" ]]; then
        log_info "session.md 中未列出涉及的项目,跳过分支创建"
        exit 0
    fi

    log_info "涉及的项目:"
    echo "$involved_projects" | while read -r proj; do
        log_info "  - $proj"
    done

    # 7. 执行分支创建
    export PROJECT_CONFIG
    export SESSION_ID="$session_id"
    export INVOLVED_PROJECTS="$involved_projects"

    log_info "开始创建分支..."

    if create_branches_python "$session_id" "$involved_projects"; then
        log_success "分支创建完成"
        exit 0
    else
        log_error "分支创建过程中遇到错误"
        exit 1
    fi
}

# 执行主函数
main "$@"
