来源: https://palantir.com/docs/zh/foundry/foundryts/functions-unit-conversion/

# foundryts.functions.unit_conversion

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.functions.unit_conversion

## foundryts.functions.unit_conversion(from_unit, to_unit)

返回一个函数，该函数将单个时间序列中的所有值从指定单位值转换为指定单位。

传入的单位可以是Unit中的一个值，也可以是以下可用单位和转换列表中的一个有效Alias：

长度

| 单位 | 别名 | 名称 |
| --- | --- | --- |
| m | meter | 米 |
| cm | centimeter | 厘米 |
| mm | millimeter | 毫米 |
| μm | micron, micrometer | 微米 |
| nm | nanometer | 纳米 |
| angstrom |  | 埃 |
| km | kilometer | 公里 |
| in | inch | 英寸 |
| ft | foot | 英尺 |
| yd | yard | 码 |
| mi | mile | 英里 |

温度单位

| 单位 | 别名 | 名称 |
| --- | --- | --- |
| °C | Celsius | 摄氏度 |
| K | kelvin | 开尔文 |
| °F | Fahrenheit | 华氏度 |
| °R | °Ra, rankine | 兰氏度 |

压力单位

| 单位 | 别名 | 名称 |
| --- | --- | --- |
| Pa | n/m2, pascal | 帕斯卡 |
| hPa | hectopascal | 百帕斯卡 |
| kPa | kPaa, kilopascal | 千帕斯卡 |
| kPag |  | 千帕斯卡表压 |
| atm |  | 标准大气压 |
| bar | bara | 巴 |
| barg |  | 巴表压 |
| fth2o |  | 水柱英尺 |
| inh2o |  | 水柱英寸 |
| inhg |  | 汞柱英寸 |
| Torr | mmhg | 托（毫米汞柱） |
| mTorr |  | 毫托 |
| psi | psia | 磅力每平方英寸 |
| psig |  | 磅力每平方英寸表压 |

时间单位

| 单位 | 别名 | 名称 |
| --- | --- | --- |
| s | second | 秒 |
| ms | millisecond | 毫秒 |
| μs | microsecond | 微秒 |
| ns | nanosecond | 纳秒 |
| min | minute | 分钟 |
| hr | hour | 小时 |

质量单位

| 单位 | 别名 | 名称 |
| --- | --- | --- |
| kg | kilogram | 千克 |
| g | gram | 克 |
| lb | pound | 磅 |

联系您的服务管理员以访问和扩展部署的单位和转换列表。

- 参数:from_unit(str) – 原始单位以进行值转换。to_unit(str) – 目标单位以进行值转换。
- from_unit(str) – 原始单位以进行值转换。
- to_unit(str) – 目标单位以进行值转换。
- 返回:一个函数，接受一个单时间序列作为输入，并返回转换为指定单位的时间序列。
- 返回类型:(FunctionNode) ->FunctionNode
## 数据框架结构

| 列名 | 类型 | 描述 |
| --- | --- | --- |
| timestamp | pandas.Timestamp | 点的时间戳 |
| value | float | 点的值 |

此函数仅适用于数值系列。

## 示例

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
>>> series = F.points(
...     (1, 8.0),
...     (101, 4.0),
...     (200, 2.0),
...     (201, 1.0),
...     (299, 35.0),
...     (300, 16.0),
...     (1000, 64.0),
...     name="series",
... )
>>> series.to_pandas()
                      timestamp  value
0 1970-01-01 00:00:00.000000001    8.0
1 1970-01-01 00:00:00.000000101    4.0
2 1970-01-01 00:00:00.000000200    2.0
3 1970-01-01 00:00:00.000000201    1.0
4 1970-01-01 00:00:00.000000299   35.0
5 1970-01-01 00:00:00.000000300   16.0
6 1970-01-01 00:00:00.000001000   64.0
```

这个代码片段展示了如何使用F.points方法创建一个时间序列对象series，其中包含一组时间戳和对应的值。接着，使用to_pandas方法将这个时间序列转换为一个 Pandas DataFrame，以便更方便地进行数据分析和处理。时间戳是以纳秒为单位的时间点。

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
>>> unit_converted = F.unit_conversion("m", "mm")(series)
# 将单位从米("m")转换为毫米("mm")

>>> unit_converted.to_pandas()
# 将转换后的数据转换为 Pandas DataFrame 进行查看
                      timestamp    value
0 1970-01-01 00:00:00.000000001   8000.0
1 1970-01-01 00:00:00.000000101   4000.0
2 1970-01-01 00:00:00.000000200   2000.0
3 1970-01-01 00:00:00.000000201   1000.0
4 1970-01-01 00:00:00.000000299  35000.0
5 1970-01-01 00:00:00.000000300  16000.0
6 1970-01-01 00:00:00.000001000  64000.0
```
