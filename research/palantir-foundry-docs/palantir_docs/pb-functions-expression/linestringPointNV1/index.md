来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/linestringPointNV1/

# 线串中的第n个点

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 线串中的第n个点

> 支持于: 批处理，流处理

支持于: 批处理，流处理

返回几何中单个线串中的第n个点。索引是基于1的，索引0是越界的。负索引从线串的末尾向后计数，因此-1是最后一个点。对于以下任何条件返回null：几何不是单个线串，提供了要素集合或几何集合，索引越界，或至少一个参数为null。

表达式类别: 地理空间

## 声明的参数

- Linestring- 要检索第n个点的线串。Expression<Geometry>
- N- 要检索的点的索引。索引是基于1的，索引0是越界的。负索引从线串的末尾向后计数，因此-1是最后一个点。Expression<Byte | Integer | Long | Short>
输出类型:GeoPoint

## 示例

### 示例 1: 基础案例

参数值:

- Linestring:linestring
- N:n
| linestring | n | 输出 |
| --- | --- | --- |
| {"type":"LineString","coordinates":[[30.0,2.0],[35.0,0.0],[50.0,3.0]]} | 1 | {latitude: 2.0,longitude: 30.0,} |
| {"type":"LineString","coordinates":[[30.0,2.0],[35.0,0.0],[50.0,3.0]]} | 3 | {latitude: 3.0,longitude: 50.0,} |
| {"type":"LineString","coordinates":[[45.0,9.0],[90.0,4.0],[40.0,0.0]]} | -1 | {latitude: 0.0,longitude: 40.0,} |

### 示例 2: Null 情况

参数值:

- Linestring:linestring
- N:n
| linestring | n | 输出 |
| --- | --- | --- |
| {"type":"LineString","coordinates":[[10.0,4.0],[75.0,0.0]]} | null | null |
| null | 1 | null |

### 示例 3: 边缘案例

参数值:

- Linestring:linestring
- N:n
| linestring | n | 输出 |
| --- | --- | --- |
| {"type":"MultiLineString","coordinates":[[[100.0,0.0]], [[102.0,2.0]]]} | 2 | null |
| {"type":"GeometryCollection","geometries":{"type":"LineString","coordinates":[[10.0,4.0]]}} | 1 | null |
| {"type":"LineString","coordinates":[[10.0,4.0],[75.0,0.0],[25.0,3.0]]} | 0 | null |
| {"type":"LineString","coordinates":[[12.0,3.0],[76.0,2.0],[98.0,8.0]]} | 4 | null |
| {"type":"LineString","coordinates":[[90.0,1.0],[34.0,1.0],[19.0,7.0]]} | -4 | null |
