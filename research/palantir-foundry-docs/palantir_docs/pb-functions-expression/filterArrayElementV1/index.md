来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/filterArrayElementV1/

# 筛选数组元素

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 筛选数组元素

> 支持于：批处理，流处理

支持于：批处理，流处理

根据筛选表达式筛选数组。注意，数组索引从1开始。

表达式类别：数组

## 声明的参数

- 数组- 要筛选的数组。表达式<数组<T>>
- 筛选表达式- 如果表达式对于给定元素计算结果为true，则保留该元素，如果为false则移除该元素。表达式<Boolean>
类型变量界限：T 接受 AnyType

输出类型：数组<T>

## 示例

### 示例 1：基本情况

参数值：

- 数组：array
- 筛选表达式：isNotNull(expression:element,)
| array | 输出 |
| --- | --- |
| [ 2, 5,null, 11 ] | [ 2, 5, 11 ] |

### 示例 2：基本情况

参数值：

- 数组：array
- 筛选表达式：lessThanOrEquals(left:element,right: 10,)
| array | 输出 |
| --- | --- |
| [ 2, 5,null, 11 ] | [ 2, 5 ] |

### 示例 3：基本情况

参数值：

- 数组：array
- 筛选表达式：lessThanOrEquals(left:element,right: 10,)
| array | 输出 |
| --- | --- |
| [ 2, 5, 7, 11, 12, 15 ] | [ 2, 5, 7 ] |

### 示例 4：基本情况

描述：注意数组索引从1开始。参数值：

- 数组：array
- 筛选表达式：equals(left:element,right:elementIndex,)
| array | 输出 |
| --- | --- |
| [ 1, -1, -2, 4, -5 ] | [ 1, 4 ] |

### 示例 5：基本情况

参数值：

- 数组：array
- 筛选表达式：stringContains(expression:element,ignoreCase: false,value: hello,)
| array | 输出 |
| --- | --- |
| [ hello world, hello, world ] | [ hello world, hello ] |

### 示例 6：基本情况

参数值：

- 数组：array
- 筛选表达式：lessThanOrEquals(left:add(expressions: [element, 4],),right: 10,)
| array | 输出 |
| --- | --- |
| [ 2, 5, 7, 11, 12, 15 ] | [ 2, 5 ] |

### 示例 7：空情况

参数值：

- 数组：array
- 筛选表达式：lessThanOrEquals(left:element,right: 10,)
| array | 输出 |
| --- | --- |
| null | null |
