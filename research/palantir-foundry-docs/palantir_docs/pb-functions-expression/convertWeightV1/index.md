来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/convertWeightV1/

# 在重量单位之间转换

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 在重量单位之间转换

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

表达式类别: 数值

## 声明的参数

- 当前单位的数量-无描述Expression<DefiniteNumeric>
- 当前单位- 转换前的单位。Enum<Centigram, Decagram, Decigram, Grain, Gram, Hectogram, Kilogram, Long hundredweight, Megagram, Metric ton, and more ...>
- 目标单位- 转换后的期望单位。Enum<Centigram, Decagram, Decigram, Grain, Gram, Hectogram, Kilogram, Long hundredweight, Megagram, Metric ton, and more ...>
输出类型:Double

## 示例

### 示例 1: 基本情况

参数值:

- 当前单位的数量:kilograms
- 当前单位:kilogram
- 目标单位:gram
| kilograms | 输出 |
| --- | --- |
| 5 | 5000.0 |

### 示例 2: 基本情况

参数值:

- 当前单位的数量:kilograms
- 当前单位:kilogram
- 目标单位:gram
| kilograms | 输出 |
| --- | --- |
| null | null |
