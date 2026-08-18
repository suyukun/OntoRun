来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/interpolateGeoPointAlongLinestringV1/

# 在折线段上插值地理点

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 在折线段上插值地理点

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

返回沿线插值的点。实现将线解释为最短路径，使用地球的球形近似。

表达式类别: 地理空间

## 声明的参数

- Fraction- 在折线段总长度上从起始点开始抽取地理点的比例。必须是介于0和1之间的浮点数。表达式<Decimal | Double | Float>
- Linestring- 用于插值地理点的折线段。表达式<Geometry>
输出类型:GeoPoint

## 示例

### 示例 1: 基本情况

参数值:

- Fraction:fraction
- Linestring:linestring
| linestring | fraction | 输出 |
| --- | --- | --- |
| {"type":"LineString","coordinates":[[0.0,2.0],[30.0,0.0]]} | 0.5 | {latitude: 1.0352686301676643,longitude: 15.004677545504547,} |
| {"type":"LineString","coordinates":[[30.0,2.0],[50.0,3.0]]} | 0.8 | {latitude: 2.8256098405656185,longitude: 45.99752305664789,} |
| {"type":"LineString","coordinates":[[45.0,9.0],[90.0,4.0]]} | 0.2 | {latitude: 8.363732883448177,longitude: 54.073497456494955,} |

### 示例 2: 基本情况

参数值:

- Fraction:fraction
- Linestring:linestring
| linestring | fraction | 输出 |
| --- | --- | --- |
| {"type":"LineString","coordinates":[[0.0,2.0],[30.0,0.0]]} | 0.5 | {latitude: 1.0352686301676643,longitude: 15.004677545504547,} |
| {"type":"LineString","coordinates":[[30.0,2.0],[50.0,3.0]]} | 0.8 | {latitude: 2.8256098405656185,longitude: 45.99752305664789,} |
| {"type":"LineString","coordinates":[[45.0,9.0],[90.0,4.0]]} | 0.2 | {latitude: 8.363732883448177,longitude: 54.073497456494955,} |

### 示例 3: 基本情况

参数值:

- Fraction:fraction
- Linestring:linestring
| linestring | fraction | 输出 |
| --- | --- | --- |
| {"type":"LineString","coordinates":[[0.0,2.0],[30.0,0.0]]} | 0.5 | {latitude: 1.0352686301676643,longitude: 15.004677545504547,} |
| {"type":"LineString","coordinates":[[30.0,2.0],[50.0,3.0]]} | 0.8 | {latitude: 2.825609851378893,longitude: 45.99752329517703,} |
| {"type":"LineString","coordinates":[[45.0,9.0],[90.0,4.0]]} | 0.2 | {latitude: 8.363732872387065,longitude: 54.0734975914614,} |

### 示例 4: 空值情况

参数值:

- Fraction:fraction
- Linestring:linestring
| linestring | fraction | 输出 |
| --- | --- | --- |
| {"type":"LineString","coordinates":[[10.0,4.0],[75.0,0.0]]} | null | null |
| {"type":"LineString","coordinates":[[10.0,8.0],[35.0,0.0]]} | -0.5 | null |
| {"type":"LineString","coordinates":[[10.0,8.0],[35.0,0.0]]} | 1.6 | null |
| {"type":"MultiLineString","coordinates":[[[100.0,0.0]], [[102.0,2.0]]]} | 0.4 | null |
| {"type":"GeometryCollection","geometries":{"type":"LineString","coordinates":[[10.0,4.0]]}} | 0.5 | null |
| null | 1.0 | null |

### 示例 5: 边缘情况

描述: Fraction值为0时返回起始点的GeoPoint，Fraction值为1时返回终点的GeoPoint。存在浮点数误差，但应足够精确以满足几乎所有应用案例。参数值:

- Fraction:fraction
- Linestring:linestring
| linestring | fraction | 输出 |
| --- | --- | --- |
| {"type":"LineString","coordinates":[[10.0,4.0],[75.0,0.0]]} | 0.0 | {latitude: 4.0,longitude: 9.999999999999998,} |
| {"type":"LineString","coordinates":[[10.0,8.0],[35.0,0.0]]} | 1.0 | {latitude: 0.0,longitude: 35.0,} |
| {"type":"LineString","coordinates":[[10.0,8.4],[35.0,0.0],[163.0,67.9]]} | 1.0 | {latitude: 67.90000000000002,longitude: 163.0,} |
| {"type":"LineString","coordinates":[[10.0,8.4],[35.0,0.0],[163.0,67.9]]} | 0.0 | {latitude: 8.400000000000002,longitude: 9.999999999999998,} |
