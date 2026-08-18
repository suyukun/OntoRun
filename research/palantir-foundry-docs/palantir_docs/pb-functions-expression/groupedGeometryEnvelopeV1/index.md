来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/groupedGeometryEnvelopeV1/

# 分组几何包络

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 分组几何包络

> 支持于: 批处理

支持于: 批处理

返回给定列中所有有效几何的包络。无效几何被视为null并被忽略。

表达式类别: 地理空间

## 声明的参数

- 表达式- 要计算包络的几何列。表达式<几何>
输出类型:几何

## 示例

### 示例 1: 基本情况

参数值:

- 表达式:geometry
给定输入表:

| 几何 |
| --- |
| {"type":"LineString","coordinates":[[1,0],[0,8.4]]} |
| {"type":"Point","coordinates":[125.6, -92.3]} |
| {"type":"Polygon","coordinates":[[[0,0],[1,6.3],[-6,1],[0,0]]]} |

输出:{"type":"Polygon","coordinates":[[[-6.0,-92.3],[-6.0,8.4],[125.6,8.4],[125.6,-92.3],[-6.0,-92.3]]]}

### 示例 2: Null 情况

参数值:

- 表达式:geometry
给定输入表:

| 几何 |
| --- |
| null |

输出:null

### 示例 3: 边缘情况

参数值:

- 表达式:geometry
给定输入表:

| 几何 |
| --- |
| Invalid GeoJSON |
| {"type":"LineString","coordinates":[[2,0],[0,4.8]]} |

输出:{"type":"Polygon","coordinates":[[[0.0,0.0],[0.0,4.8],[2.0,4.8],[2.0,0.0],[0.0,0.0]]]}
