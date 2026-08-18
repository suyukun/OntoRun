来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/epochSecondsToTimestampV1/

# 从纪元秒到时间戳

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 从纪元秒到时间戳

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

将纪元秒转换为UTC时间戳。

表达式类别: 转换, 日期时间

## 声明的参数

- 表达式-无描述表达式<Double | Integer | Long>
输出类型:时间戳

## 示例

### 示例 1: 基本情况

描述: 您可以将纪元时间戳转换为时间戳类型参数值:

- 表达式: 1673964111
输出:2023-01-17T14:01:51Z

### 示例 2: 空值情况

描述: 空列保持为空参数值:

- 表达式:input
| input | 输出 |
| --- | --- |
| null | null |
