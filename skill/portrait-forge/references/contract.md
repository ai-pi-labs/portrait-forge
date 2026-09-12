# 档案合同 v1

所有文件使用 UTF-8 JSON，拒绝重复键、未知字段、非有限数。具体字段键、中文标签、结构枚举和原创必填项唯一维护在 [fields.json](../assets/fields.json)。根对象：

```json
{
  "schema_version": 1,
  "request": {"text": "本轮原话", "mode": "reference", "deliverable": "text", "image_authorized": false},
  "policy": {"locks": {}, "same_makeup": false, "distinct": false, "min_groups": 3, "min_core": 2},
  "cards": [{"id": "p01", "intent": "只分析妆容", "fields": {
    "makeup.lip_color": {"value": "低饱和砖红", "status": "observed", "evidence": "图1：唇部有可见砖红色，受暖光影响"}
  }, "locks": {}, "assumptions": []}]
}
```

`fields` 是平铺路径字典（键内的点不是嵌套对象）。每个 cell 恰含 value/status/evidence；unknown 只能是 null，其他状态必须非空字符串。结构值用枚举代码，普通表现值用中文；枚举排除“圆脸或长脸”这类未决状态。

`policy.locks` 对所有人有效，`card.locks` 对单人有效，两者不得冲突。value=null 表示锁定已登记的未知项，不表示删除。锁定的具体值必须在 fields 中以 designed/observed 存在。未知不算阵容差异，不能在同妆检查中当作已知妆。

`intent` 和 `assumptions` 是沟通信息，不自动编译，任何需要呈现在图中的信息必须填 fields。全局 min_groups=1..6，min_core=1..3 且不大于 min_groups；仅 distinct=true 使用。threshold 是设计目标，应在创作前确定。

原始文字稿没有 JSON 时先进行有限映射；不能保证未编码自由文本的自动锁定。要求逐字保留时直接对原文本做限定替换并人工比对，不称已通过 JSON 校验。

编辑格式由 revise 生成，revision 包含 base_sha256、allowed、changes。不要手填虚构的变化日志。CLI 的 validate 会对 edit 强制要求基线；Python validate 函数只做形状与合同检查，调用方还须 compare。JSON Schema 为辅助文档，可由开发工具重新生成；跨字段规则以运行时验证器为准。
