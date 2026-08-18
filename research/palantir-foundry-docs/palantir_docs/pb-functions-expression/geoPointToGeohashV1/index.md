来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/geoPointToGeohashV1/

# 将 GeoPoint 转换为 Geohash

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 将 GeoPoint 转换为 Geohash

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

将 GeoPoint 转换为包含该 GeoPoint 的指定精度的 base32 编码 Geohash。有关 Geohash 的更多信息，请参见:https://en.wikipedia.org/wiki/Geohash。

表达式类别: 地理空间

## 声明的参数

- GeoPoint- 要转换的 GeoPoint。Expression<GeoPoint>
- 输出 Geohash 精度- 输出 Geohash 字符串中返回的 base32 字符数。Expression<Integer>
输出类型:Geohash

## 示例

### 示例 1: 基本案例

参数值:

- GeoPoint:point
- 输出 Geohash 精度: 5
| point | 输出 |
| --- | --- |
| {latitude: -20.0,longitude: 80.0,} | mu2yh |
| {latitude: -77.0599,longitude: 38.9031,} | hf79t |
| null | null |

### 示例 2: 基本案例

参数值:

- GeoPoint:point
- 输出 Geohash 精度:precision
| point | precision | 输出 |
| --- | --- | --- |
| {latitude: -20.0,longitude: 80.0,} | 5 | mu2yh |
| {latitude: -77.0599,longitude: 38.9031,} | 3 | hf7 |
| {latitude: -82.77450568,longitude: -179.55742495,} | 12 | 0123456789zb |
| {latitude: 1.0,longitude: -1.0,} | 12 | ebpm9npc6m9b |
| {latitude: 1.0,longitude: -1.0,} | null | null |
