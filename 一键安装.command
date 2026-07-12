#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

APP_ID=8930
DEPOTS=(235586 16870 235580)
DEFAULT_CONTENT="$HOME/Library/Application Support/Steam/Steam.AppBundle/Steam/Contents/MacOS/steamapps/content/app_8930"
STEAM_CONTENT="${CIV5_STEAM_CONTENT:-$DEFAULT_CONTENT}"
GAME_APP="$HOME/Library/Application Support/Steam/steamapps/common/Sid Meier's Civilization V/Civilization V.app"

pause_on_error() {
  printf '\n安装没有完成。按回车关闭窗口。'
  read -r _
}
trap pause_on_error ERR

printf '%s\n' '=== 文明 V macOS 简体中文补丁 ==='

if [[ "$(uname -s)" != "Darwin" ]]; then
  printf '%s\n' '错误：当前工具仅支持 macOS。'
  exit 1
fi

if [[ ! -d "$GAME_APP" ]]; then
  printf '%s\n' '错误：没有在默认 Steam 目录找到 Civilization V.app。'
  printf '实际位置不同的话，请参照 README 使用 --game 参数手动安装。\n'
  exit 1
fi

if pgrep -f 'Civilization V.app' >/dev/null 2>&1; then
  printf '%s\n' '错误：文明 V 正在运行，请完全退出游戏后重试。'
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  printf '%s\n' '错误：没有找到 Python 3。请先安装 Python 3.11 或更高版本。'
  printf '%s\n' '下载地址：https://www.python.org/downloads/macos/'
  exit 1
fi

PYTHON_VERSION="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
if ! python3 -c 'import sys; raise SystemExit(sys.version_info < (3, 11))'; then
  printf '错误：当前 Python 为 %s，需要 3.11 或更高版本。\n' "$PYTHON_VERSION"
  exit 1
fi

missing=()
for depot in "${DEPOTS[@]}"; do
  [[ -d "$STEAM_CONTENT/depot_$depot" ]] || missing+=("$depot")
done

if (( ${#missing[@]} > 0 )); then
  commands='download_depot 8930 235586
download_depot 8930 16870
download_depot 8930 235580'
  printf '%s' "$commands" | pbcopy
  open 'steam://nav/console'
  printf '\n缺少官方中文 depot：%s\n' "${missing[*]}"
  printf '%s\n' 'Steam 控制台已打开，三条下载命令也已复制到剪贴板。'
  printf '%s\n' '请每次粘贴一行并按回车，等到 Depot download complete 再执行下一行。'
  printf '%s\n' '全部下载完成后，回到这个窗口按回车继续。'
  read -r _
  for depot in "${DEPOTS[@]}"; do
    if [[ ! -d "$STEAM_CONTENT/depot_$depot" ]]; then
      printf '错误：仍未找到 depot_%s：%s\n' "$depot" "$STEAM_CONTENT"
      exit 1
    fi
  done
fi

printf '\n[1/3] 创建独立 Python 环境并安装依赖...\n'
if [[ ! -x .venv/bin/python ]]; then
  python3 -m venv .venv
fi
PIP_INDEX_URL="${PIP_INDEX_URL:-https://mirrors.aliyun.com/pypi/simple/}" \
  .venv/bin/python -m pip install --disable-pip-version-check -r requirements.txt

printf '\n[2/3] 从本人 Steam 文件生成简体中文补丁...\n'
.venv/bin/python build_patch.py --steam-root "$STEAM_CONTENT"

printf '\n[3/3] 备份原文件并安装补丁...\n'
.venv/bin/python install_patch.py --game "$GAME_APP"

trap - ERR
printf '\n%s\n' '安装完成。现在可以从 Steam 启动文明 V。'
printf '%s\n' '如需恢复英文原版，请双击“一键恢复.command”。'
printf '%s' '按回车关闭窗口。'
read -r _
