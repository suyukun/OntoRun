来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/geometryTranslateV1/

# 几何变换表达式

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 几何变换表达式

> 支持于：批处理，流处理

支持于：批处理，流处理

对几何应用一个平移。只有在提供 z 偏移时，二维几何才会转换为三维几何。

表达式类别：地理空间

## 声明的参数

- 几何列- 要被平移的几何。Expression<字符串>
- 投影坐标系统- 坐标系统标识符，格式为 "authority"。例如，UTM 区 18N 可以通过 EPSG:32618 标识。几何将被转换到源坐标系统，应用平移，然后重新转换为 WGS84。Literal<字符串>
- X 偏移- 几何在坐标参考系统中将被平移到正 x 方向的距离。Literal<Double>
- Y 偏移- 几何在坐标参考系统中将被平移到正 y 方向的距离。Literal<Double>
- 非必填Z 偏移- 几何在坐标参考系统中将被平移到正 z 方向的距离。Literal<Double>
输出类型：Geometry

## 示例

### 示例 1：基本情况

参数值：

- 几何列:geometry
- 投影坐标系统: EPSG:4326
- X 偏移: 1.0
- Y 偏移: -1.0
- Z 偏移:null
| 几何 | 输出 |
| --- | --- |
| {"type":"Point","coordinates":[0.0, 0.0]} | {"type":"Point","coordinates":[1.0, -1.0]} |
| {"type":"LineString","coordinates":[[0.0, 0.0], [1.0, 1.0]]} | {"type":"LineString","coordinates":[[1.0, -1.0], [2.0, 0.0]]} |
| {"type":"Polygon","coordinates":[[[0.0, 0.0],[1.0, 0.0],[1.0, 1.0],[0.0, 1.0], [0.0, 0.0]]]} | {"type":"Polygon","coordinates":[[[1.0, -1.0],[2.0, -1.0],[2.0, 0.0],[1.0, 0.0],[1.0, -1.0]]]} |

### 示例 2：基本情况

参数值：

- 几何列:geometry
- 投影坐标系统: EPSG:4326
- X 偏移: 1.0
- Y 偏移: -1.0
- Z 偏移: 1.0
| 几何 | 输出 |
| --- | --- |
| {"type":"Point","coordinates":[0.0, 0.0]} | {"type":"Point","coordinates":[1.0, -1.0, 1.0]} |
| {"type":"LineString","coordinates":[[0.0, 0.0], [1.0, 1.0]]} | {"type":"LineString","coordinates":[[1.0, -1.0, 1.0], [2.0, 0.0, 1.0]]} |
| {"type":"Polygon","coordinates":[[[0.0, 0.0],[1.0, 0.0],[1.0, 1.0],[0.0, 1.0], [0.0, 0.0]]]} | {"type":"Polygon","coordinates":[[[1.0, -1.0, 1.0],[2.0, -1.0, 1.0],[2.0, 0.0, 1.0],[1.0, 0.0, 1.0],[1.0, -1.0, 1.0]]]} |

### 示例 3：基本情况

参数值：

- 几何列:geometry
- 投影坐标系统: EPSG:4326
- X 偏移: 1.0
- Y 偏移: -1.0
- Z 偏移: 1.0
| 几何 | 输出 |
| --- | --- |
| {"type":"Point","coordinates":[0.0, 0.0, -1.0]} | {"type":"Point","coordinates":[1.0, -1.0, 0.0]} |
| {"type":"LineString","coordinates":[[0.0, 0.0, -1.0], [1.0, 1.0, -1.0]]} | {"type":"LineString","coordinates":[[1.0, -1.0, 0.0], [2.0, 0.0, 0.0]]} |
| {"type":"Polygon","coordinates":[[[0.0, 0.0, -1.0],[1.0, 0.0, -1.0],[1.0, 1.0, -1.0],[0.0, 1.0, -1.0],[0.0, 0.0, -1.0]]]} | {"type":"Polygon","coordinates":[[[1.0, -1.0, 0.0],[2.0, -1.0, 0.0],[2.0, 0.0, 0.0],[1.0, 0.0, 0.0],[1.0, -1.0, 0.0]]]} |

### 示例 4：基本情况

参数值：

- 几何列:geometry
- 投影坐标系统: EPSG:32618
- X 偏移: 100.0
- Y 偏移: -200.0
- Z 偏移:null
| 几何 | 输出 |
| --- | --- |
| {"type":"Point","coordinates":[-77.0, 20.0]} | {"type":"Point","coordinates":[-76.99902180032066, 19.99820455178219]} |

### 示例 5：空值情况

参数值：

- 几何列:geometry
- 投影坐标系统: EPSG:4326
- X 偏移: 1.0
- Y 偏移: -1.0
- Z 偏移: 1.0
| 几何 | 输出 |
| --- | --- |
| null | null |
