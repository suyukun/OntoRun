来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/dmsToGeoPointV1/

# 将DMS转换为GeoPoint

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 将DMS转换为GeoPoint

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

将以度、分、秒（DMS）格式的地理坐标字符串转换为符合用户提供格式的GeoPoint。默认格式为DDD*°MM*'SS*"H和DDD*MMSSssH。格式按顺序运行，第一个匹配的格式将被返回。请参阅格式指南了解如何编写用户生成的格式。

表达式类别: 地理空间

## 声明的参数

- Coordinates- 要转换为GeoPoint的DMS坐标。Expression<字符串>
- 非必填Formats- 格式默认为DDD*°MM*'SS*"H和DDD*MMSSssH。List<Literal<字符串>>
输出类型:GeoPoint

## 示例

### 示例 1: 基本情况

参数值:

- Coordinates:coordinates
- Formats:null
| coordinates | 输出 |
| --- | --- |
| 078261594N075220923E | {latitude: 78.43776111111112,longitude: 75.36923055555555,} |
| 046115095S069524119W | {latitude: -46.19748611111111,longitude: -69.87810833333333,} |
| 023°45'55"N 069°52'11"W | {latitude: 23.76527777777777,longitude: -69.86972222222222,} |
| -123°55'55"N 069°53'00"W | {latitude: -123.93194444444445,longitude: -69.88333333333334,} |
| 123456789N23456789E | {latitude: 123.76885833333333,longitude: 23.768858333333334,} |

### 示例 2: 基本情况

参数值:

- Coordinates:coordinates
- Formats: [H[orth][est][ast][outh] DDD*degrees,MM*minutes, andSS*.sss*seconds]
| coordinates | 输出 |
| --- | --- |
| North 75 degrees, 3 minutes, and 0.33 seconds; East 123 degrees, 22 minutes, and 17.2 seconds | {latitude: 75.05009166666666,longitude: 123.37144444444444,} |
| South 75 degrees, 3 minutes, and 0.33 seconds; West 123 degrees, 22 minutes, and 17.2 seconds | {latitude: -75.05009166666666,longitude: -123.37144444444444,} |

### 示例 3: 基本情况

参数值:

- Coordinates:coordinates
- Formats:null
| coordinates | 输出 |
| --- | --- |
| hSllo, World! | null |
| 02345N123456789E | null |
| 023456784R123456789E | null |
| 023456784N123456789 | null |
| 023456784R123456789 | null |
| 078261594N075220923E075220923N | null |
| 078261594N | null |
| 23°°45'55"N 069°52'11"W | null |
| 23° 45' 55"N 069° 52' 11"W | null |
| 23°55"N 069°52'11"W | null |
| 23°452233'55"N 069°52'11"W | null |

### 示例 4: 基本情况

参数值:

- Coordinates:coordinates
- Formats: [DDD``minutes:``MM``seconds:``SS]
| coordinates | 输出 |
| --- | --- |
| degrees:123minutes:45seconds:67,degrees:087minutes:54seconds:32 | {latitude: 123.76861111111111,longitude: 87.9088888888889,} |

### 示例 5: 边界情况

参数值:

- Coordinates:coordinates
- Formats: [SSSSSSSSS*.sssssss*H]
| coordinates | 输出 |
| --- | --- |
| 123452.4222N 98544.333E | {latitude: 34.2923395,longitude: 27.373425833333332,} |

### 示例 6: 边界情况

参数值:

- Coordinates:coordinates
- Formats: [DDD*:MM*H]
| coordinates | 输出 |
| --- | --- |
| 123:45:24222N 98:54:4333E | {latitude: 123.75672833333333,longitude: 98.91203611111112,} |
| 078261594N075220923E | null |
| -123°55'55"N 069°53'00"W | null |
