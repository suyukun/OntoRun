来源: https://palantir.com/docs/zh/foundry/geospatial/vector_data_in_transforms/

# 在变换中使用矢量数据

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 在变换中使用矢量数据

## 概览

您可以使用Pipeline Builder应用程序加载、变换和运用地理空间数据，而无需编写任何代码。Pipeline Builder的地理空间套件几乎与下文描述的Geospatial Tools Python库相媲美。了解有关Pipeline Builder地理空间功能的更多信息。

Geospatial Tools是一个Python库，托管可重用的逻辑，用于在Foundry中的矢量地理空间数据管道上执行常见变换。此库中提供的函数旨在用于Python变换中，以简化这些常见操作与您其余管道逻辑的集成。

该库目前包括辅助函数以：

- 清理地理空间数据
- 空间函数
- 空间合并
## 安装

导入geospatial-tools和Spark 配置文件GEOSPARK到您的Python库中。如需安装帮助，请联系您的Palantir代表。

切换隐藏文件和文件夹，并在/transforms-python/build.gradle的最底部添加以下代码块：

```
Copied!1
2
3
4
dependencies {
    condaJars "org.apache.sedona:sedona-spark-shaded-3.5_2.13:1.7.1"
    condaJars "org.datasyslab:geotools-wrapper:1.7.0-28.5"
}
```

## 使用

所有使用geospatial-tools库的变换都需要使用@geospatial()装饰器（位于任何其他装饰器之上，例如@transform_df()和@configure()）。这将在您的 Spark 环境中启用 Apache Sedona，并添加绑定以在 PySpark DataFrame 上进行空间合并。

```
Copied!1
2
3
4
5
6
7
8
from transforms.api import transform_df, configure, Input, Output
from geospatial_tools import geospatial

@geospatial()  # 应用地理空间装饰器，用于处理地理空间相关的数据
@configure(...)  # 配置函数参数，具体配置内容需要根据实际需求填写
@transform_df(...)  # 转换DataFrame的装饰器，参数需要指定输入和输出DataFrame
def compute(input_df):
    ...
```

### 清理地理空间数据

在 Foundry 中清理后的地理空间数据是：

- 表格化的，因此数据可以在 Spark 变换中使用
- 格式化为有效的GeoJSON ↗或 geohash，因此数据可以在 Foundry Ontology 中使用
- 使用EPSG:4326 ↗CRS 投影，以便空间合并的双方使用相同的投影，Foundry 地图将正确渲染特征。
geospatial-tools库提供了clean_geometry()和lat_long_to_geometry()来执行步骤 (2) 和 (3)。如果您的原始数据是 GeoJSON、Shapefile、GDB、KML 或 KMZ，您可以使用内置解析辅助函数来执行步骤 (1)。

#### clean_geometry()

clean_geometry(geometry, input_crs, geometry_format='geojson', lat_long=False, output_format='geojson')

通过使其有效并将 CRS 规范化为 EPSG:4326 来清理地理空间几何列。

- 参数geometry(str): 输入几何列名称。input_crs(str): 输入几何 CRS。geometry_format(str, 非必填): 输入几何格式。支持的格式有geojson、geohash（包含latitude,longitude的字符串）、wkt和wkb。默认是geojson。lat_long(bool, 非必填): 如果输入几何坐标按latitude,longitude排列，则为true，这可能是geohash输入的情况，但对于geojson或wkt则不是。默认是false。output_format(str, 非必填): 输出几何格式（geojson或geohash）。默认是geojson。
- geometry(str): 输入几何列名称。
- input_crs(str): 输入几何 CRS。
- geometry_format(str, 非必填): 输入几何格式。支持的格式有geojson、geohash（包含latitude,longitude的字符串）、wkt和wkb。默认是geojson。
- lat_long(bool, 非必填): 如果输入几何坐标按latitude,longitude排列，则为true，这可能是geohash输入的情况，但对于geojson或wkt则不是。默认是false。
- output_format(str, 非必填): 输出几何格式（geojson或geohash）。默认是geojson。
- 示例Copied!123456789101112from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import clean_geometry

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    raw_df=Input('/my/input/dataset'),
)
def compute(raw_df):
    clean_df = raw_df.withColumn('geometry', clean_geometry('geometry', 'EPSG:26910'))
    return clean_df
```
Copied!1
2
3
4
5
6
7
8
9
10
11
12
from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import clean_geometry

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    raw_df=Input('/my/input/dataset'),
)
def compute(raw_df):
    clean_df = raw_df.withColumn('geometry', clean_geometry('geometry', 'EPSG:26910'))
    return clean_df
```

#### lat_long_to_geometry()

lat_long_to_geometry(lat, long, input_crs, output_format='geojson')

将纬度和经度列转换为清理后的几何列。

