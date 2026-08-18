来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/stringToTimestampV2/

# 将字符串转换为时间戳

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 将字符串转换为时间戳

> 支持于: Batch, Streaming

支持于: Batch, Streaming

根据Java DateTimeFormatter，将给定格式的字符串返回为时间戳。默认格式为yyyy-MM-dd'T'HH:mm:ss.SSSXXX和yyyy-MM-dd。格式按顺序运行，返回第一个匹配的格式。

表达式类别: 转换, 日期时间

## 声明的参数

- 字符串- 要转换为时间戳的字符串列。Expression<字符串>
- 非必填格式- 格式默认为ISO8601yyyy-MM-dd'T'HH:mm:ss.SSSXXX和yyyy-MM-dd。List<Literal<字符串>>
- 非必填时区- 用于解析不包括时区的格式。如果格式也包括一个区域，此参数将覆盖它 - 参见示例了解详情。TimeZone
输出类型:时间戳

## 示例

### 示例 1: 基本情况

参数值:

- 字符串:timestamp
- 格式: [yyyy-MM-dd'T'HH:mm.SSSSSSX]
- 时区:null
| timestamp | 输出 |
| --- | --- |
| 2020-04-28T01:30:02.005110Z | 2020-04-28T01:30:02.00511Z |

### 示例 2: 基本情况

参数值:

- 字符串:timestamp
- 格式:null
- 时区:null
| timestamp | 输出 |
| --- | --- |
| 2020-04-28T01:30:02.005Z | 2020-04-28T01:30:02.005Z |

### 示例 3: 基本情况

参数值:

- 字符串:timestamp
- 格式:null
- 时区:null
| timestamp | 输出 |
| --- | --- |
| 2020-04-28 | 2020-04-28T00:00:00Z |

### 示例 4: 基本情况

参数值:

- 字符串:timestamp
- 格式: [dd-yyyy-MM HH:mm, yyyy-MM-dd]
- 时区:null
| timestamp | 输出 |
| --- | --- |
| 28-2020-04 10:09:00 | 2020-04-28T10:09:00Z |
| 2020-04-28 | 2020-04-28T00:00:00Z |

### 示例 5: 基本情况

参数值:

- 字符串:timestamp
- 格式: [yyyy-DDD HH:mm]
- 时区:null
| timestamp | 输出 |
| --- | --- |
| 2022-334 10:09:00 | 2022-11-30T10:09:00Z |

### 示例 6: 基本情况

参数值:

- 字符串:timestamp
- 格式: [dd MMMM yyyy HH:mm]
- 时区:null
| timestamp | 输出 |
| --- | --- |
| 30 November 2022 10:09:00 | 2022-11-30T10:09:00Z |

### 示例 7: 基本情况

参数值:

- 字符串:timestamp
- 格式: [yyyy-MM-dd h:mma]
- 时区:null
| timestamp | 输出 |
| --- | --- |
| 2022-11-30 1:30:00 PM | 2022-11-30T13:30:00Z |

### 示例 8: 基本情况

参数值:

- 字符串:timestamp
- 格式: [yyyy-MM-dd HH:m]
- 时区:null
| timestamp | 输出 |
| --- | --- |
| 2022-11-30 13:9:00 | 2022-11-30T13:09:00Z |

### 示例 9: 基本情况

参数值:

- 字符串:timestamp
- 格式: [dd-MMM-yyyy HH:mm]
- 时区:null
| timestamp | 输出 |
| --- | --- |
| 30-Nov-2022 10:09:00 | 2022-11-30T10:09:00Z |

### 示例 10: 基本情况

参数值:

- 字符串:timestamp
- 格式: [yyyy-DDD]
- 时区:null
| timestamp | 输出 |
| --- | --- |
| 2022-334 | 2022-11-30T00:00:00Z |

### 示例 11: 基本情况

参数值:

- 字符串:timestamp
- 格式: [yyyy-MM-dd HH:mm]
- 时区:null
| timestamp | 输出 |
| --- | --- |
| 2022-11-30 13:09:0 | 2022-11-30T13:09:00Z |

### 示例 12: 基本情况

参数值:

- 字符串:timestamp
- 格式: [yy-MM-dd HH:mm]
- 时区:null
| timestamp | 输出 |
| --- | --- |
| 22-11-30 10:09:00 | 2022-11-30T10:09:00Z |

### 示例 13: 基本情况

参数值:

- 字符串:timestamp
- 格式: [dd-MMM-yyyy HH:mm]
- 时区:null
| timestamp | 输出 |
| --- | --- |
| 01-Nov-2023 10:09:00 | 2023-11-01T10:09:00Z |

### 示例 14: 基本情况

参数值:

- 字符串:timestamp
- 格式: [dd-MMM-yyyy HH:mm]
- 时区:null
| timestamp | 输出 |
| --- | --- |
| 01-NOV-2023 10:09:00 | 2023-11-01T10:09:00Z |

### 示例 15: 基本情况

