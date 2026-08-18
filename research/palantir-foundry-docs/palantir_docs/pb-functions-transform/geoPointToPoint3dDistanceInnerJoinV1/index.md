来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/geoPointToPoint3dDistanceInnerJoinV1/

# GeoPoint-to-GeoPoint 3d距离内合并

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# GeoPoint-to-GeoPoint 3d距离内合并

> 支持于: 批处理

支持于: 批处理

内合并基于点几何之间的距离将左和右数据集合并。几何必须表示点，并且可以选择性地包括z坐标。在合并之前，内部将几何转换为给定的投影坐标参考系统，然后再转换回WGS84。非点几何将被忽略，并且整个右侧数据集必须能够适应驱动程序和执行器内存。一个3 gb的执行器应能处理邻居数据集中最多400万个点。

变换类别: 地理空间, 合并

## 声明的参数

- 选择左侧列的条件- 将测试左侧输入模式中的所有列以查看它们是否符合此条件。如果符合，该列将在输出中被选中。ColumnPredicate
- 选择右侧列的条件- 将测试右侧输入模式中的所有列以查看它们是否符合此条件。如果符合，该列将在输出中被选中。ColumnPredicate
- 距离- 在此距离内合并几何，以坐标参考系统的单位为准。Literal<DefiniteNumeric>
- 合并键- 用于合并的左侧和右侧输入中的geojson列。Tuple<Column<Geometry>, Column<Geometry>>
- 左侧数据集- 用于合并的左侧数据集。Table
- 投影坐标系统- 合并前输入几何将转换为此坐标系统，并将以给定坐标系统的单位测量距离。格式为"authority"，例如UTM第18N区可通过EPSG:32618识别。Literal<String>
- 右侧数据集- 用于合并的右侧数据集。Table
- 使用z坐标- 是否包括z坐标并计算三维距离。如果为false，z坐标将被忽略并计算二维距离。Literal<Boolean>
- 非必填右侧列的前缀- 在右侧所有列前添加的前缀。Literal<String>
## 示例

### 示例 1: 基本情况

参数值:

- 选择左侧列的条件:columnNameIsIn(columnNames: [geometryColLhs, lhs-1],)
- 选择右侧列的条件:columnNameIsIn(columnNames: [geometryCol, arrayCol],)
- 距离: 2.5
- 合并键: (geometryColLhs,geometryCol)
- 左侧数据集: ri.foundry.main.dataset.left
- 投影坐标系统: EPSG:4326
- 右侧数据集: ri.foundry.main.dataset.right
- 使用z坐标: false
- 右侧列的前缀: rhs_
输入:ri.foundry.main.dataset.left

| geometryColLhs | lhs-1 |
| --- | --- |
| {"coordinates": [0.0, 0.0, 0.0], "type":"Point"} | 42.0 |
| {"coordinates": [0.0, 0.0, 5.0], "type":"Point"} | 43.0 |
| {"coordinates": [0.0, 0.0], "type":"Point"} | 44.0 |

ri.foundry.main.dataset.right

| geometryCol | col1 | arrayCol |
| --- | --- | --- |
| {"coordinates": [0.0, 0.0, 2.0], "type":"Point"} | rhsVal1 | [ 0.0, 1.0 ] |
| {"coordinates": [0.0, 1.0], "type":"Point"} | rhsVal2 | [ 0.0, 1.0 ] |

输出:

| geometryColLhs | lhs-1 | rhs_geometryCol | rhs_arrayCol |
| --- | --- | --- | --- |
| {"coordinates": [0.0, 0.0, 0.0], "type":"Point"} | 42.0 | {"coordinates": [0.0, 0.0, 2.0], "type":"Point"} | [ 0.0, 1.0 ] |
| {"coordinates": [0.0, 0.0, 0.0], "type":"Point"} | 42.0 | {"coordinates": [0.0, 1.0], "type":"Point"} | [ 0.0, 1.0 ] |
| {"coordinates": [0.0, 0.0, 5.0], "type":"Point"} | 43.0 | {"coordinates": [0.0, 0.0, 2.0], "type":"Point"} | [ 0.0, 1.0 ] |
| {"coordinates": [0.0, 0.0, 5.0], "type":"Point"} | 43.0 | {"coordinates": [0.0, 1.0], "type":"Point"} | [ 0.0, 1.0 ] |
| {"coordinates": [0.0, 0.0], "type":"Point"} | 44.0 | {"coordinates": [0.0, 0.0, 2.0], "type":"Point"} | [ 0.0, 1.0 ] |
| {"coordinates": [0.0, 0.0], "type":"Point"} | 44.0 | {"coordinates": [0.0, 1.0], "type":"Point"} | [ 0.0, 1.0 ] |

