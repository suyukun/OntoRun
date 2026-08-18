来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/geoDistanceInnerJoinV1/

# 地理距离内合并

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 地理距离内合并

> 支持于: 批处理

支持于: 批处理

内合并基于输入几何之间的距离将左侧和右侧数据集合并。在合并之前，将几何内部转换为给定的投影坐标参考系统，然后再转换回WGS84。

变换类别: 地理空间, 合并

## 声明的参数

- 选择左侧列的条件- 将测试左侧输入模式中的所有列以查看它们是否符合此条件。如果符合，该列将被选中输出。ColumnPredicate
- 选择右侧列的条件- 将测试右侧输入模式中的所有列以查看它们是否符合此条件。如果符合，该列将被选中输出。ColumnPredicate
- 距离- 在此距离内合并几何，单位与坐标参考系统相同。Literal<DefiniteNumeric>
- 合并键- 左右输入中的geojson列用于合并。Tuple<Column<Geometry>, Column<Geometry>>
- 左侧数据集- 用于合并的左侧数据集。Table
- 投影坐标系统- 输入几何将在合并前转换为此坐标系统，并在给定坐标系统的单位中测量距离。格式为"authority"，例如UTM区域18N可以通过EPSG:32618识别。Literal<字符串>
- 右侧数据集- 用于合并的右侧数据集。Table
- 非必填右侧列的前缀- 添加到右侧所有列的前缀。Literal<字符串>
## 示例

### 示例1: 基本案例

参数值:

- 选择左侧列的条件:columnNameIsIn(columnNames: [geometryColLhs, lhs-1],)
- 选择右侧列的条件:columnNameIsIn(columnNames: [geometryCol, arrayCol],)
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

输出:

| geometryColLhs | lhs-1 | rhs_geometryCol | rhs_arrayCol |
| --- | --- | --- | --- |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 42.0 | {"coordinates": [[[20.0, 10.0], [27.0, 10.0], [27.0, 17.0], [20.0, 17.0], [20.0, 10.0]]], "type": "Polygon"} | [ 0.0, 1.0 ] |
| {"coordinates": [[25.0, 0.0], [0.0, 25.0]], "type":"LineString"} | 44.0 | {"coordinates": [[[20.0, 10.0], [27.0, 10.0], [27.0, 17.0], [20.0, 17.0], [20.0, 10.0]]], "type": "Polygon"} | [ 0.0, 1.0 ] |

### 示例2: 基本案例

参数值:

- 选择左侧列的条件:columnNameIsIn(columnNames: [geometryColLhs, lhs-1],)
- 选择右侧列的条件:columnNameIsIn(columnNames: [geometryColRhs, rhs-1],)
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

### 示例3: 基本案例

参数值:

- 选择左侧列的条件:columnNameIsIn(columnNames: [geometryColLhs, lhs-1],)
- 选择右侧列的条件:columnNameIsIn(columnNames: [geometryColRhs, rhs-1],)
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

### 示例4: 基本案例

参数值:

- 选择左侧列的条件:columnNameIsIn(columnNames: [geometryColLhs, lhs-1],)
- 选择右侧列的条件:columnNameIsIn(columnNames: [],)
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

ri.foundry.main.dataset.right

| geometryCol | col1 | arrayCol |
| --- | --- | --- |
| {"coordinates": [[[20.0, 10.0], [27.0, 10.0], [27.0, 17.0], [20.0, 17.0], [20.0, 10.0]]], "type": "Polygon"} | rhsVal1 | [ 0.0, 1.0 ] |
| {"coordinates": [[[21.0, 21.0], [27.0, 21.0], [27.0, 27.0], [21.0, 27.0], [21.0, 21.0]]], "type": "Polygon"} | rhsVal2 | [ 0.0, 1.0 ] |

输出:

| geometryColLhs | lhs-1 |
| --- | --- |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 42.0 |

### 示例5: 基本案例

参数值:

- 选择左侧列的条件:columnNameIsIn(columnNames: [],)
- 选择右侧列的条件:columnNameIsIn(columnNames: [geometryCol, arrayCol],)
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

ri.foundry.main.dataset.right

| geometryCol | col1 | arrayCol |
| --- | --- | --- |
| {"coordinates": [[[20.0, 10.0], [27.0, 10.0], [27.0, 17.0], [20.0, 17.0], [20.0, 10.0]]], "type": "Polygon"} | rhsVal1 | [ 0.0, 1.0 ] |
| {"coordinates": [[[21.0, 21.0], [27.0, 21.0], [27.0, 27.0], [21.0, 27.0], [21.0, 21.0]]], "type": "Polygon"} | rhsVal2 | [ 0.0, 1.0 ] |

输出:

| rhs_geometryCol | rhs_arrayCol |
| --- | --- |
| {"coordinates": [[[20.0, 10.0], [27.0, 10.0], [27.0, 17.0], [20.0, 17.0], [20.0, 10.0]]], "type": "Polygon"} | [ 0.0, 1.0 ] |

### 示例6: 空案例

参数值:

- 选择左侧列的条件:columnNameIsIn(columnNames: [geometryColLhs, lhs-1],)
- 选择右侧列的条件:columnNameIsIn(columnNames: [geometryCol, col1, arrayCol],)
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
| null | 43.0 |

ri.foundry.main.dataset.right

| geometryCol | col1 | arrayCol |
| --- | --- | --- |
| {"coordinates": [[[20.0, 10.0], [27.0, 10.0], [27.0, 17.0], [20.0, 17.0], [20.0, 10.0]]], "type": "Polygon"} | rhsVal1 | [ 0.0, 1.0 ] |
| {"coordinates": [[[21.0, 21.0], [27.0, 21.0], [27.0, 27.0], [21.0, 27.0], [21.0, 21.0]]], "type": "Polygon"} | rhsVal2 | [ 0.0, 1.0 ] |
| null | rhsVal3 | [ 0.0, 1.0 ] |

输出:

| geometryColLhs | lhs-1 | rhs_geometryCol | rhs_col1 | rhs_arrayCol |
| --- | --- | --- | --- | --- |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 42.0 | {"coordinates": [[[20.0, 10.0], [27.0, 10.0], [27.0, 17.0], [20.0, 17.0], [20.0, 10.0]]], "type": "Polygon"} | rhsVal1 | [ 0.0, 1.0 ] |
