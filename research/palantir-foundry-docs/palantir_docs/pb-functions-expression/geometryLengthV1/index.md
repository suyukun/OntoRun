来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/geometryLengthV1/

# 几何长度

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 几何长度

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

获取几何中线字符串和多线字符串的长度，单位为米。使用球形近似地球。非线性几何（多边形和点）计为0。

表达式类别: 地理空间

## 声明的参数

- 表达式- GeoJSON 字符串。表达式<Geometry>
输出类型:Double

## 示例

### 示例 1: 基本情况

参数值:

- 表达式:geometry
| geometry | 输出 |
| --- | --- |
| {"type":"LineString","coordinates":[[-73.778128,40.641195],[-118.408535,33.941563]]} | 3974344.7433354934 |
| {"type":"LineString","coordinates":[[0.0,0.0],[1.0,0.0],[1.0,1.0],[1.0,2.0]]} | 333585.2407005987 |
| {"type":"MultiLineString","coordinates":[[[0.0,0.0],[1.0,0.0],[1.0,1.0]], [[1.0,2.0],[2.0,2.0]]]} | 333517.50194413937 |

### 示例 2: 空值情况

参数值:

- 表达式:geometry
| geometry | 输出 |
| --- | --- |
| null | null |

### 示例 3: 边缘情况

参数值:

- 表达式:geometry
| geometry | 输出 |
| --- | --- |
| {"type":"GeometryCollection","geometries":[{"type":"Polygon","coordinates":[[[-1.0,-1.0],[-3.0,-1.0]... | 333517.50194413937 |
| {"type":"Polygon","coordinates":[[[-1.0,-1.0],[-3.0,-1.0],[-2.0,-2.0],[-1.0,-1.0]]]} | 0.0 |
| {"type":"MultiPoint","coordinates":[[23.0,30.0],[12.0,15.3]]} | 0.0 |
