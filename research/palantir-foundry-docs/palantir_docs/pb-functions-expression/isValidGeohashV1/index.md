来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/isValidGeohashV1/

# 是否为有效的Geohash

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 是否为有效的Geohash

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

如果输入是有效的Geohash输入字符串，则返回true。

表达式类别: 地理空间

## 声明的参数

- 表达式- 要检查的Geohash。Expression<字符串>
输出类型:布尔值

## 示例

### 示例 1: 基本案例

参数值:

- 表达式:geohash
| geohash | 输出 |
| --- | --- |
| sk4d | true |
| dt9zy9cg36j7 | true |
| 不是Geohash字符串 | false |
| null | false |