- 参数lat(str): 输入纬度列名称。long(str): 输入经度列名称。input_crs(str): 输入几何 CRS。output_format(str, 非必填): 输出几何格式（geojson或geohash）。默认是geojson。
- lat(str): 输入纬度列名称。
- long(str): 输入经度列名称。
- input_crs(str): 输入几何 CRS。
- output_format(str, 非必填): 输出几何格式（geojson或geohash）。默认是geojson。
- 示例Copied!123456789101112from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import lat_long_to_geometry

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    raw_df=Input('/my/input/dataset'),
)
def compute(raw_df):
    clean_df = raw_df.withColumn('geohash', lat_long_to_geometry('latitude', 'longitude', 'EPSG:26910', output_format='geohash'))
    return clean_df.drop('latitude', 'longitude')
```
Copied!1
2
3
4
5
6
7
8
9
10
11
12
from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import lat_long_to_geometry

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    raw_df=Input('/my/input/dataset'),
)
def compute(raw_df):
    clean_df = raw_df.withColumn('geohash', lat_long_to_geometry('latitude', 'longitude', 'EPSG:26910', output_format='geohash'))
    return clean_df.drop('latitude', 'longitude')
```

### 解析辅助函数

#### geojson_to_dataframe()

geojson_to_dataframe(dataset, properties=None, glob='*.geojson', batch_size=100000)

将 GeoJSON 文件转换为数据帧。使用流处理来处理非常大的文件而不会耗尽驱动内存。

- 参数dataset(transforms.api.Input): 包含 GeoJSON 文件的输入数据集。properties(list[str], 非必填): 要创建列的属性列表。如果未提供，所有属性将包含在 JSON "properties" 列中。glob(str, 非必填): 用于识别数据集中 GeoJSON 文件的 glob 模式。默认是*.geojson。batch_size(int, 非必填): 每批处理的记录数。如果驱动内存不足，应减小批量大小。默认是 100000。
- dataset(transforms.api.Input): 包含 GeoJSON 文件的输入数据集。
- properties(list[str], 非必填): 要创建列的属性列表。如果未提供，所有属性将包含在 JSON "properties" 列中。
- glob(str, 非必填): 用于识别数据集中 GeoJSON 文件的 glob 模式。默认是*.geojson。
- batch_size(int, 非必填): 每批处理的记录数。如果驱动内存不足，应减小批量大小。默认是 100000。
- 示例Copied!12345678910111213from transforms.api import transform, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.parsers import geojson_to_dataframe

@geospatial()
@transform(
    output=Output('/my/output/dataset'),
    raw=Input('/my/input/dataset'),
)
def compute(raw, output):
    return output.write_dataframe(
        geojson_to_dataframe(raw)
    )
```
Copied!1
2
3
4
5
6
7
8
9
10
11
12
13
from transforms.api import transform, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.parsers import geojson_to_dataframe

@geospatial()
@transform(
    output=Output('/my/output/dataset'),
    raw=Input('/my/input/dataset'),
)
def compute(raw, output):
    return output.write_dataframe(
        geojson_to_dataframe(raw)
    )
```

#### shapefile_to_dataframe()

shapefile_to_dataframe(dataset, glob='*.shp')

将 shapefiles 转换为数据帧。

- 参数dataset(transforms.api.Input): 包含 shapefiles 的输入数据集。glob(str, 非必填): 用于识别数据集中 .shp 文件的 glob 模式。也期望其他相关文件存在，例如 .shp、.shx、.dbf。默认是*.shp。
- dataset(transforms.api.Input): 包含 shapefiles 的输入数据集。
- glob(str, 非必填): 用于识别数据集中 .shp 文件的 glob 模式。也期望其他相关文件存在，例如 .shp、.shx、.dbf。默认是*.shp。
- 示例Copied!12345678910111213from transforms.api import transform, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.parsers import shapefile_to_dataframe

@geospatial()
@transform(
    output=Output('/my/output/dataset'),
    raw=Input('/my/input/dataset'),
)
def compute(raw, output):
    return output.write_dataframe(
        shapefile_to_dataframe(raw)
    )
```
Copied!1
2
3
4
5
6
7
8
9
10
11
12
13
from transforms.api import transform, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.parsers import shapefile_to_dataframe

@geospatial()
@transform(
    output=Output('/my/output/dataset'),
    raw=Input('/my/input/dataset'),
)
def compute(raw, output):
    return output.write_dataframe(
        shapefile_to_dataframe(raw)
    )
```

#### gdb_to_dataframe()

gdb_to_dataframe(dataset, glob='*.gdb.zip', layer=None)

将 GeoDatabase 文件转换为数据帧。

- 参数dataset(transforms.api.Input): 包含压缩 GDB 文件的输入数据集。glob(str, 非必填): 用于识别数据集中 GDB 文件的 glob 模式。默认是*.gdb.zip。layer(str, 非必填): 要读取的特定层。
- dataset(transforms.api.Input): 包含压缩 GDB 文件的输入数据集。
- glob(str, 非必填): 用于识别数据集中 GDB 文件的 glob 模式。默认是*.gdb.zip。
- layer(str, 非必填): 要读取的特定层。
- 示例Copied!12345678910111213from transforms.api import transform, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.parsers import gdb_to_dataframe

