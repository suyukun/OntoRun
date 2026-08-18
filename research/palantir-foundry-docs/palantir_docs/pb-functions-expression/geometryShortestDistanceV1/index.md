来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/geometryShortestDistanceV1/

# 几何最短距离

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 几何最短距离

> 支持于: 批处理，流处理

支持于: 批处理，流处理

给定两个有效的几何体，计算它们之间的最短（大圆）距离，单位为米。使用球形近似地球。重叠的几何体距离为零。

表达式类别: 地理空间

## 声明的参数

- Geometry a- 几何体 a。Expression<Geometry>
- Geometry b- 几何体 b。Expression<Geometry>
输出类型:Double

## 示例

### 示例 1: 基本情况

参数值:

- Geometry a:geometry_a
- Geometry b:geometry_b
| geometry_a | geometry_b | 输出 |
| --- | --- | --- |
| {"type":"LineString","coordinates":[[-40, 0],[-30, 0]]}} | {"type":"Polygon","coordinates":[[[-30,-30],[-30, 30],[30, 30],[30, -30],[-30, -30]]]} | 0.0 |
| {"type":"Point","coordinates":[0,0]}} | {"type":"Polygon","coordinates":[[[-30,-30],[-30, 30],[30, 30],[30, -30],[-30, -30]]]} | 0.0 |
| {"type":"Point","coordinates":[-30,29]}} | {"type":"Polygon","coordinates":[[[-30,-30],[-30, 30],[30, 30],[30, -30],[-30, -30]]]} | 0.0 |
| {"type":"Polygon","coordinates":[[[40,0],[-40,0],[0,40],[40,0]]]} | {"type":"Polygon","coordinates":[[[-30,-30],[-30, 30],[30, 30],[30,-30],[-30,-30]]]} | 0.0 |
| {"type":"Polygon","coordinates":[[[-40,0],[40,0],[0,40],[-40,0]]]} | {"type":"Polygon","coordinates":[[[-30,-30],[-30,0],[30,0],[30,-30],[-30,-30]]]} | 0.0 |

### 示例 2: 基本情况

参数值:

