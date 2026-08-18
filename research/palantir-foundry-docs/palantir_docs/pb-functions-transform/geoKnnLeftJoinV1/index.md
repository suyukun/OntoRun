来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/geoKnnLeftJoinV1/

# 几何 knn 左合并

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 几何 knn 左合并

> 支持于: 批量

支持于: 批量

为基准数据集中每个有效输入几何选择邻居数据集中的k个最近点。内部将输入数据集转换为给定的坐标参考系，并返回到WGS84。整个邻居数据集必须能够适应于驱动程序和执行器的内存。一个3 gb的执行器应该能够处理邻居数据集中的多达100万个点。

变换类别: 地理空间, 合并

## 声明的参数

- 基准数据集- 用于合并的基准数据集。表
- 左侧选择列的条件- 将测试左侧输入模式中的所有列是否符合此条件。如果符合，列将被选入输出。ColumnPredicate
- 右侧选择列的条件- 将测试右侧输入模式中的所有列是否符合此条件。如果符合，列将被选入输出。ColumnPredicate
- 合并键- 查询数据集中的GeoJSON列和邻居数据集中的地理点列。Tuple<Column<Geometry>, Column<GeoPoint>>
- K- 从右侧数据集中为左侧数据集中每个有效几何选择的邻居数量。Literal<Integer>
- 邻居数据集- 用于合并的潜在邻居数据集。表
- 投影坐标系- 输入几何将在合并前转换为此坐标系，并以给定坐标系的单位测量距离。格式为"authority"，例如UTM zone 18N可以通过EPSG:32618标识。Literal<字符串>
- 非必填右侧列的前缀- 添加到右侧所有列名称的前缀。Literal<字符串>
## 示例

### 示例 1: 基础案例

参数值:

- 基准数据集: ri.foundry.main.dataset.left
- 左侧选择列的条件:columnNameIsIn(columnNames: [geometryCol, lhsCol],)
- 右侧选择列的条件:columnNameIsIn(columnNames: [geometryCol, col],)
- 合并键: (geometryCol,geometryCol)
- K: 2
- 邻居数据集: ri.foundry.main.dataset.right
- 投影坐标系: epsg:2868
- 右侧列的前缀: rhs_
输入:ri.foundry.main.dataset.left

| geometryCol | lhsCol |
| --- | --- |
| {"coordinates": [-112.14843750000001,33.440609443703586], "type":"Point"} | 42.0 |

ri.foundry.main.dataset.right

| geometryCol | col |
| --- | --- |
| {latitude: 33.440609443703586,longitude: -112.14843750000001,} | rhsVal1 |
| {latitude: 33.44082430962016,longitude: -112.14560508728029,} | rhsVal2 |
| {latitude: 33.440895931474124,longitude: -112.11796760559083,} | rhsVal3 |

输出:

| geometryCol | lhsCol | rhs_geometryCol | rhs_col |
| --- | --- | --- | --- |
| {"coordinates": [-112.14843750000001,33.440609443703586], "type":"Point"} | 42.0 | {latitude: 33.440609443703586,longitude: -112.14843750000001,} | rhsVal1 |
| {"coordinates": [-112.14843750000001,33.440609443703586], "type":"Point"} | 42.0 | {latitude: 33.44082430962016,longitude: -112.14560508728029,} | rhsVal2 |

### 示例 2: 基础案例

参数值:

- 基准数据集: ri.foundry.main.dataset.left
- 左侧选择列的条件:columnNameIsIn(columnNames: [geometryColLhs, lhs-1],)
- 右侧选择列的条件:columnNameIsIn(columnNames: [geometryColRhs, rhs-1],)
- 合并键: (geometryColLhs,geometryColRhs)
- K: 1
- 邻居数据集: ri.foundry.main.dataset.right
- 投影坐标系: epsg:2868
- 右侧列的前缀:null
输入:ri.foundry.main.dataset.left

| geometryColLhs | lhs-1 |
| --- | --- |

ri.foundry.main.dataset.right

| geometryColRhs | rhs-1 |
| --- | --- |

输出:

| geometryColLhs | lhs-1 | geometryColRhs | rhs-1 |
| --- | --- | --- | --- |

### 示例 3: 基础案例

参数值:

