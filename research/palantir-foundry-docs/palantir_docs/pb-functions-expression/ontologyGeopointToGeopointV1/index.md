来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/ontologyGeopointToGeopointV1/

# 从Ontology GeoPoint转换

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 从Ontology GeoPoint转换

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

将一个Ontology GeoPoint转换为一个常规GeoPoint。Ontology GeoPoint是格式为'{lat},{lon}'的字符串，其中-90 <= lat <= 90 且 -180 <= lon <= 180。常规GeoPoint是格式为{"longitude": {long},"latitude": {lat}}的结构。

表达式类别: 地理空间

## 声明的参数

- 表达式- 要转换的Ontology GeoPoint。表达式<Ontology GeoPoint>
输出类型:GeoPoint

## 例子

### 例子 1: 基本情况

参数值:

- 表达式:geopoint
| geopoint | 输出 |
| --- | --- |
| -20.0000000,80.0000000 | {latitude: -20.0,longitude: 80.0,} |
| 38.9031000,-77.0599000 | {latitude: 38.9031,longitude: -77.0599,} |
| 41.9876543,-99.1234568 | {latitude: 41.9876543,longitude: -99.1234568,} |

### 例子 2: 空值情况

参数值:

- 表达式:geopoint
| geopoint | 输出 |
| --- | --- |
| 38.9031000, 41.9876543, 80.0000000 | null |
| A, 41.9876543 | null |
| this is a, test string | null |
| null | null |
