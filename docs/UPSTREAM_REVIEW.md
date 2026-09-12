# 原仓库审查

来源：https://github.com/nuyoah-ai-works/nuyoah-portrait-character-designer

本次审查当前提交 `99b9a2c90e5b09507c6a61b5c27b9e2740ddb63d`，manifest 声明版本 0.2.1。审查覆盖所有19个非 .git 文件（含 .gitignore），逐项内容、大小和 SHA-256 见 [清单](upstream-inventory.json)。原仓库测试实际执行为 11/11 通过；manifest 的18个文件条目哈希匹配。

原仓库的价值是细致的视觉规则与清楚的授权/未知边界。主要工程空间在规则到输出的衔接：内部16轴不覆盖全部骨相与肤色摄影，Prompt 为手工编写，局部修改缺少机器可验证的基线差异。新版不将这些已明确说明的边界说成原代码缺陷。

本项目从独立字段模型、编译与修订链路重建。只保留 Agent Skill 必需/惯用的 SKILL.md、agents/openai.yaml 等接口约定，没有复制原项目架构、提示词案例或旧说明文案。参考思想在第三方声明中列明。

## .gitignore

仅忽略 .DS_Store；新版也忽略 Python 缓存和本地工作目录。

## LICENSE

MIT；记录来源，并在第三方声明中保留原许可。

## README.md

定位、安装与验证边界清晰；发行叙述和运行入口放在仓库根。新版分离工程与独立技能。

## SKILL.md

按任务读取规则，默认文字、显式生图；新版改为档案驱动的执行流程。

## agents/interface.yaml

额外兼容/信任字段为项目自定义层；新版不把自定义清单冒充宿主执行能力。

## agents/openai.yaml

官方宿主显示元数据和默认隐式调用；新版保留这种必要标准结构。

## evals/cases.json

21条自然语言人工/模型材料，原仓库明确非自动模型全部执行。新版提供24条独立设计的待执行评估。

## examples/real-cases.md

4份真实提示词及偏差说明，未附公开原图；新版提供合成、可执行JSON示例并明确未生图。

## manifest.json

全部18条文件哈希与字节数核对；sourceCommit 与当前提交不同，属于声明的发布来源，不当作当前HEAD。

## references/acceptance-and-gpt.md

已有多层验收和源派生导出；新版不固定宣称宿主编辑器字数限制或能力配置。

## references/check-contract.md

完整说明16轴与脚本边界；同脸要求完整轴，额外锁定由自然语言核查。新版局部任务允许未知基线。

## references/decision-rules.md

模式与主副气质处理完整，Prompt 主要靠 Agent 手工组织。新版增加确定性编译。

## references/lexicon.md

候选丰富，不把文化绑定脸型；新版以可执行字段目录与聚焦规则分工。

## references/makeup-adaptation.md

区分原生脸与妆效，按目标适配；新版将唇色、质地、边缘拆开支持单项修改。

## references/sources.md

列明依据和未验证事项；新版保留来源边界，不复述原会话文案。

## references/structure-and-compatibility.md

骨相三区、兼容性、六组差异及五人候选详细；部分骨相不在脚本字段中。新版覆盖骨相锁定和编译。

## scripts/check_design.py

只校验16轴和4个同妆字段，结构计数组完整，重复键防护存在；不编译Prompt，不自动验证肤色摄影锁定。

## scripts/export_gpt.py

按真源合并规则、有哈希；导出配置并非线上应用，固定8000限制。新版输出通用阅读资料，不代替安装。

## tests/test_design.py

11项程序测试实际运行全部通过，覆盖原编码合同；新版加入编译、修订、安装、CLI及派生物检查。
