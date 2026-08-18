来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/complexCrossJoinV1/

# 笛卡尔积合并

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 笛卡尔积合并

> 支持于: 批处理

支持于: 批处理

笛卡尔积合并将左侧和右侧数据集输入合并在一起，将每一侧的所有行与另一侧的所有行匹配。输出是两个数据集的笛卡尔积。

变换类别: 合并

## 声明的参数

- 选择左侧列的条件- 将测试左侧输入模式中的所有列以查看它们是否满足此条件。如果满足，列将在输出中被选择。ColumnPredicate
- 选择右侧列的条件- 将测试右侧输入模式中的所有列以查看它们是否满足此条件。如果满足，列将在输出中被选择。ColumnPredicate
- 左侧数据集- 用于合并的左侧数据集。Table
- 右侧数据集- 用于合并的右侧数据集。Table
- 非必填右侧列的前缀- 添加到右侧所有列的前缀。Literal<字符串>
## 示例

### 示例 1: 基本情况

参数值:

- 选择左侧列的条件:columnNameIsIn(columnNames: [tail_number, airline],)
- 选择右侧列的条件:columnNameIsIn(columnNames: [home_airport],)
- 左侧数据集: ri.foundry.main.dataset.left
- 右侧数据集: ri.foundry.main.dataset.right
- 右侧列的前缀:null
输入:ri.foundry.main.dataset.left

| tail_number | airline | miles | factor |
| --- | --- | --- | --- |
| XB-123 | foundry air | 124 | 2 |
| MT-222 | new airline | 1123 | 5 |
| PA-452 | new air | 212 | 2 |

ri.foundry.main.dataset.right

| tail_number | home_airport |
| --- | --- |
| XB-123 | LHR |
| MT-222 | CPH |
| KK-452 | JFK |
| JR-201 | IAD |

输出:

| tail_number | airline | home_airport |
| --- | --- | --- |
| XB-123 | foundry air | LHR |
| XB-123 | foundry air | CPH |
| XB-123 | foundry air | JFK |
| XB-123 | foundry air | IAD |
| MT-222 | new airline | LHR |
| MT-222 | new airline | CPH |
| MT-222 | new airline | JFK |
| MT-222 | new airline | IAD |
| PA-452 | new air | LHR |
| PA-452 | new air | CPH |
| PA-452 | new air | JFK |
| PA-452 | new air | IAD |

### 示例 2: 基本情况

参数值:

- 选择左侧列的条件:allColumns()
- 选择右侧列的条件:columnNameIsIn(columnNames: [home_airport],)
- 左侧数据集: ri.foundry.main.dataset.left
- 右侧数据集: ri.foundry.main.dataset.right
- 右侧列的前缀:null
输入:ri.foundry.main.dataset.left

| tail_number | airline | miles | factor |
| --- | --- | --- | --- |
| XB-123 | foundry air | 124 | 2 |
| MT-222 | new airline | 1123 | 5 |
| PA-452 | new air | 212 | 2 |

ri.foundry.main.dataset.right

| tail_number | home_airport |
| --- | --- |
| XB-123 | LHR |
| MT-222 | CPH |
| KK-452 | JFK |
| JR-201 | IAD |

输出:

| tail_number | airline | miles | factor | home_airport |
| --- | --- | --- | --- | --- |
| XB-123 | foundry air | 124 | 2 | LHR |
| XB-123 | foundry air | 124 | 2 | CPH |
| XB-123 | foundry air | 124 | 2 | JFK |
| XB-123 | foundry air | 124 | 2 | IAD |
| MT-222 | new airline | 1123 | 5 | LHR |
| MT-222 | new airline | 1123 | 5 | CPH |
| MT-222 | new airline | 1123 | 5 | JFK |
| MT-222 | new airline | 1123 | 5 | IAD |
| PA-452 | new air | 212 | 2 | LHR |
| PA-452 | new air | 212 | 2 | CPH |
| PA-452 | new air | 212 | 2 | JFK |
| PA-452 | new air | 212 | 2 | IAD |
