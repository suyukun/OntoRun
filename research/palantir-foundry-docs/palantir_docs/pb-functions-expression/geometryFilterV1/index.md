来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/geometryFilterV1/

# 以几何类型筛选

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 以几何类型筛选

> 支持于: 批处理，流处理

支持于: 批处理，流处理

将几何列中不属于提供的几何类型的任何值设为空。

表达式类别: 地理空间

## 声明参数

- 表达式- 要筛选的几何列。Expression<Geometry>
- 几何类型- 要保留的几何类型集合。Set<Enum<Feature, FeatureCollection, GeometryCollection, LineString, MultiLineString, MultiPoint, MultiPolygon, Point, Polygon>>
输出类型:Geometry

## 示例

### 示例 1: 基本情况

参数值:

- 表达式:geometry
- 几何类型: {POINT}
| geometry | 输出 |
| --- | --- |
| {"type":"Point","coordinates": [32.0, 58.0]} | {"type":"Point","coordinates": [32.0, 58.0]} |

### 示例 2: 基本情况

参数值:

- 表达式:geometry
- 几何类型: {POINT}
| geometry | 输出 |
| --- | --- |
| {"type":"LineString","coordinates":[[-112.94377956164206,34.81725414459382],[-112.94377956164206,30.006795384733323]]} | null |

### 示例 3: 基本情况

参数值:

- 表达式:geometry
- 几何类型: {LINESTRING}
| geometry | 输出 |
| --- | --- |
| {"type":"LineString","coordinates":[[-112.94377956164206,34.81725414459382],[-112.94377956164206,30.006795384733323]]} | {"type":"LineString","coordinates":[[-112.94377956164206,34.81725414459382],[-112.94377956164206,30.006795384733323]]} |
| {"type": "GeometryCollection","geometries": [{"type":"LineString","coordinates":[[-77.07368071728229... | null |

### 示例 4: 基本情况

参数值:

- 表达式:geometry
- 几何类型: {LINESTRING,POINT}
| geometry | 输出 |
| --- | --- |
| {"type":"LineString","coordinates":[[-112.94377956164206,34.81725414459382],[-112.94377956164206,30.006795384733323]]} | {"type":"LineString","coordinates":[[-112.94377956164206,34.81725414459382],[-112.94377956164206,30.006795384733323]]} |
| {"type":"Point","coordinates": [32.0, 58.0]} | {"type":"Point","coordinates": [32.0, 58.0]} |

### 示例 5: 空情况

参数值:

- 表达式:geometry
- 几何类型: {POINT}
| geometry | 输出 |
| --- | --- |
| null | null |
