来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/geoDistanceLeftJoinV1/

# 地理距离左合并

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 地理距离左合并

> 支持于: 批处理

支持于: 批处理

如果输入几何之间的距离小于或等于指定的距离，则将数据集左合并在一起。内部将几何转换为给定的投影坐标参考系统，然后再合并回WGS84。

变换类别: 地理空间, 合并

## 声明参数

- 左侧列选择条件- 将测试左侧输入模式中的所有列是否符合此条件。如果匹配，则该列将在输出中被选中。ColumnPredicate
- 右侧列选择条件- 将测试右侧输入模式中的所有列是否符合此条件。如果匹配，则该列将在输出中被选中。ColumnPredicate
- 距离- 用于合并几何的距离，单位与坐标参考系统一致。Literal<DefiniteNumeric>
- 合并键- 左侧和右侧输入中的geojson列，用于合并。Tuple<Column<Geometry>, Column<Geometry>>
- 左侧数据集- 用于合并的左侧数据集。Table
- 投影坐标系统- 输入几何将在合并前转换为该坐标系统，并且距离将以给定坐标系统的单位进行测量。格式为"authority"，例如UTM区域18N可以用EPSG:32618标识。Literal<字符串>
- 右侧数据集- 用于合并的右侧数据集。Table
- 非必填右侧列的前缀- 要添加到右侧所有列的前缀。Literal<字符串>
## 示例

### 示例 1: 基础案例

参数值:

- 左侧列选择条件:columnNameIsIn(columnNames: [geometryColLhs, lhs-1],)
- 右侧列选择条件:columnNameIsIn(columnNames: [geometryColRhs, rhs-1],)
- 距离: 1640.42
- 合并键: (geometryColLhs,geometryColRhs)
- 左侧数据集: ri.foundry.main.dataset.left
- 投影坐标系统: epsg:2868
- 右侧数据集: ri.foundry.main.dataset.right
- 右侧列的前缀:null
输入:ri.foundry.main.dataset.left

| geometryColLhs | lhs-1 |
| --- | --- |
| {"coordinates": [-112.14843750000001,33.440609443703586], "type":"Point"} | 42.0 |
| null | 43.0 |

ri.foundry.main.dataset.right

| geometryColRhs | rhs-1 |
| --- | --- |
| {"coordinates": [-112.14560508728029,33.44082430962016], "type":"Point"} | rhsVal1 |
| {"coordinates": [-112.11796760559083,33.440895931474124], "type":"Point"} | rhsVal2 |

输出:

| geometryColLhs | lhs-1 | geometryColRhs | rhs-1 |
| --- | --- | --- | --- |
| {"coordinates": [-112.14843750000001,33.440609443703586], "type":"Point"} | 42.0 | {"coordinates": [-112.14560508728029,33.44082430962016], "type":"Point"} | rhsVal1 |
| null | 43.0 | null | null |

### 示例 2: 基础案例

参数值:

- 左侧列选择条件:columnNameIsIn(columnNames: [geometryColLhs, lhs-1],)
- 右侧列选择条件:columnNameIsIn(columnNames: [geometryCol, col1, arrayCol],)
- 距离: 10.0
- 合并键: (geometryColLhs,geometryCol)
- 左侧数据集: ri.foundry.main.dataset.left
- 投影坐标系统: EPSG:4326
- 右侧数据集: ri.foundry.main.dataset.right
- 右侧列的前缀: rhs_
输入:ri.foundry.main.dataset.left

| geometryColLhs | lhs-1 |
| --- | --- |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 42.0 |
| {"coordinates": [55.0, 5.0], "type":"Point"} | 43.0 |
| {"coordinates": [[25.0, 0.0], [0.0, 25.0]], "type":"LineString"} | 44.0 |

ri.foundry.main.dataset.right

| geometryCol | col1 | arrayCol |
| --- | --- | --- |
| {"coordinates": [[[20.0, 10.0], [27.0, 10.0], [27.0, 17.0], [20.0, 17.0], [20.0, 10.0]]], "type": "Polygon"} | rhsVal1 | [ 0.0, 1.0 ] |
| {"coordinates": [[[21.0, 21.0], [27.0, 21.0], [27.0, 27.0], [21.0, 27.0], [21.0, 21.0]]], "type": "Polygon"} | rhsVal2 | [ 0.0, 1.0 ] |
| {"coordinates": [0.0, 0.0], "type":"Point"} | rhsVal3 | [ 0.0, 1.0 ] |
| {"coordinates": [10.0, 10.0], "type":"Point"} | rhsVal4 | [ 0.0, 1.0 ] |
| {"coordinates": [14.0, 14.0], "type":"Point"} | rhsVal5 | [ 0.0, 1.0 ] |
| {"coordinates": [25.0, 25.0], "type":"Point"} | rhsVal6 | [ 0.0, 1.0 ] |

输出:

