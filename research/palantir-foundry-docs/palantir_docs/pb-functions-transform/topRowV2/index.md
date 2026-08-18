来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/topRowV2/

# 顶部行

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 顶部行

> 支持于: 批处理

支持于: 批处理

选择每个排序分区中的顶部行。

变换类别: 聚合

## 声明的参数

- 数据集- 输入数据集。表格
- 按列分区- 确定每个分区的列集合。集合<列<任何类型>>
- 排序规范- 如何对每个分区进行排序的规范。至少需要一个规范。列表<元组<列<任何类型>, 枚举<升序, 降序>>>
- 非必填行数- 要选择的行数，默认为1。字面量<整数>
## 示例

### 示例 1: 基本情况

参数值:

- 数据集: ri.foundry.main.dataset.a
- 按列分区: {airline}
- 排序规范: [(airport,DESCENDING), (miles,ASCENDING)]
- 行数:null
输入:

| airline | airport | miles |
| --- | --- | --- |
| foundry airways | JFK | 1002345 |
| foundry airways | LHR | 2221324 |
| new air | SFO | 21356673 |
| new air | JFK | 12323456 |
| foundry airways | LHR | 12542352 |
| new air | JFK | 12232355 |

输出:

| airline | airport | miles |
| --- | --- | --- |
| foundry airways | LHR | 2221324 |
| new air | SFO | 21356673 |

### 示例 2: 基本情况

参数值:

- 数据集: ri.foundry.main.dataset.a
- 按列分区: {}
- 排序规范: [(airline,DESCENDING), (airport,DESCENDING), (miles,ASCENDING)]
- 行数: 2
输入:

| airline | airport | miles |
| --- | --- | --- |
| foundry airways | JFK | 1002345 |
| foundry airways | LHR | 2221324 |
| new air | SFO | 21356673 |
| new air | JFK | 12323456 |
| foundry airways | LHR | 12542352 |
| new air | JFK | 12232355 |

输出:

| airline | airport | miles |
| --- | --- | --- |
| new air | SFO | 21356673 |
| new air | JFK | 12232355 |

### 示例 3: 基本情况

参数值:

- 数据集: ri.foundry.main.dataset.a
- 按列分区: {}
- 排序规范: []
- 行数: 1
输入:

| airline | airport | miles |
| --- | --- | --- |
| foundry airways | JFK | 1002345 |
| foundry airways | LHR | 2221324 |
| new air | SFO | 21356673 |
| new air | JFK | 12323456 |
| foundry airways | LHR | 12542352 |
| new air | JFK | 12232355 |

输出:

| airline | airport | miles |
| --- | --- | --- |
| foundry airways | JFK | 1002345 |
