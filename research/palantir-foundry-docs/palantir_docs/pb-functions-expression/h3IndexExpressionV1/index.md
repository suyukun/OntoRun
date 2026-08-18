来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/h3IndexExpressionV1/

# 获取H3索引

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 获取H3索引

> 支持于: 批处理, 流式处理

支持于: 批处理, 流式处理

将GeoPoint转换为给定分辨率的H3索引。对于分辨率<0或>15返回null。

表达式类别: 地理空间

## 声明的参数

- GeoPoint- 要转换为H3索引的GeoPoint (lon,lat)。Expression<GeoPoint>
- Resolution- H3网格分辨率，范围在0到15之间（包括0和15）。Expression<Byte | Integer | Long | Short>
输出类型:H3 索引

## 示例

### 示例 1: 基本案例

参数值:

- GeoPoint:point
- Resolution: 5
| point | 输出 |
| --- | --- |
| {latitude: -20.0,longitude: 80.0,} | 85aa614bfffffff |
| {latitude: 38.9031,longitude: -77.0599,} | 852aa84ffffffff |

### 示例 2: 基本案例

参数值:

- GeoPoint:constructGeoPoint(latitude: 80.0,longitude: -20.0,)
- Resolution: 5
输出:8507b297fffffff
