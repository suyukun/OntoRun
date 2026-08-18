来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/geoPointToMgrsV1/

# 将GeoPoint转换为MGRS

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 将GeoPoint转换为MGRS

> 支持于：批处理，流处理

支持于：批处理，流处理

将遵循WGS84坐标系统（即EPSG:4326）的GeoPoint转换为MGRS（军事网格参考系统）坐标。输出的MGRS将采用以空格分隔的格式，精确到5位数字。

表达式类别：地理空间

## 声明的参数

- 表达式- 要转换的GeoPoint。Expression<GeoPoint>
输出类型：MGRS

## 示例

### 示例 1：基本情况

参数值：

- 表达式:geoPoint
| geoPoint | 输出 |
| --- | --- |
| {latitude -> 88.99999659707431,longitude -> 0.9996456505181999,} | Z AF 01937 88990 |

### 示例 2：基本情况

参数值：

- 表达式:geoPoint
| geoPoint | 输出 |
| --- | --- |
| {latitude -> 21.409796671597924,longitude -> -157.91608117421092,} | 4Q FJ 12345 67889 |
| {latitude -> 21.338665624760598,longitude -> -157.93921670599434,} | 4Q FJ 10000 59999 |
| {latitude -> 21.40898645576642,longitude -> -157.91652127483704,} | 4Q FJ 12300 67799 |

### 示例 3：空值情况

参数值：

- 表达式:geoPoint
| geoPoint | 输出 |
| --- | --- |
| null | null |
