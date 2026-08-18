来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/pivotExpressionV1/

# 透视

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 透视

> 支持于: 流式处理

支持于: 流式处理

在透视上下文中应用聚合表达式。聚合将在透视表达式的每个不同值范围内作为一组单独的聚合运行。输出是从透视值到聚合表达式值的映射。

表达式类别: 聚合

## 声明的参数

- 聚合表达式- 要应用的聚合表达式。Expression<V>
- 透视表达式- 要应用的透视表达式。Expression<K>
类型变量界限:K 接受 ComparableType**V 接受 AnyType

输出类型:Map<K, V>

## 示例

### 示例 1: 基本情况

参数值:

- 聚合表达式:sum(expression:value,)
- 透视表达式:pivot
给定输入表:

| pivot | value |
| --- | --- |
| a | 1 |
| b | 2 |
| a | 3 |

输出:{a -> 4,b -> 2,}

### 示例 2: 基本情况

参数值:

- 聚合表达式:sum(expression:value,)
- 透视表达式:cleanString(cleanActions: {trim},expression:pivot,)
给定输入表:

| pivot | value |
| --- | --- |
| a | 1 |
| b | 2 |
| a | 3 |

输出:{a -> 4,b -> 2,}
