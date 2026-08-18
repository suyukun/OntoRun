来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/geoIntersectionInnerJoinV1/

# 地理交集内合并

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 地理交集内合并

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

内合并左侧和右侧数据集基于输入几何是否重叠。结果中仅包括接触的几何。

变换类别: 地理空间, 合并

## 声明的参数

- 左侧要选择的列的条件- 将测试左侧输入架构中的所有列以查看它们是否符合此条件。如果符合，列将被选入输出。ColumnPredicate
- 右侧要选择的列的条件- 将测试右侧输入架构中的所有列以查看它们是否符合此条件。如果符合，列将被选入输出。ColumnPredicate
- 合并键- 用于合并的左侧和右侧输入的GeoJSON列。Tuple<Column<Geometry>, Column<Geometry>>
- 左侧数据集- 用于合并的左侧数据集。Table
- 右侧数据集- 用于合并的右侧数据集。Table
- 非必填右侧列的前缀- 添加到右侧所有列的前缀。Literal<字符串>
## 示例

### 示例 1: 基本情况

参数值:

- 左侧要选择的列的条件:allColumns()
- 右侧要选择的列的条件:allColumns()
- 合并键: (geometryColLhs,geometryColRhs)
- 左侧数据集: ri.foundry.main.dataset.left
- 右侧数据集: ri.foundry.main.dataset.right
- 右侧列的前缀:null
输入:ri.foundry.main.dataset.left

| geometryColLhs | col1Lhs |
| --- | --- |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 42.0 |

ri.foundry.main.dataset.right

| geometryColRhs | col1Rhs |
| --- | --- |
| {"coordinates": [[[2.0, 2.0], [7.0, 2.0], [7.0, 7.0], [2.0, 7.0], [2.0, 2.0]]], "type": "Polygon"} | rhsVal1 |
| {"coordinates": [[[12.0, 12.0], [17.0, 12.0], [17.0, 17.0], [12.0, 17.0], [12.0, 12.0]]], "type": "Polygon"} | rhsVal2 |
| {"coordinates": [0.0, 0.0], "type":"Point"} | rhsVal3 |
| {"coordinates": [15.0, 15.0], "type":"Point"} | rhsVal4 |
| {"coordinates": [[-1.0, -1.0], [5.0, 5.0]], "type":"LineString"} | rhsVal5 |
| {"coordinates": [[20.0, 20.0], [21.0, 23.0]], "type":"LineString"} | rhsVal6 |
| {"coordinates": [[-1.0, -1.0], [5.0, 5.0]], "type":"LineString"} | rhsVal7 |
| {"coordinates": [[20.0, 20.0], [21.0, 23.0]], "type":"LineString"} | rhsVal8 |
| {"coordinates": [[[[2.0, 2.0], [7.0, 2.0], [7.0, 7.0], [2.0, 7.0], [2.0, 2.0]]], [[[12.0, 12.0], [17.0, 12.0], [17.0, 17.0], [12.0, 17.0], [12.0, 12.0]]]], "type":"MultiPolygon"} | rhsVal9 |
| {"coordinates": [[[[170.0, 170.0], [190.0, 170.0], [190.0, 190.0], [170.0, 190.0], [170.0, 170.0]]], [[[12.0, 12.0], [17.0, 12.0], [17.0, 17.0], [12.0, 17.0], [12.0, 12.0]]]], "type":"MultiPolygon"} | rhsVal10 |

输出:

| geometryColLhs | col1Lhs | geometryColRhs | col1Rhs |
| --- | --- | --- | --- |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 42.0 | {"coordinates": [[[2.0, 2.0], [7.0, 2.0], [7.0, 7.0], [2.0, 7.0], [2.0, 2.0]]], "type": "Polygon"} | rhsVal1 |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 42.0 | {"coordinates": [0.0, 0.0], "type":"Point"} | rhsVal3 |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 42.0 | {"coordinates": [[-1.0, -1.0], [5.0, 5.0]], "type":"LineString"} | rhsVal5 |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 42.0 | {"coordinates": [[-1.0, -1.0], [5.0, 5.0]], "type":"LineString"} | rhsVal7 |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 42.0 | {"coordinates": [[[[2.0, 2.0], [7.0, 2.0], [7.0, 7.0], [2.0, 7.0], [2.0, 2.0]]], [[[12.0, 12.0], [17.0, 12.0], [17.0, 17.0], [12.0, 17.0], [12.0, 12.0]]]], "type":"MultiPolygon"} | rhsVal9 |

### 示例 2: 基本情况

