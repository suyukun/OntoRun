来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/createQualifiedTimeSeriesIdV1/

# 创建时间序列参考值

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 创建时间序列参考值

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

创建时间序列参考值。

表达式类别: 字符串

## 声明的参数

- 系列标识符- 时间序列同步中包含的系列标识符。表达式<字符串>
- 时间序列同步 RID- 包含系列标识符的时间序列同步的资源标识符 (RID)。表达式<字符串>
输出类型:字符串

## 示例

### 示例 1: 基本情况

参数值:

- 系列标识符:seriesId
- 时间序列同步 RID: ri.time-series-catalog.main.sync.11111111
| seriesId | 输出 |
| --- | --- |
| seriesOne | {"seriesId":"seriesOne","syncRid":"ri.time-series-catalog.main.sync.11111111"} |

### 示例 2: 基本情况

参数值:

- 系列标识符:seriesId
- 时间序列同步 RID:syncRid
| seriesId | syncRid | 输出 |
| --- | --- | --- |
| seriesOne | ri.time-series-catalog.main.sync.11111111 | {"seriesId":"seriesOne","syncRid":"ri.time-series-catalog.main.sync.11111111"} |
| seriesTwo | ri.time-series-catalog.main.sync.22222222 | {"seriesId":"seriesTwo","syncRid":"ri.time-series-catalog.main.sync.22222222"} |

### 示例 3: 空值情况

参数值:

- 系列标识符:seriesId
- 时间序列同步 RID: ri.time-series-catalog.main.sync.11111111
| seriesId | 输出 |
| --- | --- |
| null | {"seriesId":"null","syncRid":"ri.time-series-catalog.main.sync.11111111"} |

### 示例 4: 空值情况

参数值:

- 系列标识符:seriesId
- 时间序列同步 RID:null
| seriesId | 输出 |
| --- | --- |
| seriesOne | {"seriesId":"seriesOne","syncRid":"null"} |
