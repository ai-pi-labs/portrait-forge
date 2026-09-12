# 扩展与维护

## 增加一个字段

1. 在 skill/portrait-forge/assets/fields.json 添加唯一路径、中文 label、section、identity、required_create。可选 values 限定枚举；字段用于结构差异时才设 group。
2. 修改对应 reference，说明此轴与相邻轴的区别。没有证据时保持 unknown；普通文本值不加入结构计分。
3. 若 required_create=true，更新所有原创/阵容样例。新增身份字段在同脸任务中需被锁定；局部白名单默认不会放行新字段。
4. 执行 `python3 tools/schema.py` 生成 Schema。新增跨字段语义门槛在 contracts.py 实现，不能只写在 Schema。
5. 增加能体现行为不变量的测试，重新生成受影响示例输出，再运行测试；不要只测试某个词出现。

例如要精细控制眼线颜色和方向，可把 makeup.liner 拆成独立字段。属于数据格式变更，应提升 schema_version，并写显式迁移器；不要悄悄改变 v1 同一路径的含义。旧版本未知项不能在迁移中自动补造。

## 新增风格

在对应规则提供可选关系与适用目标，不把文化、肤色或性别绑定到固定脸。新增独立示例，注明是创作还是实际图像案例。无需增加另一份编译器。

## 新增宿主

保留内核 JSON 与编译结果不变。适配器只做宿主字段转换、附件引用、调用和结果回读。测试无工具、失败返回、普通文字请求、明确生图、否定/引用、局部修改和持久保存。不能把自动保存未确认写成已安装。

## 新增输出格式

从 compile_plan 返回值派生 Markdown、英文或第三方语法；保留 source_sha256 和 trace。LLM 翻译/润色需要重新核对锁定语义，不继承确定性文本保证。

## 发布

```bash
python3 -m unittest discover -s tests -v
python3 tools/schema.py
python3 tools/release.py --out ../portrait-forge-release
```

release 生成完整工程 ZIP、独立技能 ZIP、哈希清单，并更新根 manifest（不包含自身，避免递归哈希）。ZIP 固定文件时间和排序，以相同内容构建可得到相同文件；构建过程不发布到网络。

发布前更新 docs/VALIDATION.md 中的实际运行环境和结果。若自然语言评估或图片没有执行，保持 NOT RUN；不要把材料数量变成通过数量。
