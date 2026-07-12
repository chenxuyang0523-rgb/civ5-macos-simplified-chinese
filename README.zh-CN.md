# 文明 V macOS 简体中文补丁构建器

这是一个非官方、开源的《文明 V》Steam macOS 版简体中文补丁构建与可回滚安装工具。

本仓库**只发布原创工具代码**，不包含或分发《文明 V》文本、2K/Firaxis/Aspyr 资源、Apple 字体或生成后的字体图集。用户必须拥有游戏及相应 DLC，由工具读取本人 Steam 可用文件并在本机生成补丁。

## 当前支持

- 已在 Steam Civ V 1.4.2、Apple Silicon、macOS 15.7.7 上验证。
- 包含本体、Gods & Kings 和 Brave New World 文本。
- 使用 OpenCC `t2s` 繁转简。
- 复用 Mac 版已有的 `zh_Hant_HK` 语言槽位。
- 从用户本机字体生成 DXT5 位图字体图集。
- 目前仅支持 macOS，不支持 Windows 或 Linux。

## 重要合规说明

你必须拥有《文明 V》以及参与构建的 DLC。生成物仅供你配合本人合法游戏副本使用。**不要传播 `dist/` 生成物**，其中会包含转换后的游戏文本及从本机字体栅格化的字形。

项目与 2K、Firaxis、Aspyr、Apple、Valve/Steam 均无隶属或背书关系。详见 [LEGAL.md](LEGAL.md) 和 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## 安装依赖

建议使用独立 Python 环境：

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## 构建

游戏所有者先通过 Steam 控制台下载所需官方语言 depot，然后运行：

```sh
python build_patch.py \
  --steam-root "$HOME/Library/Application Support/Steam/Steam.AppBundle/Steam/Contents/MacOS/steamapps/content/app_8930"
```

工具需要 depot `235586`、`16870` 和 `235580`。生成物位于 `dist/Civ5_Simplified_Chinese_Mac/`，该目录默认不会进入 Git。

也可以明确指定本机字体和 TTC 字体序号：

```sh
python build_patch.py --steam-root /path/to/app_8930 \
  --font /path/to/local/CJK-font.ttc --font-index 0
```

## 安装与恢复

关闭游戏后安装：

```sh
python install_patch.py
```

安装器会先备份被替换文件、`config.ini` 和本地化缓存。恢复最近一次备份：

```sh
python uninstall_patch.py
```

Steam 更新或验证游戏文件可能覆盖补丁，此后需要重新构建和安装。

## 反馈安全

提交问题时不要上传生成补丁、游戏文件、带个人路径的完整崩溃报告、Steam 账户信息或其他私密数据。
