来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/getBearingV1/

# 从起点到终点的方位角计算

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 从起点到终点的方位角计算

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

使用地球的球面近似计算从第一个点到第二个点的绝对真方位角（相对于地理北方的顺时针角度），单位为度。

表达式类别: 地理空间

## 声明的参数

- 终点- 终点的经度和纬度。Expression<GeoPoint>
- 起点- 起点的经度和纬度。Expression<GeoPoint>
输出类型:Double

## 示例

### 示例 1: 基本案例

参数值:

- 终点:end_point
- 起点:start_point
| start_point | end_point | 输出 |
| --- | --- | --- |
| {latitude: 40.69325025929194,longitude: -74.00522662934995,} | {latitude: 51.4988509390695,longitude: -0.1238396067697046,} | 51.20964213763489 |

### 示例 2: 边界案例

参数值:

- 终点:end_point
- 起点:start_point
| start_point | end_point | 输出 |
| --- | --- | --- |
| {latitude: -41.304077,longitude: 174.75,} | {latitude: -31.304077,longitude: 174.749,} | 359.99507958062 |

### 示例 3: 边界案例

参数值:

- 终点:end_point
- 起点:start_point
| start_point | end_point | 输出 |
| --- | --- | --- |
| {latitude: -41.304077,longitude: 174.75,} | {latitude: -31.304077,longitude: 174.75,} | 0.0 |

### 示例 4: 边界案例

参数值:

- 终点:end_point
- 起点:start_point
| start_point | end_point | 输出 |
| --- | --- | --- |
| {latitude: -41.304077,longitude: 174.774535,} | {latitude: 37.42984400901383,longitude: -122.16950590121428,} | 45.56453711814595 |

### 示例 5: 边界案例

参数值:

- 终点:end_point
- 起点:start_point
| start_point | end_point | 输出 |
| --- | --- | --- |
| null | null | null |

### 示例 6: 边界案例

参数值:

- 终点:end_point
- 起点:start_point
| start_point | end_point | 输出 |
| --- | --- | --- |
| {latitude: 48.8567,longitude: 2.3508,} | {latitude: 48.8567,longitude: 2.3508,} | 0.0 |
