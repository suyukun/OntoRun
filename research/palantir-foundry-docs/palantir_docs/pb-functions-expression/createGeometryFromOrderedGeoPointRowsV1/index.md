来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/createGeometryFromOrderedGeoPointRowsV1/

# 从有序的GeoPoints行创建简单几何图形

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 从有序的GeoPoints行创建简单几何图形

> 支持于: 批处理

支持于: 批处理

给定一列GeoPoints和一个排序，通过按指定顺序连接GeoPoints返回一个多边形或线字符串。此函数假定数据是表格形式的，每行表示线字符串或多边形外壳中的一个单独的GeoPoint，以及指定这些点顺序的一列。对于多边形，此排序应识别当您逆时针移动外壳时的点。给定这些点的排序和分区（分组），该函数通过按order-by列的升序连接GeoPoints来构造该分区所需的几何图形。

表达式类别: 地理空间

## 声明的参数

- GeoPoint- 构建几何图形的GeoPoints列。数据集中的每行应表示一个单独的GeoPoint。如果有空值，这些行将被忽略。Expression<GeoPoint>
- 按升序排序- 用于构建线字符串或所需多边形外壳的GeoPoints排序的一列值。如果组内的值相同，则排序是随机的。如果有空值，这些行将被忽略。Expression<Byte | Date | Decimal | Double | Float | Integer | Long | Short | Timestamp>
- 输出几何类型- 输出应该是多边形还是线字符串。Enum<LineString, Polygon>
输出类型:几何图形

## 示例

### 示例 1: 基本情况

参数值:

- GeoPoint:geo_point
- 按升序排序:order
- 输出几何类型:LINE_STRING
给定输入表:

| geo_point | order |
| --- | --- |
| {latitude -> 0.0,longitude -> 0.0,} | 0 |
| {latitude -> 1.0,longitude -> 0.0,} | 1 |
| {latitude -> 1.0,longitude -> 1.0,} | 2 |

输出:{"type":"LineString","coordinates": [[0.0,0.0],[0.0, 1.0],[1.0,1.0]]}

### 示例 2: 基本情况

参数值:

- GeoPoint:geo_point
- 按升序排序:order
- 输出几何类型:POLYGON
给定输入表:

| geo_point | order |
| --- | --- |
| {latitude -> 0.0,longitude -> 0.0,} | 0 |
| {latitude -> 1.0,longitude -> 0.0,} | 3 |
| {latitude -> 1.0,longitude -> 1.0,} | 2 |
| {latitude -> 0.0,longitude -> 0.0,} | 4 |
| {latitude -> 0.0,longitude -> 1.0,} | 1 |

输出:{"type":"Polygon","coordinates": [[[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0]]]}

### 示例 3: 基本情况

参数值:

- GeoPoint:geo_point
- 按升序排序:order
- 输出几何类型:LINE_STRING
给定输入表:

| geo_point | order |
| --- | --- |
| {latitude -> 0.0,longitude -> 0.0,} | 0.0 |
| null | 1.0 |
| null | 2.0 |
| {latitude -> 0.0,longitude -> 1.0,} | 2.0 |

输出:{"type":"LineString","coordinates": [[0.0,0.0],[1.0, 0.0]]}

### 示例 4: 基本情况

参数值:

- GeoPoint:geo_point
- 按升序排序:order
- 输出几何类型:LINE_STRING
给定输入表:

| geo_point | order |
| --- | --- |
| {latitude -> 0.0,longitude -> 0.0,} | 0.0 |

输出:null

### 示例 5: 基本情况

参数值:

- GeoPoint:geo_point
- 按升序排序:order
- 输出几何类型:POLYGON
给定输入表:

| geo_point | order |
| --- | --- |
| {latitude -> 0.0,longitude -> 0.0,} | 0 |
| {latitude -> 1.0,longitude -> 1.0,} | 2 |
| {latitude -> 1.0,longitude -> 0.0,} | 3 |
| {latitude -> 0.0,longitude -> 1.0,} | 1 |

输出:{"type":"Polygon","coordinates": [[[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0]]]}

### 示例 6: 基本情况

参数值:

- GeoPoint:geo_point
- 按升序排序:order
- 输出几何类型:POLYGON
给定输入表:

| geo_point | order |
| --- | --- |
| {latitude -> 0.0,longitude -> 0.0,} | 0 |
| {latitude -> 1.0,longitude -> 0.0,} | 1 |

输出:null

### 示例 7: 空值情况

参数值:

- GeoPoint:geo_point
- 按升序排序:order
- 输出几何类型:POLYGON
给定输入表:

| geo_point | order |
| --- | --- |
| null | 0 |

输出:null

### 示例 8: 空值情况

参数值:

- GeoPoint:geo_point
- 按升序排序:order
- 输出几何类型:LINE_STRING
给定输入表:

| geo_point | order |
| --- | --- |
| {latitude -> 0.0,longitude -> 0.0,} | 0 |
| {latitude -> 1.0,longitude -> 1.0,} | null |
| {latitude -> 1.0,longitude -> 0.0,} | 1 |

输出:{"type":"LineString","coordinates": [[0.0,0.0],[0.0, 1.0]]}
