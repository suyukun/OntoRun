来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/createOntologyGeopointV1/

# 转换为 Ontology GeoPoint

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 转换为 Ontology GeoPoint

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

将 GeoPoint 转换为字符串，以便 Ontology 接受地理索引列（地理哈希类型列）。Ontology GeoPoint 是格式为 '{lat},{lon}' 的字符串，其中 -90 <= lat <= 90 且 -180 <= lon <= 180。

表达式类别: 地理空间

## 声明的参数

- 表达式- 要转换的 GeoPoint。Expression<GeoPoint>
输出类型:Ontology GeoPoint

## 示例

### 示例 1: 基本案例

参数值:

- 表达式:point
| point | 输出 |
| --- | --- |
| {latitude: -20.0,longitude: 80.0,} | -20.0000000,80.0000000 |
| {latitude: 38.9031,longitude: -77.0599,} | 38.9031000,-77.0599000 |
| {latitude: 41.987654321,longitude: -99.123456789,} | 41.9876543,-99.1234568 |
| null | null |