### 示例 2: 基本情况

参数值:

- 选择左侧列的条件:columnNameIsIn(columnNames: [geometryColLhs, lhs-1],)
- 选择右侧列的条件:columnNameIsIn(columnNames: [geometryCol, arrayCol],)
- 距离: 2.5
- 合并键: (geometryColLhs,geometryCol)
- 左侧数据集: ri.foundry.main.dataset.left
- 投影坐标系统: EPSG:4326
- 右侧数据集: ri.foundry.main.dataset.right
- 使用z坐标: true
- 右侧列的前缀: rhs_
输入:ri.foundry.main.dataset.left

| geometryColLhs | lhs-1 |
| --- | --- |
| {"coordinates": [0.0, 0.0, 0.0], "type":"Point"} | 42.0 |
| {"coordinates": [0.0, 0.0, 5.0], "type":"Point"} | 43.0 |
| {"coordinates": [0.0, 5.0], "type":"Point"} | 44.0 |

ri.foundry.main.dataset.right

| geometryCol | col1 | arrayCol |
| --- | --- | --- |
| {"coordinates": [0.0, 0.0, 2.0], "type":"Point"} | rhsVal1 | [ 0.0, 1.0 ] |
| {"coordinates": [1.0, 1.0, 6.0], "type":"Point"} | rhsVal2 | [ 0.0, 1.0 ] |
| {"coordinates": [0.0, 0.0, 3.0], "type":"Point"} | rhsVal3 | [ 0.0, 1.0 ] |
| {"coordinates": [0.0, 0.0], "type":"Point"} | rhsVal4 | [ 0.0, 1.0 ] |

输出:

| geometryColLhs | lhs-1 | rhs_geometryCol | rhs_arrayCol |
| --- | --- | --- | --- |
| {"coordinates": [0.0, 0.0, 0.0], "type":"Point"} | 42.0 | {"coordinates": [0.0, 0.0, 2.0], "type":"Point"} | [ 0.0, 1.0 ] |
| {"coordinates": [0.0, 0.0, 5.0], "type":"Point"} | 43.0 | {"coordinates": [0.0, 0.0, 3.0], "type":"Point"} | [ 0.0, 1.0 ] |
| {"coordinates": [0.0, 0.0, 5.0], "type":"Point"} | 43.0 | {"coordinates": [1.0, 1.0, 6.0], "type":"Point"} | [ 0.0, 1.0 ] |

### 示例 3: 基本情况

参数值:

- 选择左侧列的条件:columnNameIsIn(columnNames: [geometryColLhs, lhs-1],)
- 选择右侧列的条件:columnNameIsIn(columnNames: [geometryColRhs, rhs-1],)
- 距离: 1641
- 合并键: (geometryColLhs,geometryColRhs)
- 左侧数据集: ri.foundry.main.dataset.left
- 投影坐标系统: epsg:2868
- 右侧数据集: ri.foundry.main.dataset.right
- 使用z坐标: false
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

### 示例 4: 基本情况

参数值:

- 选择左侧列的条件:columnNameIsIn(columnNames: [geometryColLhs, lhs-1],)
- 选择右侧列的条件:columnNameIsIn(columnNames: [],)
- 距离: 10.0
- 合并键: (geometryColLhs,geometryCol)
- 左侧数据集: ri.foundry.main.dataset.left
- 投影坐标系统: EPSG:4326
- 右侧数据集: ri.foundry.main.dataset.right
- 使用z坐标: false
- 右侧列的前缀: rhs_
输入:ri.foundry.main.dataset.left

