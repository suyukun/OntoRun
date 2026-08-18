来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/transformArrayElementV1/

# 变换数组元素

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 变换数组元素

> 支持于: 批处理，流处理

支持于: 批处理，流处理

使用表达式映射数组的每个元素。注意，数组索引从1开始。

表达式类别: 数组

## 声明的参数

- 数组- 包含要应用表达式的元素的输入数组。Expression<Array<AnyType>>
- 要应用的表达式。- 对数组的每个元素应用一次的表达式。Expression<T>
类型变量边界:T 接受 AnyType

输出类型:Array<T>

## 示例

### 示例 1: 基本案例

参数值:

- 数组:flight_number
- 要应用的表达式。:stringBeforeDelimiter(delimiter: -,expression:element,ignoreCase: false,)
| flight_number | 输出 |
| --- | --- |
| [ XB-134, MT-111 ] | [ XB, MT ] |

### 示例 2: 基本案例

参数值:

- 数组:miles
- 要应用的表达式。:add(expressions: [previous_miles,element],)
| miles | previous_miles | 输出 |
| --- | --- | --- |
| [ 12300, 12342 ] | 10000 | [ 22300, 22342 ] |

### 示例 3: 基本案例

描述: 将索引添加到数组元素。注意索引从1开始。参数值:

- 数组:array
- 要应用的表达式。:add(expressions: [elementIndex,element],)
| array | 输出 |
| --- | --- |
| [ 1, 1, 1 ] | [ 2, 3, 4 ] |

### 示例 4: 基本案例

参数值:

- 数组:miles
- 要应用的表达式。:cast(expression:element,type: 字符串,)
| miles | 输出 |
| --- | --- |
| [ 12300, 12342 ] | [ 12300, 12342 ] |

### 示例 5: 基本案例

描述: 从结构数组中获取结构元素。参数值:

- 数组:raw_data
- 要应用的表达式。:getStructField(locator: miles,struct:element,)
| raw_data | 输出 |
| --- | --- |
| [ {miles: 22300,tail_number: XB-112,}, {miles: 22342,tail_number: XB-112,} ] | [ 22300, 22342 ] |

### 示例 6: 基本案例

描述: 从结构数组中获取结构元素。参数值:

- 数组:raw_data
- 要应用的表达式。:transformMapKeys(expression:uppercase(expression:key,),map:element,)
| raw_data | 输出 |
| --- | --- |
| [ {miles -> 22300,tail_number -> XB-112,}, {miles -> 22342L,tail_number -> XB-112,} ] | [ {MILES -> 22300,TAIL_NUMBER -> XB-112,}, {MILES -> 22342L,TAIL_NUMBER -> XB-112,} ] |