参数值:

- 字符串:timestamp
- 格式: [yyyy-MM-dd HH:mmz]
- 时区:null
| timestamp | 输出 |
| --- | --- |
| 2022-11-30 10:09:00 PST | 2022-11-30T18:09:00Z |

### 示例 16: 基本情况

参数值:

- 字符串:timestamp
- 格式: [yyyy-MM-dd'T'HH:mm.SSS;z]
- 时区:null
| timestamp | 输出 |
| --- | --- |
| 2022-11-29T09:50:04.187;EST | 2022-11-29T14:50:04.187Z |

### 示例 17: 基本情况

参数值:

- 字符串:timestamp
- 格式: [yyyy-MM-dd'T'HH:mm.SSSXXX]
- 时区:null
| timestamp | 输出 |
| --- | --- |
| 2022-11-29T09:50:04.187-05:00 | 2022-11-29T14:50:04.187Z |

### 示例 18: 基本情况

参数值:

- 字符串:timestamp
- 格式: [dd-yyyy-MM HH:mm]
- 时区: Australia/Sydney
| timestamp | 输出 |
| --- | --- |
| 28-2020-04 04:12:00 | 2020-04-28T04:12:00+10:00 |

### 示例 19: 基本情况

参数值:

- 字符串:timestamp
- 格式: [dd-yyyy-MM HH:mm]
- 时区: +10
| timestamp | 输出 |
| --- | --- |
| 28-2020-04 04:12:00 | 2020-04-28T04:12:00+10:00 |

### 示例 20: 空情况

参数值:

- 字符串:timestamp
- 格式: [dd-yyyy-MM HH:mm, yyyy-MM-dd]
- 时区:null
| timestamp | 输出 |
| --- | --- |
| 202021-04-28 | null |

### 示例 21: 边缘情况

参数值:

- 字符串:timestamp
- 格式: [yyyy-MM-dd'T'HH:mm.SSS;v]
- 时区:null
| timestamp | 输出 |
| --- | --- |
| 2022-11-29T09:50:04.187;Australia/Sydney | 2022-11-28T22:50:04.187Z |

### 示例 22: 边缘情况

参数值:

- 字符串:timestamp
- 格式: [yyyy-MM-dd'T'HH:mm.SSS;z]
- 时区: Australia/Sydney
| timestamp | 输出 |
| --- | --- |
| 2022-11-29T09:50:04.187;EST | 2022-11-28T22:50:04.187Z |

### 示例 23: 边缘情况

参数值:

- 字符串:timestamp
- 格式: [yyyy-MM-dd hh:mma]
- 时区:null
| timestamp | 输出 |
| --- | --- |
| 2022-11-30 10:09:00 AM | 2022-11-30T10:09:00Z |

### 示例 24: 边缘情况

参数值:

- 字符串:timestamp
- 格式: [yyyy-MM-dd hh:mma]
- 时区:null
| timestamp | 输出 |
| --- | --- |
| 2022-11-30 10:09:00 PM | 2022-11-30T22:09:00Z |

### 示例 25: 边缘情况

参数值:

- 字符串:timestamp
- 格式: [yyyyDDD]
- 时区: UTC
| timestamp | 输出 |
| --- | --- |
| 2023010 | 2023-01-10T00:00:00Z |

### 示例 26: 边缘情况

参数值:

- 字符串:timestamp
- 格式: [yyyyDDD]
- 时区: EST
| timestamp | 输出 |
| --- | --- |
| 2023010 | 2023-01-10T05:00:00Z |

### 示例 27: 边缘情况

参数值:

- 字符串:timestamp
- 格式: [yyyyDDD]
- 时区:null
| timestamp | 输出 |
| --- | --- |
| 2023010 | 2023-01-10T00:00:00Z |

### 示例 28: 边缘情况

参数值:

- 字符串:timestamp
- 格式: [yyyyMMddHHmmss]
- 时区: UTC
| timestamp | 输出 |
| --- | --- |
| 20230110000000 | 2023-01-10T00:00:00Z |

### 示例 29: 边缘情况

参数值:

- 字符串:timestamp
- 格式: [yyyyMMddHHmmss]
- 时区:null
| timestamp | 输出 |
| --- | --- |
| 20230110000000 | 2023-01-10T00:00:00Z |

### 示例 30: 边缘情况

参数值:

- 字符串:timestamp
- 格式: [yyyy-MM-dd'T'HH:mm.SSSXXX;z]
- 时区:null
| timestamp | 输出 |
| --- | --- |
| 2022-11-29T09:50:04.187Z;EST | 2022-11-29T09:50:04.187Z |

### 示例 31: 边缘情况

参数值:

- 字符串:timestamp
- 格式: [yyyy-MM-dd'T'HH:mm.SSSSSSX]
- 时区:null
| timestamp | 输出 |
| --- | --- |
| 2020-04-28T01:30:02.005112Z | 2020-04-28T01:30:02.005112Z |
