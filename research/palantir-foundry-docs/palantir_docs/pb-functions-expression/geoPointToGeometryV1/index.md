来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/geoPointToGeometryV1/

# 将 GeoPoint 转换为几何

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 将 GeoPoint 转换为几何

> 支持于：批处理，流处理

支持于：批处理，流处理

将 GeoPoint 转换为类型为点的 GeoJSON。

表达式类别：地理空间

## 声明的参数

- 表达式- 一个有效的 GeoPoint。Expression<GeoPoint>
输出类型：Geometry

## 示例

### 示例 1：基本情况

参数值：

- 表达式:geoPoint
| geoPoint | 输出 |
| --- | --- |
| {latitude -> 58.0,longitude -> 32.0,} | {"type":"Point","coordinates": [32.0, 58.0]} |
| null | null |
| {latitude -> 40.753206,longitude -> -73.989015,} | {"type":"Point","coordinates": [-73.989015, 40.753206]} |