@geospatial()
@transform(
    output=Output('/my/output/dataset'),
    raw=Input('/my/input/dataset'),
)
def compute(raw, output):
    return output.write_dataframe(
        gdb_to_dataframe(raw)
    )
```
Copied!1
2
3
4
5
6
7
8
9
10
11
12
13
from transforms.api import transform, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.parsers import gdb_to_dataframe

@geospatial()
@transform(
    output=Output('/my/output/dataset'),
    raw=Input('/my/input/dataset'),
)
def compute(raw, output):
    return output.write_dataframe(
        gdb_to_dataframe(raw)
    )
```

#### kml_to_dataframe()

kml_to_dataframe(dataset, glob='*.kml')

将 KML 文件转换为数据帧。

- 参数dataset(transforms.api.Input): 包含 KML 文件的输入数据集。glob(str, 非必填): 用于识别数据集中 KML 文件的 glob 模式。默认是*.kml。drop_invalid_layers(bool, 非必填): 默认为false。如果设置为true，则会默默删除 KML 文件中空的/无法解析的层。否则，会引发出错。
- dataset(transforms.api.Input): 包含 KML 文件的输入数据集。
- glob(str, 非必填): 用于识别数据集中 KML 文件的 glob 模式。默认是*.kml。
- drop_invalid_layers(bool, 非必填): 默认为false。如果设置为true，则会默默删除 KML 文件中空的/无法解析的层。否则，会引发出错。
- 示例Copied!12345678910111213from transforms.api import transform, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.parsers import kml_to_dataframe

@geospatial()
@transform(
    output=Output('/my/output/dataset'),
    raw=Input('/my/input/dataset'),
)
def compute(raw, output):
    return output.write_dataframe(
        kml_to_dataframe(raw)
    )
```
Copied!1
2
3
4
5
6
7
8
9
10
11
12
13
from transforms.api import transform, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.parsers import kml_to_dataframe

@geospatial()
@transform(
    output=Output('/my/output/dataset'),
    raw=Input('/my/input/dataset'),
)
def compute(raw, output):
    return output.write_dataframe(
        kml_to_dataframe(raw)
    )
```

#### kmz_to_dataframe()

kmz_to_dataframe(dataset, glob='*.kmz')

将 KMZ 文件转换为数据帧。

- 参数dataset(transforms.api.Input): 包含 KMZ 文件的输入数据集。glob(str, 非必填): 用于识别数据集中 KMZ 文件的 glob 模式。默认是*.kmz。
- dataset(transforms.api.Input): 包含 KMZ 文件的输入数据集。
- glob(str, 非必填): 用于识别数据集中 KMZ 文件的 glob 模式。默认是*.kmz。
- 示例Copied!12345678910111213from transforms.api import transform, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.parsers import kmz_to_dataframe

@geospatial()
@transform(
    output=Output('/my/output/dataset'),
    raw=Input('/my/input/dataset'),
)
def compute(raw, output):
    return output.write_dataframe(
        kmz_to_dataframe(raw)
    )
```
Copied!1
2
3
4
5
6
7
8
9
10
11
12
13
from transforms.api import transform, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.parsers import kmz_to_dataframe

@geospatial()
@transform(
    output=Output('/my/output/dataset'),
    raw=Input('/my/input/dataset'),
)
def compute(raw, output):
    return output.write_dataframe(
        kmz_to_dataframe(raw)
    )
```

### 空间函数

#### geohash_to_geojson()

geohash_to_geojson(geometry)

将 geohash (lat,long) 列转换为 GeoJSON。

- 参数geometry(str): geohash 列名称。
- geometry(str): geohash 列名称。
- 示例Copied!1234567891011from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import geohash_to_geojson

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('geometry', geohash_to_geojson('geohash'))
```
Copied!1
2
3
4
5
6
7
8
9
10
11
from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import geohash_to_geojson

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('geometry', geohash_to_geojson('geohash'))
```

#### geojson_to_geohash()

geojson_to_geohash(geometry)

将点 GeoJSON 列转换为 geohash (lat,long)。

- 参数geometry(str): 点 GeoJSON 几何列名称。
- geometry(str): 点 GeoJSON 几何列名称。
- 示例Copied!1234567891011from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import geojson_to_geohash

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('geohash', geojson_to_geohash('geometry'))
```
Copied!1
2
3
4
5
6
7
8
9
10
11
from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import geojson_to_geohash

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('geohash', geojson_to_geohash('geometry'))
```

#### buffer()

buffer(geometry, meters, metric_crs='EPSG:3395')

根据给定距离缓冲 GeoJSON。