参数值:

- 左侧要选择的列的条件:allColumns()
- 右侧要选择的列的条件:allColumns()
- 合并键: (geometryColLhs,geometryColRhs)
- 左侧数据集: ri.foundry.main.dataset.left
- 右侧数据集: ri.foundry.main.dataset.right
- 右侧列的前缀:null
输入:ri.foundry.main.dataset.left

| geometryColLhs | lhs1 |
| --- | --- |
| {} | 42.0 |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 43.0 |

ri.foundry.main.dataset.right

| geometryColRhs | rhs1 |
| --- | --- |
| {"coordinates": [[[2.0, 2.0], [7.0, 2.0], [7.0, 7.0], [2.0, 7.0], [2.0, 2.0]]], "type": "Polygon"} | rhsVal1 |

输出:

| geometryColLhs | lhs1 | geometryColRhs | rhs1 |
| --- | --- | --- | --- |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 43.0 | {"coordinates": [[[2.0, 2.0], [7.0, 2.0], [7.0, 7.0], [2.0, 7.0], [2.0, 2.0]]], "type": "Polygon"} | rhsVal1 |

### 示例 3: 基本情况

参数值:

- 左侧要选择的列的条件:allColumns()
- 右侧要选择的列的条件:allColumns()
- 合并键: (geometryColLhs,geometryColRhs)
- 左侧数据集: ri.foundry.main.dataset.left
- 右侧数据集: ri.foundry.main.dataset.right
- 右侧列的前缀: right_
输入:ri.foundry.main.dataset.left

| geometryColLhs | col1Lhs |
| --- | --- |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 42.0 |

ri.foundry.main.dataset.right

| geometryColRhs | col1Rhs |
| --- | --- |
| {"coordinates": [[[2.0, 2.0], [7.0, 2.0], [7.0, 7.0], [2.0, 7.0], [2.0, 2.0]]], "type": "Polygon"} | rhsVal1 |

输出:

| geometryColLhs | col1Lhs | right_geometryColRhs | right_col1Rhs |
| --- | --- | --- | --- |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 42.0 | {"coordinates": [[[2.0, 2.0], [7.0, 2.0], [7.0, 7.0], [2.0, 7.0], [2.0, 2.0]]], "type": "Polygon"} | rhsVal1 |

### 示例 4: 基本情况

参数值:

- 左侧要选择的列的条件:columnNameIsIn(columnNames: [geometryColLhs],)
- 右侧要选择的列的条件:columnNameIsIn(columnNames: [geometryColRhs],)
- 合并键: (geometryColLhs,geometryColRhs)
- 左侧数据集: ri.foundry.main.dataset.left
- 右侧数据集: ri.foundry.main.dataset.right
- 右侧列的前缀:null
输入:ri.foundry.main.dataset.left

| geometryColLhs | col1Lhs |
| --- | --- |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 42.0 |

ri.foundry.main.dataset.right

| geometryColRhs | col1Rhs |
| --- | --- |
| {"coordinates": [[[2.0, 2.0], [7.0, 2.0], [7.0, 7.0], [2.0, 7.0], [2.0, 2.0]]], "type": "Polygon"} | rhsVal1 |

输出:

| geometryColLhs | geometryColRhs |
| --- | --- |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | {"coordinates": [[[2.0, 2.0], [7.0, 2.0], [7.0, 7.0], [2.0, 7.0], [2.0, 2.0]]], "type": "Polygon"} |

### 示例 5: 空值情况

参数值:

- 左侧要选择的列的条件:allColumns()
- 右侧要选择的列的条件:allColumns()
- 合并键: (geometryColLhs,geometryColRhs)
- 左侧数据集: ri.foundry.main.dataset.left
- 右侧数据集: ri.foundry.main.dataset.right
- 右侧列的前缀:null
输入:ri.foundry.main.dataset.left

| geometryColLhs | lhs1 |
| --- | --- |
| null | 42.0 |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 43.0 |

ri.foundry.main.dataset.right

| geometryColRhs | rhs1 |
| --- | --- |
| {"coordinates": [[[2.0, 2.0], [7.0, 2.0], [7.0, 7.0], [2.0, 7.0], [2.0, 2.0]]], "type": "Polygon"} | rhsVal1 |
| {"coordinates": [0.0, 0.0], "type":"Point"} | rhsVal2 |
| null | rhsVal3 |

输出:

