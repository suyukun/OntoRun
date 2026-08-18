来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/geometryDifferenceV1/

# 几何差异

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 几何差异

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

计算几何体a中不与几何体b相交的部分。

表达式类别: 地理空间

## 声明的参数

- 几何体a- 几何体b。Expression<Geometry>
- 几何体b- 几何体a。Expression<Geometry>
输出类型:Geometry

## 示例

### 示例 1: 基本情况

参数值:

- 几何体a:geometry_a
- 几何体b:geometry_b
| geometry_a | geometry_b | 输出 |
| --- | --- | --- |
| {"type":"Polygon","coordinates":[[[0.0,0.0],[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0]]]} | {"type":"Polygon","coordinates":[[[0.25,0.25],[0.5,0.25],[0.5,0.5],[0.25,0.5],[0.25,0.25]]]} | {"type":"Polygon","coordinates":[[[0.0,0.0],[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0]],[[0.25,0.25],[0.5,0.25],[0.5,0.5],[0.25,0.5],[0.25,0.25]]]} |
| {"type":"Polygon","coordinates":[[[0.0,0.0],[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0]]]} | {"type":"Polygon","coordinates":[[[0.0,0.0],[0.5,0.0],[0.5,1.0],[0.0,1.0],[0.0,0.0]]]} | {"type":"Polygon","coordinates":[[[0.5,1.0],[1.0,1.0],[1.0,0.0],[0.5,0.0],[0.5,1.0]]]} |
| {"type":"Polygon","coordinates":[[[0.0,0.0],[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0]]]} | {"type":"Polygon","coordinates":[[[5.0,5.0],[5.0,6.0],[6.0,6.0],[6.0,5.0],[5.0,5.0]]]} | {"type":"Polygon","coordinates":[[[0.0,0.0],[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0]]]} |
| {"type":"Polygon","coordinates":[[[0.0,0.0],[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0]]]} | {"type":"LineString","coordinates":[[0.0,0.0],[0.0,1.0]]} | {"type":"Polygon","coordinates":[[[0.0,0.0],[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0]]]} |

### 示例 2: 边界情况

参数值:

- 几何体a:geometry_a
- 几何体b:geometry_b
| geometry_a | geometry_b | 输出 |
| --- | --- | --- |
| {"type":"Point","coordinates":[0.0,0.0]} | {"type":"Point","coordinates":[0.0,0.0]} | {"type":"Point","coordinates":[]} |
| {"type":"Polygon","coordinates":[[[0.0,0.0],[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0]]]} | {"type":"Polygon","coordinates":[[[0.0,0.0],[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0]]]} | {"type":"Polygon","coordinates":[[]]} |
| {"type":"Point","coordinates":[0.0,0.0]} | {"type":"LineString","coordinates":[[0.0,0.0],[0.0,1.0]]} | {"type":"Point","coordinates":[]} |
| {"type":"LineString","coordinates":[[0.0,0.0],[0.0,1.0]]} | {"type":"Polygon","coordinates":[[[0.0,0.0],[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0]]]} | {"type":"LineString","coordinates":[]} |
