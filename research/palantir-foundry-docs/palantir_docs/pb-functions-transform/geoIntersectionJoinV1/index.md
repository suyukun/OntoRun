来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/geoIntersectionJoinV1/

# 几何交集合并

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 几何交集合并

> 支持于: Batch

支持于: Batch

内连接将左侧和右侧数据集合并，基于输入几何图形是否重叠。如果连接键列对具有相交的几何图形，则返回包含两个数据集所有列的行。目前不支持在多个连接键上进行合并。静默筛选空连接键几何值。左侧和右侧数据集的列名不能相同。连接列中无效的GeoJSON将被静默置空。

变换类别: 地理空间, 合并

## 声明的参数

- 连接键- 用于连接的来自左侧和右侧输入的GeoJSON列列表。如果此列表中的任何列对具有相交的几何图形，则会选中该行。List<Tuple<Column<Geometry>, Column<Geometry>>>
- 左侧数据集- 用于合并的左侧数据集。Table
- 右侧数据集- 用于合并的右侧数据集。Table
## 示例

### 示例 1: 基本情况

参数值:

- 连接键: [(geometryColLhs,geometryColRhs)]
- 左侧数据集: ri.foundry.main.dataset.left
- 右侧数据集: ri.foundry.main.dataset.right
输入:ri.foundry.main.dataset.left

| geometryColLhs | lhs-1 |
| --- | --- |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 42.0 |

ri.foundry.main.dataset.right

| geometryColRhs | rhs-1 |
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

| geometryColLhs | lhs-1 | geometryColRhs | rhs-1 |
| --- | --- | --- | --- |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 42.0 | {"coordinates": [[[2.0, 2.0], [7.0, 2.0], [7.0, 7.0], [2.0, 7.0], [2.0, 2.0]]], "type": "Polygon"} | rhsVal1 |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 42.0 | {"coordinates": [0.0, 0.0], "type":"Point"} | rhsVal3 |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 42.0 | {"coordinates": [[-1.0, -1.0], [5.0, 5.0]], "type":"LineString"} | rhsVal5 |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 42.0 | {"coordinates": [[-1.0, -1.0], [5.0, 5.0]], "type":"LineString"} | rhsVal7 |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 42.0 | {"coordinates": [[[[2.0, 2.0], [7.0, 2.0], [7.0, 7.0], [2.0, 7.0], [2.0, 2.0]]], [[[12.0, 12.0], [17.0, 12.0], [17.0, 17.0], [12.0, 17.0], [12.0, 12.0]]]], "type":"MultiPolygon"} | rhsVal9 |

### 示例 2: 基本情况

参数值:

- 连接键: [(geometryColLhs,geometryColRhs)]
- 左侧数据集: ri.foundry.main.dataset.left
- 右侧数据集: ri.foundry.main.dataset.right
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

### 示例 3: 空情况

参数值:

- 连接键: [(geometryColLhs,geometryColRhs)]
- 左侧数据集: ri.foundry.main.dataset.left
- 右侧数据集: ri.foundry.main.dataset.right
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

### 示例 4: 空情况

参数值:

- 连接键: [(geometryColLhs,geometryColRhs)]
- 左侧数据集: ri.foundry.main.dataset.left
- 右侧数据集: ri.foundry.main.dataset.right
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

### 示例 5: 边缘情况

参数值:

- 连接键: [(geometryColLhs,geometryColRhs)]
- 左侧数据集: ri.foundry.main.dataset.left
- 右侧数据集: ri.foundry.main.dataset.right
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

### 示例 6: 边缘情况

参数值:

- 连接键: [(geometryColLhs,geometryColRhs)]
- 左侧数据集: ri.foundry.main.dataset.left
- 右侧数据集: ri.foundry.main.dataset.right
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

### 示例 7: 边缘情况

参数值:

- 连接键: [(geometryColLhs,geometryColRhs)]
- 左侧数据集: ri.foundry.main.dataset.left
- 右侧数据集: ri.foundry.main.dataset.right
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

### 示例 8: 边缘情况

参数值:

- 连接键: [(geometryColLhs,geometryColRhs)]
- 左侧数据集: ri.foundry.main.dataset.left
- 右侧数据集: ri.foundry.main.dataset.right
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

### 示例 9: 边缘情况

参数值:

- 连接键: [(geometryColLhs,geometryColRhs)]
- 左侧数据集: ri.foundry.main.dataset.left
- 右侧数据集: ri.foundry.main.dataset.right
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