| geometryColLhs | lhs-1 |
| --- | --- |
| {"coordinates": [15.0, 5.0], "type":"Point"} | 42.0 |
| {"coordinates": [55.0, 5.0], "type":"Point"} | 43.0 |

ri.foundry.main.dataset.right

| geometryCol | col1 | arrayCol |
| --- | --- | --- |
| {"coordinates": [15.0, 5.0], "type":"Point"} | rhsVal1 | [ 0.0, 1.0 ] |

输出:

| geometryColLhs | lhs-1 |
| --- | --- |
| {"coordinates": [15.0, 5.0], "type":"Point"} | 42.0 |

### 示例 5: 基本情况

参数值:

- 选择左侧列的条件:columnNameIsIn(columnNames: [],)
- 选择右侧列的条件:columnNameIsIn(columnNames: [geometryCol, arrayCol],)
- 距离: 10.0
- 合并键: (geometryColLhs,geometryCol)
- 左侧数据集: ri.foundry.main.dataset.left
- 投影坐标系统: EPSG:4326
- 右侧数据集: ri.foundry.main.dataset.right
- 使用z坐标: false
- 右侧列的前缀: rhs_
输入:ri.foundry.main.dataset.left

| geometryColLhs | lhs-1 |
| --- | --- |
| {"coordinates": [15.0, 5.0], "type":"Point"} | 42.0 |
| {"coordinates": [55.0, 5.0], "type":"Point"} | 43.0 |

ri.foundry.main.dataset.right

| geometryCol | col1 | arrayCol |
| --- | --- | --- |
| {"coordinates": [55.0, 5.0], "type":"Point"} | rhsVal1 | [ 0.0, 1.0 ] |

输出:

| rhs_geometryCol | rhs_arrayCol |
| --- | --- |
| {"coordinates": [55.0, 5.0], "type":"Point"} | [ 0.0, 1.0 ] |

### 示例 6: Null情况

参数值:

- 选择左侧列的条件:columnNameIsIn(columnNames: [geometryColLhs, lhs-1],)
- 选择右侧列的条件:columnNameIsIn(columnNames: [geometryCol, col1, arrayCol],)
- 距离: 10.0
- 合并键: (geometryColLhs,geometryCol)
- 左侧数据集: ri.foundry.main.dataset.left
- 投影坐标系统: EPSG:4326
- 右侧数据集: ri.foundry.main.dataset.right
- 使用z坐标: false
- 右侧列的前缀: rhs_
输入:ri.foundry.main.dataset.left

| geometryColLhs | lhs-1 |
| --- | --- |
| {"coordinates": [15.0, 5.0], "type":"Point"} | 42.0 |
| {"coordinates": [55.0, 5.0], "type":"Point"} | 43.0 |
| {"coordinates": [[[20.0, 10.0], [27.0, 10.0], [27.0, 17.0], [20.0, 17.0], [20.0, 10.0]]], "type": "Polygon"} | 44.0 |
| null | 45.0 |

ri.foundry.main.dataset.right

| geometryCol | col1 | arrayCol |
| --- | --- | --- |
| {"coordinates": [15.0, 5.0], "type":"Point"} | rhsVal1 | [ 0.0, 1.0 ] |
| {"coordinates": [[[21.0, 21.0], [27.0, 21.0], [27.0, 27.0], [21.0, 27.0], [21.0, 21.0]]], "type": "Polygon"} | rhsVal2 | [ 0.0, 1.0 ] |
| {"coordinates": [[[20.0, 10.0], [27.0, 10.0], [27.0, 17.0], [20.0, 17.0], [20.0, 10.0]]], "type": "Polygon"} | rhsVal3 | [ 0.0, 1.0 ] |
| null | rhsVal4 | [ 0.0, 1.0 ] |

输出:

| geometryColLhs | lhs-1 | rhs_geometryCol | rhs_col1 | rhs_arrayCol |
| --- | --- | --- | --- | --- |
| {"coordinates": [15.0, 5.0], "type":"Point"} | 42.0 | {"coordinates": [15.0, 5.0], "type":"Point"} | rhsVal1 | [ 0.0, 1.0 ] |
