来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/createGeoLineStringV1/

# 创建线段几何

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 创建线段几何

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

从给定的点创建GeoJSON线段几何。

表达式类别: 地理空间

## 声明参数

- Points（点）- 构成线段的点。Expression<Array<T>>
类型变量界限:T 接受 Struct<longitude, latitude>

输出类型:Geometry（几何）

## 示例

### 示例 1: 基本情况

参数值:

- Points（点）:points
| points（点） | 输出 |
| --- | --- |
| [ {latitude（纬度）: 10.0,longitude（经度）: 0.0,}, {latitude（纬度）: 10.0,longitude（经度）: 10.0,} ] | {"type":"LineString","coordinates":[[0.0,10.0],[10.0,10.0]]} |
| [ {latitude（纬度）: 10.0,longitude（经度）: 10.0,}, {latitude（纬度）: 20.0,<... | {"type":"LineString","coordinates":[[10.0,10.0],[20.0,20.0],[30.0,30.0]]} |
| [ {latitude（纬度）: 0.0,longitude（经度）: 179.0,}, {latitude（纬度）: 0.0,longitude（经度）: 181.0,} ] | {"type":"MultiLineString","coordinates":[[[179.0,0.0],[180.0,0.0]],[[-180.0,0.0],[-179.0,0.0]]]} |
| [ {latitude（纬度）: 0.0,longitude（经度）: -179.0,}, {latitude（纬度）: 0.0,longitude（经度）: -181.0,} ] | {"type":"MultiLineString","coordinates":[[[180.0,0.0],[179.0,0.0]],[[-179.0,0.0],[-180.0,0.0]]]} |

### 示例 2: 空值情况

参数值:

- Points（点）:points
| points（点） | 输出 |
| --- | --- |
| null | null |
| [ {latitude（纬度）: 0.0,longitude（经度）: 0.0,},null] | null |

### 示例 3: 边缘情况

参数值:

- Points（点）:points
| points（点） | 输出 |
| --- | --- |
| [  ] | null |
| [ {latitude（纬度）: 0.0,longitude（经度）: 0.0,} ] | null |
