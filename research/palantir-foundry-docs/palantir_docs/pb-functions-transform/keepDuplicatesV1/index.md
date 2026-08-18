来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/keepDuplicatesV1/

# 保留重复项

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 保留重复项

> 支持于: 批处理

支持于: 批处理

从输入中保留重复行。

变换类别: 其他

## 声明的参数

- 列子集- 如果指定了任何列，仅在确定唯一性时使用这些列。Set<Column<AnyType>>
- 数据集- 要保留重复行的数据集。Table
## 示例

### 示例 1: 基本情况

参数值:

- 列子集: {tail_number}
- 数据集: ri.foundry.main.dataset.aggregate
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

| tail_number | airline | miles | factor |
| --- | --- | --- | --- |
| XB-123 | foundry air | 124 | 2 |
| MT-222 | new airline | 1123 | 5 |
| XB-123 | foundry airline | 335 | 5 |
| MT-222 | new air | 565 | 4 |
| XB-123 | foundry airline | 1134 | 3 |

### 示例 2: 基本情况

描述: 无子集查找精确重复项。参数值:

- 列子集: {}
- 数据集: ri.foundry.main.dataset.aggregate
输入:

| tail_number | airline | miles | factor |
| --- | --- | --- | --- |
| XB-123 | foundry air | 124 | 2 |
| XB-123 | foundry air | 124 | 2 |
| XB-123 | foundry air | 124 | 2 |
| MT-222 | new airline | 1123 | 6 |
| MT-222 | new airline | 1123 | 5 |

输出:

| tail_number | airline | miles | factor |
| --- | --- | --- | --- |
| XB-123 | foundry air | 124 | 2 |
| XB-123 | foundry air | 124 | 2 |
| XB-123 | foundry air | 124 | 2 |

### 示例 3: 空值情况

参数值:

- 列子集: {tail_number}
- 数据集: ri.foundry.main.dataset.aggregate
输入:

| tail_number | airline | miles | factor |
| --- | --- | --- | --- |
| null | foundry air | 124 | 2 |
| null | new airline | 1123 | 5 |
| null | foundry airline | 335 | 5 |
| MT-222 | new air | 565 | 4 |
| KK-452 | new air | 222 | 1 |
| XB-123 | foundry airline | 1134 | 3 |

输出:

| tail_number | airline | miles | factor |
| --- | --- | --- | --- |
| null | foundry air | 124 | 2 |
| null | new airline | 1123 | 5 |
| null | foundry airline | 335 | 5 |
