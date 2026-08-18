来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/extractMapValuesV1/

# 提取映射值

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 提取映射值

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

将映射值返回为数组。请注意，数组元素的顺序是不确定的。

表达式类别: 映射

## 声明的参数

- 映射- 映射表达式。表达式<映射<任意类型, V>>
类型变量界限:V 接受任意类型

输出类型:数组<V>

## 示例

### 示例 1: 基本情况

参数值:

- 映射:flight_number
| flight_number | 输出 |
| --- | --- |
| {MT-111 -> 2,XB-134 -> 1,} | [ 1, 2 ] |

### 示例 2: 空值情况

参数值:

- 映射:flight_number
| flight_number | 输出 |
| --- | --- |
| {MT-111 -> 2,XB-134 ->null,} | [null, 2 ] |
| null | null |