- 参数geometry(str): GeoJSON 几何列名称。meters(double): 缓冲距离（米）。metric_crs(str, 非必填): 用于转换和缓冲的指标 CRS（注意：此投影在中间步骤中使用。输出将保持与输入相同的投影）。应在目标区域附近居中以最小化失真。默认是EPSG:3395。
- geometry(str): GeoJSON 几何列名称。
- meters(double): 缓冲距离（米）。
- metric_crs(str, 非必填): 用于转换和缓冲的指标 CRS（注意：此投影在中间步骤中使用。输出将保持与输入相同的投影）。应在目标区域附近居中以最小化失真。默认是EPSG:3395。
- 示例Copied!1234567891011from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import buffer

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('geometry', buffer('geometry', meters=10))
```
Copied!1
2
3
4
5
6
7
8
9
10
11
from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import buffer

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('geometry', buffer('geometry', meters=10))
```

#### convex_hull()

convex_hull(geometry)

返回 GeoJSON 列的凸包。

- 参数geometry(str): GeoJSON 几何列名称。
- geometry(str): GeoJSON 几何列名称。
- 示例Copied!1234567891011from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import convex_hull

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('convex_hull', convex_hull('geometry'))
```
Copied!1
2
3
4
5
6
7
8
9
10
11
from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import convex_hull

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('convex_hull', convex_hull('geometry'))
```

#### bounding_box()

bounding_box(geometry)

返回 GeoJSON 列的边界框。

- 参数geometry(str): GeoJSON 几何列名称。
- geometry(str): GeoJSON 几何列名称。
- 示例Copied!1234567891011from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import bounding_box

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('bounding_box', bounding_box('geometry'))
```
Copied!1
2
3
4
5
6
7
8
9
10
11
from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import bounding_box

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('bounding_box', bounding_box('geometry'))
```

#### bounding_circle()

bounding_circle(geometry, segments=100)

返回 GeoJSON 列的边界圆。

- 参数geometry(str): GeoJSON 几何列名称。segments(int, 非必填): 构成圆的线段数。默认是100。
- geometry(str): GeoJSON 几何列名称。
- segments(int, 非必填): 构成圆的线段数。默认是100。
- 示例Copied!1234567891011from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import bounding_circle

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('bounding_circle', bounding_circle('geometry'))
```
Copied!1
2
3
4
5
6
7
8
9
10
11
from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import bounding_circle

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('bounding_circle', bounding_circle('geometry'))
```

#### simplify()

simplify(geometry, tolerance, metric_crs='EPSG:3395')

减少 GeoJSON 形状中的顶点数。

- 参数geometry(str): GeoJSON 几何列名称。tolerance(double): 新顶点与原始形状之间的最大距离（米）。metric_crs(str, 非必填): 用于计算容差的指标 CRS（注意：此投影在中间步骤中使用。输出将保持与输入相同的投影）。应在目标区域附近居中以最小化失真。默认是EPSG:3395。
- geometry(str): GeoJSON 几何列名称。
- tolerance(double): 新顶点与原始形状之间的最大距离（米）。
- metric_crs(str, 非必填): 用于计算容差的指标 CRS（注意：此投影在中间步骤中使用。输出将保持与输入相同的投影）。应在目标区域附近居中以最小化失真。默认是EPSG:3395。
- 示例Copied!1234567891011from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import simplify

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('geometry', simplify('geometry', tolerance='10'))
```
Copied!1
2
3
4
5
6
7
8
9
10
11
from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import simplify

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('geometry', simplify('geometry', tolerance='10'))
```

#### start_point()

start_point(geometry)

返回 GeoJSON LineString 列的第一个点。

- 参数geometry(str): GeoJSON 几何列名称。
- geometry(str): GeoJSON 几何列名称。
- 示例Copied!1234567891011from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import start_point

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('start_point', start_point('geometry'))
```
Copied!1
2
3
4
5
6
7
8
9
10
11
from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import start_point

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('start_point', start_point('geometry'))
```

#### end_point()

end_point(geometry)

返回 GeoJSON LineString 列的最后一个点。

- 参数geometry(str): GeoJSON 几何列名称。
- geometry(str): GeoJSON 几何列名称。
- 示例Copied!1234567891011from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import end_point

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('end_point', end_point('geometry'))
```
Copied!1
2
3
4
5
6
7
8
9
10
11
from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import end_point

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('end_point', end_point('geometry'))
```

#### centroid()

centroid(geometry)

返回 GeoJSON 列的质心。

- 参数geometry(str): GeoJSON 几何列名称。
- geometry(str): GeoJSON 几何列名称。
- 示例Copied!1234567891011from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import centroid

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('centroid', centroid('geometry'))
```
Copied!1
2
3
4
5
6
7
8
9
10
11
from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import centroid

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('centroid', centroid('geometry'))
```

#### intersection()

intersection(geometry1, geometry2)

返回两个 GeoJSON 相交的形状。

- 参数geometry1(str): 第一个 GeoJSON 几何列名称。geometry2(str): 第二个 GeoJSON 几何列名称。
- geometry1(str): 第一个 GeoJSON 几何列名称。
- geometry2(str): 第二个 GeoJSON 几何列名称。
- 示例Copied!1234567891011from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import intersection

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('intersection', intersection('geometry1', 'geometry2'))
```
Copied!1
2
3
4
5
6
7
8
9
10
11
from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import intersection

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('intersection', intersection('geometry1', 'geometry2'))
```

