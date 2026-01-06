#!/bin/bash

# validate-session.sh
# 验证会话目录一致性
# 用途：检查所有会话目录的结构完整性，查找孤儿会话和重复目录

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
# 动态获取项目根目录（脚本在 .claude/scripts/ 下）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SESSION_DIR="$PROJECT_ROOT/.claude/sessions"
REQUIRED_SUBDIRS=("analysis" "planning" "execution" "workflow")

# 计数器
total_sessions=0
valid_sessions=0
invalid_sessions=0
orphan_files=0

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}会话目录一致性验证工具${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查 sessions 目录是否存在
if [ ! -d "$SESSION_DIR" ]; then
    echo -e "${RED}✗ 错误: sessions 目录不存在${NC}"
    echo -e "  路径: $SESSION_DIR"
    exit 1
fi

echo -e "${GREEN}✓${NC} sessions 目录存在: $SESSION_DIR"
echo ""

# 遍历所有会话目录
echo -e "${BLUE}检查会话目录结构...${NC}"
echo ""

for session_path in "$SESSION_DIR"/[0-9]*; do
    # 跳过非目录
    if [ ! -d "$session_path" ]; then
        continue
    fi

    session_id=$(basename "$session_path")
    total_sessions=$((total_sessions + 1))

    echo -e "${YELLOW}会话 $total_sessions:${NC} $session_id"

    # 验证 session-id 格式
    if [[ ! $session_id =~ ^[0-9]{3}-.+-[0-9]{8}-[0-9]{4}$ ]]; then
        echo -e "  ${RED}✗ 格式错误${NC}: session-id 格式不符合 NNN-描述-YYYYMMDD-HHMM"
        invalid_sessions=$((invalid_sessions + 1))
        echo ""
        continue
    fi

    session_valid=true

    # 检查必需的子目录
    for subdir in "${REQUIRED_SUBDIRS[@]}"; do
        subdir_path="$session_path/$subdir"
        if [ -d "$subdir_path" ]; then
            file_count=$(find "$subdir_path" -type f 2>/dev/null | wc -l)
            echo -e "  ${GREEN}✓${NC} $subdir/ (${file_count} 个文件)"
        else
            echo -e "  ${RED}✗${NC} $subdir/ ${RED}缺失${NC}"
            session_valid=false
        fi
    done

    # 检查关键文件
    if [ -f "$session_path/workflow/session.md" ]; then
        echo -e "  ${GREEN}✓${NC} workflow/session.md"
    else
        echo -e "  ${YELLOW}⚠${NC} workflow/session.md ${YELLOW}不存在${NC}"
    fi

    if [ -f "$session_path/workflow/progress.json" ]; then
        echo -e "  ${GREEN}✓${NC} workflow/progress.json"
    else
        echo -e "  ${YELLOW}⚠${NC} workflow/progress.json ${YELLOW}不存在（可能未到执行阶段）${NC}"
    fi

    # 统计结果
    if [ "$session_valid" = true ]; then
        valid_sessions=$((valid_sessions + 1))
    else
        invalid_sessions=$((invalid_sessions + 1))
    fi

    echo ""
done

# 检查孤儿文件（非标准目录名）
echo -e "${BLUE}检查孤儿文件和目录...${NC}"
echo ""

for item in "$SESSION_DIR"/*; do
    item_name=$(basename "$item")

    # 跳过 .template, README.md 等预期文件
    if [ "$item_name" = ".template" ] || [ "$item_name" = "README.md" ]; then
        continue
    fi

    # 检查是否符合会话ID格式
    if [[ ! $item_name =~ ^[0-9]{3}-.+-[0-9]{8}-[0-9]{4}$ ]]; then
        echo -e "  ${YELLOW}⚠${NC} 发现非标准项: $item_name"
        if [ -d "$item" ]; then
            file_count=$(find "$item" -type f 2>/dev/null | wc -l)
            echo -e "     类型: 目录 (包含 $file_count 个文件)"
        else
            echo -e "     类型: 文件"
        fi
        orphan_files=$((orphan_files + 1))
        echo ""
    fi
done

# 检查重复的会话
echo -e "${BLUE}检查重复会话（相同描述但不同时间戳）...${NC}"
echo ""

declare -A session_descs
duplicates_found=false

for session_path in "$SESSION_DIR"/[0-9]*; do
    if [ ! -d "$session_path" ]; then
        continue
    fi

    session_id=$(basename "$session_path")
    # 提取描述部分（去掉序号和时间戳）
    desc=$(echo "$session_id" | sed 's/^[0-9]\{3\}-\(.*\)-[0-9]\{8\}-[0-9]\{4\}$/\1/')

    if [ -n "${session_descs[$desc]}" ]; then
        if [ "$duplicates_found" = false ]; then
            echo -e "${YELLOW}发现可能重复的会话：${NC}"
            duplicates_found=true
        fi
        echo -e "  描述: ${YELLOW}$desc${NC}"
        echo -e "    - ${session_descs[$desc]}"
        echo -e "    - $session_id"
        echo ""
    else
        session_descs[$desc]="$session_id"
    fi
done

if [ "$duplicates_found" = false ]; then
    echo -e "${GREEN}✓${NC} 未发现重复会话"
    echo ""
fi

# 总结报告
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}验证总结${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "总会话数:       ${BLUE}$total_sessions${NC}"
echo -e "有效会话:       ${GREEN}$valid_sessions${NC}"
echo -e "无效会话:       ${RED}$invalid_sessions${NC}"
echo -e "孤儿文件/目录:  ${YELLOW}$orphan_files${NC}"
echo ""

# 退出状态
if [ $invalid_sessions -gt 0 ] || [ $orphan_files -gt 0 ]; then
    echo -e "${YELLOW}⚠ 发现问题，请检查上述报告${NC}"
    exit 1
else
    echo -e "${GREEN}✓ 所有会话目录结构正常${NC}"
    exit 0
fi
