来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/geometrySymmetricDifferenceV1/

# 几何对称差

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 几何对称差

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

计算在任一几何中但不在其交集中部分。

表达式类别: 地理空间

## 声明的参数

- 几何 a- 几何 b。Expression<Geometry>
- 几何 b- 几何 a。Expression<Geometry>
输出类型:Geometry

## 示例

### 示例 1: 基本情况

参数值:

- 几何 a:geometry_a
- 几何 b:geometry_b
| geometry_a | geometry_b | 输出 |
| --- | --- | --- |
| {"type":"Polygon","coordinates":[[[0.0,0.0],[0.0,1.0],[2.0,1.0],[2.0,0.0],[0.0,0.0]]]} | {"type":"Polygon","coordinates":[[[1.0,0.0],[1.0,1.0],[3.0,1.0],[3.0,0.0],[1.0,0.0]]]} | {"type":"MultiPolygon","coordinates":[[[[0.0,0.0],[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0]]],[[[2.0,0.0],[2.0,1.0],[3.0,1.0],[3.0,0.0],[2.0,0.0]]]]} |
| {"type":"Polygon","coordinates":[[[0.0,0.0],[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0]]]} | {"type":"Polygon","coordinates":[[[0.0,0.0],[0.5,0.0],[0.5,1.0],[0.0,1.0],[0.0,0.0]]]} | {"type":"Polygon","coordinates":[[[0.5,1.0],[1.0,1.0],[1.0,0.0],[0.5,0.0],[0.5,1.0]]]} |
| {"type":"Polygon","coordinates":[[[0.0,0.0],[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0]]]} | {"type":"Polygon","coordinates":[[[0.25,0.25],[0.5,0.25],[0.5,0.5],[0.25,0.5],[0.25,0.25]]]} | {"type":"Polygon","coordinates":[[[0.0,0.0],[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0]],[[0.25,0.25],[0.5,0.25],[0.5,0.5],[0.25,0.5],[0.25,0.25]]]} |
| {"type":"Polygon","coordinates":[[[0.0,0.0],[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0]]]} | {"type":"Polygon","coordinates":[[[5.0,5.0],[5.0,6.0],[6.0,6.0],[6.0,5.0],[5.0,5.0]]]} | {"type":"MultiPolygon","coordinates":[[[[0.0,0.0],[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0]]],[[[5.0,5.0],[5.0,6.0],[6.0,6.0],[6.0,5.0],[5.0,5.0]]]]} |

### 示例 2: 空值情况

参数值:

- 几何 a:geometry_a
- 几何 b:geometry_b
| geometry_a | geometry_b | 输出 |
| --- | --- | --- |
| null | {"type":"LineString","coordinates":[]} | null |
| {"type":"LineString","coordinates":[]} | null | null |
| null | null | null |

### 示例 3: 边缘情况

参数值:

- 几何 a:geometry_a
- 几何 b:geometry_b
| geometry_a | geometry_b | 输出 |
| --- | --- | --- |
| {"type":"Point","coordinates":[0.0,0.0]} | {"type":"Point","coordinates":[0.0,0.0]} | {"type":"Point","coordinates":[]} |
| {"type":"Polygon","coordinates":[[[0.0,0.0],[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0]]]} | {"type":"Polygon","coordinates":[[[0.0,0.0],[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0]]]} | {"type":"Polygon","coordinates":[[]]} |
| {"type":"Point","coordinates":[0.0,0.0]} | {"type":"LineString","coordinates":[[0.0,0.0],[0.0,1.0]]} | {"type":"LineString","coordinates":[[0.0,0.0],[0.0,1.0]]} |
| {"type":"LineString","coordinates":[[0.0,0.0],[0.0,1.0]]} | {"type":"Polygon","coordinates":[[[0.0,0.0],[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0]]]} | {"type":"Polygon","coordinates":[[[0.0,0.0],[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0]]]} |
| {"type":"Point","coordinates":[0.0,0.0]} | {"type":"Point","coordinates":[0.0,0.0]} | {"type":"Point","coordinates":[]} |