- 基准数据集: ri.foundry.main.dataset.left
- 左侧选择列的条件:columnNameIsIn(columnNames: [geometryCol, lhsCol],)
- 右侧选择列的条件:columnNameIsIn(columnNames: [geometryCol, col],)
- 合并键: (geometryCol,geometryCol)
- K: 2
- 邻居数据集: ri.foundry.main.dataset.right
- 投影坐标系: epsg:2868
- 右侧列的前缀: rhs_
输入:ri.foundry.main.dataset.left

| geometryCol | lhsCol |
| --- | --- |
| {"coordinates": [-112.14843750000001,33.440609443703586], "type":"Point"} | 42.0 |
| {"coordinates": [-112.14843750000001,33.440609443703586], "type":"Point"} | 43.0 |

ri.foundry.main.dataset.right

| geometryCol | col |
| --- | --- |
| {latitude: 33.440609443703586,longitude: -112.14843750000001,} | rhsVal1 |
| {latitude: 33.44082430962016,longitude: -112.14560508728029,} | rhsVal2 |
| {latitude: 33.440895931474124,longitude: -112.11796760559083,} | rhsVal3 |

输出:

| geometryCol | lhsCol | rhs_geometryCol | rhs_col |
| --- | --- | --- | --- |
| {"coordinates": [-112.14843750000001,33.440609443703586], "type":"Point"} | 42.0 | {latitude: 33.440609443703586,longitude: -112.14843750000001,} | rhsVal1 |
| {"coordinates": [-112.14843750000001,33.440609443703586], "type":"Point"} | 43.0 | {latitude: 33.440609443703586,longitude: -112.14843750000001,} | rhsVal1 |
| {"coordinates": [-112.14843750000001,33.440609443703586], "type":"Point"} | 42.0 | {latitude: 33.44082430962016,longitude: -112.14560508728029,} | rhsVal2 |
| {"coordinates": [-112.14843750000001,33.440609443703586], "type":"Point"} | 43.0 | {latitude: 33.44082430962016,longitude: -112.14560508728029,} | rhsVal2 |

### 示例 4: 基础案例

参数值:

- 基准数据集: ri.foundry.main.dataset.left
- 左侧选择列的条件:columnNameIsIn(columnNames: [geometryCol, lhsCol],)
- 右侧选择列的条件:columnNameIsIn(columnNames: [geometryCol, col],)
- 合并键: (geometryCol,geometryCol)
- K: 3
- 邻居数据集: ri.foundry.main.dataset.right
- 投影坐标系: epsg:2868
- 右侧列的前缀: rhs_
输入:ri.foundry.main.dataset.left

| geometryCol | lhsCol |
| --- | --- |
| {"coordinates": [-112.14843750000001,33.440609443703586], "type":"Point"} | 42.0 |

ri.foundry.main.dataset.right

| geometryCol | col |
| --- | --- |
| {latitude: 33.440609443703586,longitude: -112.14843750000001,} | rhsVal1 |
| {latitude: 33.440609443703586,longitude: -112.14843750000001,} | rhsVal1 |
| {latitude: 33.44082430962016,longitude: -112.14560508728029,} | rhsVal2 |
| {latitude: 33.44082430962016,longitude: -112.14560508728029,} | rhsVal2 |
| {latitude: 33.440895931474124,longitude: -112.11796760559083,} | rhsVal3 |

输出:

| geometryCol | lhsCol | rhs_geometryCol | rhs_col |
| --- | --- | --- | --- |
| {"coordinates": [-112.14843750000001,33.440609443703586], "type":"Point"} | 42.0 | {latitude: 33.440609443703586,longitude: -112.14843750000001,} | rhsVal1 |
| {"coordinates": [-112.14843750000001,33.440609443703586], "type":"Point"} | 42.0 | {latitude: 33.440609443703586,longitude: -112.14843750000001,} | rhsVal1 |
| {"coordinates": [-112.14843750000001,33.440609443703586], "type":"Point"} | 42.0 | {latitude: 33.44082430962016,longitude: -112.14560508728029,} | rhsVal2 |

### 示例 5: 基础案例

参数值:

