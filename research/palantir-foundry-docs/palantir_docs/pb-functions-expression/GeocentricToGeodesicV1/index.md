来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/GeocentricToGeodesicV1/

# 将地心坐标转换为WGS 84大地坐标

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 将地心坐标转换为WGS 84大地坐标

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

将地心笛卡尔坐标转换为大地极坐标。高度定义为椭球体上的高度。如果任何坐标为null，则输出将为null。

表达式类别: 地理空间

## 声明的参数

- X坐标- 源坐标系中的X坐标。表达式<数值>
- Y坐标- 源坐标系中的Y坐标。表达式<数值>
- Z坐标- 源坐标系中的Z坐标。表达式<数值>
输出类型:带高度的GeoPoint

## 示例

### 示例1: 基本情况

参数值:

- X坐标:x_coordinate
- Y坐标:y_coordinate
- Z坐标:z_coordinate
| x_coordinate | y_coordinate | z_coordinate | 输出 |
| --- | --- | --- | --- |
| 0.0 | 6378137.0 | 0.0 | {altitude -> 0.0,geoPoint -> {latitude -> 0.0,longitude -> 90.0,},} |
| 0.0 | -6378137.0 | 0.0 | {altitude -> 0.0,geoPoint -> {latitude -> 0.0,longitude -> -90.0,},} |
| -6378137.0 | 0.0 | 0.0 | {altitude -> 0.0,geoPoint -> {latitude -> 0.0,longitude -> 180.0,},} |
| -6378137.0 | -0.0 | 0.0 | {altitude -> 0.0,geoPoint -> {latitude -> 0.0,longitude -> -180.0,},} |
| 0.0 | 0.0 | 6356752.314245179 | {altitude -> 0.0,geoPoint -> {latitude -> 90.0,longitude -> 0.0,},} |
| 0.0 | 0.0 | -6356752.314245179 | {altitude -> 0.0,geoPoint -> {latitude -> -90.0,longitude -> 0.0,},} |

### 示例2: 空值情况

参数值:

- X坐标:x_coordinate
- Y坐标:y_coordinate
- Z坐标:z_coordinate
| x_coordinate | y_coordinate | z_coordinate | 输出 |
| --- | --- | --- | --- |
| null | 0.0 | 0.0 | null |
| 0.0 | null | 0.0 | null |
| 0.0 | 0.0 | null | null |

### 示例3: 边缘情况

参数值:

- X坐标:x_coordinate
- Y坐标:y_coordinate
- Z坐标:z_coordinate
| x_coordinate | y_coordinate | z_coordinate | 输出 |
| --- | --- | --- | --- |
| 1.0E-7 | 0.0 | 6356752.314245179 | {altitude -> 0.0,geoPoint -> {latitude -> 89.9999999999991,longitude -> 0.0,},} |
| 1.0E-7 | 0.0 | -6356752.314245179 | {altitude -> 0.0,geoPoint -> {latitude -> -89.9999999999991,longitude -> 0.0,},} |
| -6378137.0 | -1.0E-7 | 0.0 | {altitude -> 0.0,geoPoint -> {latitude -> 0.0,longitude -> -179.9999999999991,},} |
| -6378137.0 | 1.0E-7 | 0.0 | {altitude -> 0.0,geoPoint -> {latitude -> 0.0,longitude -> 179.9999999999991,},} |
