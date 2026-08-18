来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/epochMillisToDateV1/

# Epoch 毫秒到日期

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Epoch 毫秒到日期

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

将 epoch 毫秒转换为日期，UTC。

表达式类别: 转换, 日期时间

## 声明的参数

- 表达式- Epoch 毫秒表达式。表达式<Double | Long>
输出类型:日期

## 示例

### 示例 1: 基本情况

描述: 你可以将以毫秒为单位的 epoch 时间戳转换为日期类型参数值:

- 表达式: 1673964111000
输出:2023-01-17

### 示例 2: 空值情况

描述: 空列保持为空参数值:

- 表达式:input
| input | 输出 |
| --- | --- |
| null | null |
