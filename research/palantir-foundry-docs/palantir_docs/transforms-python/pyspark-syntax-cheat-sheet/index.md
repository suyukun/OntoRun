来源: https://palantir.com/docs/zh/foundry/transforms-python/pyspark-syntax-cheat-sheet/

# 语法备忘单

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 语法备忘单

一个关于 PySpark SQL 中最常用模式和函数的快速参考指南：

- 常用模式日志输出导入函数和类型筛选合并列操作类型转换和合并空值及重复值
- 日志输出
- 导入函数和类型
- 筛选
- 合并
- 列操作
- 类型转换和合并空值及重复值
- 字符串操作字符串筛选字符串函数
- 字符串筛选
- 字符串函数
- 数字操作
- 日期和时间戳操作
- 数组操作
- 聚合操作
- 高级操作重新分区UDFs（用户定义函数）
- 重新分区
- UDFs（用户定义函数）
如果您找不到所需内容，可能会在PySpark 官方文档 ↗中找到。

## 常用模式

#### 日志输出

```
Copied!1
2
3
4
5
6
7
# 在代码工作簿中
print("example log output")  # 打印日志输出示例

# 在代码仓库中
import logging
logger = logging.getLogger(__name__)  # 获取一个以当前模块命名的logger
logger.info("example log output")     # 记录信息级别的日志
```

#### 导入函数和类型

```
Copied!1
2
# 可以通过 F.my_function() 和 T.my_type() 来方便地引用这些函数和类型
from pyspark.sql import functions as F, types as T
```

#### 筛选

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
# 根据相等条件进行过滤
df = df.filter(df.is_adult == 'Y')

# 根据 >, <, >=, <= 条件进行过滤
df = df.filter(df.age > 25)

# 多个条件需要在每个条件周围加上括号
df = df.filter((df.age > 25) & (df.is_adult == 'Y'))

# 对比一个允许值的列表
df = df.filter(col('first_name').isin([3, 4, 7]))

# 排序结果
df = df.orderBy(df.age.asc())   # 按年龄升序排序
df = df.orderBy(df.age.desc())  # 按年龄降序排序
```

#### 合并

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
20
21
22
23
# 在另一个数据集中进行左连接
df = df.join(person_lookup_table, 'person_id', 'left')

# 在另一个数据集中进行左反连接（返回左侧数据集中未匹配的行）
df = df.join(person_lookup_table, 'person_id', 'leftanti');

# 在左侧和右侧数据集中不同的列上进行匹配
df = df.join(other_table, df.id == other_table.person_id, 'left')

# 在多个列上进行匹配
df = df.join(other_table, ['first_name', 'last_name'], 'left')

# 用于一行代码的查找连接
def lookup_and_replace(df1, df2, df1_key, df2_key, df2_value):
    return (
        df1
        .join(df2[[df2_key, df2_value]], df1[df1_key] == df2[df2_key], 'left')
        .withColumn(df1_key, F.coalesce(F.col(df2_value), F.col(df1_key)))  # 使用coalesce函数替换空值
        .drop(df2_key)  # 删除不需要的列
        .drop(df2_value)  # 删除不需要的列
    )

df = lookup_and_replace(people, pay_codes, id, pay_code_id, pay_code_desc)
```

#### 列操作

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
20
21
22
23
24
25
26
27
# 添加一个新的静态列
df = df.withColumn('status', F.lit('PASS'))

# 构建一个新的动态列
df = df.withColumn('full_name', F.when(
    (df.fname.isNotNull() & df.lname.isNotNull()), F.concat(df.fname, df.lname)
).otherwise(F.lit('N/A')))  # 如果fname和lname不为null，则连接它们，否则填充为'N/A'

# 选择需要保留的列，可以选择性地重命名一些列
df = df.select(
    'name',
    'age',
    F.col('dob').alias('date_of_birth'),  # 将'dob'列重命名为'date_of_birth'
)

# 删除列
df = df.drop('mod_dt', 'mod_username')  # 删除'mod_dt'和'mod_username'列

# 重命名列
df = df.withColumnRenamed('dob', 'date_of_birth')  # 将'dob'列重命名为'date_of_birth'

# 保留所有在另一个数据集(df2)中也存在的列
df = df.select(*(F.col(c) for c in df2.columns))  # 选择df2中也存在的列

# 批量重命名/清理列名
for col in df.columns:
    df = df.withColumnRenamed(col, col.lower().replace(' ', '_').replace('-', '_'))  # 将列名转换为小写，并用下划线替换空格和破折号
