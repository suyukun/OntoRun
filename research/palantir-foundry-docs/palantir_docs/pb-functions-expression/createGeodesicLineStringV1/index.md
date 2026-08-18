来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/createGeodesicLineStringV1/

# 创建大地线字符串

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 创建大地线字符串

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

在两点之间创建一条大地线。

表达式类别: 地理空间

## 声明的参数

- 终点- 终点的经度和纬度。Expression<GeoPoint>
- 起始点- 起始点的经度和纬度。Expression<GeoPoint>
- 非必填步数- 在大地线段的起点和终点之间返回的点数。默认值为24点。Expression<Byte | Integer | Long | Short>
输出类型:Geometry

## 示例

### 示例 1: 基本情况

参数值:

- 终点:endPoint
- 起始点:startPoint
- 步数:numSteps
| startPoint | endPoint | numSteps | 输出 |
| --- | --- | --- | --- |
| {latitude: 20.92,longitude: 179.0,} | {latitude: 20.92,longitude: -178.0,} | 3 | {"type":"MultiLineString","coordinates":[[[-180.0, 20.925458598035362],[-179.5, 20.926550359447504],... |

### 示例 2: 基本情况

参数值:

- 终点:endPoint
- 起始点:startPoint
- 步数:numSteps
| startPoint | endPoint | numSteps | 输出 |
| --- | --- | --- | --- |
| {latitude: 38.9072,longitude: -77.0369,} | {latitude: 20.92,longitude: -70.0,} | 8 | {"type":"LineString","coordinates":[[-77.0369, 38.90720000000001],[-76.10884874732801, 36.9298141100... |

### 示例 3: 基本情况

参数值:

- 终点:endPoint
- 起始点:startPoint
- 步数:numSteps
| startPoint | endPoint | numSteps | 输出 |
| --- | --- | --- | --- |
| {latitude: 34.1309,longitude: -88.908,} | {latitude: 34.496,longitude: -83.9651,} | 4 | {"type":"LineString","coordinates":[[-88.90800000000002, 34.13089999999999],[-87.9230399151116, 34.2... |

### 示例 4: 基本情况

参数值:

- 终点:endPoint
- 起始点:startPoint
- 步数:numSteps
| startPoint | endPoint | numSteps | 输出 |
| --- | --- | --- | --- |
| {latitude: 39.4953,longitude: -89.6352,} | {latitude: 61.0928,longitude: 62.2376,} | 4 | {"type":"LineString","coordinates":[[-89.6352, 39.4953],[-83.5342527561974, 54.30031923899314],[-70.... |

### 示例 5: 基本情况

参数值:

- 终点:endPoint
- 起始点:startPoint
- 步数:numSteps
| startPoint | endPoint | numSteps | 输出 |
| --- | --- | --- | --- |
| {latitude: 38.9072,longitude: -77.0369,} | {latitude: 20.92,longitude: -70.0,} | null | {"type":"LineString","coordinates":[[-77.0369, 38.90720000000001],[-76.69701959729164, 38.1961853930... |

### 示例 6: 基本情况

参数值:

- 终点:endPoint
- 起始点:startPoint
- 步数:numSteps
| startPoint | endPoint | numSteps | 输出 |
| --- | --- | --- | --- |
| {latitude: 20.92,longitude: -70.0,} | {latitude:null,longitude: -77.0369,} | 8 | null |

### 示例 7: 基本情况

参数值:

- 终点:endPoint
- 起始点:startPoint
- 步数:numSteps
| startPoint | endPoint | numSteps | 输出 |
| --- | --- | --- | --- |
| {latitude: 20.92,longitude: -70.0,} | {latitude:null,longitude:null,} | 8 | null |

### 示例 8: 基本情况

参数值:

- 终点:endPoint
- 起始点:startPoint
- 步数:numSteps
| startPoint | endPoint | numSteps | 输出 |
| --- | --- | --- | --- |
| {latitude: 20.92,longitude: -70.0,} | {latitude: 38.9072,longitude:null,} | 8 | null |

### 示例 9: 基本情况

参数值:

- 终点:endPoint
- 起始点:startPoint
- 步数:numSteps
| startPoint | endPoint | numSteps | 输出 |
| --- | --- | --- | --- |
| {latitude: 39.4953,longitude: -89.6352,} | null | 8 | null |

### 示例 10: 基本情况

参数值:

- 终点:endPoint
- 起始点:startPoint
- 步数:numSteps
| startPoint | endPoint | numSteps | 输出 |
| --- | --- | --- | --- |
| {latitude:null,longitude:null,} | {latitude:null,longitude:null,} | 8 | null |

### 示例 11: 基本情况

参数值:

- 终点:endPoint
- 起始点:startPoint
- 步数:numSteps
| startPoint | endPoint | numSteps | 输出 |
| --- | --- | --- | --- |
| {latitude:null,longitude:null,} | {latitude:null,longitude:null,} | null | null |

### 示例 12: 基本情况

参数值:

- 终点:endPoint
- 起始点:startPoint
- 步数:numSteps
| startPoint | endPoint | numSteps | 输出 |
| --- | --- | --- | --- |
| null | null | 8 | null |

### 示例 13: 基本情况

参数值:

- 终点:endPoint
- 起始点:startPoint
- 步数:numSteps
| startPoint | endPoint | numSteps | 输出 |
| --- | --- | --- | --- |
| {latitude:null,longitude: -77.0369,} | {latitude: 20.92,longitude: -70.0,} | 8 | null |

### 示例 14: 基本情况

参数值:

- 终点:endPoint
- 起始点:startPoint
- 步数:numSteps
| startPoint | endPoint | numSteps | 输出 |
| --- | --- | --- | --- |
| {latitude:null,longitude:null,} | {latitude: 20.92,longitude: -70.0,} | 8 | null |

### 示例 15: 基本情况

参数值:

- 终点:endPoint
- 起始点:startPoint
- 步数:numSteps
| startPoint | endPoint | numSteps | 输出 |
| --- | --- | --- | --- |
| {latitude: 38.9072,longitude:null,} | {latitude: 20.92,longitude: -70.0,} | 8 | null |

### 示例 16: 基本情况

参数值:

- 终点:endPoint
- 起始点:startPoint
- 步数:numSteps
| startPoint | endPoint | numSteps | 输出 |
| --- | --- | --- | --- |
| null | {latitude: 20.92,longitude: -70.0,} | 8 | null |
