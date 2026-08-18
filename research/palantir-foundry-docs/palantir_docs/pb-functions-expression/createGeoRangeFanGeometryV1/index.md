来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/createGeoRangeFanGeometryV1/

# 创建范围扇形几何图形

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 创建范围扇形几何图形

> 支持于: 批处理, 流式处理

支持于: 批处理, 流式处理

近似一个范围扇形为一个多边形，指定所有点到原点的haversine距离在最小和最大半径之间的区域，以及从原点到指定方位参数的角度范围内的区域。范围扇形的左右两侧被绘制为沿WGS84椭球表面计算的测地线，近似地球表面。如果范围跨越超过180度同时也跨越反子午线，或者如果最大半径跨越超过地球周长的一半，则返回null。

表达式类别: 地理空间

## 声明的参数

- 方位- 范围扇形相对于北极的方位。Expression<DefiniteNumeric>
- 最大半径长度- 椭圆的最大半径长度。必须大于最小半径且小于地球周长的一半。Expression<DefiniteNumeric>
- 最大半径长度单位- 最大半径的单位。Enum<Centimeter, Data mile, Decameter, Decimeter, Foot, Hectometer, Inch, Kilometer, Meter, Mile, and more ...>
- 最小半径长度- 椭圆的最小半径长度。必须小于最大半径。Expression<DefiniteNumeric>
- 最小半径长度单位- 最小半径的单位。Enum<Centimeter, Data mile, Decameter, Decimeter, Foot, Hectometer, Inch, Kilometer, Meter, Mile, and more ...>
- 原点- 范围扇形的经度和纬度。Expression<GeoPoint>
- 范围- 范围扇形的角度范围，围绕其方位。必须大于0度。目前不支持同时跨越180度且跨越反子午线的范围扇形，返回null。Expression<DefiniteNumeric>
- 非必填方位角单位- 方位的单位，默认是度。Enum<Degrees, Minutes, Radians, Seconds>
- 非必填弧点数- 用于近似范围扇形每侧弧线的点数。Expression<Byte | Integer | Long | Short>
- 非必填侧边点数- 用于近似范围扇形侧边的点数。Expression<Byte | Integer | Long | Short>
- 非必填范围角单位- 范围的单位，默认是度。Enum<Degrees, Minutes, Radians, Seconds>
输出类型:Geometry