```

#### 转换和合并空值及重复项

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
# 将列转换为不同的数据类型
df = df.withColumn('price', df.price.cast(T.DoubleType()))

# 用特定值替换所有的空值
df = df.fillna({
    'first_name': 'Tom',  # 如果first_name为null，则替换为'Tom'
    'age': 0,             # 如果age为null，则替换为0
})

# 取第一个非空值
df = df.withColumn('last_name', F.coalesce(df.last_name, df.surname, F.lit('N/A')))
# 如果last_name为null，则尝试使用surname，如果surname也为null，则使用'N/A'

# 删除数据集中重复的行（与distinct()功能相同）
df = df.dropDuplicates()

# 删除重复的行，但只考虑特定的列
df = df.dropDuplicates(['name', 'height'])
# 仅在'name'和'height'这两列的组合上检查重复
```

## 字符串操作

#### 字符串筛选

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
20
21
22
23
# 包含 - col.contains(string)
df = df.filter(df.name.contains('o'))  # 过滤name列中包含'o'的行

# 以...开始 - col.startswith(string)
df = df.filter(df.name.startswith('Al'))  # 过滤name列中以'Al'开头的行

# 以...结束 - col.endswith(string)
df = df.filter(df.name.endswith('ice'))  # 过滤name列中以'ice'结尾的行

# 为空 - col.isNull()
df = df.filter(df.is_adult.isNull())  # 过滤is_adult列为空值的行

# 不为空 - col.isNotNull()
df = df.filter(df.first_name.isNotNull())  # 过滤first_name列不为空值的行

# 类似 - col.like(string_with_sql_wildcards)
df = df.filter(df.name.like('Al%'))  # 过滤name列中以'Al'开头的行（SQL通配符）

# 正则表达式匹配 - col.rlike(regex)
df = df.filter(df.name.rlike('[A-Z]*ice$'))  # 过滤name列中符合正则表达式'[A-Z]*ice$'的行

# 在列表中 - col.isin(*values)
df = df.filter(df.name.isin('Bob', 'Mike'))  # 过滤name列中值为'Bob'或'Mike'的行
```

#### 字符串函数

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
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
# Substring - col.substr(startPos, length) (1-based indexing)
# 截取子字符串 - col.substr(startPos, length) （基于1的索引）
df = df.withColumn('short_id', df.id.substr(1, 10))

# Trim - F.trim(col)
# 去除字符串首尾空格 - F.trim(col)
df = df.withColumn('name', F.trim(df.name))

# Left Pad - F.lpad(col, len, pad)
# 左填充 - F.lpad(col, len, pad)
# Right Pad - F.rpad(col, len, pad)
# 右填充 - F.rpad(col, len, pad)
df = df.withColumn('id', F.lpad('id', 4, '0'))

# Left Trim - F.ltrim(col)
# 去除字符串左侧空格 - F.ltrim(col)
# Right Trim - F.rtrim(col)
# 去除字符串右侧空格 - F.rtrim(col)
df = df.withColumn('id', F.ltrim('id'))

# Concatenate - F.concat(*cols) (null if any column null)
# 连接字符串 - F.concat(*cols) （如果任何列为null，则结果为null）
df = df.withColumn('full_name', F.concat('fname', F.lit(' '), 'lname'))

# Concatenate with Separator/Delimiter - F.concat_ws(delimiter, *cols) (ignores nulls)
# 使用分隔符连接字符串 - F.concat_ws(delimiter, *cols) （忽略null值）
df = df.withColumn('full_name', F.concat_ws('-', 'fname', 'lname'))

# Regex Replace - F.regexp_replace(str, pattern, replacement)
# 正则表达式替换 - F.regexp_replace(str, pattern, replacement)
df = df.withColumn('id', F.regexp_replace(id, '0F1(.*)', '1F1-$1'))

# Regex Extract - F.regexp_extract(str, pattern, idx)
# 正则表达式提取 - F.regexp_extract(str, pattern, idx)
df = df.withColumn('id', F.regexp_extract(id, '[0-9]*', 0))
```

## 数字运算

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
20
# 四舍五入 - F.round(col, scale=0)
df = df.withColumn('price', F.round('price', 0))

# 向下取整 - F.floor(col)
df = df.withColumn('price', F.floor('price'))

# 向上取整 - F.ceil(col)
df = df.withColumn('price', F.ceil('price'))

# 绝对值 - F.abs(col)
df = df.withColumn('price', F.abs('price'))

# x 的 y 次幂 – F.pow(x, y)
df = df.withColumn('exponential_growth', F.pow('x', 'y'))

# 选择多个列中的最小值 – F.least(*cols)
df = df.withColumn('least', F.least('subtotal', 'total'))