- Geometry a:geometry_a
- Geometry b:geometry_b
| geometry_a | geometry_b | 输出 |
| --- | --- | --- |
| {"type":"GeometryCollection","geometries":[{"type":"Point","coordinates":[87.0,77.0]},{"type":"LineString","coordinates":[[80.0,0],[90.0,0]]}]} | {"type":"GeometryCollection","geometries":[{"type":"Point","coordinates":[70.0,-100.0]},{"type":"Lin... | 39438.65354637 |
| {"type":"GeometryCollection","geometries":[{"type":"Point","coordinates":[170,90]},{"type":"LineStri... | {"type":"GeometryCollection","geometries":[{"type":"Point","coordinates":[-87,-73]},{"type":"LineStr... | 5310295.471462 |
| {"type":"GeometryCollection","geometries":[{"type":"MultiPoint","coordinates":[[170,90],[171,91]]},{... | {"type":"GeometryCollection","geometries":[{"type":"Point","coordinates":[-87,-73]},{"type":"LineStr... | 5327143.5044855 |

### 示例 3: 基本情况

描述: 一种几何体是点，另一种是任意几何集合的情况。表达式应识别出点与几何体之间的最短距离位于一个多边形边的中间。参数值:

- Geometry a:geometry_a
- Geometry b:geometry_b
| geometry_a | geometry_b | 输出 |
| --- | --- | --- |
| {"type":"Point","coordinates":[1,24]} | {"type":"GeometryCollection","geometries":[{"type":"Point","coordinates":[70.0,-100.0]},{"type":"Lin... | 3285803.956493 |
| {"type":"GeometryCollection","geometries":[{"type":"Point","coordinates":[70.0,-100.0]},{"type":"Lin... | {"type":"Point","coordinates":[1.0,-14.0]} | 1227726.9895314 |

### 示例 4: 基本情况

描述: 基本情况，从点到线的最短路径是到LineString内部某点（而不是端点）的一个大圆线。参数值:

- Geometry a:geometry_a
- Geometry b:geometry_b
| geometry_a | geometry_b | 输出 |
| --- | --- | --- |
| {"type":"Point","coordinates":[1,23]} | {"type":"LineString","coordinates":[[51.93,95.6],[-43.7,22.2]]}} | 4557966.282534 |

### 示例 5: 基本情况

描述: 基本情况，从点到线的最短路径是到LineString端点的线。特别是，应该计算到LineString第一个点的距离。参数值:

- Geometry a:geometry_a
- Geometry b:geometry_b
| geometry_a | geometry_b | 输出 |
| --- | --- | --- |
| {"type":"Point","coordinates":[171,23]} | {"type":"LineString","coordinates":[[-174,21],[-43.7,22.2]]} | 1561650.083282 |

### 示例 6: 基本情况

参数值:

- Geometry a:geometry_a
- Geometry b:geometry_b
| geometry_a | geometry_b | 输出 |
| --- | --- | --- |
| {"type":"Point","coordinates":[12.3,45.6]} | {"type":"Point","coordinates":[3,3.5]} | 4767896.596327 |
| {"type":"Point","coordinates":[-172.45613,-80]} | {"type":"Point","coordinates":[7.54387,-80]} | 2223902.02355 |

### 示例 7: 基本情况

描述: 基本情况，从点到线的最短路径是到多边形的一个边的内部（而不是它的角）的一个大圆线。参数值:

- Geometry a:geometry_a
- Geometry b:geometry_b
| geometry_a | geometry_b | 输出 |
| --- | --- | --- |
| {"type":"Point","coordinates":[1,23]} | {"type":"Polygon","coordinates":[[[33.969414,27.763400],[20.325411,69.748301],[37.607794,71.926251],[47.741855,42.169452],[33.969414,27.763400]]]} | 3328300.4609136 |
| {"type":"Point","coordinates":[36.06123680798,52.664515483941]} | {"type":"Polygon","coordinates":[[[33.969414,27.7634],[47.741855,42.169452],[37.607794,71.926251],[2... | 67765.90969341 |

### 示例 8: 基本情况

描述: 从点到线的最短路径是到多边形一个角的线的情况。参数值:

- Geometry a:geometry_a
- Geometry b:geometry_b
| geometry_a | geometry_b | 输出 |
| --- | --- | --- |
| {"type":"Point","coordinates":[1,23]} | {"type":"Polygon","coordinates":[[[-31.224246,67.357277],[-4.635177,38.608765],[-12.085376,85.774983],[-31.224246,67.357277]]]} | 1816109.959427 |

### 示例 9: 空值情况

参数值:

- Geometry a:geometry_a
- Geometry b:geometry_b
| geometry_a | geometry_b | 输出 |
| --- | --- | --- |
| hello, world! | {"type":"Point","coordinates":[0.0,0.0]} | null |

### 示例 10: 空值情况

参数值:

- Geometry a:geometry_a
- Geometry b:geometry_b
| geometry_a | geometry_b | 输出 |
| --- | --- | --- |
| null | {"type":"Point","coordinates":[]} | null |
| {} | {"type":"Point","coordinates":[]} | null |
| null | null | null |

### 示例 11: 边缘情况

参数值:

- Geometry a:geometry_a
- Geometry b:geometry_b
| geometry_a | geometry_b | 输出 |
| --- | --- | --- |
| {"type":"Point","coordinates":[19.409686726843,-10.140156318979]} | {"type":"Point","coordinates":[-160.590313273157, 10.140156318979]} | 2.0015118211947E7 |
| {"type":"Point","coordinates":[69,-90]} | {"type":"Point","coordinates":[0,90]} | 2.0015118211947E7 |
