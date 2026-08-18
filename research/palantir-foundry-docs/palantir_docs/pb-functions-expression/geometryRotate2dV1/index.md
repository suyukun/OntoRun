来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/geometryRotate2dV1/

# 几何旋转2D

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 几何旋转2D

> 支持于: 流式

支持于: 流式

将提供的几何图形以提供的GeoPoint为中心进行顺时针二维旋转。此旋转发生在提供的坐标参考系中，然后投影回WGS84。

表达式类别: 地理空间

## 声明的参数

- 角度（度）- 顺时针旋转的角度（度）。Literal<Double>
- 中心GeoPoint- 旋转围绕发生的中心GeoPoint。假定为WGS84。Expression<GeoPoint>
- 几何列- 应用旋转的几何图形。Expression<Geometry>
- 投影坐标系统- 格式为"authority"的坐标系统标识符。例如，UTM带18N可通过EPSG:32618识别。几何图形将被投影到源坐标系统，应用旋转，然后投影回WGS84。Literal<字符串>
输出类型:Geometry

## 示例

### 示例 1: 基本案例

参数值:

- 角度（度）: 90.0
- 中心GeoPoint:geoPoint
- 几何列:geometry
- 投影坐标系统: EPSG:4326
| geometry | geoPoint | 输出 |
| --- | --- | --- |
| {"type":"Point","coordinates":[1.0, 0.0]} | {latitude -> 0.0,longitude -> 0.0,} | {"type":"Point","coordinates":[6.123233995736766E-17, -1.0]} |

### 示例 2: 基本案例

参数值:

- 角度（度）: 270.0
- 中心GeoPoint:geoPoint
- 几何列:geometry
- 投影坐标系统: EPSG:32618
| geometry | geoPoint | 输出 |
| --- | --- | --- |
| {"type":"Point","coordinates":[-77.0, 20.0]} | {latitude -> 22.0,longitude -> -76.0,} | {"type":"Point","coordinates":[-73.8719606865239, 21.041418391118174]} |

### 示例 3: 基本案例

参数值:

- 角度（度）: 180.0
- 中心GeoPoint:geoPoint
- 几何列:geometry
- 投影坐标系统: EPSG:4326
| geometry | geoPoint | 输出 |
| --- | --- | --- |
| {"type":"LineString","coordinates":[[0.0, 0.0], [1.0, 0.0]]} | {latitude -> 1.0,longitude -> 1.0,} | {"type":"LineString","coordinates":[[2.0, 2.0], [0.9999999999999999, 2.0]]} |

### 示例 4: 空案例

参数值:

- 角度（度）: 90.0
- 中心GeoPoint:geoPoint
- 几何列:geometry
- 投影坐标系统: EPSG:4326
| geometry | geoPoint | 输出 |
| --- | --- | --- |
| null | null | null |