# 选择多个列中的最大值 – F.greatest(*cols)
df = df.withColumn('greatest', F.greatest('subtotal', 'total'))
```

## 日期和时间戳操作

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
20
21
22
23
24
25
26
27
28
29
30
31
32
33
# 将已知格式的字符串转换为日期（不包括时间信息）
df = df.withColumn('date_of_birth', F.to_date('date_of_birth', 'yyyy-MM-dd'))

# 将已知格式的字符串转换为时间戳（包括时间信息）
df = df.withColumn('time_of_birth', F.to_timestamp('time_of_birth', 'yyyy-MM-dd HH:mm:ss'))

# 从日期中获取年份：      F.year(col)
# 从日期中获取月份：      F.month(col)
# 从日期中获取天数：      F.dayofmonth(col)
# 从日期中获取小时：      F.hour(col)
# 从日期中获取分钟：      F.minute(col)
# 从日期中获取秒数：      F.second(col)
df = df.filter(F.year('date_of_birth') == F.lit('2017'))

# 加/减天数
df = df.withColumn('three_days_after', F.date_add('date_of_birth', 3))
df = df.withColumn('three_days_before', F.date_sub('date_of_birth', 3))

# 加/减月份
df = df.withColumn('next_month', F.add_months('date_of_birth', 1))
df = df.withColumn('previous_month', F.add_months('date_of_birth', -1))

# 获取两个日期之间的天数
df = df.withColumn('days_between', F.datediff('end', 'start'))

# 获取两个日期之间的月数
df = df.withColumn('months_between', F.months_between('end', 'start'))

# 仅保留date_of_birth在2017-05-10和2018-07-21之间的行
df = df.filter(
    (F.col('date_of_birth') >= F.lit('2017-05-10')) &
    (F.col('date_of_birth') <= F.lit('2018-07-21'))
)
```

## 数组和结构体操作

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
# 列数组 - F.array(*cols)
df = df.withColumn('full_name', F.array('fname', 'lname'))  # 将'fname'和'lname'列组合成一个数组，作为'full_name'列

# 空数组 - F.array(*cols)
df = df.withColumn('empty_array_column', F.array(F.lit("")))  # 创建一个包含空字符串的数组，并添加到'empty_array_column'列

# 从现有列创建数组或结构体列
df = df.withColumn('guardians', F.array('guardian_1', 'guardian_2'))  # 将'guardian_1'和'guardian_2'列组合成一个数组，作为'guardians'列
df = df.withColumn('properties', F.struct('hair_color', 'eye_color'))  # 将'hair_color'和'eye_color'列组合成一个结构体，作为'properties'列

# 通过索引或键从数组或结构体列中提取（无效时返回null）
df = df.withColumn('hair_color', F.element_at(F.col('properties'), F.col('hair_color')))  # 从'properties'结构体中提取'hair_color'字段的值

# 将数组或结构体列展开为多行
df = df.select(F.col('child_name'), F.explode(F.col('guardians')))  # 将'guardians'数组展开为多行，每个元素一行
df = df.select(F.col('child_name'), F.explode(F.col('properties')))  # 将'properties'结构体展开为多行（不常用，可能误用）

# 将结构体列展开为多个列
df = df.select(F.col('child_name'), F.col('properties.*'))  # 将'properties'结构体的每个字段展开为单独的列
```

## 聚合操作

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
# 行计数:                F.count(*cols), F.countDistinct(*cols)
# 组内行之和:            F.sum(*cols)
# 组内行的平均值:        F.mean(*cols)
# 组内行的最大值:        F.max(*cols)
# 组内行的最小值:        F.min(*cols)
# 组内的第一行:          F.first(*cols, ignorenulls=False)
df = df.groupBy(col('address')).agg(
  count('uuid').alias('num_residents'),  # 计算每个地址的居民数
  max('age').alias('oldest_age'),        # 找出每个地址的最高年龄
  first('city', True).alias('city')      # 找出每个地址的第一个城市，忽略空值
)

# 收集组内所有行的集合:       F.collect_set(col)
# 收集组内所有行的列表:       F.collect_list(col)
df = df.groupBy('address').agg(F.collect_set('name').alias('resident_names'))  # 收集每个地址的居民姓名集合
```

## 高级操作

#### 重新分区

```
Copied!1
2
3
# 重分区 – df.repartition(num_output_partitions)
# 重新将数据分区为一个分区
df = df.repartition(1)
```

#### UDFs（用户定义函数）

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
# 将每行的年龄列乘以二
times_two_udf = F.udf(lambda x: x * 2)
df = df.withColumn('age', times_two_udf(df.age))

# 随机选择一个值作为行的名称
import random

random_name_udf = F.udf(lambda: random.choice(['Bob', 'Tom', 'Amy', 'Jenna']))
df = df.withColumn('name', random_name_udf())
```
