来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/transformMapKeysV1/

# 变换映射键

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 变换映射键

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

通过对每个键值对应用表达式来变换映射的键。

表达式类别: 映射

## 声明的参数

- 要应用的表达式。- 对映射的每个键值对应用一次的表达式。Expression<K>
- 映射- 映射表达式。Expression<Map<AnyType, V>>
类型变量界限:K 接受 AnyType**V 接受 AnyType

输出类型:Map<K, V>

## 示例

### 示例 1: 基础案例

参数值:

- 要应用的表达式。:stringBeforeDelimiter(delimiter: -,expression:key,ignoreCase: false,)
- 映射:flight_number
| flight_number | 输出 |
| --- | --- |
| {MT-111 -> 2,XB-134 -> 1,} | {MT -> 2,XB -> 1,} |

### 示例 2: 基础案例

参数值:

- 要应用的表达式。:cast(expression:key,type: Integer,)
- 映射:flight_number
| flight_number | 输出 |
| --- | --- |
| {11 -> 1,22 -> 2,} | {11 -> 1,22 -> 2,} |

### 示例 3: 基础案例

参数值:

- 要应用的表达式。:cast(expression:value,type: 字符串,)
- 映射:flight_number
| flight_number | 输出 |
| --- | --- |
| {11 -> 1,22 -> 2,} | {1 -> 1,2 -> 2,} |

### 示例 4: 基础案例

参数值:

- 要应用的表达式。:concatStrings(expressions: [stringBeforeDelimiter(delimiter: -,expression:key,ignoreCase: false,),value],separator: -,)
- 映射:flight_number
| flight_number | 输出 |
| --- | --- |
| {MT-111 -> BB,XB-134 -> AA,} | {MT-BB -> BB,XB-AA -> AA,} |
