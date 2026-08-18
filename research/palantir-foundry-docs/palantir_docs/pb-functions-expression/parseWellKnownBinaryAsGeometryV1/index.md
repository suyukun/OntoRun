来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/parseWellKnownBinaryAsGeometryV1/

# 将知名二进制解析为几何

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 将知名二进制解析为几何

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

将知名二进制 (WKB) 转换为几何逻辑类型。无效的 WKB 输入将返回为空。可选择提供源坐标系标识符，以便从源坐标系转换为 WGS 84（如果 WKB 尚未在 WGS 84 中）。

表达式类别：地理空间

## 声明的参数

- 表达式- 作为二进制的有效知名二进制。Expression<Binary>
- 非必填源坐标系- 如果知名二进制不是 WGS 84，则为非必填的坐标系标识符。格式为 "authority"。例如，UTM 第 18N 区域可以通过 EPSG:32618 来识别。Literal<字符串>
输出类型：Geometry

## 示例

### 示例 1：基本情况

参数值：

- 表达式:wkb
- 源坐标系:null
| wkb | 输出 |
| --- | --- |
| AAAAAAFACAAAAAAAAEAUAAAAAAAA | {"type":"Point","coordinates":[3.0, 5.0]} |
| AIAAAAFACAAAAAAAAEAUAAAAAAAAQAAAAAAAAAA= | {"type":"Point","coordinates":[3.0, 5.0, 2.0]} |
| AAAAAAMAAAABAAAABAAAAAAAAAAAAAAAAAAAAAA/8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= | {"type":"Polygon","coordinates":[[[0.0,0.0],[1.0,0.0],[0.0,1.0],[0.0,0.0]]]} |
| AAAAAAIAAAACAAAAAAAAAAAAAAAAAAAAAD/wAAAAAAAAAAAAAAAAAAA= | {"type":"LineString","coordinates":[[0.0,0.0],[1.0,0.0]]} |

### 示例 2：基本情况

参数值：

- 表达式:wkb
- 源坐标系: EPSG:32618
| wkb | 输出 |
| --- | --- |
| AAAAAAFBE4gAAAAAAEFQZzgAAAAA | {"type":"Point","coordinates":[-77.07368071728229,38.83040844313318]} |
| AIAAAAFBE4gAAAAAAEFQZzgAAAAAQAAAAAAAAAA= | {"type":"Point","coordinates":[-77.07368071728229,38.83040844313318, 2.0]} |
| AAAAAAMAAAABAAAABEETiAAAAAAAQVBnOAAAAABBE4mQAAAAAEFQZzgAAAAAQROIAAAAAABBUGdRAAAAAEETiAAAAAAAQVBnOAAAAAA= | {"type":"Polygon","coordinates":[[[-77.07368071728229,38.83040844313318],[-77.0725293738795,38.83042888342659],[-77.07370685720375,38.83130901341597],[-77.07368071728229,38.83040844313318]]]} |
| AAAAAAIAAAACQROIAAAAAABBUGc4AAAAAEETiZAAAAAAQVBnOAAAAAA= | {"type":"LineString","coordinates":[[-77.07368071728229,38.83040844313318],[-77.0725293738795,38.83042888342659]]} |

### 示例 3：空情况

参数值：

- 表达式:wkb
- 源坐标系:null
| wkb | 输出 |
| --- | --- |
|  | null |
| null | null |
