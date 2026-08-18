来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/latLonBoundingBoxV1/

# 获取纬度/经度边界框结构

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 获取纬度/经度边界框结构

> 支持于: 批处理，流处理

支持于: 批处理，流处理

给定一个有效的几何体或几何体数组，返回一个包含几何体或几何体边界的结构。

表达式类别: 地理空间

## 声明的参数

- 表达式- GeoJSON字符串或GeoJSON字符串数组。Expression<Array<Geometry> | Geometry>
输出类型:LatLonBoundingBox

## 示例

### 示例 1: 基本情况

参数值:

- 表达式:geometry
| geometry | 输出 |
| --- | --- |
| {"type":"Polygon","coordinates":[[[0.0,0.0],[1.0,0.0],[0.0,1.0]]]} | {maxLat -> 1.0,maxLon -> 1.0,minLat -> 0.0,minLon -> 0.0,} |

### 示例 2: 基本情况

参数值:

- 表达式:geometryArray
| geometryArray | 输出 |
| --- | --- |
| [ {"type":"LineString","coordinates":[[1,0],[0,8.4]]}, {"type":"Point","coordinates":[125.6, -92.3]}, {"type":"Polygon","coordinates":[[[0,0],[1,6.3],[-6,1],[0,0]]]} ] | {maxLat -> 8.4,maxLon -> 125.6,minLat -> -92.3,minLon -> -6.0,} |

### 示例 3: 空情况

参数值:

- 表达式:geometryArray
| geometryArray | 输出 |
| --- | --- |
| null | null |

### 示例 4: 边缘情况

参数值:

- 表达式:geometryArray
| geometryArray | 输出 |
| --- | --- |
| [ Invalid GeoJSON, {"type":"LineString","coordinates":[[2,0],[0,4.8]]} ] | {maxLat -> 4.8,maxLon -> 2.0,minLat -> 0.0,minLon -> 0.0,} |
