来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/complexAntiJoinV1/

# 反连接

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 反连接

> 支持于: 批处理

支持于: 批处理

反连接将左侧和右侧数据集输入合并在一起，移除所有符合提供条件的行。

变换类别: 合并

## 声明的参数

- 左侧选择列的条件- 将测试左侧输入架构中的所有列是否符合此条件。如果符合，列将在输出中被选择。ColumnPredicate
- 连接条件- 用于合并的条件。Expression<Boolean>
- 左侧数据集- 在合并中使用的左侧数据集。Table
- 右侧数据集- 在合并中使用的右侧数据集。Table
## 示例

### 示例 1: 基本案例

参数值:

- 左侧选择列的条件:columnNameIsIn(columnNames: [tail_number, airline],)
- 连接条件:equals(left:tail_number,right:tail_number,)
- 左侧数据集: ri.foundry.main.dataset.left
- 右侧数据集: ri.foundry.main.dataset.right
输入:ri.foundry.main.dataset.left

| tail_number | airline | miles | factor |
| --- | --- | --- | --- |
| XB-123 | foundry air | 124 | 2 |
| MT-222 | new airline | 1123 | 5 |
| XB-123 | foundry airline | 335 | 5 |
| MT-222 | new air | 565 | 4 |
| KK-452 | new air | 222 | 1 |
| PA-452 | new air | 212 | 2 |
| XB-123 | foundry airline | 1134 | 2 |

ri.foundry.main.dataset.right

| tail_number | home_airport |
| --- | --- |
| XB-123 | LHR |
| MT-222 | CPH |
| KK-452 | JFK |
| JR-201 | IAD |

输出:

| tail_number | airline |
| --- | --- |
| PA-452 | new air |

### 示例 2: 基本案例

描述: 简单复杂的合并条件。参数值:

- 左侧选择列的条件:columnNameIsIn(columnNames: [tail_number, airline, factor],)
- 连接条件:and(conditions: [lessThan(left:factor,right:factor,),equals(left:tail_number,right:tail_number,)],)
- 左侧数据集: ri.foundry.main.dataset.left
- 右侧数据集: ri.foundry.main.dataset.right
输入:ri.foundry.main.dataset.left

| tail_number | airline | miles | factor |
| --- | --- | --- | --- |
| XB-123 | foundry air | 124 | 2 |
| MT-222 | new airline | 1123 | 5 |
| XB-123 | foundry airline | 335 | 5 |
| MT-222 | new air | 565 | 4 |
| KK-452 | new air | 222 | 1 |
| PA-452 | new air | 212 | 2 |
| XB-123 | foundry airline | 1134 | 2 |

ri.foundry.main.dataset.right

| tail_number | home_airport | factor |
| --- | --- | --- |
| XB-123 | LHR | 2 |
| MT-222 | CPH | 1 |
| KK-452 | JFK | 10 |
| JR-201 | IAD | 4 |

输出:

| tail_number | airline | factor |
| --- | --- | --- |
| XB-123 | foundry air | 2 |
| MT-222 | new airline | 5 |
| XB-123 | foundry airline | 5 |
| MT-222 | new air | 4 |
| PA-452 | new air | 2 |
| XB-123 | foundry airline | 2 |

### 示例 3: 基本案例

参数值:

- 左侧选择列的条件:columnNameIsIn(columnNames: [tail_number, airline, factor],)
- 连接条件:and(conditions: [equals(left:tail_number,right:tail_number,),equals(left:factor,right:factor,)],)
- 左侧数据集: ri.foundry.main.dataset.left
- 右侧数据集: ri.foundry.main.dataset.right
输入:ri.foundry.main.dataset.left

| tail_number | airline | miles | factor |
| --- | --- | --- | --- |
| XB-123 | foundry air | 124 | 2 |
| MT-222 | new airline | 1123 | 5 |
| XB-123 | foundry airline | 335 | 5 |
| MT-222 | new air | 565 | 4 |
| KK-452 | new air | 222 | 1 |
| PA-452 | new air | 212 | 2 |
| XB-123 | foundry airline | 1134 | 2 |

ri.foundry.main.dataset.right

| tail_number | home_airport | factor |
| --- | --- | --- |
| XB-123 | LHR | 2 |
| MT-222 | CPH | 1 |
| KK-452 | JFK | 10 |
| JR-201 | IAD | 4 |

输出:

| tail_number | airline | factor |
| --- | --- | --- |
| MT-222 | new airline | 5 |
| XB-123 | foundry airline | 5 |
| MT-222 | new air | 4 |
| KK-452 | new air | 1 |
| PA-452 | new air | 2 |

### 示例 4: 基本案例

参数值:

- 左侧选择列的条件:allColumns()
- 连接条件:equals(left:tail_number,right:tail_number,)
- 左侧数据集: ri.foundry.main.dataset.left
- 右侧数据集: ri.foundry.main.dataset.right
输入:ri.foundry.main.dataset.left

| tail_number | airline | miles | factor |
| --- | --- | --- | --- |
| XB-123 | foundry air | 124 | 2 |
| MT-222 | new airline | 1123 | 5 |
| XB-123 | foundry airline | 335 | 5 |
| MT-222 | new air | 565 | 4 |
| KK-452 | new air | 222 | 1 |
| PA-452 | new air | 212 | 2 |
| XB-123 | foundry airline | 1134 | 2 |

ri.foundry.main.dataset.right

| tail_number | home_airport |
| --- | --- |
| XB-123 | LHR |
| MT-222 | CPH |
| KK-452 | JFK |
| JR-201 | IAD |

输出:

| tail_number | airline | miles | factor |
| --- | --- | --- | --- |
| PA-452 | new air | 212 | 2 |
