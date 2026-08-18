来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/applyExpressionV1/

# 应用表达式

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 应用表达式

> 支持于: 批处理，流处理

支持于: 批处理，流处理

通过应用单个表达式变换输入数据集。

变换类别: 其它

## 声明的参数

- 数据集- 需要应用表达式的数据集。Table
- 表达式- 要应用的表达式。Expression<AnyType>
## 示例

### 示例 1: 基本案例

参数值:

- 数据集: ri.foundry.main.dataset.a
- 表达式:alias(alias: kilometers,expression:convertDistance(amount:miles,currentUnit:mile,targetUnit:kilometer,),)
输入:

| airline | miles |
| --- | --- |
| foundry airways | 2500 |
| new air | 3000 |

输出:

| kilometers | airline | miles |
| --- | --- | --- |
| 4023.36 | foundry airways | 2500 |
| 4828.03 | new air | 3000 |