#### difference()

difference(geometry1, geometry2)

返回geometry1中不与geometry2相交的部分。

- 参数geometry1(str): 第一个 GeoJSON 几何列名称。geometry2(str): 第二个 GeoJSON 几何列名称。
- geometry1(str): 第一个 GeoJSON 几何列名称。
- geometry2(str): 第二个 GeoJSON 几何列名称。
- 示例Copied!1234567891011from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import difference

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('difference', difference('geometry1', 'geometry2'))
```
Copied!1
2
3
4
5
6
7
8
9
10
11
from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import difference

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('difference', difference('geometry1', 'geometry2'))
```

#### symmetric_difference()

symmetric_difference(geometry1, geometry2)

返回一个形状，其中包含geometry1和geometry2不重叠的部分。

- 参数geometry1(str): 第一个 GeoJSON 几何列名称。geometry2(str): 第二个 GeoJSON 几何列名称。
- geometry1(str): 第一个 GeoJSON 几何列名称。
- geometry2(str): 第二个 GeoJSON 几何列名称。
- 示例Copied!1234567891011from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import symmetric_difference

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('symmetric_difference', symmetric_difference('geometry1', 'geometry2'))
```
Copied!1
2
3
4
5
6
7
8
9
10
11
from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import symmetric_difference

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('symmetric_difference', symmetric_difference('geometry1', 'geometry2'))
```

#### union()

union(geometry1, geometry2)

返回两个形状的并集。

- 参数geometry1(str): 第一个 GeoJSON 几何列名称。geometry2(str): 第二个 GeoJSON 几何列名称。
- geometry1(str): 第一个 GeoJSON 几何列名称。
- geometry2(str): 第二个 GeoJSON 几何列名称。
- 示例Copied!1234567891011from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import union

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('union', union('geometry1', 'geometry2'))
```
Copied!1
2
3
4
5
6
7
8
9
10
11
from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import union

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('union', union('geometry1', 'geometry2'))
```

#### distance()

distance(geometry1, geometry2, metric_crs='EPSG:3395')

返回两个 GeoJSON 几何之间的欧氏距离（米）。

- 参数geometry1(str): 第一个 GeoJSON 几何列名称。geometry2(str): 第二个 GeoJSON 几何列名称。metric_crs(str, 非必填): 用于计算距离的指标 CRS。应在目标区域附近居中以最小化失真。默认是EPSG:3395。
- geometry1(str): 第一个 GeoJSON 几何列名称。
- geometry2(str): 第二个 GeoJSON 几何列名称。
- metric_crs(str, 非必填): 用于计算距离的指标 CRS。应在目标区域附近居中以最小化失真。默认是EPSG:3395。
- 示例Copied!1234567891011from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import distance

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('distance', distance('geometry1', 'geometry2'))
```
Copied!1
2
3
4
5
6
7
8
9
10
11
from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import distance

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('distance', distance('geometry1', 'geometry2'))
```

#### length()

length(geometry, metric_crs='EPSG:3395')

返回 GeoJSON 形状的长度/周长（米）。

- 参数geometry(str): GeoJSON 几何列名称。metric_crs(str, 非必填): 用于计算长度的指标 CRS。应在目标区域附近居中以最小化失真。默认是EPSG:3395。
- geometry(str): GeoJSON 几何列名称。
- metric_crs(str, 非必填): 用于计算长度的指标 CRS。应在目标区域附近居中以最小化失真。默认是EPSG:3395。
- 示例Copied!1234567891011from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import length

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('perimeter', length('geometry'))
```
Copied!1
2
3
4
5
6
7
8
9
10
11
from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import length

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('perimeter', length('geometry'))
```

#### area()

area(geometry, metric_crs='EPSG:3395')

返回 GeoJSON 多边形的面积（平方米）。

- 参数geometry(str): GeoJSON 几何列名称。metric_crs(str, 非必填): 用于计算面积的指标 CRS。应在目标区域附近居中以最小化失真。默认是EPSG:3395。
- geometry(str): GeoJSON 几何列名称。
- metric_crs(str, 非必填): 用于计算面积的指标 CRS。应在目标区域附近居中以最小化失真。默认是EPSG:3395。
- 示例Copied!1234567891011from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import area

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('area', area('geometry'))
```
Copied!1
2
3
4
5
6
7
8
9
10
11
from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import area

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('area', area('geometry'))
```

#### contains()

contains(geometry1, geometry2)

如果geometry1完全包含geometry2，则返回true。

- 参数geometry1(str): 定义谓词的 GeoJSON 列。geometry2(str): 要针对geometry1测试的 GeoJSON 列。
- geometry1(str): 定义谓词的 GeoJSON 列。
- geometry2(str): 要针对geometry1测试的 GeoJSON 列。
- 示例Copied!1234567891011from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import contains

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('geometry1_contains_geometry2', contains('geometry1', 'geometry2'))
```
Copied!1
2
3
4
5
6
7
8
9
10
11
from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import contains

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('geometry1_contains_geometry2', contains('geometry1', 'geometry2'))
```

