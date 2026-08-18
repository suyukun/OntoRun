来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/dropV1/

# 删除列

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 删除列

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

通过删除指定列来变换输入数据集。

变换类别: 热门

## 声明的参数

- 要删除的列- 要删除的列列表。Set<Column<AnyType>>
- 数据集- 要从中删除列的数据集。Table
## 示例

### 示例 1: 基本情况

参数值:

- 要删除的列: {miles}
- 数据集: ri.foundry.main.dataset.a
输入:

| airline | miles | airports |
| --- | --- | --- |
| foundry airways | 3000 | [ JFK, SFO ] |

输出:

| airline | airports |
| --- | --- |
| foundry airways | [ JFK, SFO ] |
