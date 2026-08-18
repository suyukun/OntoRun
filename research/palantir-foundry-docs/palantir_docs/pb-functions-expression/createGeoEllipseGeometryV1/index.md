来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/createGeoEllipseGeometryV1/

# 创建椭圆几何形状

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 创建椭圆几何形状

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

将椭圆近似为一个以给定地理坐标为中心的多边形。点之间的距离沿着近似地球表面的WGS84椭球体表面计算。

表达式类别: 地理空间

## 声明的参数

- 中心- 椭圆中心的经度和纬度。Expression<GeoPoint>
- 半长轴长度- 椭圆最长半径（轴的一半）的长度。Expression<DefiniteNumeric>
- 半长轴长度单位- 半长轴长度的单位。Enum<Centimeter, Data mile, Decameter, Decimeter, Foot, Hectometer, Inch, Kilometer, Meter, Mile, and more ...>
- 半短轴- 椭圆最短半径（轴的一半）的长度。Expression<DefiniteNumeric>
- 半短轴长度单位- 半短轴长度的单位。Enum<Centimeter, Data mile, Decameter, Decimeter, Foot, Hectometer, Inch, Kilometer, Meter, Mile, and more ...>
- 非必填方位角- 主轴与y轴之间的角度。正角表示顺时针旋转，负角表示逆时针旋转。Expression<DefiniteNumeric>
- 非必填方位角单位- 方位角的单位。Enum<Degrees, Minutes, Radians, Seconds>
- 非必填点的数量- 用于近似椭圆的点的数量。Expression<Byte | Integer | Long | Short>
输出类型:Geometry
