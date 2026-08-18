来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/aggregateV1/

# 聚合

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 聚合

> 支持于: 批处理

支持于: 批处理

对输入数据集执行指定的聚合，以一组列进行分组。

变换类别: 聚合, 热门

## 声明参数

- 聚合- 要在数据集上执行的聚合列表。List<Expression<AnyType>>
- 数据集- 要进行聚合的数据集。Table
- 非必填按列分组- 聚合时用于分组数据集的列列表。如果为空，则不应用分组。List<Column<AnyType>>
## 示例

### 示例 1: 基本情况

参数值:

- 聚合: [alias(alias: factor,expression:sum(expression:factor,),)]
- 数据集: ri.foundry.main.dataset.aggregate
- 按列分组: [tail_number]
输入:

| tail_number | airline | miles | factor |
| --- | --- | --- | --- |
| XB-123 | foundry air | 124 | 2 |
| MT-222 | new airline | 1123 | 5 |
| XB-123 | foundry airline | 335 | 5 |
| MT-222 | new air | 565 | 4 |
| KK-452 | new air | 222 | 1 |
| XB-123 | foundry airline | 1134 | 3 |

输出:

| tail_number | factor |
| --- | --- |
| XB-123 | 10 |
| MT-222 | 9 |
| KK-452 | 1 |
