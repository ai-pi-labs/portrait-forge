# 人像工坊 Portrait Forge

将人物需求整理为可复用角色档案，生成完整中文 Prompt；修改时只动指定字段，并检查前后差异。支持原创、固定脸换妆、同妆不同脸、角色阵容和限定范围参考图分析。

本项目是从零实现的独立 Skill 与本地工具包。它不附带图像模型；自然语言设计由宿主 Agent 完成，Python 工具负责确定性校验、修改和编译，实际生图使用宿主已有能力。

## 快速安装

从 GitHub 下载完整源码，或克隆本仓库：

```bash
git clone https://github.com/EthanYu-YW/portrait-forge.git
cd portrait-forge
```

私有仓库需要已获授权的 GitHub 账号。

下载完整项目并解压，进入本文件所在目录。Python 3.9+，无第三方依赖，无 API key：

```bash
python3 tools/install.py --dest "$HOME/.agents/skills"
```

安装结果为 `~/.agents/skills/portrait-forge/SKILL.md`。如果目标已存在，脚本拒绝覆盖；先备份自己的旧版或选择新的技能父目录。也可将 `skill/portrait-forge` 整个文件夹手动复制到该位置。项目范围安装可使用 `--dest /你的项目/.agents/skills`。安装操作仅在你执行命令时发生。

若使用独立 Skill ZIP，解压得到的 `portrait-forge` 文件夹就是要复制的技能；不要只复制 SKILL.md，也不要多套一层目录。Codex 支持这些本地技能目录，通常自动发现；未出现时重启后检查选择器。来源：[官方技能说明](https://learn.chatgpt.com/docs/build-skills)。

## 直接调用

```text
使用 $portrait-forge，设计一位圆脸、单眼皮的成年女性，宽鼻背不改，清冷但保留圆润感。
```

默认一句方向和完整中文提示词；不用填写表格。需要复用时加一句“同时保存角色档案 JSON”。

后续例子：

```text
使用 $portrait-forge，读取这份角色档案，只把唇色换成酒红，保留其他全部设定。
使用 $portrait-forge，用同一套桃粉妆设计五位不同脸的成年人，每人给完整提示词。
使用 $portrait-forge，只分析这张图的妆容，不沿用人物的脸。看不清的地方保持未知。
按刚才的方案生成图片，保留锁定项。
```

最后一句需要宿主确有图片工具；没有工具时交付 Prompt。角色档案不等于人脸识别模型，图片一致性需看实际结果。

## ChatGPT Work 与其他 Agent

支持技能选择器的 ChatGPT 环境可在技能安装后用 `@` 选择；不要假设 `$` 在每个宿主都生效。原生安装/组织分发入口由当前账户决定，本包没有进行在线安装验证。

没有原生导入入口时，可生成会话资料包：

```bash
python3 tools/export_work.py --out ../portrait-forge-work-pack
```

将其中的 `portrait-forge-knowledge.md` 提供给能读取附件的会话，再使用 START-HERE.txt 的开场指令。这是会话资料加载，不是永久 Skill 安装。无 Python 的环境可以按规则设计并人工检查，不能宣称运行过脚本。[适配边界](docs/HOSTS.md)。

## 完整项目结构

```text
portrait-forge/
├── skill/portrait-forge/       可独立安装的完整技能
│   ├── SKILL.md               任务路由、流程与交付约定
│   ├── agents/openai.yaml     宿主显示与调用元数据
│   ├── assets/                唯一字段目录与派生 JSON Schema
│   ├── references/            需求、脸部、妆摄、证据、一致性、编译规则
│   └── scripts/               命令入口及三个独立核心模块
├── examples/                  可运行档案、局部补丁、编译结果
├── tests/                     自动回归测试
├── evals/                     自然语言评估场景与评分指南
├── tools/                     安装、资料导出、Schema 与 ZIP 构建
├── docs/                      原仓库审查、架构、适配、扩展、验证记录
├── manifest.json              发布文件清单与哈希
├── LICENSE                    本项目许可
└── THIRD_PARTY_NOTICES.md      参考来源及原项目许可保留
```

## 本地试跑

在项目根目录执行：

```bash
python3 skill/portrait-forge/scripts/portrait.py validate examples/03-roster.json
python3 skill/portrait-forge/scripts/portrait.py compile examples/01-original.json
python3 skill/portrait-forge/scripts/portrait.py revise examples/01-original.json examples/lip-patch.json --allow makeup.lip_color --request "只改唇色为酒红" > /tmp/portrait-edited.json
python3 skill/portrait-forge/scripts/portrait.py compile /tmp/portrait-edited.json --baseline examples/01-original.json
python3 -m unittest discover -s tests -v
```

命令成功返回 0，输入或合同失败返回 1；命令用法错误由参数解析器返回 2。输出为 JSON，可被其他 Agent 工具直接读取。修改输出用新文件路径，勿将输出重定向到输入文件。

[原创 Prompt](examples/compiled/01-original.md) · [五人同妆 Prompt](examples/compiled/03-roster.md) · [局部修改](examples/compiled/02-edited.md)

## 主要改进

| 部分 | 实现 |
|---|---|
| Prompt 与档案一致 | 从字段编译，输出 trace 与源文件哈希，全部确定项保留 |
| 锁定范围 | 脸、骨相、肤色、妆、发型、摄影均可锁定 |
| 局部修改 | 精确路径白名单、基线哈希、实际差异复核 |
| 未知信息 | 观察/推测/未知/设计分开，未知不自动填齐 |
| 阵容 | 所有配对比较、骨架分组防重复计数、同妆全字段检查 |
| 可维护性 | 单一字段目录驱动校验、中文编译、派生 Schema |
| 可迁移性 | 独立 Skill、无依赖 Python 工具、可导出的会话资料 |

原仓库已具备清晰设计规则、程序检查和人工评估材料；新版着重补齐可执行的数据与修改链路，没有宣称自动生图效果优于原版。[逐项审查](docs/UPSTREAM_REVIEW.md)。

## 验证与扩展

自动测试、打包校验及尚未验证范围见 [验证记录](docs/VALIDATION.md)。自然语言案例未作为自动模型成绩，未实际生成图片，也未在线安装到 ChatGPT Work。

新增字段、规则和宿主适配见 [扩展指南](docs/EXTENDING.md)。版本 1.0.0，MIT 许可；不宣称无缺陷或跨图身份绝对稳定。
