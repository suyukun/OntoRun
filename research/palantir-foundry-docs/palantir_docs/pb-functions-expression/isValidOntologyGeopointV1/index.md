来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/isValidOntologyGeopointV1/

# 是否为有效的Ontology GeoPoint

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 是否为有效的Ontology GeoPoint

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

如果输入是有效的Ontology GeoPoint，则返回true。Ontology GeoPoint是格式为'{lat},{lon}'的字符串，其中-90 <= lat <= 90且-180 <= lon <= 180。

表达式类别: 地理空间

## 声明的参数

- Expression- 要测试的字符串。Expression<字符串>
输出类型:布尔值

## 示例

### 示例 1: 基础情况

参数值:

- Expression:geopoint
| geopoint | 输出 |
| --- | --- |
| -35.307428203,149.122686883 | true |
| 149.122686883,-35.307428203 | false |
| 10.0, 20.0 | true |
| 10.0,    20.0 | true |
| not a GeoPoint | false |
| null | false |
| (10.0,20.0) | false |
