来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/epochSecondsToDateV1/

# Epoch秒数到日期

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Epoch秒数到日期

> 支持于：批处理，流处理

支持于：批处理，流处理

将Epoch秒数转换为UTC日期。

表达式类别：类型转换，日期时间

## 声明的参数

- 表达式- Epoch秒数表达式。表达式<Double | Integer | Long>
输出类型：日期

## 示例

### 示例1：基本情况

描述：您可以将Epoch时间戳转换为日期类型参数值：

- 表达式: 1673964111
输出：2023-01-17

### 示例2：空值情况

描述：空列保持为空参数值：

- 表达式:input
| 输入 | 输出 |
| --- | --- |
| null | null |