- 基准数据集: ri.foundry.main.dataset.left
- 左侧选择列的条件:columnNameIsIn(columnNames: [geometryColLhs, lhs-1],)
- 右侧选择列的条件:columnNameIsIn(columnNames: [geometryColRhs, rhs-1],)
- 合并键: (geometryColLhs,geometryColRhs)
- K: 1
- 邻居数据集: ri.foundry.main.dataset.right
- 投影坐标系: epsg:2868
- 右侧列的前缀:null
输入:ri.foundry.main.dataset.left

| geometryColLhs | lhs-1 |
| --- | --- |

ri.foundry.main.dataset.right

| geometryColRhs | rhs-1 |
| --- | --- |
| {latitude: 33.44082430962016,longitude: -112.14560508728029,} | null |
| {latitude: 33.440895931474124,longitude: -112.11796760559083,} | rhsVal2 |
| null | rhsVal3 |

输出:

| geometryColLhs | lhs-1 | geometryColRhs | rhs-1 |
| --- | --- | --- | --- |

### 示例 6: 基础案例

参数值:

- 基准数据集: ri.foundry.main.dataset.left
- 左侧选择列的条件:columnNameIsIn(columnNames: [geometryColLhs, lhs-1],)
- 右侧选择列的条件:columnNameIsIn(columnNames: [geometryColRhs, rhs-1],)
- 合并键: (geometryColLhs,geometryColRhs)
- K: 1
- 邻居数据集: ri.foundry.main.dataset.right
- 投影坐标系: epsg:2868
- 右侧列的前缀:null
输入:ri.foundry.main.dataset.left

| geometryColLhs | lhs-1 |
| --- | --- |
| {"coordinates": [-112.14843750000001,33.440609443703586], "type":"Point"} | 42.0 |
| {"coordinates": [-112.14560508728029,33.44082430962016], "type":"Point"} | 43.0 |

ri.foundry.main.dataset.right

| geometryColRhs | rhs-1 |
| --- | --- |

输出:

| geometryColLhs | lhs-1 | geometryColRhs | rhs-1 |
| --- | --- | --- | --- |
| {"coordinates": [-112.14843750000001,33.440609443703586], "type":"Point"} | 42.0 | null | null |
| {"coordinates": [-112.14560508728029,33.44082430962016], "type":"Point"} | 43.0 | null | null |

### 示例 7: 基础案例

参数值:

- 基准数据集: ri.foundry.main.dataset.left
- 左侧选择列的条件:columnNameIsIn(columnNames: [geometryCol, lhsCol],)
- 右侧选择列的条件:columnNameIsIn(columnNames: [geometryCol, col1, arrayCol],)
- 合并键: (geometryCol,geometryCol)
- K: 5
- 邻居数据集: ri.foundry.main.dataset.right
- 投影坐标系: epsg:4326
- 右侧列的前缀: rhs_
输入:ri.foundry.main.dataset.left

| geometryCol | lhsCol |
| --- | --- |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 42.0 |

ri.foundry.main.dataset.right

| geometryCol | col1 | arrayCol | toDrop |
| --- | --- | --- | --- |
| {latitude: 33.440609443703586,longitude: -112.14843750000001,} | rhsVal1 | [ 0.0, 1.1 ] | 1.0 |
| {latitude: 33.44082430962016,longitude: -112.14560508728029,} | rhsVal2 | [ 0.0, 1.1 ] | 1.0 |
| {latitude: 33.440895931474124,longitude: -112.11796760559083,} | rhsVal3 | [ 0.0, 1.1 ] | 1.0 |

输出:

| geometryCol | lhsCol | rhs_geometryCol | rhs_col1 | rhs_arrayCol |
| --- | --- | --- | --- | --- |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 42.0 | {latitude: 33.440609443703586,longitude: -112.14843750000001,} | rhsVal1 | [ 0.0, 1.1 ] |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 42.0 | {latitude: 33.44082430962016,longitude: -112.14560508728029,} | rhsVal2 | [ 0.0, 1.1 ] |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 42.0 | {latitude: 33.440895931474124,longitude: -112.11796760559083,} | rhsVal3 | [ 0.0, 1.1 ] |

### 示例 8: 基础案例

参数值:

- 基准数据集: ri.foundry.main.dataset.left
- 左侧选择列的条件:columnNameIsIn(columnNames: [geometryColLhs, lhs-1],)
- 右侧选择列的条件:columnNameIsIn(columnNames: [geometryColRhs, rhs-1],)
- 合并键: (geometryColLhs,geometryColRhs)
- K: 1
- 邻居数据集: ri.foundry.main.dataset.right
- 投影坐标系: epsg:2868
- 右侧列的前缀:null
输入:ri.foundry.main.dataset.left

| geometryColLhs | lhs-1 |
| --- | --- |
| {"coordinates": [-112.14843750000001,33.440609443703586], "type":"Point"} | 42.0 |
| null | 43.0 |

ri.foundry.main.dataset.right

| geometryColRhs | rhs-1 |
| --- | --- |
| {latitude: 33.44082430962016,longitude: -112.14560508728029,} | null |
| {latitude: 33.440895931474124,longitude: -112.11796760559083,} | rhsVal2 |
| null | rhsVal3 |

输出:

| geometryColLhs | lhs-1 | geometryColRhs | rhs-1 |
| --- | --- | --- | --- |
| {"coordinates": [-112.14843750000001,33.440609443703586], "type":"Point"} | 42.0 | {latitude: 33.44082430962016,longitude: -112.14560508728029,} | null |
| null | 43.0 | null | null |

### 示例 9: 基础案例

参数值:

- 基准数据集: ri.foundry.main.dataset.left
- 左侧选择列的条件:columnNameIsIn(columnNames: [geometryColLhs, lhs-1],)
- 右侧选择列的条件:columnNameIsIn(columnNames: [],)
- 合并键: (geometryColLhs,geometryColRhs)
- K: 1
- 邻居数据集: ri.foundry.main.dataset.right
- 投影坐标系: epsg:2868
- 右侧列的前缀:null
输入:ri.foundry.main.dataset.left

| geometryColLhs | lhs-1 |
| --- | --- |
| {"coordinates": [-112.14843750000001,33.440609443703586], "type":"Point"} | 42.0 |
| {"coordinates": [-112.14560508728029,33.44082430962016], "type":"Point"} | 43.0 |

ri.foundry.main.dataset.right

| geometryColRhs | rhs-1 |
| --- | --- |
| {latitude: 33.44082430962016,longitude: -112.14560508728029,} | null |
| {latitude: 33.440895931474124,longitude: -112.11796760559083,} | rhsVal2 |
| null | rhsVal3 |

输出:

| geometryColLhs | lhs-1 |
| --- | --- |
| {"coordinates": [-112.14843750000001,33.440609443703586], "type":"Point"} | 42.0 |
| {"coordinates": [-112.14560508728029,33.44082430962016], "type":"Point"} | 43.0 |

### 示例 10: 基础案例

参数值:

- 基准数据集: ri.foundry.main.dataset.left
- 左侧选择列的条件:columnNameIsIn(columnNames: [],)
- 右侧选择列的条件:columnNameIsIn(columnNames: [geometryColRhs, rhs-1],)
- 合并键: (geometryColLhs,geometryColRhs)
- K: 1
- 邻居数据集: ri.foundry.main.dataset.right
- 投影坐标系: epsg:2868
- 右侧列的前缀:null
输入:ri.foundry.main.dataset.left

| geometryColLhs | lhs-1 |
| --- | --- |
| {"coordinates": [-112.14843750000001,33.440609443703586], "type":"Point"} | 42.0 |
| {"coordinates": [-112.14560508728029,33.44082430962016], "type":"Point"} | 43.0 |

ri.foundry.main.dataset.right

| geometryColRhs | rhs-1 |
| --- | --- |
| {latitude: 33.44082430962016,longitude: -112.14560508728029,} | null |
| {latitude: 33.440895931474124,longitude: -112.11796760559083,} | rhsVal2 |
| null | rhsVal3 |

输出:

| geometryColRhs | rhs-1 |
| --- | --- |
| {latitude: 33.44082430962016,longitude: -112.14560508728029,} | null |
| {latitude: 33.44082430962016,longitude: -112.14560508728029,} | null |

### 示例 11: 基础案例

参数值:

- 基准数据集: ri.foundry.main.dataset.left
- 左侧选择列的条件:allColumns()
- 右侧选择列的条件:columnNameIsIn(columnNames: [geometryCol, col1, arrayCol],)
- 合并键: (geometryCol,geometryCol)
- K: 1
- 邻居数据集: ri.foundry.main.dataset.right
- 投影坐标系: epsg:4326
- 右侧列的前缀: rhs_
输入:ri.foundry.main.dataset.left

