来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/parseGeoJsonAsGeometryV1/

# 从非WGS 84坐标系解析GeoJSON

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 从非WGS 84坐标系解析GeoJSON

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

将GeoJSON字符串从非WGS 84坐标系转换为WGS 84几何。对于已经在WGS 84（经度, 纬度）的GeoJSON，“逻辑类型转换”表达式可以直接转换，开销更小。解析或转换过程中失败的字符串返回null。

表达式类别: 地理空间

## 声明的参数

- GeoJSON字符串- 作为字符串的GeoJSON。请注意，并非所有GeoJSON字符串都可以被Ontology索引；使用“规范化几何”表达式在Ontology使用之前准备几何。Expression<字符串>
- 源坐标系- 以“authority”格式的坐标系标识符。例如，UTM 18N区可以通过EPSG:32618标识。Literal<字符串>
输出类型:Geometry

## 示例

### 示例 1: 基本情况

参数值:

- GeoJSON字符串:geojson_string
- 源坐标系: EPSG:32618
| geojson_string | 输出 |
| --- | --- |
| {"type":"Point","coordinates":[320000.0,4300000.0]} | {"type":"Point","coordinates":[-77.07368071728229,38.83040844313318]} |
| {"type":"LineString","coordinates":[[320000.0,4300000.0],[320100.0,4300000.0]]} | {"type":"LineString","coordinates":[[-77.07368071728229,38.83040844313318],[-77.0725293738795,38.83042888342659]]} |
| {"type":"Polygon","coordinates":[[[320000.0,4300000.0],[320100.0,4300000.0],[320000.0,4300100.0],[320000.0,4300000.0]]]} | {"type":"Polygon","coordinates":[[[-77.07368071728229,38.83040844313318],[-77.0725293738795,38.83042888342659],[-77.07370685720375,38.83130901341597],[-77.07368071728229,38.83040844313318]]]} |

### 示例 2: 空值情况

参数值:

- GeoJSON字符串:geojson_string
- 源坐标系: EPSG:32618
| geojson_string | 输出 |
| --- | --- |
| null | null |

### 示例 3: 边缘情况

参数值:

- GeoJSON字符串:geojson_string
- 源坐标系: EPSG:32618
| geojson_string | 输出 |
| --- | --- |
| invalid geojson string | null |
