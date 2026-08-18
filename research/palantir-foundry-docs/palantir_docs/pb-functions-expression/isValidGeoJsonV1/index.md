来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/isValidGeoJsonV1/

# 是否有效的 GeoJSON

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 是否有效的 GeoJSON

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

如果输入是有效的 GeoJSON 字符串，则返回 true。并非所有 GeoJSON 字符串都可以被 Ontology 索引；在使用 Ontology 之前，请使用 "标准化几何" 表达式准备几何。

表达式类别: 地理空间

## 声明的参数

- 表达式- 要检查的 GeoJSON。请注意，并非所有 GeoJSON 字符串都可以被 Ontology 索引；在使用 Ontology 之前，请使用 "标准化几何" 表达式准备几何。Expression<字符串>
输出类型:布尔

## 示例

### 示例 1: 基本情况

参数值:

- 表达式:geoJson
| geoJson | 输出 |
| --- | --- |
| {"type":"Point","coordinates":[3.0, 5.0, 2.0]} | true |
| {"type":"Polygon","coordinates":[[[0.0,0.0],[1.0,0.0],[0.0,1.0],[0.0,0.0]]]} | true |
| {"type":"LineString","coordinates":[[0.0,0.0],[1.0,0.0]]} | true |
| 不是 GeoJSON 字符串 | false |
