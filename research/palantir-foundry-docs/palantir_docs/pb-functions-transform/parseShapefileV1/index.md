来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/parseShapefileV1/

# 从 shapefile 中提取行

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 从 shapefile 中提取行

> 支持于: 批处理

支持于: 批处理

读取文件数据集并将每个 shapefile 解析为行。除了 .shp、.shx 和 .dbf 文件之外的所有文件都将被忽略。此 shapefile 解析器仅支持点、折线、多边形和多点几何类型。输出数据集将有一个几何列，以及用户列出的每个属性的列，除了 _error 和 _file 列。如果用户未提供要提取的属性，则整个属性结构将作为字符串提取到一个属性列中。

变换类别: 文件, 地理空间

## 声明的参数

- 数据集- 要处理的 shapefile 数据集。每个 shapefile 必须有一个 .shp、.shx 和 .dbf 文件。一个 shapefile 的所有文件必须具有相同的名称。例如，具有以下文件的数据集有两个 shapefile (shapefile1 和 shapefile2): shapefile1.shp, shapefile1.shx, shapefile1.dbf, folder/shapefile2.shp, folder/shapefile2.shx, folder/shapefile2.dbf。文件
- 属性列表- 需要从这些 shapefile 中提取的属性及其类型的列表。如果提供了一个空的结构，则将所有属性提取到一个“属性”列中作为字符串。类型<Struct>
- 非必填源坐标系- 格式为 "authority" 的坐标系标识符。例如，UTM 18N 区可以由 EPSG:32618 标识。如果未指定，默认将使用 WGS84，即 EPSG:4326。文字<字符串>