| geometryColLhs | lhs1 | geometryColRhs | rhs1 |
| --- | --- | --- | --- |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 43.0 | {"coordinates": [[[2.0, 2.0], [7.0, 2.0], [7.0, 7.0], [2.0, 7.0], [2.0, 2.0]]], "type": "Polygon"} | rhsVal1 |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 43.0 | {"coordinates": [0.0, 0.0], "type":"Point"} | rhsVal2 |

### 示例 6: 空值情况

参数值:

- 左侧要选择的列的条件:allColumns()
- 右侧要选择的列的条件:allColumns()
- 合并键: (geometryColLhs,geometryColRhs)
- 左侧数据集: ri.foundry.main.dataset.left
- 右侧数据集: ri.foundry.main.dataset.right
- 右侧列的前缀:null
输入:ri.foundry.main.dataset.left

| geometryColLhs | lhs1 |
| --- | --- |
| null | 42.0 |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 43.0 |

ri.foundry.main.dataset.right

| geometryColRhs | rhs1 |
| --- | --- |
| {"coordinates": [[[2.0, 2.0], [7.0, 2.0], [7.0, 7.0], [2.0, 7.0], [2.0, 2.0]]], "type": "Polygon"} | rhsVal1 |

输出:

| geometryColLhs | lhs1 | geometryColRhs | rhs1 |
| --- | --- | --- | --- |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 43.0 | {"coordinates": [[[2.0, 2.0], [7.0, 2.0], [7.0, 7.0], [2.0, 7.0], [2.0, 2.0]]], "type": "Polygon"} | rhsVal1 |

### 示例 7: 边界情况

参数值:

- 左侧要选择的列的条件:allColumns()
- 右侧要选择的列的条件:allColumns()
- 合并键: (geometryColLhs,geometryColRhs)
- 左侧数据集: ri.foundry.main.dataset.left
- 右侧数据集: ri.foundry.main.dataset.right
- 右侧列的前缀:null
输入:ri.foundry.main.dataset.left

| geometryColLhs | lhs1 |
| --- | --- |
| {"coordinates": [[[170.0, 170.0], [190.0, 170.0], [190.0, 190.0], [170.0, 190.0], [170.0, 170.0]]], "type": "Polygon"} | 42.0 |

ri.foundry.main.dataset.right

| geometryColRhs | rhs1 |
| --- | --- |
| {"coordinates": [[[175.0, 175.0], [195.0, 175.0], [195.0, 195.0], [175.0, 195.0], [175.0, 175.0]]], "type": "Polygon"} | rhsVal1 |

输出:

| geometryColLhs | lhs1 | geometryColRhs | rhs1 |
| --- | --- | --- | --- |
| {"coordinates": [[[170.0, 170.0], [190.0, 170.0], [190.0, 190.0], [170.0, 190.0], [170.0, 170.0]]], "type": "Polygon"} | 42.0 | {"coordinates": [[[175.0, 175.0], [195.0, 175.0], [195.0, 195.0], [175.0, 195.0], [175.0, 175.0]]], "type": "Polygon"} | rhsVal1 |

### 示例 8: 边界情况

参数值:

- 左侧要选择的列的条件:allColumns()
- 右侧要选择的列的条件:allColumns()
- 合并键: (geometryColLhs,geometryColRhs)
- 左侧数据集: ri.foundry.main.dataset.left
- 右侧数据集: ri.foundry.main.dataset.right
- 右侧列的前缀:null
输入:ri.foundry.main.dataset.left

| geometryColLhs | lhs1 |
| --- | --- |
| {"coordinates": [[[0.0, 0.0], [5.0, 5.0], [0.0, 10.0], [10.0, 5.0], [0.0, 0.0]]], "type":"Polygon"} | 42.0 |

ri.foundry.main.dataset.right

| geometryColRhs | rhs1 |
| --- | --- |
| {"coordinates": [[[0.0, 5.0], [2.5, 7.5], [4.0, 5.0], [2.5, 2.5], [0.0, 5.0]]], "type":"Polygon"} | rhsVal1 |
| {"coordinates": [[[0.0, 5.0], [2.0, 7.0], [4.0, 5.0], [2.0, 3.0], [0.0, 5.0]]], "type":"Polygon"} | rhsVal2 |

输出:

| geometryColLhs | lhs1 | geometryColRhs | rhs1 |
| --- | --- | --- | --- |
| {"coordinates": [[[0.0, 0.0], [5.0, 5.0], [0.0, 10.0], [10.0, 5.0], [0.0, 0.0]]], "type":"Polygon"} | 42.0 | {"coordinates": [[[0.0, 5.0], [2.5, 7.5], [4.0, 5.0], [2.5, 2.5], [0.0, 5.0]]], "type":"Polygon"} | rhsVal1 |

