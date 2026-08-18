来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/arrayContainsNullV1/

# 数组包含null

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 数组包含null

> 支持于：批处理，流处理

支持于：批处理，流处理

如果array包含null，返回true。

表达式类别：数组，布尔值

## 声明的参数

- 表达式- 一个可能包含null值的数组。Expression<Array<ComparableType>>
输出类型：布尔值

## 示例

### 示例 1：基本情况

参数值：

- 表达式:part_ids
| part_ids | 输出 |
| --- | --- |
| [ AWE-112, BRR-123,null] | true |
| [ AWE-222, ABC-543 ] | false |

### 示例 2：Null情况

参数值：

- 表达式:part_ids
| part_ids | 输出 |
| --- | --- |
| null | false |
| [ AWE-222, ABC-543 ] | false |

### 示例 3：边缘情况

参数值：

- 表达式:part_ids
| part_ids | 输出 |
| --- | --- |
| [  ] | false |
