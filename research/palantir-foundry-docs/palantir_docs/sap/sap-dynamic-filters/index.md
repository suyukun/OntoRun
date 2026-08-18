来源: https://palantir.com/docs/zh/foundry/sap/sap-dynamic-filters/

# 动态筛选

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 动态筛选

动态筛选允许使用特殊关键字和函数来为同步创建更灵活和强大的筛选。

动态筛选在附加组件版本SP26中可用。

## 固定关键字

以下固定关键字返回动态日期值。

| 关键字 | 描述 |
| --- | --- |
| [CURRENTYEAR] | 返回当前年份，格式为YYYY |
| [TODAY] | 返回今天的日期，格式为YYYYMMDD |
| [LASTDAYOFMONTH] | 返回当前月份的最后一天，格式为YYYYMMDD |
| [LASTDAYOFLASTMONTH] | 返回上个月的最后一天，格式为YYYYMMDD |
| [FIRSTDAYOFMONTH] | 返回当前月份的第一天，格式为YYYYMMDD |
| [FIRSTDAYOFLASTMONTH] | 返回上个月的第一天，格式为YYYYMMDD |

## 日期计算的函数

以下动态函数执行各种日期计算。

| 函数 | 描述 |
| --- | --- |
| [ADDDAY] | 向选定日期添加天数（例如，[ADDDAY(22102022,1)]→23102022） |
| [ADDMONTH] | 向选定日期添加月份 |
| [ADDYEAR] | 向选定日期添加年份 |
| [GETMONTH] | 返回选定日期的月份，以两位数格式显示（01, 02, 03, ..., 12） |
| [GETDAY] | 返回月份中的某一天，以两位数格式显示 |
| [GETYEAR] | 返回选定日期的年份 |

## 函数的使用和嵌套

函数可以直接与固定关键字一起使用或嵌套在彼此内部以进行更复杂的计算。例如：

- 单一函数：[ADDDAY([TODAY], 1)]
- 嵌套函数：[GETDAY([ADDDAY([FIRSTDAYOFMONTH], -1)])]
## 筛选使用示例

动态筛选可以用于简单、嵌套或链式嵌套格式。以下是每种格式的一些示例：

- 简单筛选：BUDAT>[TODAY]
- 嵌套筛选：BUDAT>[ADDDAY([FIRSTDAYOFMONTH], -1)]
- 链式嵌套筛选：BUDAT<[ADDDAY([ADDDAY([TODAY],[GETDAY([TODAY])])],1)]
通过结合固定关键字和动态函数，可以创建多样且强大的筛选，以适应各种数据分析场景。
