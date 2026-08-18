来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/geometryIntersectionV1/

# 几何交集

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 几何交集

> 支持于: 批处理，流处理

支持于: 批处理，流处理

计算几何a与几何b相交的部分。

表达式类别: 地理空间

## 声明的参数

- 几何a- 几何a。Expression<Geometry>
- 几何b- 几何b。Expression<Geometry>
输出类型:Geometry

## 示例

### 示例 1: 基本案例

参数值:

- 几何a:geometry_a
- 几何b:geometry_b
| geometry_a | geometry_b | 输出 |
| --- | --- | --- |
| {"type":"Polygon","coordinates":[[[0.0,0.0],[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0]]]} | {"type":"Polygon","coordinates":[[[0.5,0.0],[1.5,0.0],[1.5,1.0],[0.5,1.0],[0.5,0.0]]]} | {"type":"Polygon","coordinates":[[[0.5,1.0],[1.0,1.0],[1.0,0.0],[0.5,0.0],[0.5,1.0]]]} |
| {"type":"Polygon","coordinates":[[[0.0,0.0],[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0]]]} | {"type":"Polygon","coordinates":[[[5.0,5.0],[5.0,6.0],[6.0,6.0],[6.0,5.0],[5.0,5.0]]]} | {"type":"Polygon","coordinates":[[]]} |
| {"type":"Polygon","coordinates":[[[0.0,0.0],[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0]]]} | {"type":"Polygon","coordinates":[[[1.0,0.0],[1.0,1.0],[2.0,1.0],[2.0,0.0],[1.0,0.0]]]} | {"type":"LineString","coordinates":[[1.0,1.0],[1.0,0.0]]} |
| {"type":"Point","coordinates":[0.0,0.0]} | {"type":"LineString","coordinates":[[0.0,0.0],[1.0,0.0]]} | {"type":"Point","coordinates":[0.0,0.0]} |
| {"type":"LineString","coordinates":[[0.0,0.0],[1.0,0.0]]} | {"type":"Polygon","coordinates":[[[2.0,0.0],[2.0,1.0],[3.0,1.0],[3.0,0.0],[2.0,0.0]]]} | {"type":"LineString","coordinates":[]} |
