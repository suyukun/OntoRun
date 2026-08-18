来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/geometryArrayLineDissolveV1/

# 几何数组线合并

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 几何数组线合并

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

给定一个几何体数组，将这些几何体合并为一个线性几何体。合并通过去除不必要的节点和连接可以组合的线字符串来简化输入的线字符串集合。在合并操作中将忽略Z坐标，但结果几何体中的顶点将具有与输入中相应点相同的z坐标。

表达式类别: 地理空间

## 声明的参数

- 表达式- 要合并的几何体数组。Expression<Array<T>>
类型变量界限:T 接受 Geometry

输出类型:T

## 示例

### 示例 1: 基本情况

参数值:

- 表达式:geometries
| geometries | 输出 |
| --- | --- |
| [ {"type":"LineString","coordinates":[[0,0],[0,1],[1,1]]}, {"type":"LineString","coordinates":[[1,1]... | {"type":"MultiLineString","coordinates":[[[5.0, 5.0],[4.0, 4.0],[3.0, 3.0],[2.0, 2.0],[1.0, 1.0],[0.0, 1.0],[0.0, 0.0]],[[7.0, 7.0], [6.0, 7.0], [6.0, 6.0]]]} |
| [ {"type":"LineString","coordinates":[[0,0,1],[0,1,1],[1,1,1]]}, {"type":"LineString","coordinates":[[1,1,1],[2,2,2]]}, {"type":"LineString","coordinates":[[1,1,2],[2,2,2],[3,3,3]]} ] | {"type":"LineString","coordinates":[[0.0, 0.0, 1.0],[0.0, 1.0, 1.0],[1.0, 1.0, 1.0],[2.0, 2.0, 2.0],[3.0, 3.0, 3.0]]} |

### 示例 2: 基本情况

参数值:

- 表达式:geometries
| geometries | 输出 |
| --- | --- |
| [ {"type":"LineString","coordinates":[[0,0],[0,1],[1,1]]}, {"type":"Polygon","coordinates":[[[2,2],[... | {"type":"MultiLineString","coordinates":[[[3.0, 3.0], [4.0, 4.0], [5.0, 5.0]],[[3.0, 3.0], [3.0, 2.0], [2.0, 2.0], [2.0, 3.0], [3.0, 3.0]],[[0.0, 0.0], [0.0, 1.0], [1.0, 1.0]]]} |

### 示例 3: 基本情况

参数值:

- 表达式:geometries
| geometries | 输出 |
| --- | --- |
| [ {"type":"Polygon","coordinates":[[[0.0,0.0],[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0]]]}, {"type":"Polygon","coordinates":[[[1.0,0.0],[1.0,1.0],[2.0,1.0],[2.0,0.0],[1.0,0.0]]]} ] | {"type":"MultiLineString","coordinates":[[[1.0, 0.0], [1.0, 1.0]],[[1.0, 1.0], [0.0, 1.0], [0.0, 0.0], [1.0, 0.0]],[[1.0, 0.0], [2.0, 0.0], [2.0, 1.0], [1.0, 1.0]]]} |

### 示例 4: 空情况

参数值:

- 表达式:geometries
| geometries | 输出 |
| --- | --- |
| [  ] | null |
| null | null |
