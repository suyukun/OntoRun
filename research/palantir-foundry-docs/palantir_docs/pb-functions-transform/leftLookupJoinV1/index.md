来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/leftLookupJoinV1/

# 左查找合并

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 左查找合并

> 支持于: 流式处理

支持于: 流式处理

将两个数据集合并，保留左表中的所有行以及右表中匹配的行。

变换类别: 合并

## 声明的参数

- 选择左边列的条件- 将测试左边输入模式中的所有列是否符合此条件。如果符合，该列将被选中并输出。ColumnPredicate
- 选择右边列的条件- 将测试右边输入模式中的所有列是否符合此条件。如果符合，该列将被选中并输出。ColumnPredicate
- 合并条件- 从左和右输入中列出的列来进行合并。List<Tuple<Column<Boolean | Byte | Date | Double | Float | Integer | Long | Short | 字符串 | Timestamp>, Column<Boolean | Byte | Date | Double | Float | Integer | Long | Short | 字符串 | Timestamp>>>
- 左数据集- 合并中使用的左数据集。Table
- 右数据集- 合并中使用的右数据集。Table
- 非必填右边列的前缀- 为右侧所有列添加的前缀。Literal<字符串>
## 示例

### 示例 1: 基本情况

参数值:

- 选择左边列的条件:columnNameIsIn(columnNames: [tail_number, airline],)
- 选择右边列的条件:columnNameIsIn(columnNames: [home_airport],)
- 合并条件: [(tail_number,tail_number)]
- 左数据集: ri.foundry.main.dataset.left
- 右数据集: ri.foundry.main.dataset.right
- 右边列的前缀:null
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

| tail_number | airline | home_airport |
| --- | --- | --- |
| XB-123 | foundry air | LHR |
| MT-222 | new airline | CPH |
| XB-123 | foundry airline | LHR |
| MT-222 | new air | CPH |
| KK-452 | new air | JFK |
| PA-452 | new air | null |
| XB-123 | foundry airline | LHR |

### 示例 2: 基本情况

参数值:

- 选择左边列的条件:columnNameIsIn(columnNames: [tail_number, airline, factor],)
- 选择右边列的条件:columnNameIsIn(columnNames: [home_airport],)
- 合并条件: [(tail_number,tail_number), (factor,factor)]
- 左数据集: ri.foundry.main.dataset.left
- 右数据集: ri.foundry.main.dataset.right
- 右边列的前缀:null
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

| tail_number | airline | factor | home_airport |
| --- | --- | --- | --- |
| XB-123 | foundry air | 2 | LHR |
| MT-222 | new airline | 5 | null |
| XB-123 | foundry airline | 5 | null |
| MT-222 | new air | 4 | null |
| KK-452 | new air | 1 | null |
| PA-452 | new air | 2 | null |
| XB-123 | foundry airline | 2 | LHR |

### 示例 3: 基本情况

参数值:

- 选择左边列的条件:allColumns()
- 选择右边列的条件:columnNameIsIn(columnNames: [home_airport],)
- 合并条件: [(tail_number,tail_number)]
- 左数据集: ri.foundry.main.dataset.left
- 右数据集: ri.foundry.main.dataset.right
- 右边列的前缀:null
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
| XB-123 | LGW |
| MT-222 | CPH |
| KK-452 | JFK |
| JR-201 | IAD |

输出:

| tail_number | airline | miles | factor | home_airport |
| --- | --- | --- | --- | --- |
| XB-123 | foundry air | 124 | 2 | LHR |
| XB-123 | foundry air | 124 | 2 | LGW |
| MT-222 | new airline | 1123 | 5 | CPH |
| XB-123 | foundry airline | 335 | 5 | LHR |
| XB-123 | foundry airline | 335 | 5 | LGW |
| MT-222 | new air | 565 | 4 | CPH |
| KK-452 | new air | 222 | 1 | JFK |
| PA-452 | new air | 212 | 2 | null |
| XB-123 | foundry airline | 1134 | 2 | LHR |
| XB-123 | foundry airline | 1134 | 2 | LGW |