### 示例 9: 边界情况

参数值:

- 左侧要选择的列的条件:allColumns()
- 右侧要选择的列的条件:allColumns()
- 合并键: (geometryColLhs,geometryColRhs)
- 左侧数据集: ri.foundry.main.dataset.left
- 右侧数据集: ri.foundry.main.dataset.right
- 右侧列的前缀:null
输入:ri.foundry.main.dataset.left

| geometryColLhs |
| --- |
| {"coordinates": [0.0, 0.0], "type":"Point"} |

ri.foundry.main.dataset.right

| geometryColRhs |
| --- |
| {"coordinates": [0.0, 0.0], "type":"Point"} |
| {"coordinates": [15.0, 15.0], "type":"Point"} |

输出:

| geometryColLhs | geometryColRhs |
| --- | --- |
| {"coordinates": [0.0, 0.0], "type":"Point"} | {"coordinates": [0.0, 0.0], "type":"Point"} |

### 示例 10: 边界情况

参数值:

- 左侧要选择的列的条件:allColumns()
- 右侧要选择的列的条件:allColumns()
- 合并键: (geometryColLhs,geometryColRhs)
- 左侧数据集: ri.foundry.main.dataset.left
- 右侧数据集: ri.foundry.main.dataset.right
- 右侧列的前缀:null
输入:ri.foundry.main.dataset.left

| geometryColLhs | lhs1 |
| --- | --- |
| {"coordinates": [0.0, 0.0], "type":"Point"} | 42.0 |

ri.foundry.main.dataset.right

| geometryColRhs | rhs1 |
| --- | --- |
| {"coordinates": [0.0, 0.0], "type":"Point"} | rhsVal1 |
| {"coordinates": [15.0, 15.0], "type":"Point"} | rhsVal2 |

输出:

| geometryColLhs | lhs1 | geometryColRhs | rhs1 |
| --- | --- | --- | --- |
| {"coordinates": [0.0, 0.0], "type":"Point"} | 42.0 | {"coordinates": [0.0, 0.0], "type":"Point"} | rhsVal1 |

### 示例 11: 边界情况

参数值:

- 左侧要选择的列的条件:allColumns()
- 右侧要选择的列的条件:allColumns()
- 合并键: (geometryColLhs,geometryColRhs)
- 左侧数据集: ri.foundry.main.dataset.left
- 右侧数据集: ri.foundry.main.dataset.right
- 右侧列的前缀:null
输入:ri.foundry.main.dataset.left

| geometryColLhs | lhs1 |
| --- | --- |
| {"coordinates": [[[0.0, 0.0, 0.0], [10.0, 0.0, 0.0], [10.0, 10.0, 0.0], [10.0, 10.0, 10.0], [0.0, 10.0, 10.0], [0.0, 0.0, 10.0], [0.0, 0.0, 0.0]]], "type": "Polygon"} | 42.0 |

ri.foundry.main.dataset.right

| geometryColRhs | rhs1 |
| --- | --- |
| {"coordinates": [[[2.0, 2.0, 2.0], [7.0, 2.0, 2.0], [7.0, 7.0, 2.0], [7.0, 7.0, 7.0], [2.0, 7.0, 7.0], [2.0, 2.0, 7.0], [2.0, 2.0, 2.0]]], "type": "Polygon"} | rhsVal1 |
| {"coordinates": [[[12.0, 12.0, 12.0], [17.0, 12.0, 12.0], [17.0, 17.0, 12.0], [17.0, 17.0, 17.0], [12.0, 17.0, 17.0], [12.0, 12.0, 17.0], [12.0, 12.0, 12.0]]], "type": "Polygon"} | rhsVal2 |

输出:

| geometryColLhs | lhs1 | geometryColRhs | rhs1 |
| --- | --- | --- | --- |
| {"coordinates": [[[0.0, 0.0, 0.0], [10.0, 0.0, 0.0], [10.0, 10.0, 0.0], [10.0, 10.0, 10.0], [0.0, 10.0, 10.0], [0.0, 0.0, 10.0], [0.0, 0.0, 0.0]]], "type": "Polygon"} | 42.0 | {"coordinates": [[[2.0, 2.0, 2.0], [7.0, 2.0, 2.0], [7.0, 7.0, 2.0], [7.0, 7.0, 7.0], [2.0, 7.0, 7.0], [2.0, 2.0, 7.0], [2.0, 2.0, 2.0]]], "type": "Polygon"} | rhsVal1 |
