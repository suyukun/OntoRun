来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/geoIntersectionLeftJoinV1/

# 地理交集左合并

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 地理交集左合并

> 支持于: 批处理

支持于: 批处理

基于输入几何体是否重叠来左合并输入数据集。结果中包括仅接触的几何体。

变换类别: 地理空间, 合并

## 声明的参数

- 选择左侧列的条件- 将测试左侧输入模式中的所有列是否符合此条件。如果符合，该列将在输出中被选中。ColumnPredicate
- 选择右侧列的条件- 将测试右侧输入模式中的所有列是否符合此条件。如果符合，该列将在输出中被选中。ColumnPredicate
- 合并键- 用于合并的左侧和右侧输入的GeoJSON列。Tuple<Column<Geometry>, Column<Geometry>>
- 左侧数据集- 合并中使用的左侧数据集。Table
- 右侧数据集- 合并中使用的右侧数据集。Table
- 非必填右侧列的前缀- 为右侧所有列添加的前缀。Literal<字符串>
## 示例

### 示例 1: 基础案例

参数值:

- 选择左侧列的条件:allColumns()
- 选择右侧列的条件:allColumns()
- 合并键: (geometryColLhs,geometryColRhs)
- 左侧数据集: ri.foundry.main.dataset.left
- 右侧数据集: ri.foundry.main.dataset.right
- 右侧列的前缀:null
输入:ri.foundry.main.dataset.left

| geometryColLhs | col1Lhs |
| --- | --- |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 42.0 |
| {"coordinates": [55.0, 5.0], "type":"Point"} | 43.0 |

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
| {"coordinates": [55.0, 5.0], "type":"Point"} | 43.0 | null | null |

### 示例 2: 基础案例

参数值:

- 选择左侧列的条件:allColumns()
- 选择右侧列的条件:allColumns()
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
| {} | 42.0 | null | null |

### 示例 3: 空案例

参数值:

- 选择左侧列的条件:allColumns()
- 选择右侧列的条件:allColumns()
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
| null | 42.0 | null | null |
