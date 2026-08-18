来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/isValidRidV1/

# 是否为有效的rid

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 是否为有效的rid

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

如果输入是有效的Foundry资源标识符，则返回true。

表达式类别: 布尔值

## 声明的参数

- 表达式- 表示资源标识符的字符串。Expression<字符串>
输出类型:布尔值

## 例子

### 例子 1: 基本情况

参数值:

- 表达式:rid
| rid | 输出 |
| --- | --- |
| ri.foundry.main.dataset.e9008fee-a32a-449d-8ab4-d6d65a3b4ecc | true |
| ri.foundry.main.transaction.00000049-8fbb-6a15-bd27-9f2c9ae9a47b | true |
| ri.foundry.malformed | false |
| not a rid | false |
