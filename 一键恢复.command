#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

printf '%s\n' '=== 恢复文明 V 英文原版文件 ==='
if pgrep -f 'Civilization V.app' >/dev/null 2>&1; then
  printf '%s\n' '错误：文明 V 正在运行，请完全退出游戏后重试。'
  printf '%s' '按回车关闭窗口。'
  read -r _
  exit 1
fi

if [[ ! -x .venv/bin/python ]]; then
  printf '%s\n' '错误：没有找到项目环境，请先至少运行一次“一键安装.command”。'
  printf '%s' '按回车关闭窗口。'
  read -r _
  exit 1
fi

.venv/bin/python uninstall_patch.py
printf '\n%s\n' '恢复完成。游戏存档没有被删除。'
printf '%s' '按回车关闭窗口。'
read -r _
