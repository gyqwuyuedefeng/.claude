#!/bin/bash
# Hooks 系统验证脚本
# 用于快速测试所有 hooks 是否正常工作

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ENFORCER="$SCRIPT_DIR/workflow_enforcer.py"

echo "========================================="
echo "  Hooks 系统验证脚本"
echo "========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数器
PASSED=0
FAILED=0

# 测试函数
test_hook() {
    local test_name="$1"
    local command="$2"
    local expected="$3"

    echo -n "测试: $test_name ... "

    if output=$(eval "$command" 2>&1); then
        if [ -n "$expected" ]; then
            if echo "$output" | grep -q "$expected"; then
                echo -e "${GREEN}✓ 通过${NC}"
                ((PASSED++))
            else
                echo -e "${RED}✗ 失败${NC}"
                echo "  预期包含: $expected"
                echo "  实际输出: $output"
                ((FAILED++))
            fi
        else
            # 预期无输出
            if [ -z "$output" ]; then
                echo -e "${GREEN}✓ 通过${NC}"
                ((PASSED++))
            else
                echo -e "${RED}✗ 失败${NC}"
                echo "  预期: 无输出"
                echo "  实际输出: $output"
                ((FAILED++))
            fi
        fi
    else
        echo -e "${RED}✗ 失败（执行错误）${NC}"
        echo "  错误: $output"
        ((FAILED++))
    fi
}

# 1. 检查文件存在
echo "===== 1. 文件完整性检查 ====="
echo ""

files=(
    "$SCRIPT_DIR/workflow_enforcer.py:核心强制执行器"
    "$SCRIPT_DIR/README.md:系统说明文档"
    "$SCRIPT_DIR/USAGE.md:使用指南"
    "$SCRIPT_DIR/IMPLEMENTATION_SUMMARY.md:实施总结"
    "$SCRIPT_DIR/../settings.json:Hook配置文件"
)

for file_info in "${files[@]}"; do
    IFS=':' read -r file desc <<< "$file_info"
    echo -n "检查 $desc ... "
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ 存在${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ 缺失${NC}"
        ((FAILED++))
    fi
done

echo ""

# 2. SessionStart Hook 测试
echo "===== 2. SessionStart Hook 测试 ====="
echo ""

test_hook "SessionStart 输出核心约束" \
    "python3 '$ENFORCER' session_start" \
    "工作流提醒"

echo ""

# 3. UserPromptSubmit Hook 测试
echo "===== 3. UserPromptSubmit Hook 测试 ====="
echo ""

# 3.1 应触发场景
test_hook "检测'实现XXX系统'" \
    "echo '{\"user_prompt\":\"实现用户认证系统\"}' | python3 '$ENFORCER' prompt_check" \
    "检测到工作流触发条件"

test_hook "检测'开发XXX功能'" \
    "echo '{\"user_prompt\":\"开发积分扣减功能\"}' | python3 '$ENFORCER' prompt_check" \
    "检测到工作流触发条件"

test_hook "检测引用.plan/文件" \
    "echo '{\"user_prompt\":\"参考 .plan/106-积分扣减系统设计与实现/plan.md\"}' | python3 '$ENFORCER' prompt_check" \
    "引用了 .plan/ 目录中的文件"

test_hook "检测多项目需求" \
    "echo '{\"user_prompt\":\"在 mall-portal 和 beilv-agent 中实现功能\"}' | python3 '$ENFORCER' prompt_check" \
    "涉及 2 个项目"

test_hook "检测复杂任务特征" \
    "echo '{\"user_prompt\":\"需要设计数据库表结构\"}' | python3 '$ENFORCER' prompt_check" \
    "复杂任务特征"

# 3.2 不应触发场景
test_hook "忽略简单修改" \
    "echo '{\"user_prompt\":\"修改 project.py 第123行的变量名\"}' | python3 '$ENFORCER' prompt_check" \
    ""

test_hook "忽略文档更新" \
    "echo '{\"user_prompt\":\"更新 README 文档\"}' | python3 '$ENFORCER' prompt_check" \
    ""

test_hook "忽略问答" \
    "echo '{\"user_prompt\":\"这段代码是干什么的？\"}' | python3 '$ENFORCER' prompt_check" \
    ""

# 3.3 用户拒绝工作流
test_hook "识别用户拒绝工作流" \
    "echo '{\"user_prompt\":\"实现用户认证功能，不要启动工作流，直接实现\"}' | python3 '$ENFORCER' prompt_check" \
    ""

echo ""

# 4. PreToolUse Hook 测试
echo "===== 4. PreToolUse Hook 测试 ====="
echo ""

test_hook "tool_gate 正常执行" \
    "echo '{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"test.py\"}}' | python3 '$ENFORCER' tool_gate" \
    ""

echo ""

# 5. Stop Hook 测试
echo "===== 5. Stop Hook 测试 ====="
echo ""

test_hook "response_check 正常执行" \
    "python3 '$ENFORCER' response_check" \
    ""

echo ""

# 6. 总结
echo "========================================="
echo "  测试总结"
echo "========================================="
echo ""
echo -e "通过: ${GREEN}$PASSED${NC}"
echo -e "失败: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ 所有测试通过！Hooks 系统工作正常。${NC}"
    echo ""
    echo "下一步操作："
    echo "1. 重启 Claude Code 会话"
    echo "2. 验证会话开始时是否显示工作流提醒"
    echo "3. 输入触发条件的需求，验证是否显示警告"
    exit 0
else
    echo -e "${RED}✗ 有测试失败，请检查上述错误信息。${NC}"
    exit 1
fi
