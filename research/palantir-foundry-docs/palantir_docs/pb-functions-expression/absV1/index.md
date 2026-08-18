来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/absV1/

# 绝对值

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 绝对值

> 支持于：批处理，流处理

支持于：批处理，流处理

返回绝对值。

表达式类别：数值

## 声明的参数

- 表达式- 计算此表达式的绝对值。表达式<T>
类型变量界限:T 接受数值

输出类型:T

## 示例

### 示例 1：基本情况

参数值：

- 表达式:numeric_column
| numeric_column | 输出 |
| --- | --- |
| 0.0 | 0.0 |
| 1.1 | 1.1 |
| -1.1 | 1.1 |

### 示例 2：空值情况

参数值：

- 表达式:numeric_column
| numeric_column | 输出 |
| --- | --- |
| null | null |