#### intersects()

intersects(geometry1, geometry2)

如果geometry1与geometry2相交，则返回true。

- 参数geometry1(str): 第一个 GeoJSON 几何列名称。geometry2(str): 第二个 GeoJSON 几何列名称。
- geometry1(str): 第一个 GeoJSON 几何列名称。
- geometry2(str): 第二个 GeoJSON 几何列名称。
- 示例Copied!1234567891011from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import intersects

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('geometry1_intersecting_geometry2', intersects('geometry1', 'geometry2'))
```
Copied!1
2
3
4
5
6
7
8
9
10
11
from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import intersects

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.withColumn('geometry1_intersecting_geometry2', intersects('geometry1', 'geometry2'))
```

#### agg_union()

agg_union(geometry)

返回通过合并组中所有几何体创建的形状（聚合并集）。

- 参数geometry(str): GeoJSON 几何列名称。
- geometry(str): GeoJSON 几何列名称。
- 示例Copied!1234567891011from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import agg_union

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.groupBy('country').agg(agg_union('geometry').alias('geometry'))
```
Copied!1
2
3
4
5
6
7
8
9
10
11
from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import agg_union

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.groupBy('country').agg(agg_union('geometry').alias('geometry'))
```

#### agg_intersection()

agg_intersection(geometry)

返回通过组中所有几何体的相交创建的形状（聚合相交）。

- 参数geometry(str): GeoJSON 几何列名称。
- geometry(str): GeoJSON 几何列名称。
- 示例Copied!1234567891011from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import agg_intersection

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.groupBy('country').agg(agg_intersection('geometry').alias('geometry'))
```
Copied!1
2
3
4
5
6
7
8
9
10
11
from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import agg_intersection

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.groupBy('country').agg(agg_intersection('geometry').alias('geometry'))
```

#### agg_bounding_box()

agg_bounding_box(geometry)

返回组中所有几何体的边界框（聚合边界框）。

- 参数geometry(str): GeoJSON 几何列名称。
- geometry(str): GeoJSON 几何列名称。
- 示例Copied!1234567891011from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import agg_bounding_box

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.groupBy('country').agg(agg_bounding_box('geometry').alias('geometry'))
```
Copied!1
2
3
4
5
6
7
8
9
10
11
from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import agg_bounding_box

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return df.groupBy('country').agg(agg_bounding_box('geometry').alias('geometry'))
```

#### subdivide_explode()

subdivide_explode(df, geometry, max_vertices)

将 GeoJSON 形状划分为更小的组件，返回每个组件的一行。用于优化包含非常复杂形状的列上的空间合并。

- 参数df(PySpark DataFrame): 输入数据帧。geometry(str): GeoJSON 几何列名称。max_vertices(int): 每个组件的最大顶点数。
- df(PySpark DataFrame): 输入数据帧。
- geometry(str): GeoJSON 几何列名称。
- max_vertices(int): 每个组件的最大顶点数。
- 示例Copied!1234567891011from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import subdivide_explode

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return subdivide_explode(df, 'geometry', max_vertices=1000)
```
Copied!1
2
3
4
5
6
7
8
9
10
11
from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial
from geospatial_tools.functions import subdivide_explode

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df=Input('/my/input/dataset'),
)
def compute(df):
    return subdivide_explode(df, 'geometry', max_vertices=1000)
```

### 空间合并

#### DataFrame.spatial_join()

DataFrame.spatial_join(right_df, on, how='inner', **kwargs)

使用空间交集合并两个数据帧。

- 参数right_df(PySpark DataFrame): 合并的右侧。on(tuple<str, str>):(left_geometry_column_name, right_geometry_column_name)的元组。how(str, 非必填): 合并类型（支持与常规 PySpark 合并相同的合并类型）。默认是inner。library(str, 非必填): 使用哪个库进行合并，h3或sedona。默认是h3。resolution(int, 非必填): 用于合并的 H3 分辨率（注意：这不影响结果，仅用于优化）。如果包含library='sedona'，则会引发异常。如果未包含，将推断出最佳猜测分辨率。left_partitions(int, 非必填): 使用library=sedona时左数据帧默认重新分区方案的可选覆盖。如果包含时使用 H3，会引发异常。right_partitions(int, 非必填): 使用library=sedona时右数据帧默认重新分区方案的可选覆盖。如果包含时使用 H3，会引发异常。left_pk(str, 非必填): 合并左侧的主键列。如果未设置，将自动生成一个 PK。right_pk(str, 非必填): 合并右侧的主键列。如果未设置，将自动生成一个 PK。
- right_df(PySpark DataFrame): 合并的右侧。
- on(tuple<str, str>):(left_geometry_column_name, right_geometry_column_name)的元组。
- how(str, 非必填): 合并类型（支持与常规 PySpark 合并相同的合并类型）。默认是inner。
- library(str, 非必填): 使用哪个库进行合并，h3或sedona。默认是h3。
- resolution(int, 非必填): 用于合并的 H3 分辨率（注意：这不影响结果，仅用于优化）。如果包含library='sedona'，则会引发异常。如果未包含，将推断出最佳猜测分辨率。
- left_partitions(int, 非必填): 使用library=sedona时左数据帧默认重新分区方案的可选覆盖。如果包含时使用 H3，会引发异常。
- right_partitions(int, 非必填): 使用library=sedona时右数据帧默认重新分区方案的可选覆盖。如果包含时使用 H3，会引发异常。
- left_pk(str, 非必填): 合并左侧的主键列。如果未设置，将自动生成一个 PK。
- right_pk(str, 非必填): 合并右侧的主键列。如果未设置，将自动生成一个 PK。
- 示例Copied!1234567891011from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df1=Input('/my/input/dataset1'),
    df2=Input('/my/input/dataset2'),
)
def compute(df1, df2):
    return df.spatial_join(df2, ('df1_geometry', 'df2_geometry'), 'left')
