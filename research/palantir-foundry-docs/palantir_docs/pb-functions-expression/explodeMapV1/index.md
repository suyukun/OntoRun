来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/explodeMapV1/

# 展开映射

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 展开映射

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

将映射展开为每个键值对一行。

表达式类别: 映射

## 声明的参数

- 表达式-无描述表达式<映射<TKey, TValue>>
类型变量界限:TKey 接受 AnyType**TValue 接受 AnyType

输出类型:结构<非必填[key], 非必填[value]>
