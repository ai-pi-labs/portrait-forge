# 2026-09-15 实测：原创肖像与仅改唇色

本次实际运行当前项目的全部 31 项程序测试，并通过宿主内置 `image_gen` 分两次调用生成基线肖像、引用基线编辑唇色。两张原始输出均已查看并原样保存，没有修图、拼脸或重新压缩。

| 基线：低饱和粉棕 | 引用基线：低饱和酒红 |
| --- | --- |
| ![原创成年角色基线肖像](baseline.png) | ![引用基线改为酒红唇色，其他区域存在纹理重绘](edited.png) |

## 实际结论

| 检查 | 结果 | 证据与边界 |
| --- | --- | --- |
| 当前全部程序回归 | PASS，31/31 | [完整日志](unittest.txt)，当前环境记录于 [program-results.json](program-results.json) |
| 原创、修改、比较、阵容、参考与未知基线 | PASS | 实际执行 15 个流程，包括预期失败和安装检查；不是 15 个独立模型场景 |
| 局部修改档案 | PASS | [comparison.json](comparison.json) 只有 `makeup.lip_color`；完整编译保留其他字段 |
| 缺失编辑基线、重复安装 | 预期拒绝 | 均返回 1；没有把失败退出当成成功 |
| 隔离安装 | PASS | 18 个文件与源码哈希一致；从仓库外调用安装后的编译器，输出与源码版一致 |
| 原创图像 | 已生成并查看 | 单名原创成年人、正面胸像、完整头顶与发梢；38 岁是创作设定，不是由照片识别出的年龄 |
| 唇色编辑 | 目标可见达成 | 粉棕变为较深的低饱和酒红，使用真实基线图作为唯一编辑参考 |
| 唇部以外严格保持 | **未通过** | 额头与面颊微纹理、碎发和衣料纹理出现再生成；主要外观、姿态与构图接近，不等于完全同脸或其他像素不变 |
| 24 条自然语言评估材料 | 未执行 | 本次这一条创作与编辑链路不能替代整套场景 |

图像编辑结论为 **PARTIAL**，没有为了得到通过结论修饰结果。仅做了 1 次基线生成、1 次引用编辑，没有补做修复。两图均为 1086 × 1448，3:4 竖幅。逐项目视记录与文件 SHA-256 见 [visual-review.json](visual-review.json)。本次没有使用真人照片；角色依据仓库已有原创 `lin-01` 档案创建。

## 可复现输入

- 基线：[角色档案](baseline-plan.json) · [完整编译输出](baseline-compiled.json) · [实际生图 Prompt](baseline-prompt.txt)
- 编辑：[唇色补丁](lip-patch.json) · [编辑档案](edited-plan.json) · [完整编译输出](edited-compiled.json) · [实际编辑 Prompt](edit-prompt.txt)
- 程序：[复现脚本](reproduce.sh) · [流程与安装文件哈希](program-results.json)

从仓库根目录运行以下命令。脚本只使用 Python 标准库与 Bash，把运行日志、修改稿和安装结果写入指定的仓库外目录；不会生成或上传图片。

```sh
bash examples/verified-20260915/reproduce.sh ../portrait-forge-verification
```

实际生图需要宿主提供图片工具：先按 `baseline-prompt.txt` 生成并查看第一张图，再把**实际第一张图**作为唯一编辑目标，使用 `edit-prompt.txt` 发起第二次调用。这里测试的是 Codex 内置 `image_gen`，没有使用 CLI 生图、API key 或固定 seed。程序能够复现档案与校验；再次生图不保证相同像素或相同人物外观，角色编号和文件路径不能替代真实图片引用。

## English summary

The current 31 program tests passed. Fifteen actual command flows covered creation, revision, comparison, a five-person roster, reference observations, unknown fields, missing-baseline rejection, isolated installation and overwrite rejection. All 18 installed files matched the source hashes; the installed compiler produced the same output from outside the repository.

Two separate calls to Codex's built-in `image_gen` produced an original adult portrait and an edit using the actual first image as the sole reference. Both unmodified PNG outputs were viewed. The requested muted burgundy lip color is visible, while the overall appearance and composition remain similar. Skin microtexture, flyaway hair and fabric texture were regenerated. The image edit is therefore **PARTIAL**, and strict preservation outside the lips **failed**. This is not a claim of exact identity or unchanged non-lip pixels.

The fictional character's age of 38 is a design setting, not an age inferred from an image. No real-person reference was used. The 24 natural-language evaluation scenarios remain unrun. The script above reproduces the program checks, not image pixels; image generation needs an available host tool and a real reference attachment for the second call.