```
Copied!1
2
3
4
5
6
7
8
9
10
11
from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df1=Input('/my/input/dataset1'),
    df2=Input('/my/input/dataset2'),
)
def compute(df1, df2):
    return df.spatial_join(df2, ('df1_geometry', 'df2_geometry'), 'left')
```

#### DataFrame.distance_join()

DataFrame.distance_join(right_df, on, distance_meters, how='inner', metric_crs='EPSG:3395', **kwargs)

在两个数据帧上执行距离合并。

- 参数right_df(PySpark DataFrame): 合并的右侧。on(tuple<str, str>):(left_geometry_column_name, right_geometry_column_name)的元组。distance_meters(double): 合并距离（米）。how(str, 非必填): 合并类型（支持与常规 PySpark 合并相同的合并类型）。默认是inner。metric_crs(str, 非必填): 用于计算距离的指标 CRS。应在目标区域附近居中以最小化失真。默认是EPSG:3395。left_pk(str, 非必填): 合并左侧的主键列。如果未设置，将自动生成一个 PK。right_pk(str, 非必填): 合并右侧的主键列。如果未设置，将自动生成一个 PK。library(str, 非必填): 使用哪个库进行合并，h3或sedona。默认是h3。resolution(int, 非必填): 用于合并的 H3 分辨率（注意：这不影响结果，仅用于优化）。如果包含library='sedona'，则会引发异常。如果未包含，将推断出最佳猜测分辨率。left_partitions(int, 非必填): 使用library=sedona时左数据帧默认重新分区方案的可选覆盖。如果包含时使用 H3，会引发异常。right_partitions(int, 非必填): 使用library=sedona时右数据帧默认重新分区方案的可选覆盖。如果包含时使用 H3，会引发异常。
- right_df(PySpark DataFrame): 合并的右侧。
- on(tuple<str, str>):(left_geometry_column_name, right_geometry_column_name)的元组。
- distance_meters(double): 合并距离（米）。
- how(str, 非必填): 合并类型（支持与常规 PySpark 合并相同的合并类型）。默认是inner。
- metric_crs(str, 非必填): 用于计算距离的指标 CRS。应在目标区域附近居中以最小化失真。默认是EPSG:3395。
- left_pk(str, 非必填): 合并左侧的主键列。如果未设置，将自动生成一个 PK。
- right_pk(str, 非必填): 合并右侧的主键列。如果未设置，将自动生成一个 PK。
- library(str, 非必填): 使用哪个库进行合并，h3或sedona。默认是h3。
- resolution(int, 非必填): 用于合并的 H3 分辨率（注意：这不影响结果，仅用于优化）。如果包含library='sedona'，则会引发异常。如果未包含，将推断出最佳猜测分辨率。
- left_partitions(int, 非必填): 使用library=sedona时左数据帧默认重新分区方案的可选覆盖。如果包含时使用 H3，会引发异常。
- right_partitions(int, 非必填): 使用library=sedona时右数据帧默认重新分区方案的可选覆盖。如果包含时使用 H3，会引发异常。
- 示例Copied!1234567891011from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df1=Input('/my/input/dataset1'),
    df2=Input('/my/input/dataset2'),
)
def compute(df1, df2):
    return df.distance_join(df2, ('df1_geometry', 'df2_geometry'), 10, 'left')
```
Copied!1
2
3
4
5
6
7
8
9
10
11
from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df1=Input('/my/input/dataset1'),
    df2=Input('/my/input/dataset2'),
)
def compute(df1, df2):
    return df.distance_join(df2, ('df1_geometry', 'df2_geometry'), 10, 'left')
```

#### DataFrame.knn_join()

DataFrame.knn_join(right_df, on, k, metric_crs='EPSG:3395', **kwargs)

执行右数据帧中 k 近邻的左合并。

