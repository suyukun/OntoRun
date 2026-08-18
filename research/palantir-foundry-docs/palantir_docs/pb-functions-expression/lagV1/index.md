来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/lagV1/

# 滞后

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 滞后

> 支持于: 批处理

支持于: 批处理

返回窗口中当前行之前'滞后'的输入值。

表达式类别: 聚合

## 声明的参数

- 表达式- 滞后的表达式。Expression<T>
- 非必填默认值 - 如果在当前行之前的行数少于偏移量，则使用默认值。Literal<T>
- 非必填滞后 - 滞后的行数。Literal<Integer>
类型变量界限:T 接受 AnyType

输出类型:T
