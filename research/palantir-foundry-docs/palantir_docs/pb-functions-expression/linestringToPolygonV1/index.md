来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/linestringToPolygonV1/

# 将线串转换为多边形

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 将线串转换为多边形

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

将线串几何体转换为多边形几何体。此表达式假设线串几何体是闭合的。如果不是，表达式将返回null。

表达式类别: 地理空间

## 声明的参数

- 表达式- 一个有效的线串几何体。Expression<Geometry>
输出类型:Geometry

## 示例

### 示例 1: 基本情况

参数值:

- 表达式:polygon_points
| polygon_points | 输出 |
| --- | --- |
| {"type":"LineString","coordinates":[[-77.49,38.01],[-77.47,38.15],[-77.19,38.14],[-77.49,38.01]]} | {"type":"Polygon","coordinates":[[[-77.49,38.01],[-77.47,38.15],[-77.19,38.14],[-77.49,38.01]]]} |

### 示例 2: Null情况

参数值:

- 表达式:polygon_points
| polygon_points | 输出 |
| --- | --- |
| null | null |
| {"type":"LineString","coordinates":[[-77.49,38.01],[-77.19,38.14],[-77.49,38.01]]} | null |
| {"type":"LineString","coordinates":[[-77.49,38.01],[-77.19,38.14]]} | null |
| {"type":"LineString","coordinates":[[-77.49,38.01]]} | null |
| {"type":"Polygon","coordinates":[[[-77.49,38.01],[-77.47,38.15],[-77.19,38.14],[-77.49,38.01]]]} | null |