- 参数right_df(PySpark DataFrame): 合并的右侧。on(tuple<str, str>):(left_geometry_column_name, right_geometry_column_name)的元组。k(int): 左数据帧中每条记录应匹配的右数据帧中的记录数。metric_crs(str, 非必填): 用于计算距离的指标 CRS。应在目标区域附近居中以最小化失真。默认是EPSG:3395。resolution(int, 非必填): 用于合并的 H3 分辨率（注意：这不影响结果，仅用于优化）。如果未包含，将推断出最佳猜测分辨率。left_pk(str, 非必填): 合并左侧的主键列。如果未设置，将自动生成一个 PK。right_pk(str, 非必填): 合并右侧的主键列。如果未设置，将自动生成一个 PK。
- right_df(PySpark DataFrame): 合并的右侧。
- on(tuple<str, str>):(left_geometry_column_name, right_geometry_column_name)的元组。
- k(int): 左数据帧中每条记录应匹配的右数据帧中的记录数。
- metric_crs(str, 非必填): 用于计算距离的指标 CRS。应在目标区域附近居中以最小化失真。默认是EPSG:3395。
- resolution(int, 非必填): 用于合并的 H3 分辨率（注意：这不影响结果，仅用于优化）。如果未包含，将推断出最佳猜测分辨率。
- left_pk(str, 非必填): 合并左侧的主键列。如果未设置，将自动生成一个 PK。
- right_pk(str, 非必填): 合并右侧的主键列。如果未设置，将自动生成一个 PK。
- 示例Copied!1234567891011from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df1=Input('/my/input/dataset1'),
    df2=Input('/my/input/dataset2'),
)
def compute(df1, df2):
    return df.knn_join(df2, ('df1_geometry', 'df2_geometry'), k=1)
```
Copied!1
2
3
4
5
6
7
8
9
10
11
from transforms.api import transform_df, Input, Output
from geospatial_tools import geospatial

@geospatial()
@transform_df(
    Output('/my/output/dataset'),
    df1=Input('/my/input/dataset1'),
    df2=Input('/my/input/dataset2'),
)
def compute(df1, df2):
    return df.knn_join(df2, ('df1_geometry', 'df2_geometry'), k=1)
```

#### geopandas_spatial_join()

geopandas_spatial_join(df_left, df_right, geometry_left, geometry_right, how='inner', op='intersects')

计算两个 Geopandas 数据帧的空间合并。实现 Geopandas 的 'sjoin' 方法。期望两个数据帧都包含一个 GeoJSON 几何列，其名称通过geometry_left和geometry_right参数传递。

- 对于大型数据规模，使用上面记录的DataFrame.spatial_join函数。
- 参数df_left(pandas.DataFrame↗): 左输入数据帧。df_right(pandas.DataFrame↗): 右输入数据帧。geometry_left(str): 左数据帧的几何列名称。geometry_right(str): 右数据帧的几何列名称。how(str, 非必填): 合并类型，{left,right,inner} 之一。默认是inner。op(str, 非必填): 合并条件，{intersects,contains,within} 之一。默认是intersects。
- df_left(pandas.DataFrame↗): 左输入数据帧。
- df_right(pandas.DataFrame↗): 右输入数据帧。
- geometry_left(str): 左数据帧的几何列名称。
- geometry_right(str): 右数据帧的几何列名称。
- how(str, 非必填): 合并类型，{left,right,inner} 之一。默认是inner。
- op(str, 非必填): 合并条件，{intersects,contains,within} 之一。默认是intersects。
- 示例Copied!123456789101112131415161718192021222324from transforms.api import transform, Input, Output
from geospatial_tools.spatial_joins import geopandas_spatial_join

@transform(
    output=Output('/my/output/dataset'),
    input_df_left=Input('/my/input/dataset/left'),
    input_df_right=Input('/my/input/dataset/right'),
)
def join(ctx, output, input_df_left, input_df_right):
  df_left = input_df_left.dataframe().toPandas()
  df_right = input_df_right.dataframe().toPandas()
  geometry_left = 'geometry'
  geometry_right = 'geometry'

  joined = geopandas_spatial_join(
        df_left,
        df_right,
        geometry_left,
        geometry_right,
        how='inner',
        op='intersects'
    )
    joined = ctx.spark_session.createDataFrame(joined)
    output.write_dataframe(joined)
```
Copied!1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
from transforms.api import transform, Input, Output
from geospatial_tools.spatial_joins import geopandas_spatial_join

@transform(
    output=Output('/my/output/dataset'),
    input_df_left=Input('/my/input/dataset/left'),
    input_df_right=Input('/my/input/dataset/right'),
)
def join(ctx, output, input_df_left, input_df_right):
  df_left = input_df_left.dataframe().toPandas()
  df_right = input_df_right.dataframe().toPandas()
  geometry_left = 'geometry'
  geometry_right = 'geometry'

  joined = geopandas_spatial_join(
        df_left,
        df_right,
        geometry_left,
        geometry_right,
        how='inner',
        op='intersects'
    )
    joined = ctx.spark_session.createDataFrame(joined)
    output.write_dataframe(joined)
```

## 帮助和贡献

请联系您的 Palantir 代表以报告任何问题或反馈。
