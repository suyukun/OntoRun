来源: https://palantir.com/docs/zh/foundry/transforms-python/pyspark-dates/

# 日期和时间戳

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 日期和时间戳

## 1. 添加或减去日期

### 给日期添加或减去天数

- F.date_add(start, days)
- F.date_sub(start, days)
### 给日期添加月份

- F.add_months(start, months)
### 获取两个日期之间的天数或月份数

- F.datediff(end, start)
- F.months_between(date1, date2)
### 获取月份的最后一天

- F.last_day(date)
### 获取下一个指定星期几的日期

- F.next_day(date, dayOfWeek)
## 2. 日期值

### 获取年份、月份、天、分钟、秒

- F.year(column)
- F.month(column)
- F.dayofmonth(column)
- F.hour(column)
- F.minute(column)
- F.second(column)
### 从日期获取商业季度

- F.quarter(column)
### 从日期获取一年中的某一天或周

- F.dayofyear(column)
- F.weekofyear(column)
## 3. 格式化

### 日期和时间格式语法

以下是快速参考：

| 格式 | 示例 |
| --- | --- |
| yyyy-MM-dd | 1997-01-31 |
| yyyy-MM-dd HH:mm | 1997-01-31 23:59:59 |

> 日期格式化字符串模式基于 Java 类 java.text.SimpleDateFormat。完整参考请见日期和时间格式语法表 ↗。

日期格式化字符串模式基于 Java 类 java.text.SimpleDateFormat。完整参考请见日期和时间格式语法表 ↗。

### 从字符串转换

- F.to_date(column, format=None)
- F.to_timestamp(column, format=None)
- F.to_utc_timestamp(timestamp, tz)
- F.unix_timestamp(timestamp=None, format='yyyy-MM-dd HH:mm:ss')
### 转换为字符串

- F.date_format(date, format)
- F.from_unixtime(timestamp, format='yyyy-MM-dd HH:mm:ss')
- F.from_utc_timestamp(timestamp, tz)
### 从long转换为timestamp

某些系统将时间戳存储为long数据类型，以毫秒为单位。PySpark SQL 将时间戳存储为秒。我们必须将long版本的时间戳除以1000，才能正确转换为timestamp：

```
Copied!1
2
3
4
casted_timestamp = (F.col('timestamp') / 1000).cast("timestamp")
df = df.withColumn("timestamp", casted_timestamp)
# 将时间戳从毫秒转换为秒，然后转换为标准的时间格式
# 示例: 1531860192661 => 2018年7月17日 星期二 8:43:12 下午
```

我们也可以使用F.from_unixtime(timestamp)来提高清晰度：

```
Copied!1
2
3
4
# 将Unix时间戳（以毫秒为单位）转换为常规时间格式
timestamp = F.from_unixtime(F.col('timestamp') / 1000)
# 使用转换后的时间戳更新DataFrame中的'timestamp'列
df = df.withColumn("timestamp", timestamp)
```

当从long转换为timestamp时，我们失去了一定程度的细粒度。SQL无法存储百分比或秒的小数。

### 截断

- F.trunc(date, format)
- F.date_trunc(format, timestamp)