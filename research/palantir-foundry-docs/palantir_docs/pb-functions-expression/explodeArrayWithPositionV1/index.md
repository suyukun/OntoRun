来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/explodeArrayWithPositionV1/

# 位置展开数组

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 位置展开数组

> 支持于: 批处理, 流式处理

支持于: 批处理, 流式处理

将数组展开为每个值一行，作为包含元素在数组中的相对位置和元素本身的结构。

表达式类别: 数组

## 声明的参数

- 数组- 要展开的值数组。Expression<Array<T>>
- 非必填保留空/空值数组 - 如果为true，空数组和空值将在输出中保留为空值，否则将被筛选。Literal<Boolean>
类型变量界限：T接受AnyType

输出类型：Struct<非必填[position], 非必填[element]>
