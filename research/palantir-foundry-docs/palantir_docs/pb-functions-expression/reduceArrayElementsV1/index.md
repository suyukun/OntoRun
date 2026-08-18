来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/reduceArrayElementsV1/

# 缩减数组元素

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 缩减数组元素

> 支持于: 批处理, 流式处理

支持于: 批处理, 流式处理

使用表达式缩减数组元素。

表达式类别: 数组

## 声明的参数

- 数组- 要缩减的数组。Expression<Array<Array<Boolean | Byte | Date | Double | Float | Integer | Long | Map<AnyType, AnyType> | Short | 字符串 | Timestamp> | Boolean | Byte | Date | Double | Float | Integer | Long | Map<AnyType, AnyType> | Short | 字符串 | Timestamp>>
- 缩减的表达式- 每个数组元素应用一次的表达式。Expression<T>
- 初始值- 用于初始化累加器的起始值，如果数组长度为0，则返回此值。Expression<T>
类型变量界限:T 接受 Array<Boolean | Byte | Date | Double | Float | Integer | Long | Map<AnyType, AnyType> | Short | 字符串 | Timestamp> | Boolean | Byte | Date | Double | Float | Integer | Long | Map<AnyType, AnyType> | Short | 字符串 | Timestamp

输出类型:T

## 示例

### 示例 1: 基本案例

参数值:

- 数组:miles
- 缩减的表达式:add(expressions: [accumulator,element],)
- 初始值: 0
| miles | 输出 |
| --- | --- |
| [ 12300, 12342 ] | 24642 |

### 示例 2: 基本案例

描述: 返回数组中第一个非空元素。参数值:

- 数组:miles
- 缩减的表达式:firstNonNull(expressions: [accumulator,element],)
- 初始值:init
| miles | init | 输出 |
| --- | --- | --- |
| [null,null, 12300, 12111 ] | null | 12300 |

### 示例 3: 基本案例

参数值:

- 数组:miles
- 缩减的表达式:concatStrings(expressions: [accumulator,cast(expression:element,type: 字符串,)],separator: -,)
- 初始值:空字符串
| miles | 输出 |
| --- | --- |
| [ 12300, 12342 ] | -12300-12342 |

### 示例 4: 空案例

描述: 空数组将返回空输出。参数值:

- 数组:miles
- 缩减的表达式:firstNonNull(expressions: [accumulator,element],)
- 初始值:init
| miles | init | 输出 |
| --- | --- | --- |
| null | null | null |

### 示例 5: 边缘案例

描述: 空数组将返回初始值。参数值:

- 数组:miles
- 缩减的表达式:add(expressions: [accumulator,element],)
- 初始值: 0
| miles | 输出 |
| --- | --- |
| [  ] | 0 |
