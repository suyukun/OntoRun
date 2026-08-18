来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/constructGeoPointV1/

# 构建 GeoPoint 列

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 构建 GeoPoint 列

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

从纬度和经度列构建 GeoPoint 列。验证纬度参数是否在-90和90之间（包括边界），以及经度参数是否在-180和180之间（包括边界）；如果不在范围内，则返回空值。

表达式类别: 地理空间

## 声明的参数

- 纬度- 纬度列。Expression<Double>
- 经度- 经度列。Expression<Double>
输出类型:GeoPoint

## 示例

### 示例 1: 基本情况

参数值:

- 纬度:lat
- 经度:lon
| lat | lon | 输出 |
| --- | --- | --- |
| 32.0 | 58.0 | {latitude -> 32.0,longitude -> 58.0,} |
| 320.0 | 58.0 | null |