| geometryCol | lhsCol |
| --- | --- |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 42.0 |
| {"coordinates": [55.0, 5.0], "type":"Point"} | 43.0 |
| {"coordinates": [[40.0, 0.0], [0.0, 40.0]], "type":"LineString"} | 44.0 |
| {"coordinates": [[[20.0, 10.0], [27.0, 10.0], [27.0, 17.0], [20.0, 17.0], [20.0, 10.0]]], "type": "Polygon"} | 45.0 |
| {"coordinates": [[[21.0, 21.0], [27.0, 21.0], [27.0, 27.0], [21.0, 27.0], [21.0, 21.0]]], "type": "Polygon"} | 46.0 |
| {"coordinates": [[[[2.0, 2.0], [7.0, 2.0], [7.0, 7.0], [2.0, 7.0], [2.0, 2.0]]], [[[12.0, 12.0], [17.0, 12.0], [17.0, 17.0], [12.0, 17.0], [12.0, 12.0]]]], "type":"MultiPolygon"} | 47.0 |
| {"coordinates": [[[[170.0, 170.0], [190.0, 170.0], [190.0, 190.0], [170.0, 190.0], [170.0, 170.0]]], [[[12.0, 12.0], [17.0, 12.0], [17.0, 17.0], [12.0, 17.0], [12.0, 12.0]]]], "type":"MultiPolygon"} | 48.0 |

ri.foundry.main.dataset.right

| geometryCol | col1 | arrayCol | toDrop |
| --- | --- | --- | --- |
| {latitude: 5.0,longitude: 5.0,} | rhsVal1 | [ 0.0, 1.1 ] | 1.0 |
| {latitude: 100.0,longitude: 100.0,} | rhsVal2 | [ 0.0, 1.1 ] | 1.0 |

输出:

| geometryCol | lhsCol | rhs_geometryCol | rhs_col1 | rhs_arrayCol |
| --- | --- | --- | --- | --- |
| {"coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]], "type": "Polygon"} | 42.0 | {latitude: 5.0,longitude: 5.0,} | rhsVal1 | [ 0.0, 1.1 ] |
| {"coordinates": [55.0, 5.0], "type":"Point"} | 43.0 | {latitude: 5.0,longitude: 5.0,} | rhsVal1 | [ 0.0, 1.1 ] |
| {"coordinates": [[40.0, 0.0], [0.0, 40.0]], "type":"LineString"} | 44.0 | {latitude: 5.0,longitude: 5.0,} | rhsVal1 | [ 0.0, 1.1 ] |
| {"coordinates": [[[20.0, 10.0], [27.0, 10.0], [27.0, 17.0], [20.0, 17.0], [20.0, 10.0]]], "type": "Polygon"} | 45.0 | {latitude: 5.0,longitude: 5.0,} | rhsVal1 | [ 0.0, 1.1 ] |
| {"coordinates": [[[21.0, 21.0], [27.0, 21.0], [27.0, 27.0], [21.0, 27.0], [21.0, 21.0]]], "type": "Polygon"} | 46.0 | {latitude: 5.0,longitude: 5.0,} | rhsVal1 | [ 0.0, 1.1 ] |
| {"coordinates": [[[[2.0, 2.0], [7.0, 2.0], [7.0, 7.0], [2.0, 7.0], [2.0, 2.0]]], [[[12.0, 12.0], [17.0, 12.0], [17.0, 17.0], [12.0, 17.0], [12.0, 12.0]]]], "type":"MultiPolygon"} | 47.0 | {latitude: 5.0,longitude: 5.0,} | rhsVal1 | [ 0.0, 1.1 ] |
| {"coordinates": [[[[170.0, 170.0], [190.0, 170.0], [190.0, 190.0], [170.0, 190.0], [170.0, 170.0]]], [[[12.0, 12.0], [17.0, 12.0], [17.0, 17.0], [12.0, 17.0], [12.0, 12.0]]]], "type":"MultiPolygon"} | 48.0 | {latitude: 5.0,longitude: 5.0,} | rhsVal1 | [ 0.0, 1.1 ] |
