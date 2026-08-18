来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/geometryEnvelopeV1/

# 获取几何包络

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 获取几何包络

> 支持于：批处理，流处理

支持于：批处理，流处理

给定一个有效的几何对象或几何对象数组，返回一个表示输入包络的几何对象。包络是包含几何对象的最小和最大 x 和 y 值的最小轴对齐矩形区域。

表达式类别：地理空间

## 声明参数

- 表达式- GeoJSON 字符串或 GeoJSON 字符串数组。Expression<Array<Geometry> | Geometry>
输出类型：Geometry

## 示例

### 示例 1：基本案例

参数值：

- 表达式:geometry
| geometry | 输出 |
| --- | --- |
| {"type":"Polygon","coordinates":[[[0.0,0.0],[1.0,0.0],[0.0,1.0]]]} | {"type":"Polygon","coordinates":[[[0.0,0.0],[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0]]]} |

### 示例 2：基本案例

参数值：

- 表达式:geometryArray
| geometryArray | 输出 |
| --- | --- |
| [ {"type":"LineString","coordinates":[[1,0],[0,8.4]]}, {"type":"Point","coordinates":[125.6, -92.3]}, {"type":"Polygon","coordinates":[[[0,0],[1,6.3],[-6,1],[0,0]]]} ] | {"type":"Polygon","coordinates":[[[-6.0,-92.3],[-6.0,8.4],[125.6,8.4],[125.6,-92.3],[-6.0,-92.3]]]} |

### 示例 3：空案例

参数值：

- 表达式:geometryArray
| geometryArray | 输出 |
| --- | --- |
| null | null |

### 示例 4：边界案例

参数值：

- 表达式:geometryArray
| geometryArray | 输出 |
| --- | --- |
| [ Invalid GeoJSON, {"type":"LineString","coordinates":[[2,0],[0,4.8]]} ] | {"type":"Polygon","coordinates":[[[0.0,0.0],[0.0,4.8],[2.0,4.8],[2.0,0.0],[0.0,0.0]]]} |
