来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/transformMapValuesV1/

# 变换映射值

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 变换映射值

> 支持于: 批处理

支持于: 批处理

通过对每个键值对应用表达式来变换映射的值。

表达式类别: 映射

## 声明的参数

- 要应用的表达式。- 对映射的每个键值对应用一次的表达式。Expression<V>
- 映射- 映射表达式。Expression<Map<K, AnyType>>
类型变量界限：K 接受 AnyType**V 接受 AnyType

输出类型：Map<K, V>

## 示例

### 示例 1: 基本情况

参数值:

- 要应用的表达式。:stringBeforeDelimiter(delimiter: -,expression:value,ignoreCase: false,)
- 映射:flight_number
| flight_number | 输出 |
| --- | --- |
| {1 -> XB-134,2 -> MT-111,} | {1 -> XB,2 -> MT,} |

### 示例 2: 基本情况

参数值:

- 要应用的表达式。:cast(expression:value,type: Integer,)
- 映射:flight_number
| flight_number | 输出 |
| --- | --- |
| {1 -> 11,2 -> 22,} | {1 -> 11,2 -> 22,} |

### 示例 3: 基本情况

参数值:

- 要应用的表达式。:cast(expression:key,type: 字符串,)
- 映射:flight_number
| flight_number | 输出 |
| --- | --- |
| {1 -> 11,2 -> 22,} | {1 -> 1,2 -> 2,} |

### 示例 4: 基本情况

参数值:

- 要应用的表达式。:concatStrings(expressions: [stringBeforeDelimiter(delimiter: -,expression:key,ignoreCase: false,),value],separator: -,)
- 映射:flight_number
| flight_number | 输出 |
| --- | --- |
| {MT-111 -> BB,XB-134 -> AA,} | {MT-111 -> MT-BB,XB-134 -> XB-AA,} |
