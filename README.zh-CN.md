# Custom Robo GX 简体中文本地化工具链

[English README](README.md)

**本项目基于 Ganenis 的 [Custom Robo GX Full English V1.0.1 英文本地化项目](https://github.com/Ganenis/Custom-Robo-GX-English)，进一步实现简体中文本地化。英文项目的开发与翻译成果归 Ganenis。** 日文是翻译依据，英文是技术底版和语言参考。

本工具包包含中文目标译文、原文位置索引、文本抽取/回写、字体与图片编译、ARM/Thumb 显示修复和有界验证工具。主线、主要通关后及所有界面尚未完整验收，三项最新 UI 修复仍待用户体验确认。目录中的 stage 编号是兼容历史模块的名称，不代表当前执行计划。

## 1. 安装并打开工具包

解压源码 ZIP，在终端进入其中的 `custom-robo-gx-zh` 目录。也可克隆公开仓库：`git clone https://github.com/GT0698/custom-robo-gx-zh-toolkit.git custom-robo-gx-zh`。以下命令均在该目录运行。需要 Python 3.9+ 和支持 `armv4t-none-eabi` 的 Clang；核心构建使用 Python 标准库。Pillow 仅用于可选离线图片预览。构建不需要 API Key、付费模型或模拟器。

### macOS

未安装 Apple 命令行工具时先运行：

```sh
xcode-select --install
```

完成弹出的安装流程后再继续。如果没有 Python 3.9+，从 [python.org](https://www.python.org/downloads/) 安装。随后：

```sh
cd /path/to/custom-robo-gx-zh
python3 --version
clang --version
python3 -m venv .venv
. .venv/bin/activate
```

### Ubuntu / Debian Linux

```sh
sudo apt-get update
sudo apt-get install -y python3 python3-venv clang
cd /path/to/custom-robo-gx-zh
python3 --version
clang --version
python3 -m venv .venv
. .venv/bin/activate
```

确认 Python 版本至少为 3.9。Windows 用户可在 WSL 的 Ubuntu 中执行 Linux 命令；原生 Windows 构建尚未验证。参考版重建是在 macOS 完成的，Linux 安装步骤不代表已完成独立 Linux 构建验收。

检查编译器目标并运行不需要 ROM 的检查：

```sh
mkdir -p .build
printf 'int probe(void) { return 0; }\n' > .build/clang-probe.c
clang --target=armv4t-none-eabi -mthumb -c .build/clang-probe.c -o .build/clang-probe.o
python3 tests/run.py
python3 scripts/verify_public.py
```

需要离线图片预览依赖时再安装：

```sh
python3 -m pip install -r requirements.txt
```

以后打开新终端，进入项目目录并重新运行 `. .venv/bin/activate`。下文 `/path/to/...` 均需换成你自己的路径；有空格的路径保留引号。输入文件放在公开源码目录之外。

## 2. 构建现成中文版

需要准确匹配的输入：

| 输入 | 必须匹配的 SHA-1 |
|---|---|
| 自备日版 ROM | `0b5ce051aa1fd83ab0ec79122b07b02bb41096a5` |
| 使用英文 ROM 代替 BPS 时的英文 V1.0.1 ROM | `e033251c780dbbd83b15623159b743d2e624d8a0` |

从 [Ganenis 的 Releases](https://github.com/Ganenis/Custom-Robo-GX-English/releases) 获取英文 **V1.0.1 BPS**，解压后指定 `.bps` 文件，不能传入 ZIP。本工具包不附带 ROM 或英文补丁。

推荐构建命令：

```sh
python3 scripts/build.py \
  --japanese-rom "/path/to/japanese.gba" \
  --english-bps "/path/to/english-v1.0.1.bps" \
  --verify-reference
```

已有准确的英文 V1.0.1 ROM 时：

```sh
python3 scripts/build.py \
  --japanese-rom "/path/to/japanese.gba" \
  --english-rom "/path/to/english-v1.0.1.gba" \
  --verify-reference
```

参考中文版 SHA-1 为 `4816ac49f58e5e3648e018b976de3ed50451b30c`，独立源码工具包已逐字节重建出此版本。`--verify-reference` 用于未修改的中文参考版；修改译文、字体或源码后不要加这个参数。

默认生成：

- `.build/artifacts/custom-robo-gx-zh.gba`：本机游戏，可用 GBA 模拟器打开。
- `.build/artifacts/custom-robo-gx-zh.bps`：**英文 V1.0.1 → 中文版**的补丁。
- `.build/artifacts/custom-robo-gx-zh.manifest.json`：输入/输出哈希、统计和补丁回放结果。
- `.build/artifacts/reports/`：生成的工程报告。

构建器先校验版本，再从本机 ROM 重建原文目录、审计译文、编译文本/字库/显示钩子/图片，并检查 BPS 能准确重建目标 ROM。完整日英原文不随源码分发，`.build/` 保持私有。

补丁顺序为 **日版 → 英文 V1.0.1 → 中文/其他语言 BPS**。目标 BPS 不能直接用于日版，也不能叠加到旧中文版；生成的 `.gba` 已包含全部修改。保留普通存档备份，不要跨 ROM 版本载入旧即时状态。

## 3. 制作其他语言版

### A. 为导出目录生成英文 ROM

导出器只接受英文 ROM，不接受 BPS。如果目前只有英文 BPS，先在私有目录生成一次英文底版：

```sh
mkdir -p .build/inputs
python3 src/tools/bps.py \
  "/path/to/japanese.gba" \
  "/path/to/english-v1.0.1.bps" \
  .build/inputs/english-v1.0.1.gba
```

BPS 工具检查 CRC 并拒绝覆盖已有输出；后续导出器会检查日英 ROM 的 SHA-1。如果已有准确英文 ROM，下文用它的路径替换 `.build/inputs/english-v1.0.1.gba`。

### B. 创建语言包并导出翻译表

下面以法语 `fr` 为例，可将所有 `fr` 一致替换为你的语言标签：

```sh
python3 scripts/new_locale.py fr
python3 scripts/export_catalog.py \
  --japanese-rom "/path/to/japanese.gba" \
  --english-rom .build/inputs/english-v1.0.1.gba \
  --translations locales/fr \
  --output .build/catalogs-fr
```

生成 `locales/fr/` 及三个私有 UTF-8 CSV：`dialogue.csv`、`native.csv`、`offbank.csv`。新语言包是**中文译文副本，不是自动翻译好的法语版**。CSV 列为 `id`、`source_offset`、`ja`、`en_reference`、`target`。仅编辑 `target`；保留 ID、行、CSV 引号、占位符与控制符。日文为依据。剧情的 `en_reference` 刻意留空，因为日英 ROM 相同地址并不能证明文本对应。

原文 CSV 不要提交到公开仓库。编辑后仅导入目标译文：

```sh
python3 scripts/import_catalog.py --pack locales/fr --kind dialogue --csv .build/catalogs-fr/dialogue.csv
python3 scripts/import_catalog.py --pack locales/fr --kind native --csv .build/catalogs-fr/native.csv
python3 scripts/import_catalog.py --pack locales/fr --kind offbank --csv .build/catalogs-fr/offbank.csv
```

空 `target` 会跳过并保留旧值；未知或重复 ID 会报错。其他语言也保留文件名 `*.zh.json` 和目标字段 `zh`，它们是历史接口，不能单独改名。复制过来的术语表和 `locale.json` 需另外整理，CSV 导入不会更新它们。

### C. 构建语言包

```sh
python3 scripts/build.py \
  --japanese-rom "/path/to/japanese.gba" \
  --english-rom .build/inputs/english-v1.0.1.gba \
  --translations locales/fr \
  --output .build/artifacts-fr/custom-robo-gx-fr.gba
```

需要自备兼容、具有相应许可的 12px BDF 字体时：

```sh
python3 scripts/build.py \
  --japanese-rom "/path/to/japanese.gba" \
  --english-rom .build/inputs/english-v1.0.1.gba \
  --translations locales/fr \
  --font "/path/to/compatible-12px.bdf" \
  --output .build/artifacts-fr-v2/custom-robo-gx-fr.gba
```

输出沿用指定文件的名字，产生 `.gba`、`.bps`、`.manifest.json` 和同目录 `reports/`。每个修改版使用新的输出目录/版本；已有 ROM 字节不同则拒绝覆盖。语言包创建和目录导出也拒绝已有目标，重复导出时用新的目录名。

## 4. 其他语言仍需自行适配什么

| 部分 | 需要做的工作 |
|---|---|
| 文本与术语 | 替换全部中文目标值和术语；保留控制符、玩家名占位符、资源/物品身份及真实密码。部分翻译构建仍会混有中文。 |
| 字体与编码 | 确认目标字形齐全。ASCII 步进 6px，非 ASCII 当前按两个 6px 半字组成 12px 整字，置于 16 行容器。Native 容量为 2932 个自定义逻辑字符。更宽字形、组合字符、复杂连写和从右向左文字需要改渲染器/编码。 |
| 换行与字段 | 重新核对框宽、缓冲容量、缩写、对齐和行数。中文整字换行不等于拉丁语言按单词换行。不要全局放宽缓冲或后台身份规则。 |
| 固定 UI 文案 | 修改 `src/stage3/build_chapter1.py` 及 `src/stage4/build_redirect.py` 中辅助标签；CSV 不覆盖所有常量。 |
| 图片文字 | 检查 `src/stage5/*_assets.py`、`equipment_model_labels.py` 和 `league_graphics.py`。有些标题/位图硬编码中文并具有固定尺寸，单改语言包不会替换它们。保持调色板、图块、指针与内存分配无冲突。 |
| 验证与验收 | 运行源码/目录/构建检查，对改动的渲染路径选代表性有界函数探针；不能把工程检查当作主线、奖励和通关后体验验收，应另收集用户反馈。 |
| 发布 | 保留英文底版、中文工具链来源与字体许可；确定适用授权后分发审核过的源码/补丁，排除 ROM、存档、原文目录及个人配置。 |

详细机制见[本地化指南](docs/LOCALIZATION_GUIDE.md)、[架构](docs/ARCHITECTURE.md)、[测试](docs/TESTING.md)和[验证](docs/VERIFICATION.md)。可选 mGBA 探针需要自行构建匹配的 mGBA 库，不是构建 ROM 的必需步骤，也不自动游玩。

## 5. 检查、报错与许可状态

```sh
python3 tests/run.py
python3 scripts/verify_public.py
```

- `Wrong Japanese ROM` / `English input must beV1.0.1`：输入版本错误，核对哈希，不要绕过校验。
- Clang 目标报错：确认 PATH 中的 `clang` 能完成安装章节中的目标编译检查。
- 缺字、控制符或长度审计失败：修改字体、译文或经过审计的布局，不要关闭检查。
- `Reference build differs`：只对未修改的参考译文、字体和代码使用 `--verify-reference`。
- 输出/目录/语言包已存在：换新路径，保留此前工作。

CI 仅运行无需 ROM 的源码隐私检查和 BPS/输入解码测试，不代表游戏验收。贡献约束见 [CONTRIBUTING](CONTRIBUTING.md)。

源码包不含 ROM、存档、即时状态、用户截图、聊天/会话、个人路径、凭据或本机模型配置。生成的原文和构建报告保留在私有目录。

**项目自有工具和技术文档采用 MIT**，该许可不覆盖第三方或游戏衍生内容。字体保持 OFL-1.1 与原有来源许可；实验版译文不等于给原游戏或英文成果授予 MIT/CC 许可。本项目以非商业实验和知识分享为目的，这不额外限制 MIT 工具的复用，也不授权分发 ROM。详细范围见[许可说明](LICENSE_STATUS.md)及[来源署名](CREDITS.md)。