| geometryColLhs | lhs-1 | rhs_geometryCol | rhs_col1 | rhs_arrayCol |
| --- | --- | --- | --- | --- |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 42.0 | {"coordinates": [[[20.0, 10.0], [27.0, 10.0], [27.0, 17.0], [20.0, 17.0], [20.0, 10.0]]], "type": "Polygon"} | rhsVal1 | [ 0.0, 1.0 ] |
| {"coordinates": [55.0, 5.0], "type":"Point"} | 43.0 | null | null | null |
| {"coordinates": [[25.0, 0.0], [0.0, 25.0]], "type":"LineString"} | 44.0 | {"coordinates": [[[20.0, 10.0], [27.0, 10.0], [27.0, 17.0], [20.0, 17.0], [20.0, 10.0]]], "type": "Polygon"} | rhsVal1 | [ 0.0, 1.0 ] |
| {"coordinates": [[25.0, 0.0], [0.0, 25.0]], "type":"LineString"} | 44.0 | {"coordinates": [10.0, 10.0], "type":"Point"} | rhsVal4 | [ 0.0, 1.0 ] |
| {"coordinates": [[25.0, 0.0], [0.0, 25.0]], "type":"LineString"} | 44.0 | {"coordinates": [14.0, 14.0], "type":"Point"} | rhsVal5 | [ 0.0, 1.0 ] |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 42.0 | {"coordinates": [10.0, 10.0], "type":"Point"} | rhsVal4 | [ 0.0, 1.0 ] |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 42.0 | {"coordinates": [0.0, 0.0], "type":"Point"} | rhsVal3 | [ 0.0, 1.0 ] |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 42.0 | {"coordinates": [14.0, 14.0], "type":"Point"} | rhsVal5 | [ 0.0, 1.0 ] |

### 示例 3: 基础案例

参数值:

- 左侧列选择条件:columnNameIsIn(columnNames: [geometryColLhs, lhs-1],)
- 右侧列选择条件:columnNameIsIn(columnNames: [geometryColRhs, rhs-1],)
- 距离: 1641
- 合并键: (geometryColLhs,geometryColRhs)
- 左侧数据集: ri.foundry.main.dataset.left
- 投影坐标系统: epsg:2868
- 右侧数据集: ri.foundry.main.dataset.right
- 右侧列的前缀:null
输入:ri.foundry.main.dataset.left

| geometryColLhs | lhs-1 |
| --- | --- |
| {"coordinates": [-112.14843750000001,33.440609443703586], "type":"Point"} | 42.0 |
| null | 43.0 |

ri.foundry.main.dataset.right

| geometryColRhs | rhs-1 |
| --- | --- |
| {"coordinates": [-112.14560508728029,33.44082430962016], "type":"Point"} | rhsVal1 |
| {"coordinates": [-112.11796760559083,33.440895931474124], "type":"Point"} | rhsVal2 |

输出:

| geometryColLhs | lhs-1 | geometryColRhs | rhs-1 |
| --- | --- | --- | --- |
| {"coordinates": [-112.14843750000001,33.440609443703586], "type":"Point"} | 42.0 | {"coordinates": [-112.14560508728029,33.44082430962016], "type":"Point"} | rhsVal1 |
| null | 43.0 | null | null |

### 示例 4: 基础案例

参数值:

- 左侧列选择条件:columnNameIsIn(columnNames: [geometryColLhs, lhs-1],)
- 右侧列选择条件:columnNameIsIn(columnNames: [geometryColRhs, rhs-1],)
- 距离: 1641
- 合并键: (geometryColLhs,geometryColRhs)
- 左侧数据集: ri.foundry.main.dataset.left
- 投影坐标系统: epsg:2868
- 右侧数据集: ri.foundry.main.dataset.right
- 右侧列的前缀:null
输入:ri.foundry.main.dataset.left

| geometryColLhs | lhs-1 |
| --- | --- |
| {"coordinates": [-112.14843750000001,33.440609443703586], "type":"Point"} | 42.0 |
| null | 43.0 |

ri.foundry.main.dataset.right

| geometryColRhs | rhs-1 |
| --- | --- |
| {"coordinates": [-112.14560508728029,33.44082430962016], "type":"Point"} | rhsVal1 |
| {"coordinates": [-112.11796760559083,33.440895931474124], "type":"Point"} | rhsVal2 |

输出:

| geometryColLhs | lhs-1 | geometryColRhs | rhs-1 |
| --- | --- | --- | --- |
| {"coordinates": [-112.14843750000001,33.440609443703586], "type":"Point"} | 42.0 | {"coordinates": [-112.14560508728029,33.44082430962016], "type":"Point"} | rhsVal1 |
| null | 43.0 | null | null |

### 示例 5: 空案例

参数值:

- 左侧列选择条件:columnNameIsIn(columnNames: [geometryColLhs, lhs-1],)
- 右侧列选择条件:columnNameIsIn(columnNames: [geometryColRhs, rhs-1],)
- 距离: 1640.42
- 合并键: (geometryColLhs,geometryColRhs)
- 左侧数据集: ri.foundry.main.dataset.left
- 投影坐标系统: EPSG:2868
- 右侧数据集: ri.foundry.main.dataset.right
- 右侧列的前缀:null
输入:ri.foundry.main.dataset.left

| geometryColLhs | lhs-1 |
| --- | --- |
| {"coordinates": [-112.14843750000001,33.440609443703586], "type":"Point"} | 42.0 |
| null | 43.0 |

ri.foundry.main.dataset.right

| geometryColRhs | rhs-1 |
| --- | --- |
| {"coordinates": [-112.14560508728029,33.44082430962016], "type":"Point"} | rhsVal1 |
| {"coordinates": [-112.11796760559083,33.440895931474124], "type":"Point"} | rhsVal2 |
| null | rhsVal3 |

输出:

| geometryColLhs | lhs-1 | geometryColRhs | rhs-1 |
| --- | --- | --- | --- |
| {"coordinates": [-112.14843750000001,33.440609443703586], "type":"Point"} | 42.0 | {"coordinates": [-112.14560508728029,33.44082430962016], "type":"Point"} | rhsVal1 |
| null | 43.0 | null | null |
