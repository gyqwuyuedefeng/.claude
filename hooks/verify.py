#!/usr/bin/env python3
"""
Hooks 系统验证脚本
用于快速测试所有 hooks 是否正常工作
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# 颜色定义
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

class HooksVerifier:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.enforcer = self.script_dir / "workflow_enforcer.py"
        self.passed = 0
        self.failed = 0

    def print_header(self, title):
        print(f"\n{'='*50}")
        print(f"  {title}")
        print(f"{'='*50}\n")

    def print_section(self, title):
        print(f"\n{'='*5} {title} {'='*5}\n")

    def check_file(self, file_path, description):
        """检查文件是否存在"""
        print(f"检查 {description} ... ", end="")
        if file_path.exists():
            print(f"{Colors.GREEN}✓ 存在{Colors.NC}")
            self.passed += 1
            return True
        else:
            print(f"{Colors.RED}✗ 缺失{Colors.NC}")
            self.failed += 1
            return False

    def test_hook(self, test_name, command, input_data=None, expected=None):
        """测试 hook 功能"""
        print(f"测试: {test_name} ... ", end="")

        try:
            if input_data:
                # 通过 stdin 传递 JSON 数据
                result = subprocess.run(
                    ["python3", str(self.enforcer)] + command,
                    input=json.dumps(input_data),
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            else:
                # 不需要 stdin
                result = subprocess.run(
                    ["python3", str(self.enforcer)] + command,
                    capture_output=True,
                    text=True,
                    timeout=5
                )

            output = result.stdout.strip()

            if expected:
                # 预期有特定输出
                if expected in output:
                    print(f"{Colors.GREEN}✓ 通过{Colors.NC}")
                    self.passed += 1
                else:
                    print(f"{Colors.RED}✗ 失败{Colors.NC}")
                    print(f"  预期包含: {expected}")
                    print(f"  实际输出: {output[:200]}")
                    self.failed += 1
            else:
                # 预期无输出
                if not output:
                    print(f"{Colors.GREEN}✓ 通过{Colors.NC}")
                    self.passed += 1
                else:
                    print(f"{Colors.RED}✗ 失败{Colors.NC}")
                    print(f"  预期: 无输出")
                    print(f"  实际输出: {output[:200]}")
                    self.failed += 1

        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}✗ 失败（超时）{Colors.NC}")
            self.failed += 1
        except Exception as e:
            print(f"{Colors.RED}✗ 失败（异常）{Colors.NC}")
            print(f"  错误: {e}")
            self.failed += 1

    def verify(self):
        """执行所有验证"""
        self.print_header("Hooks 系统验证脚本")

        # 1. 文件完整性检查
        self.print_section("1. 文件完整性检查")

        files = [
            (self.script_dir / "workflow_enforcer.py", "核心强制执行器"),
            (self.script_dir / "README.md", "系统说明文档"),
            (self.script_dir / "USAGE.md", "使用指南"),
            (self.script_dir / "IMPLEMENTATION_SUMMARY.md", "实施总结"),
            (self.script_dir.parent / "settings.json", "Hook配置文件"),
        ]

        for file_path, description in files:
            self.check_file(file_path, description)

        # 2. SessionStart Hook 测试
        self.print_section("2. SessionStart Hook 测试")

        self.test_hook(
            "SessionStart 输出核心约束",
            ["session_start"],
            expected="工作流提醒"
        )

        # 3. UserPromptSubmit Hook 测试
        self.print_section("3. UserPromptSubmit Hook 测试")

        # 3.1 应触发场景
        self.test_hook(
            "检测'实现XXX系统'",
            ["prompt_check"],
            input_data={"user_prompt": "实现用户认证系统"},
            expected="检测到工作流触发条件"
        )

        self.test_hook(
            "检测'开发XXX功能'",
            ["prompt_check"],
            input_data={"user_prompt": "开发积分扣减功能"},
            expected="检测到工作流触发条件"
        )

        self.test_hook(
            "检测引用.plan/文件",
            ["prompt_check"],
            input_data={"user_prompt": "参考 .plan/106-积分扣减系统设计与实现/plan.md"},
            expected="引用了 .plan/ 目录中的文件"
        )

        self.test_hook(
            "检测多项目需求",
            ["prompt_check"],
            input_data={"user_prompt": "在 project-a 和 project-b 中实现功能"},
            expected="涉及 2 个项目"
        )

        self.test_hook(
            "检测复杂任务特征",
            ["prompt_check"],
            input_data={"user_prompt": "需要设计数据库表结构"},
            expected="复杂任务特征"
        )

        # 3.2 不应触发场景
        self.test_hook(
            "忽略简单修改",
            ["prompt_check"],
            input_data={"user_prompt": "修改 project.py 第123行的变量名"},
            expected=None
        )

        self.test_hook(
            "忽略文档更新",
            ["prompt_check"],
            input_data={"user_prompt": "更新 README 文档"},
            expected=None
        )

        self.test_hook(
            "忽略问答",
            ["prompt_check"],
            input_data={"user_prompt": "这段代码是干什么的？"},
            expected=None
        )

        # 3.3 用户拒绝工作流
        self.test_hook(
            "识别用户拒绝工作流",
            ["prompt_check"],
            input_data={"user_prompt": "实现用户认证功能，不要启动工作流，直接实现"},
            expected=None
        )

        # 4. PreToolUse Hook 测试
        self.print_section("4. PreToolUse Hook 测试")

        self.test_hook(
            "tool_gate 正常执行",
            ["tool_gate"],
            input_data={"tool_name": "Write", "tool_input": {"file_path": "test.py"}},
            expected=None
        )

        # 5. Stop Hook 测试
        self.print_section("5. Stop Hook 测试")

        self.test_hook(
            "response_check 正常执行",
            ["response_check"],
            expected=None
        )

        # 6. 总结
        self.print_header("测试总结")

        print(f"通过: {Colors.GREEN}{self.passed}{Colors.NC}")
        print(f"失败: {Colors.RED}{self.failed}{Colors.NC}\n")

        if self.failed == 0:
            print(f"{Colors.GREEN}✓ 所有测试通过！Hooks 系统工作正常。{Colors.NC}\n")
            print("下一步操作：")
            print("1. 重启 Claude Code 会话")
            print("2. 验证会话开始时是否显示工作流提醒")
            print("3. 输入触发条件的需求，验证是否显示警告")
            return 0
        else:
            print(f"{Colors.RED}✗ 有测试失败，请检查上述错误信息。{Colors.NC}")
            return 1

def main():
    verifier = HooksVerifier()
    exit_code = verifier.verify()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
