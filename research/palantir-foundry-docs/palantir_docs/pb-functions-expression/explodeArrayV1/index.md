来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/explodeArrayV1/

# 拆分数组

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 拆分数组

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

将数组拆分为每个值的一行。

表达式类别: 数组

## 声明的参数

- 表达式-无描述Expression<Array<T>>
- 非必填保留空/空值数组- 如果为true，空数组和空值将在输出中保留为空值，否则它们将被筛选。Literal<Boolean>
类型变量界限:T 接受 AnyType

输出类型:T
