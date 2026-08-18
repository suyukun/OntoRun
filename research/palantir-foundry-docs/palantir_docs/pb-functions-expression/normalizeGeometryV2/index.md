来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/normalizeGeometryV2/

# 准备几何图形

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 准备几何图形

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

通过将几何字符串转换为有效的GeoJSON，准备供下游使用的几何图形，例如索引到Ontology。多边形将被闭合和去重。跨越反子午线的几何图形（由宽度> 180度指示）将在反子午线的每一侧分成多个特征。如果输入字符串无法读取为GeoJSON或几何图形包含超出边界的坐标，则输出为空。

表达式类别: 地理空间

## 声明的参数

- 表达式- 要解析并转换为GeoJSON的字符串。表达式<字符串>
输出类型:Geometry

## 示例

### 示例 1: 基本情况

参数值:

- 表达式:geometry
| geometry | 输出 |
| --- | --- |
| {"type":"Polygon","coordinates":[[[0.0,0.0],[1.0,0.0], [0.0,1.0], [0.0,0.0]]]} | {"type":"Polygon","coordinates":[[[0.0,0.0],[0.0,1.0],[1.0,0.0],[0.0,0.0]]]} |
| {"type":"Polygon","coordinates":[[[0.0,0.0,1.0],[1.0,0.0,1.0], [0.0,1.0,1.0],[0.0,0.0,1.0]]]} | {"type":"Polygon","coordinates":[[[0.0,0.0,1.0],[0.0,1.0,1.0],[1.0,0.0,1.0],[0.0,0.0,1.0]]]} |
| {"type":"Polygon","coordinates":[[[0.0,0.0],[1.0,0.0], [0.0,1.0]]]} | {"type":"Polygon","coordinates":[[[0.0,0.0],[0.0,1.0],[1.0,0.0],[0.0,0.0]]]} |
| {"type":"Polygon","coordinates":[[[0.0,0.0],[1.0,0.0], [1.0,0.0], [0.0,1.0], [0.0,0.0]]]} | {"type":"Polygon","coordinates":[[[0.0,0.0],[0.0,1.0],[1.0,0.0],[0.0,0.0]]]} |
| {"type":"Polygon","coordinates":[[[179.0,-30.0],[-179.0,-30.0],[-179.0,30.0],[179.0,30.0],[179.0,-30]]]} | {"type":"MultiPolygon","coordinates":[[[[-180.0,-30.0],[-180.0,30.0],[-179.0,30.0],[-179.0,-30.0],[-180.0,-30.0]]],[[[180.0,30.0],[180.0,-30.0],[179.0,-30.0],[179.0,30.0],[180.0,30.0]]]]} |
| {"type":"LineString","coordinates":[[179.0,30.0],[-179.0,30.0]]} | {"type":"MultiLineString","coordinates":[[[179.0,30.0],[180.0,30.0]],[[-180.0,30.0],[-179.0,30.0]]]} |
| {"type":"GeometryCollection","geometries":[{"type":"LineString","coordinates":[[40.0,10.0],[0.0,1.0]... | {"type":"GeometryCollection","geometries":[{"type":"LineString","coordinates":[[40.0,10.0],[0.0,1.0]... |
| {"type":"GeometryCollection","geometries":[{"type":"Point","coordinates":[1.0,0.0]},{"type":"LineString","coordinates":[[179.0,30.0],[-179.0,30.0]]}]} | {"type":"GeometryCollection","geometries":[{"type":"Point","coordinates":[1.0,0.0]},{"type":"MultiLineString","coordinates":[[[179.0,30.0],[180.0,30.0]],[[-180.0,30.0],[-179.0,30.0]]]}]} |

### 示例 2: 基本情况

参数值:

- 表达式:geometry
| geometry | 输出 |
| --- | --- |
| {"type":"MultiPolygon","coordinates":[[[[102.0,2.0],[102.0,3.0],[103.0,3.0],[103.0,2.0],[102.0,2.0]]]]} | {"type":"Polygon","coordinates":[[[102.0,2.0],[102.0,3.0],[103.0,3.0],[103.0,2.0],[102.0,2.0]]]} |
| {"type":"FeatureCollection","features":[{"geometry":{"type":"MultiPolygon","coordinates":[[[[0.0,0.0],[0.0,1.0],[1.0,0.0],[0.0,0.0]]]]},"properties":{"gaccname":"namehere"},"type":"Feature"}]} | {"coordinates":[[[0.0,0.0],[0.0,1.0],[1.0,0.0],[0.0,0.0]]],"type":"Polygon"} |
| {"type":"GeometryCollection","geometries":[{"type":"LineString","coordinates":[[40.0,11.0],[0.0,1.0]]},{"type":"LineString","coordinates":[[10.0,10.0],[20.0,20.0],[10.0,40.0]]}]} | {"coordinates":[[[40.0,11.0],[0.0,1.0]],[[10.0,10.0],[20.0,20.0],[10.0,40.0]]],"type":"MultiLineString"} |

### 示例 3: 基本情况

参数值:

- 表达式:geometry
| geometry | 输出 |
| --- | --- |
| {"type":"Polygon","coordinates":[[[0.0,0.0],[1.0,1.0],[0.0,1.0], [1.0,0.0], [0.0,0.0]]]} | {"type":"MultiPolygon","coordinates":[[[[0.0,0.0],[0.5,0.5],[1.0,0.0],[0.0,0.0]]],[[[0.5,0.5],[0.0,1.0],[1.0,1.0],[0.5,0.5]]]]} |
| {"type":"Polygon","coordinates":[[[0.0,0.0],[2.0,0.0],[1.0,1.0],[2.0,2.0],[0.0,2.0],[1.0,1.0],[0.0,0.0]]]} | {"type":"MultiPolygon","coordinates":[[[[0.0,0.0],[1.0,1.0],[2.0,0.0],[0.0,0.0]]],[[[1.0,1.0],[0.0,2.0],[2.0,2.0],[1.0,1.0]]]]} |
| {"type":"Polygon","coordinates":[[[0.0,0.0],[2.0,0.0],[2.0,2.0],[0.0,2.0],[0.0,0.0]],[[0.0,0.0],[2.0,0.0],[1.0,1.0],[0.0,0.0]]]} | {"type":"Polygon","coordinates":[[[0.0,2.0],[2.0,2.0],[2.0,0.0],[1.0,1.0],[0.0,0.0],[0.0,2.0]]]} |
| {"type":"Polygon","coordinates":[[[0.0,0.0],[1.0,0.0],[1.0,1.0],[0.0,1.0],[0.0,0.0]],[[3.0,3.0],[4.0,3.0],[4.0,4.0],[3.0,4.0],[3.0,3.0]]]} | {"type":"MultiPolygon","coordinates":[[[[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0],[0.0,1.0]]],[[[3.0,4.0],[4.0,4.0],[4.0,3.0],[3.0,3.0],[3.0,4.0]]]]} |

### 示例 4: 空值情况

参数值:

- 表达式:geometry
| geometry | 输出 |
| --- | --- |
| null | null |
| Not geojson | null |
| {"type":"Polygon","coordinates":[[[0.0,0.0],[1.0,0.0,1.0], [0.0,1.0], [0.0,0.0]]]} | null |
| {"type":"LineString","coordinates":[[0.0,0.0]]} | null |
| {"type":"Polygon","coordinates":[[[0.0,0.0],[1.0,91.0], [0.0,1.0], [0.0,0.0]]]} | null |
| {"type":"Polygon","coordinates":[[[0.0,-90.1],[1.0,0.0], [0.0,1.0], [0.0,0.0]]]} | null |
| {"type":"Polygon","coordinates":[[[0.0,0.0],[181.0,89.0], [0.0,1.0], [0.0,0.0]]]} | null |
| {"type":"Polygon","coordinates":[[[0.0,0.0],[-182.0,89.0], [0.0,1.0], [0.0,0.0]]]} | null |

### 示例 5: 空值情况

参数值:

- 表达式:geometry
| geometry | 输出 |
| --- | --- |
| {"type":"Polygon","coordinates":[[]]} | null |
| {"type":"MultiPolygon","coordinates":[[[]],[[[102.0,2.0],[103.0,2.0],[103.0,3.0],[102.0,3.0],[102.0,2.0]]]]} | null |

### 示例 6: 边缘情况

参数值:

- 表达式:geometry
| geometry | 输出 |
| --- | --- |
| {"coordinates": [[[-191.9065788394177,5.453742403668187],[-191.9065788394177,-11.163604962907428],[-... | {"type":"MultiPolygon","coordinates":[[[[-180.0,-11.163604962907428],[-180.0,5.453742403668187],[-15... |

### 示例 7: 边缘情况

参数值:

- 表达式:geometry
| geometry | 输出 |
| --- | --- |
| {"type":"LineString","coordinates":[[1.0, 1.0], [1.0, 1.0], [1.0, 1.0]]} | {"type":"Point","coordinates":[1.0, 1.0]} |

### 示例 8: 边缘情况

参数值:

- 表达式:geometry
| geometry | 输出 |
| --- | --- |
| {"type":"MultiPolygon","coordinates":[[[[0.0,0.0],[1.0,0.0],[0.0,0.0]]],[[[102.0,2.0],[103.0,2.0],[103.0,3.0],[102.0,3.0],[102.0,2.0]]]]} | {"geometries":[{"coordinates":[[0.0, 0.0], [1.0, 0.0]], "type":"LineString"},{"coordinates... |
