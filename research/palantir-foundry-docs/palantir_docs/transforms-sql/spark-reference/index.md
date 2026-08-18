来源: https://palantir.com/docs/zh/foundry/transforms-sql/spark-reference/

# Spark SQL 参考

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Spark SQL 参考

本节介绍编写 Spark SQL 数据变换与其他类型 SQL 查询之间的一些关键区别。还包含可用 Spark SQL 函数的列表。

在查找资源时，请记住 Spark SQL 实际上基于 HiveQL 方言。您可以在线找到有关 HiveQL 的更多信息。

## 起始

### 基本查询格式

每个 SQL 数据变换查询必须创建一个表。您的 SQL 查询的一般格式是：

```
Copied!1
2
CREATE TABLE _____ AS SELECT _____
-- 创建一个新的表，并使用SELECT语句从其他表中选择数据填充这个新表
```

不要在语句末尾包含分号。包含分号将导致出错。

### 注释语法

您可以在SQL代码中包含注释，如下所示：

```
Copied!1
2
3
-- 你可以使用这种语法创建注释

/* 你也可以使用这种语法创建注释 */
```

### 引用数据集

要引用数据集，请提供用反引号包围的数据集路径：

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
CREATE TABLE `/path/to/target/dataset` AS
SELECT * FROM `/path/to/source/dataset`

-- 创建一个新的表 `/path/to/target/dataset`，并从源数据集中选择所有数据复制到目标数据集

-- Alternative syntax
-- 另一种语法

CREATE TABLE `/path/to/target/dataset` AS (
    SELECT * FROM `/path/to/source/dataset`
)
```

以上 SQL 语句用于创建一个新的表，并将源数据集中的所有数据复制到目标数据集中。这可以用于备份、迁移或数据复制等操作。
请注意，数据集名称区分大小写。

### 引用列

要引用数据集中的特定列，请提供列名：

```
Copied!1
2
-- 从指定的数据集路径中选择“Name”列
SELECT Name FROM `/path/to/source/dataset`
```

请注意，列名区分大小写。

### 衍生列和别名

衍生列是通过对数据集列调用函数的结果。您必须为任何衍生列定义一个别名：

```
Copied!1
2
SELECT Sum(Val) AS Total FROM `/path/to/source/dataset`
-- 选择数据集中 Val 列的值的总和，并将结果命名为 Total
```

以下查询将导致出错：

```
Copied!1
2
-- 计算指定路径数据集中的 Val 列的总和
SELECT Sum(Val) FROM `/path/to/source/dataset`
```

请注意，别名区分大小写。

### SQL子句中的派生列

您不能在以下SQL子句中使用别名：WHERE和GROUP BY。因此，您必须在WHERE或GROUP BY子句中引用实际的函数和数据集列：

```
Copied!1
2
3
4
5
6
7
SELECT Lower(Name) AS LowercaseName
-- 从数据集中选择名称并转换为小写，过滤条件为名称的小写形式等于"sara"
FROM `/path/to/source/dataset` WHERE Lower(Name) = "sara"

SELECT Lower(Name) AS LowercaseName, Sum(Val) AS Total
-- 从数据集中选择名称并转换为小写，并对Val进行求和，按名称的小写形式分组
FROM `/path/to/source/dataset` GROUP BY Lower(Name)
```

您可以在以下SQL子句中使用别名：ORDER BY和HAVING。因此，以下任何查询都将有效：

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
-- 以下两个查询都是有效的

SELECT Lower(Name) AS LowercaseName, Sum(Val) AS Total
FROM `/path/to/source/dataset` GROUP BY Lower(Name) ORDER BY Total

-- 此查询按Lower(Name)分组，并按聚合结果Total排序

SELECT Lower(Name) AS LowercaseName, Sum(Val) AS Total
FROM `/path/to/source/dataset` GROUP BY Lower(Name) ORDER BY Sum(Val)

-- 此查询按Lower(Name)分组，并直接按Sum(Val)排序，效果与上一个相同

-- 以下两个查询都是有效的

SELECT Lower(Name) AS LowercaseName, Sum(Val) AS Total
FROM `/path/to/source/dataset` GROUP BY Lower(Name) HAVING Total > 100

-- 此查询在分组后，使用HAVING子句筛选出总和大于100的组，使用别名Total

SELECT Lower(Name) AS LowercaseName, Sum(Val) AS Total
FROM `/path/to/source/dataset` GROUP BY Lower(Name) HAVING Sum(Val) > 100

-- 此查询在分组后，使用HAVING子句筛选出Sum(Val)大于100的组，直接使用聚合函数
```

### 类型转换

您可以通过类型转换表达式将其从一种类型转换为另一种类型。类型转换的语法为：

```
Copied!1
2
3
CAST(expr AS <TYPE>)
-- 将表达式 `expr` 转换为指定的数据类型 `<TYPE>`。
-- 常用于将数据类型不匹配的字段进行类型转换，以便在查询中进行比较或计算。
```

请注意，expr表示您想要转换的表达式，而<TYPE>表示您想要将表达式转换成的类型。如果CAST(expr AS <TYPE>)未成功，它将返回 null。<TYPE>的可用值有：

- boolean
- tinyint
- smallint
- int
- bigint
- float
- double
- decimal
- date
- timestamp
- binary
- 字符串
### 格式化日期

您可能想要重新格式化日期值或将字符串转换为日期格式。一个date的格式为 yyyy-MM-dd，并且没有时间部分。您可以使用CAST函数和可用的日期时间函数将字符串转换为日期。以下是一些快速示例：

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
-- 将格式为 'yyyy-MM-dd' 的字符串转换为日期
CAST('2016-07-30' AS DATE)

-- 将格式为 'yyyy-MM-dd' 的字符串转换为时间戳（时间戳将基于提供日期的午夜）
CAST('2016-07-30' AS TIMESTAMP)

-- 将格式为 'ddMMyyyy' 的日期字符串转换为日期
TO_DATE(CAST(UNIX_TIMESTAMP('07302016', 'MMddyyyy') AS TIMESTAMP))

-- 将格式为 'ddMMyyyy HH:mm:ss' 的时间戳字符串转换为仅日期
CAST('2016-07-30 11:29:27' AS DATE)

-- 从 ISO 8601 时间戳中提取出日期
TO_DATE('2016-07-30T11:29:27.000+00:00')

-- 从格式为 'yyyy-MM-dd HH:mm:ss' 的时间戳中提取出日期
TO_DATE('2016-07-30 11:29:27')
```

请注意，如果字符串未格式化为日期/时间戳，则无法将字符串转换为日期。因此，类似于CAST('20160730' AS DATE)的语句将返回null。

## 聚合函数

| 函数 | 描述 |
| --- | --- |
| APPROX_COUNT_DISTINCT | 返回组中不同项目的大致数量。 |
| AVG | 返回组中值的平均值。 |
| COLLECT_LIST | 返回包含重复项的对象列表。 |
| COLLECT_SET | 返回去除重复元素的对象集合。 |
| CORR | 返回两列的皮尔逊相关系数。 |
| COUNT | 返回组中项目的数量。 |
| COVAR_POP | 返回两列的总体协方差。 |
| COVAR_SAMP | 返回两列的样本协方差。 |
| FIRST | 返回组中的第一个值。 |
| GROUPING | 指示GROUP BY列表中指定列是否被聚合。 |
| KURTOSIS | 返回组中值的峰度。 |
| LAST | 返回组中的最后一个值。 |
| MAX | 返回组中表达式的最大值。 |
| MEAN | 返回组中值的平均值。 |
| MIN | 返回组中表达式的最小值。 |
| SKEWNESS | 返回组中值的偏度。 |
| STDDEV | stddev_samp的别名。 |
| STDDEV_POP | 返回组中表达式的总体标准差。 |
| STDDEV_SAMP | 返回组中表达式的样本标准差。 |
| SUM | 返回表达式中所有值的总和。 |
| VARIANCE | 返回组中值的无偏方差。 |
| VAR_POP | 返回组中值的总体方差。 |
| VAR_SAMP | 返回组中值的无偏方差。 |

### APPROX_COUNT_DISTINCT

描述：聚合函数：返回组中不同项目的大致数量。最大允许估计误差默认为0.05，除非提供rsd。

签名：

```
Copied!1
2
3
4
5
6
7
8
APPROXCOUNTDISTINCT(Column e)
-- 估计不同元素的数量。用于快速计算大规模数据集中的不同值数量。
-- 默认情况下，使用相对标准偏差（RSD）来控制近似度。

APPROXCOUNTDISTINCT(Column e, double rsd)
-- 估计不同元素的数量，同时允许用户指定相对标准偏差（RSD）。
-- RSD 是一个介于 0 到 1 之间的双精度值，表示近似计数的相对误差。
-- 较小的 RSD 提供更高的准确性，但计算开销可能更大。
```

### AVG

描述：聚合函数：返回组内值的平均值。

签名：

```
Copied!1
AVG(Column e) -- 计算列 e 的平均值
```

### COLLECT_LIST

描述：聚合函数：返回包含重复项的对象列表。

签名：

```
Copied!1
COLLECT_LIST(Column e)
```

COLLECT_LIST是一个用于聚合的函数，它将指定列e中的所有非空值收集到一个列表中。这个函数常用于数据分析和处理场景中，需要将某一列中的所有值合并为一个列表，以便后续的操作或分析。

### COLLECT_SET

描述：聚合函数：返回一个对象集合，并消除重复元素。

签名：

```
Copied!1
COLLECT_SET(Column e)
```

COLLECT_SET是一个 SQL 函数，用于从指定列中收集唯一值，并将它们作为一个集合返回。这个函数会自动去除重复值。

### CORR

描述：聚合函数：返回两列的皮尔逊相关系数。

签名：

```
Copied!1
CORR(Column column1, Column column2)
```

CORR是一个用于计算两列之间皮尔逊相关系数的函数。

- column1: 第一列的数据。
- column2: 第二列的数据。
皮尔逊相关系数是用来衡量两列数据之间线性关系的强度和方向。结果范围在 -1 到 1 之间：

- -1 表示完全负相关，
- 0 表示无相关，
- 1 表示完全正相关。
### COUNT

描述:聚合函数: 返回组中项目的数量。

签名:

```
Copied!1
COUNT(Column e) -- 计算列e中的非空值数量
```

### COVAR_POP

描述：聚合函数：返回两列的总体协方差。签名：

```
Copied!1
COVAR_POP(Column column1, Column column2)
```

```
Copied!1
2
3
-- COVAR_POP 函数用于计算两个列之间的总体协方差。
-- 它采用两个列作为参数，返回它们之间的总体协方差。
-- 总体协方差是衡量两个变量之间关系的统计量。
```

### COVAR_SAMP

描述:聚合函数：返回两列的样本协方差。

签名:

```
Copied!1
COVAR_SAMP(Column column1, Column column2)
```

COVAR_SAMP是一个 SQL 函数，用于计算两个列column1和column2的样本协方差。样本协方差衡量两个变量之间的线性关系程度。

### FIRST

描述:聚合函数：返回组中的第一个值。默认情况下，返回其看到的第一个值。如果ignoreNulls设置为true，它将返回其看到的第一个非空值。如果所有值都为空，则返回null。

签名：

```
Copied!1
2
FIRST(Column e) -- 返回指定列的第一个值
FIRST(Column e, boolean ignoreNulls) -- 返回指定列的第一个值，并可以选择忽略空值
```

### GROUPING

描述：聚合函数：指示 GROUP BY 列表中的指定列是否被聚合。在结果集中，聚合返回1，不聚合返回0。

签名：

```
Copied!1
2
3
GROUPING(Column e)
-- GROUPING 函数用于标识在 GROUP BY 子句中哪个列是经过分组的。
-- 它返回 1 表示该列是分组的结果，0 表示该列不是分组的结果。
```

### KURTOSIS

描述：聚合函数：返回组内值的峰度。

签名：

```
Copied!1
KURTOSIS(Column e) -- 计算列e的峰度，用于衡量数据分布的尖锐程度
```

### LAST

描述:聚合函数: 返回组中的最后一个值。默认情况下，返回它看到的最后一个值。如果ignoreNulls设置为true，它将返回它看到的最后一个非空值。如果所有值都是空，则返回空。

签名:

```
Copied!1
2
LAST(Column e) -- 返回列 e 中的最后一个非空值
LAST(Column e, boolean ignoreNulls) -- 返回列 e 中的最后一个值，ignoreNulls 为 true 时忽略空值
```

### MAX

描述：聚合函数：返回组中表达式的最大值。

签名：

```
Copied!1
MAX(Column e) -- 返回列 e 中的最大值
```

### MEAN

描述:聚合函数：返回组内值的平均值。

签名:

```
Copied!1
MEAN(Column e) -- 计算列 e 的平均值
```

### MIN

描述:聚合函数：返回组中表达式的最小值。

签名:

```
Copied!1
MIN(Column e)  -- 计算列e的最小值
```

### SKEWNESS

描述:聚合函数：返回一组值的偏度。

签名:

```
Copied!1
SKEWNESS(Column e)
```

SKEWNESS函数用于计算数据分布的偏度（Skewness），它是描述数据分布不对称性的统计量。Column e代表需要计算偏度的列。偏度的值可以帮助判断数据的分布形态：正偏（右偏）、负偏（左偏）或接近对称。

### STDDEV

描述：聚合函数：是 stddev_samp 的别名。

签名：

```
Copied!1
STDDEV(Column e)  -- 计算列 e 的标准偏差
```

### STDDEV_POP

描述:聚合函数：返回组中表达式的总体标准差。

签名：

```
Copied!1
STDDEV_POP(Column e)
```

STDDEV_POP是一个 SQL 聚合函数，用于计算总体标准差（population standard deviation）。在这里，它计算列e的总体标准差。总体标准差适用于整个人群数据集，而不是样本数据集。

### STDDEV_SAMP

描述：聚合函数：返回组中表达式的样本标准差。

签名：

```
Copied!1
2
STDDEV_SAMP(Column e)
-- 计算样本标准差：用于估计列e中值的标准差
```

### SUM

描述：聚合函数：返回表达式中所有值的总和。

签名：

```
Copied!1
SUM(Column e) -- 计算列 e 的总和
```

### VARIANCE

描述：聚合函数：返回组内值的无偏方差。是VAR_SAMP函数的别名。

签名：

```
Copied!1
VARIANCE(Column e) -- 计算列 e 的方差
```

### VAR_POP

描述：聚合函数：返回组内值的总体方差。

签名：

```
Copied!1
VAR_POP(Column e)
```

VAR_POP是一个 SQL 聚合函数，用于计算指定列（在此例中为 "Column e"）中所有值的总体方差。总体方差是所有数据点与总体均值之间差异的平方和的平均值。

### VAR_SAMP

描述：聚合函数：返回组内值的无偏方差。

签名：

```
Copied!1
2
VAR_SAMP(Column e)
-- 计算样本方差
```

## 字符串函数

| 函数 | 描述 |
| --- | --- |
| ASCII | 计算字符串列第一个字符的数值，并将结果返回为一个int列。 |
| BASE64 | 计算二进制列的BASE64编码，并将其返回为一个字符串列。 |
| CONCAT | 将多个输入字符串列连接在一起成为一个字符串列。 |
| DECODE | 使用提供的字符集将第一个参数从二进制计算为字符串。 |
| ENCODE | 使用提供的字符集将第一个参数从字符串计算为二进制。 |
| FORMAT_NUMBER | 将数值列格式化为类似‘#,###,###.##’的格式，并四舍五入到d个小数位。 |
| GET_JSON_OBJECT | 根据指定的json路径从json字符串中提取json对象，并返回提取出的json对象的json字符串。 |
| INSTR | 定位子字符串在给定字符串列中首次出现的位置。 |
| JSON_TUPLE | 根据给定的字段名称为json列创建一个新行。 |
| LENGTH | 计算给定字符串或二进制列的长度。 |
| LEVENSHTEIN | 计算两个给定字符串列的Levenshtein距离。 |
| LOWER | 将字符串列转换为小写。 |
| LPAD | 用填充字符左填充字符串列至指定长度。 |
| LTRIM | 从指定字符串值的左端修剪空格。 |
| REGEXP_EXTRACT | 从指定字符串列中提取由Java正则表达式匹配的特定组。 |
| REGEXP_REPLACE | 将指定字符串值中匹配正则表达式的所有子字符串替换为rep。 |
| REPEAT | 将字符串列重复n次，并将其返回为新字符串列。 |
| REVERSE | 反转字符串列并将其返回为新字符串列。 |
| RPAD | 用填充字符右填充字符串列至指定长度。 |
| RTRIM | 从指定字符串值的右端修剪空格。 |
| SOUNDEX | 返回指定表达式的soundex代码。 |
| SPLIT | 围绕模式（模式是一个正则表达式）拆分str。 |
| SUBSTRING | 返回字符串或二进制类型列的子字符串。 |
| SUBSTRING_INDEX | 返回字符串在分隔符出现次数之前的子字符串。 |
| TRANSLATE | 将src中的任何字符用replaceString中的字符进行翻译。 |
| TRIM | 从指定字符串列的两端修剪空格。 |
| UNBASE64 | 解码BASE64编码的字符串列，并将其返回为二进制列。 |
| UNHEX | hex的逆操作。 |
| UPPER | 将字符串列转换为大写。 |

### ASCII

描述:计算字符串列第一个字符的数值，并将结果返回为一个int列。

签名:

```
Copied!1
ASCII(Column e) -- 返回列 e 中第一个字符的 ASCII 码值
```

### BASE64

描述：计算二进制列的BASE64编码，并将其返回为字符串列。

签名：

```
Copied!1
BASE64(Column e)
```

这个SQL函数用于将列e中的值进行Base64编码。Base64编码是一种常用于数据传输的编码方式，它可以将二进制数据表示为文本字符串。

### CONCAT

描述:将多个输入字符串列连接在一起，形成一个字符串列。

签名:

```
Copied!1
CONCAT(Column... exprs)
```

CONCAT函数用于将多个列或表达式的值连接在一起。多个列或表达式之间可以用逗号分隔。

### DECODE

描述:使用提供的charset将第一个参数从二进制计算为字符串, 其中charset可以是以下之一：

- ‘US-ASCII’
- ‘ISO-8859-1’
- ‘UTF-8’
- ‘UTF-16BE’
- ‘UTF-16LE’
- ‘UTF-16’
如果任一参数为null, 则结果也为null。

签名:

```
Copied!1
2
3
4
5
-- DECODE 函数用于将加密的数据解码为原始格式。
-- 它通常用于从数据库中提取时解码被加密的数据。
-- Column value: 指定要解码的列的值。
-- String charset: 指定解码时使用的字符集。
DECODE(Column value, String charset)
```

### ENCODE

描述：使用提供的charset将第一个参数从字符串计算为二进制，charset可以是以下之一：

- ‘US-ASCII’
- ‘ISO-8859-1’
- ‘UTF-8’
- ‘UTF-16BE’
- ‘UTF-16LE’
- ‘UTF-16’
如果任一参数为null，结果也将为null。

签名：

```
Copied!1
2
3
4
5
ENCODE(Column value, String charset)
-- 该函数用于对数据库中的列值进行编码转换
-- 参数说明：
-- Column value：需要编码的列值
-- String charset：目标字符集
```

### FORMAT_NUMBER

描述:将数字列x格式化为类似‘#,###,###.##’的格式，并以HALF_EVEN舍入模式（也称为高斯舍入或银行家舍入）舍入到d小数位。结果作为字符串列返回。如果d为0，则结果没有小数点或小数部分。如果d小于0，则结果为null。

签名:

```
Copied!1
FORMAT_NUMBER(Column x, int d)
```

FORMAT_NUMBER是一个用于格式化数字的函数。在 SQL 中，这个函数的作用是将列x中的数值格式化为保留d位小数的字符串。具体来说：

- Column x：需要格式化的数值列。
- int d：指定保留的小数位数。
这个函数通常用于将数值转换为字符串格式，以便在报告或显示时更易于阅读。

### GET_JSON_OBJECT

描述:根据指定的jsonpath从json字符串中提取json对象，并返回提取的json对象的json字符串。如果输入的json字符串无效，则返回null。

签名：

```
Copied!1
GET_JSON_OBJECT(Column e, String path)
```

GET_JSON_OBJECT函数用于从JSON格式的字符串中提取指定路径的数据。

- Column e：包含JSON字符串的数据列。
- String path：JSON路径表达式，用于指定从JSON中提取数据的路径。
### INSTR

描述：定位给定字符串列中substring第一次出现的位置。如果任一参数为null，则返回null；如果在str中找不到substring，则返回0。结果位置是基于1的索引，而不是基于0的。

签名：

```
Copied!1
2
3
4
-- INSTR 函数用于在字符串中查找子字符串的位置。
-- 语法：INSTR(字符串, 子字符串)
-- 返回值：如果找到子字符串，返回其在字符串中的位置（从1开始）；如果未找到，返回0。
INSTR(Column str, String substring)
```

### JSON_TUPLE

描述：根据给定的字段名称为json列创建新行。

签名：

```
Copied!1
2
3
4
5
6
-- JSON_TUPLE 是一个用于处理JSON数据的函数
-- 第一种函数签名接受一个JSON列和一个字段序列
JSON_TUPLE(Column json, scala.collection.Seq<String> fields)

-- 第二种函数签名接受一个JSON列和多个字段
JSON_TUPLE(Column json, String... fields)
```

以上代码展示了JSON_TUPLE函数的两种不同签名。第一个签名适用于Scala中的字段序列，而第二个签名则适用于多个字段输入。此函数用于从JSON数据中提取指定字段的值。

### LENGTH

描述:计算给定字符串或二进制列的长度。

签名:

```
Copied!1
LENGTH(Column e)  -- 计算列 e 中字符串的长度
```

### LEVENSHTEIN

描述:计算给定两个字符串列的Levenshtein距离。

签名:

```
Copied!1
LEVENSHTEIN(Column l, Column r)
```

LEVENSHTEIN函数用于计算两个字符串之间的莱文斯坦距离（或编辑距离）。这个距离表示将一个字符串转换成另一个字符串所需的最小单字符编辑操作（插入、删除、替换）的数量。参数Column l和Column r分别代表要比较的两个列。

### LOWER

描述：将字符串列转换为小写。

签名：

```
Copied!1
LOWER(Column e) -- 将列 e 中的所有字符转换为小写
```

### LPAD

描述：使用pad将字符串列左填充到len的长度。

签名：

```
Copied!1
2
3
4
5
6
LPAD(Column str, int len, String pad)
-- 该函数用于在字符串的左侧填充指定的字符，使其达到指定的长度。
-- 参数说明：
-- str: 要进行填充的原始字符串。
-- len: 填充后字符串的总长度。
-- pad: 用于填充的字符。如果原始字符串长度大于或等于指定长度，则不会进行填充。
```

### LTRIM

描述:从指定字符串值的左端去除空格。

签名:

```
Copied!1
2
3
LTRIM(Column e)
-- LTRIM 函数用于去除字符串左侧的空格。
-- 在这里，'Column e' 表示要处理的列，函数将返回去掉左侧空格后的字符串。
```

### REGEXP_EXTRACT

描述：从指定的字符串列中提取由Java正则表达式（exp）匹配的特定组（groupIdx）。如果正则表达式未匹配，或指定的组未匹配，则返回空字符串。

签名：

```
Copied!1
REGEXP_EXTRACT(Column e, String exp, int groupIdx)
```

REGEXP_EXTRACT函数用于从字符串中提取与正则表达式匹配的子字符串。

- Column e: 要应用正则表达式的列。
- String exp: 用于匹配的正则表达式。
- int groupIdx: 指定要返回的匹配组的索引。索引从 1 开始。
此函数常用于数据清洗和文本解析中，以提取特定格式的数据。

### REGEXP_REPLACE

描述:将指定字符串值中所有匹配Java正则表达式pattern的子字符串替换为replacement.

签名:

```
Copied!1
2
REGEXP_REPLACE(Column e, String pattern, String replacement)
-- REGEXP_REPLACE 函数用于替换列 e 中符合正则表达式 pattern 的子字符串为 replacement。
```

### REPEAT

描述：将一个字符串列重复n次，并将其作为一个新的字符串列返回。

签名：

```
Copied!1
REPEAT(Column str, int n)
```

REPEAT函数用于将字符串str重复n次。例如，如果str是 "abc" 且n是 3，结果将是 "abcabcabc"。

### REVERSE

描述:反转字符串列并将其作为新的字符串列返回。

签名:

```
Copied!1
2
REVERSE(Column str)
-- 将字符串str反转
```

### RPAD

描述:使用pad将字符串列右填充到长度len。

签名:

```
Copied!1
RPAD(Column str, int len, String pad)
```

RPAD函数用于将字符串str右填充到指定长度len。如果str的长度小于len，它会使用指定的填充字符串pad进行填充。

### RTRIM

描述:从指定字符串值的右端去除空格。

签名：

```
Copied!1
2
3
RTRIM(Column e)
-- RTRIM函数用于删除指定字符串末尾的空格。
-- 这里将对名为“Column e”的列执行此操作。
```

### SOUNDEX

描述：返回指定表达式的soundex代码。

签名：

```
Copied!1
SOUNDEX(Column e)
```

SOUNDEX是一种用于将文本字段转换为语音编码的函数，通常用于模糊音近匹配。通过将文本转换为表示其发音的编码，可以进行不严格的匹配，例如在数据库中查找发音相似的名称。

### SPLIT

描述:根据pattern拆分str，其中pattern是一个正则表达式。

签名:

```
Copied!1
SPLIT(Column str, String pattern)
```

此SQL函数用于将给定的字符串列str按照指定的pattern模式进行拆分。拆分后的结果通常是一个数组，数组中的每个元素都是原字符串中匹配模式之前或之后的子字符串。在数据处理中，这种操作经常用于解析和处理字符串数据。

### SUBSTRING

描述:当str是字符串类型时，返回从pos起始、长度为len的子字符串。当str是二进制类型时，返回从字节pos起始、长度为len的字节数组切片。

签名:

```
Copied!1
SUBSTRING(Column str, int pos, int len)
```

SUBSTRING是一个SQL函数，用于从字符串中提取子字符串。

- Column str：字符串列的名称。
- int pos：子字符串的起始位置（从1开始计数）。
- int len：子字符串的长度。
### SUBSTRING_INDEX

描述:返回字符串str中delim分隔符出现count次之前的子字符串。搜索delim时执行区分大小写的匹配。如果count为正数，则返回最终分隔符（从左边计数）左边的所有内容。如果count为负数，则返回最终分隔符（从右边计数）右边的所有内容。

签名:

```
Copied!1
SUBSTRING_INDEX(Column str, String delim, int count)
```

SUBSTRING_INDEX是一个用于字符串操作的函数。它的作用是返回原始字符串中某个定界符出现的指定次数之前的子字符串。

- Column str：需要处理的字符串列。
- String delim：定界符，用于分隔字符串。
- int count：定界符出现的次数。如果count为正数，则返回从字符串左边开始到定界符出现的第count次的位置的子字符串；如果为负数，则返回从字符串右边开始到定界符出现的第count次的位置的子字符串。
例如，SUBSTRING_INDEX('a,b,c,d', ',', 2)将返回'a,b'，而SUBSTRING_INDEX('a,b,c,d', ',', -2)将返回'c,d'。

### TRANSLATE

描述：通过replaceString中的字符翻译src中的任何字符。replaceString中的字符与matchingString中的字符相对应。当字符串中的任何字符与matchingString中的字符匹配时，将进行翻译。

签名：

```
Copied!1
TRANSLATE(Column src, String matchingString, String replaceString)
```

这个SQL函数TRANSLATE用于将源列src中的所有匹配字符串matchingString替换为目标字符串replaceString。

### TRIM

描述:修剪指定字符串列两端的空格。

签名:

```
Copied!1
TRIM(Column e) -- 去除列 e 的字符串首尾的空格
```

### UNBASE64

描述:解码一个BASE64编码的字符串列并将其返回为二进制列。

签名:

```
Copied!1
UNBASE64(Column e) -- 对列e进行BASE64解码
```

### UNHEX

描述:与hex相反。将每对字符解释为十六进制数并转换为数字的字节表示形式。

签名:

```
Copied!1
UNHEX(Column column)
```

UNHEX函数用于将十六进制编码的字符串转换为其原始的字节序列。它通常用于处理存储为十六进制格式的数据。在这里，Column column代表要转换的列。

### UPPER

描述：将字符串列转换为大写。

签名：

```
Copied!1
2
UPPER(Column e)
-- 将列e中的字符转换为大写
```

## 日期时间函数

| 函数 | 描述 |
| --- | --- |
| ADD_MONTHS | 返回在 startDate 之后 numMonths 的日期。 |
| DATEDIFF | 返回从开始到结束的天数。 |
| DATE_ADD | 返回在 start 之后 days 天的日期。 |
| DATE_FORMAT | 将日期/时间戳/字符串转换为指定日期格式的字符串值。 |
| DATE_SUB | 返回在 start 之前 days 天的日期。 |
| DAYOFMONTH | 从给定的日期/时间戳/字符串中提取月份中的天数作为整数。 |
| DAYOFYEAR | 从给定的日期/时间戳/字符串中提取年份中的天数作为整数。 |
| FROM_UNIXTIME | 将从 Unix 纪元开始的秒数转换为字符串，表示当前系统时区中该时刻的时间戳。 |
| FROM_UTC_TIMESTAMP | 假设给定时间戳为 UTC 并转换为给定时区。 |
| HOUR | 从给定的日期/时间戳/字符串中提取小时数作为整数。 |
| LAST_DAY | 给定一个日期列，返回该日期所属月份的最后一天。 |
| MINUTE | 从给定的日期/时间戳/字符串中提取分钟数作为整数。 |
| MONTH | 从给定的日期/时间戳/字符串中提取月份作为整数。 |
| MONTHS_BETWEEN | 返回日期 date1 和 date2 之间的月份数。 |
| NEXT_DAY | 给定一个日期列，返回在该日期列的值之后的第一个指定星期几的日期。 |
| QUARTER | 从给定的日期/时间戳/字符串中提取季度作为整数。 |
| SECOND | 从给定的日期/时间戳/字符串中提取秒数作为整数。 |
| TO_DATE | 将列转换为日期类型。 |
| TO_UTC_TIMESTAMP | 假设给定时间戳位于给定时区并转换为 UTC。 |
| TRUNC | 返回根据格式指定的单位截断的日期。 |
| UNIX_TIMESTAMP | 将格式为 yyyy-MM-dd HH:mm的时间字符串转换为 Unix 时间戳（以秒为单位），使用默认时区和默认语言环境。 |
| WEEKOFYEAR | 从给定的日期/时间戳/字符串中提取周数作为整数。 |
| WINDOW | 给定一个时间戳指定的列，生成滚动或滑动时间窗口。 |
| YEAR | 从给定的日期/时间戳/字符串中提取年份作为整数。 |

### ADD_MONTHS

描述:返回在startDate指定的日期/时间戳/字符串之后numMonths的日期。如果startDate是字符串，则必须为格式 ‘yyyy-MM-dd’ 或 ‘yyyy-MM-dd HH:mm’。

如果startDate有时间成分，则忽略。结果月份具有与startDate相同的日期成分。如果startDate是月份的最后一天，或者结果月份的天数少于startDate的天数，则返回结果月份的最后一天。

签名:

```
Copied!1
2
-- 将startDate列的日期增加numMonths个月
ADD_MONTHS(Column startDate, int numMonths)
```

### DATEDIFF

描述:返回从start到end的天数。

签名:

```
Copied!1
DATEDIFF(Column end, Column start) -- 计算两个日期列之间的天数差
```

### DATE_ADD

描述：返回在start之后days天的日期。

签名：

```
Copied!1
2
3
DATE_ADD(Column start, int days)
-- 在SQL中，DATE_ADD函数用于将指定的天数（days）添加到给定的日期列（Column start）中。
-- 这个函数对于计算基于日期的值或生成未来的日期特别有用。
```

### DATE_FORMAT

描述：将日期/时间戳/字符串转换为指定格式的字符串值。如果dateExpr是一个字符串，则它必须是‘yyyy-MM-dd’或‘yyyy-MM-dd HH:mm’格式。

对于模式字符串format，可以使用SimpleDateFormat的模式字母。更多信息请参考Java SimpleDateFormat 文档 ↗。

签名：

```
Copied!1
DATE_FORMAT(Column dateExpr, String format)
```

DATE_FORMAT是一个用于格式化日期的函数。在这个函数中：

- Column dateExpr: 这是日期列或者日期表达式，表示你想要格式化的日期。
- String format: 这是格式化字符串，指定日期应该被格式化成什么样的形式。
例如，如果你想将日期格式化为“年-月-日”的格式，你可以使用以下代码：

```
Copied!1
DATE_FORMAT(date_column, 'yyyy-MM-dd')
```

在这个例子中，date_column是你想要格式化的日期列，而'yyyy-MM-dd'是格式化字符串。

### DATE_SUB

描述:返回在start之前days天的日期。

签名:

```
Copied!1
2
3
4
DATE_SUB(Column start, int days)
-- 减去指定的天数，返回一个新的日期
-- 例如，如果 Column start 是 '2023-10-10' 且 days 是 5，
-- 则结果将是 '2023-10-05'
```

### DAYOFMONTH

描述：从给定的日期/时间戳/字符串中提取月份中的天数作为整数。字符串必须是格式为‘yyyy-MM-dd’或‘yyyy-MM-dd HH:mm’。

签名：

```
Copied!1
DAYOFMONTH(Column e) -- 返回日期字段 'e' 中的日（1 到 31）
```

### DAYOFYEAR

描述:从给定的日期/时间戳/字符串中提取一年中的第几天作为整数。字符串必须是‘yyyy-MM-dd’或‘yyyy-MM-dd HH:mm’格式。

签名:

```
Copied!1
2
3
DAYOFYEAR(Column e)
-- 返回一年中的第几天，范围为1到366
-- 例如：如果 Column e 是 '2023-01-01'，则返回值为1
```

### FROM_UNIXTIME

描述:将自 Unix 纪元 (1970-01-01 00:00:00 UTC) 开始的秒数转换为在当前系统时区中以给定格式表示该时刻的时间戳字符串。如果未提供模式字符串f，则结果字符串的默认格式为 yyyy-MM-dd HH:mm。要更改结果字符串的格式，请提供模式字符串f。可以使用 SimpleDateFormat 的模式字母作为模式字符串。有关更多信息，请参阅Java SimpleDateFormat 文档 ↗。

签名:

```
Copied!1
2
3
4
5
6
7
8
-- `FROM_UNIXTIME` 函数用于将Unix时间戳转换为日期格式
-- 语法：FROM_UNIXTIME(unix_timestamp[, format])
-- 第一个参数是Unix时间戳（例如：秒数）
-- 第二个可选参数是日期格式的字符串

-- 示例用法
FROM_UNIXTIME(Column ut) -- 仅转换为默认的日期格式
FROM_UNIXTIME(Column ut, String f) -- 转换为指定格式的日期
```

### FROM_UTC_TIMESTAMP

描述：假设给定的时间戳是UTC，并将其转换为由tz指定的给定时区。
给定一个时间戳（对应于UTC中的某个时间），返回另一个时间戳，该时间戳对应于由tz指定的给定时区中的相同时间。

签名：

```
Copied!1
FROM_UTC_TIMESTAMP(Column ts, String tz)
```

FROM_UTC_TIMESTAMP是一个用于将 UTC 时间转换为指定时区时间的函数。

- Column ts：表示要转换的时间戳列，格式通常是 UTC 时间。
- String tz：表示目标时区的字符串。例如，可以是 'Asia/Shanghai' 表示东八区时间。
这个函数在处理跨时区的数据时非常有用，尤其是在全球化应用中。

### HOUR

描述：从给定的日期/时间戳/字符串中提取小时作为整数。字符串必须为‘yyyy-MM-dd’或‘yyyy-MM-dd HH:mm’格式。

签名：

```
Copied!1
HOUR(Column e)
```

```
Copied!1
-- HOUR 函数从给定的时间或日期时间值 (Column e) 中提取小时部分。
```

### LAST_DAY

描述:给定一个日期列，返回该日期所在月份的最后一天。

签名:

```
Copied!1
LAST_DAY(Column e)
```

LAST_DAY函数用于获取指定日期所在月份的最后一天。

- Column e：这是包含日期的列，LAST_DAY将返回该日期所在月份的最后一天。
### MINUTE

描述:从给定的日期/时间戳/字符串中提取分钟，作为整数。字符串必须是‘yyyy-MM-dd’或‘yyyy-MM-dd HH:mm’格式。

签名:

```
Copied!1
MINUTE(Column e) -- 提取时间列 e 中的分钟数
```

### MONTH

描述：从给定的日期/时间戳/字符串中提取月份为整数。字符串必须为格式‘yyyy-MM-dd’或‘yyyy-MM-dd HH:mm’。

签名：

```
Copied!1
2
3
MONTH(Column e)
-- 这个函数用于从日期列中提取月份。
-- "Column e" 是包含日期的列，函数将返回该列中日期对应的月份（1 到 12）。
```

### MONTHS_BETWEEN

描述:返回日期date1和date2之间的月份数。如果date1晚于date2，结果为正数。如果date1早于date2，结果为负数。如果两个日期是同一个月的同一天或都是月的最后一天，结果为整数。否则，结果四舍五入到小数点后8位。

签名:

```
Copied!1
MONTHS_BETWEEN(Column date1, Column date2)
```

- MONTHS_BETWEEN是一个用于计算两个日期之间的月份数的SQL函数。
- date1和date2是日期类型的列。
- 该函数返回date1和date2之间的完整月份差异。
### NEXT_DAY

描述:给定一个date列，返回在指定dayOfWeek之后的第一个日期。dayOfWeek参数不区分大小写，可以是以下之一：

- ‘Mon’
- ‘Tue’
- ‘Wed’
- ‘Thu’
- ‘Fri’
- ‘Sat’
- ‘Sun’
签名:

```
Copied!1
NEXT_DAY(Column date, String dayOfWeek)
```

```
Copied!1
2
3
4
-- NEXT_DAY 函数用于返回下一个指定的星期几的日期。
-- 参数：
-- Column date：指定的日期列。
-- String dayOfWeek：目标星期几，可以用字符串形式表示，如 'Monday', 'Tuesday' 等。
```

### QUARTER

描述:从给定的日期/时间戳/字符串中提取季度为整数。字符串必须为格式‘yyyy-MM-dd’或‘yyyy-MM-dd HH:mm’。结果季度的范围是1到4。

签名:

```
Copied!1
2
QUARTER(Column e)
-- 返回列 e 中日期所属的季度
```

### SECOND

描述:从给定的日期/时间戳/字符串中提取秒数作为整数。字符串必须为格式‘yyyy-MM-dd’或‘yyyy-MM-dd HH:mm’。

签名:

```
Copied!1
SECOND(Column e)
```

SECOND是一个SQL函数，用于从一个时间值中提取秒部分。这里的Column e代表一个包含时间数据的列。

### TO_DATE

描述：将列转换为日期类型。

签名：

```
Copied!1
2
-- 将 'Column e' 中的日期字符串转换为日期数据类型。
TO_DATE(Column e)
```

### TO_UTC_TIMESTAMP

描述：假设提供的时间戳（ts）在提供的时区（tz）中，并转换为UTC。

签名：

```
Copied!1
2
TO_UTC_TIMESTAMP(Column ts, String tz)
-- 将时间戳 ts 从时区 tz 转换为 UTC 时间戳
```

### TRUNC

描述:返回截断到由format指定单位的日期。format参数可以是‘year’，‘yyyy’，‘yy’以按年截断，或‘month’，‘mon’，‘mm’以按月截断。

签名:

```
Copied!1
2
3
4
5
TRUNC(Column date, String format)
-- TRUNC是一个用于截断日期的SQL函数。
-- 参数解释：
-- Column date: 要截断的日期列。
-- String format: 截断的格式，可以是 'YEAR'、'MONTH'、'DAY' 等，表示截断到哪一级别。
```

### UNIX_TIMESTAMP

描述：使用默认时区和默认语言环境将时间字符串转换为 Unix 时间戳（以秒为单位）。如果字符串转换为时间戳失败，则返回 null。

如果未提供模式字符串，则输入列s的默认格式为 yyyy-MM-dd HH:mm。如果输入列的格式不同，请提供模式字符串p。模式字符串可以使用 SimpleDateFormat 的模式字母。有关更多信息，请参考Java SimpleDateFormat 文档 ↗。

签名：

```
Copied!1
2
3
-- UNIX_TIMESTAMP 函数用于返回从 '1970-01-01 00:00:00'（UTC）到指定时间的秒数。
-- 第一种用法：UNIX_TIMESTAMP(Column s) 将转换指定列中的时间。
-- 第二种用法：UNIX_TIMESTAMP(Column s, String p) 用于指定时间列和格式模式。
```

### WEEKOFYEAR

描述：从给定的日期/时间戳/字符串中提取周数作为整数。字符串必须采用‘yyyy-MM-dd’或‘yyyy-MM-dd HH:mm’格式。

签名：

```
Copied!1
2
WEEKOFYEAR(Column e)
-- 返回指定日期列（Column e）所在的周数（1-53），根据ISO 8601标准进行计算。
```

### WINDOW

描述：在指定的时间戳列上生成固定或滑动时间窗口。如果未提供slideDuration，则生成固定时间窗口。如果提供了slideDuration，则通过将行划分为一个或多个时间窗口来生成滑动时间窗口。

窗口的开始是包含的，窗口的结束是排除的，因此12:05将在窗口[12:05,12:10)中，但不在[12:00,12:05)中。窗口可以支持微秒精度。不支持以月为单位的窗口。

窗口的起始时间为1970-01-01 00:00:00 UTC，除非提供了startTime。
此函数接受以下参数：

- timeColumn: 用作时间窗口时间戳的列。时间列必须是TimestampType类型。
- windowDuration: 指定窗口宽度的字符串，例如10分钟，1秒。请注意，持续时间是固定长度的时间，不会根据日历随时间变化。
- slideDuration: 指定窗口滑动间隔的字符串，例如1分钟。每个slideDuration将生成一个新窗口。必须小于或等于windowDuration。此持续时间同样是绝对的，不会根据日历变化。
- startTime: 相对于1970-01-01 00:00:00 UTC的偏移量，用于开始窗口间隔。例如，要创建每小时的固定窗口，起始于每小时的15分钟（例如12:15-13:15, 13:15-14:15...），请将startTime设置为15分钟。
签名：

```
Copied!1
2
3
4
5
6
7
8
-- 定义窗口函数，按时间列和窗口持续时间进行分组
WINDOW(Column timeColumn, String windowDuration)

-- 定义窗口函数，按时间列、窗口持续时间和滑动间隔进行分组
WINDOW(Column timeColumn, String windowDuration, String slideDuration)

-- 定义窗口函数，按时间列、窗口持续时间、滑动间隔和起始时间进行分组
WINDOW(Column timeColumn, String windowDuration, String slideDuration, String startTime)
```

### YEAR

描述:从给定的日期/时间戳/字符串中提取年份作为整数。字符串必须是‘yyyy-MM-dd’或‘yyyy-MM-dd HH:mm’格式。

签名:

```
Copied!1
YEAR(Column e)  -- 提取列e中的年份
```

## 数学函数

| 函数 | 描述 |
| --- | --- |
| ABS | 计算绝对值。 |
| ACOS | 计算给定值的反余弦。 |
| ASIN | 计算给定值的反正弦。 |
| ATAN | 计算给定值的反正切。 |
| ATAN2 | 将直角坐标 (x, y) 转换为极坐标 (r, theta) 并返回角度 theta。 |
| BIN | 返回给定长整型列的二进制值的字符串表示。 |
| BROUND | 返回列 e 的四舍五入值。 |
| CBRT | 计算给定值的立方根。 |
| CEIL | 计算给定值的上限。 |
| CONV | 将字符串列中的数字从一个进制转换为另一个进制。 |
| COS | 计算给定值的余弦。 |
| COSH | 计算给定值的双曲余弦。 |
| EXP | 计算给定值的指数。 |
| EXPM1 | 计算给定值的指数减去一。 |
| FACTORIAL | 计算给定值的阶乘。 |
| FLOOR | 计算给定值的下限。 |
| HYPOT | 计算 sqrt(a^2^ + b^2^) 而不会出现中间溢出或下溢。 |
| LOG | 计算给定值的自然对数。 |
| LOG10 | 计算给定值的以10为底的对数。 |
| LOG1P | 计算给定值加一的自然对数。 |
| LOG2 | 计算给定列的以2为底的对数。 |
| NEGATIVE | 一元负运算。 |
| PMOD | 返回被除数模除数的正值。 |
| POW | 返回第一个参数的值的第二个参数次方。 |
| RINT | 返回最接近参数且等于数学整数的双精度值。 |
| ROUND | 返回列 e 四舍五入到0个小数位的值。 |
| SHIFTLEFT | 将给定值左移 numBits 位。 |
| SHIFTRIGHT | 将给定值右移 numBits 位。 |
| SHIFTRIGHTUNSIGNED | 将给定值无符号右移 numBits 位。 |
| SIGNUM | 计算给定值的符号函数。 |
| SIN | 计算给定值的正弦。 |
| SINH | 计算给定值的双曲正弦。 |
| SQRT | 计算指定浮点值的平方根。 |
| TAN | 计算给定值的正切。 |
| TANH | 计算给定值的双曲正切。 |
| TODEGREES | 将以弧度测量的角度转换为大致等效的以度数测量的角度。 |
| TORADIANS | 将以度数测量的角度转换为大致等效的以弧度测量的角度。 |

### ABS

描述:计算绝对值。

签名:

```
Copied!1
ABS(Column e) -- 返回列e中每个值的绝对值
```

### ACOS

描述:计算给定值的反余弦。返回的角度在0.0到pi的范围内。

签名:

```
Copied!1
ACOS(Column e)
```

ACOS(Column e)是一个SQL函数，用于计算列e中每个值的反余弦（反三角函数）。返回的值以弧度为单位，并且输入值必须在-1到1之间。

### ASIN

描述：计算给定值的反正弦。返回的角度范围为 -pi/2 到 pi/2。

签名：

```
Copied!1
2
ASIN(Column e)
-- 计算列 e 的反正弦值（弧度）。ASIN 函数返回给定数字的反正弦，输入值范围应在 -1 到 1 之间。
```

### ATAN

描述：计算给定值的反正切。

签名：

```
Copied!1
ATAN(Column e)
```

ATAN(Column e)是一个SQL函数，它用于计算指定列e中每个值的反正切（arctangent）。此函数返回的结果是弧度值。使用这个函数的场景通常是在需要进行三角学计算的查询中。

### ATAN2

描述：返回从直角坐标 (x, y) 转换到极坐标 (r, theta) 的角度 theta。

签名：

```
Copied!1
2
3
4
-- 计算反正切函数，支持不同类型的参数
ATAN2(Column l, Column r)          -- 接受两个列作为参数
ATAN2(Column l, double r)          -- 接受一列和一个双精度浮点数作为参数
ATAN2(Column l, String rightName)  -- 接受一列和一个字符串（用于查找列名）作为参数
```

### BIN

描述:返回给定长整型列的二进制值的字符串表示。

签名:

```
Copied!1
BIN(Column e) -- 返回列e的二进制表示形式
```

### BROUND

描述：当仅提供列e时，返回列e的值，四舍五入到0位小数，使用HALF_EVEN舍入模式。这也被称为高斯舍入或银行家舍入。

当也提供scale时，返回列e的值，四舍五入到scale位小数（如果scale>= 0，则使用HALF_EVEN舍入模式；如果scale< 0，则在整数部分舍入）。

签名：

```
Copied!1
2
BROUND(Column e) -- 将列 e 的值四舍五入到最接近的整数
BROUND(Column e, int scale) -- 将列 e 的值四舍五入到最接近的指定小数位数
```

### CBRT

描述:计算给定值的立方根。

签名:

```
Copied!1
CBRT(Column e) -- 计算列 e 中每个值的立方根
```

### CEIL

描述:计算给定值的上限。

签名:

```
Copied!1
2
3
CEIL(Column e)
-- CEIL 函数用于向上取整，即返回不小于给定数值的最小整数。
-- 在这里，CEIL(Column e) 将对列 e 中的数值进行向上取整。
```

### CONV

描述:将字符串列中的数字从一个进制转换为另一个进制。

签名:

```
Copied!1
CONV(Column num, int fromBase, int toBase)
```

CONV函数用于将一个数字从一个进制系统转换到另一个进制系统。

- Column num：要转换的数字列。
- int fromBase：原始进制。
- int toBase：目标进制。
该函数在数据库处理时，特别是在需要不同进制表示的数据时非常有用。

### COS

描述:计算给定值的余弦值。

签名:

```
Copied!1
COS(Column e) -- 计算列e的余弦值
```

### COSH

描述：计算给定值的双曲余弦。

签名：

```
Copied!1
2
-- COSH函数用于计算e列中每个值的双曲余弦值
COSH(Column e)
```

### EXP

描述:计算给定值的指数。

签名:

```
Copied!1
2
3
EXP(Column e)
-- 该函数用于返回 e 的指数值，即 e 的 e 次幂。EXP 是指数函数的缩写。
-- 例如，EXP(1) 将返回 e^1 ≈ 2.71828。
```

### EXPM1

描述：计算给定值的指数减一。

签名：

```
Copied!1
EXPM1(Column e)
```

在SQL中，EXPM1函数用于计算指定列中每个值的指数减去1，即返回exp(e) - 1的结果。这个函数在数值计算中特别有用，尤其是在需要处理接近零的指数计算时，因为它可以提高计算的精度。

### FACTORIAL

描述:计算给定值的阶乘。

签名:

```
Copied!1
FACTORIAL(Column e)
```

这是一个SQL函数调用，FACTORIAL用于计算指定列e中每个值的阶乘。阶乘是一个数学函数，表示为 n!，即从 1 乘到 n 的所有整数的积。

### FLOOR

描述：计算给定值的向下取整。

签名：

```
Copied!1
2
3
FLOOR(Column e)
-- FLOOR 函数用于向下取整，返回小于或等于给定数值的最大整数。
-- 在这里，Column e 是要进行取整操作的列。
```

### HYPOT

描述:计算 sqrt(a^2^ + b^2^)，避免中间溢出或下溢。

签名：

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
-- HYPOT函数用于计算两个参数的欧几里得距离（即直角三角形的斜边长度）
-- 这里有三种重载形式：

HYPOT(Column l, Column r)
-- 计算两个列的值的欧几里得距离

HYPOT(Column l, double r)
-- 计算一列的值与一个常数值之间的欧几里得距离

HYPOT(Column l, String rightName)
-- 计算一列的值与另一个列（通过其名称指定）之间的欧几里得距离
```

### LOG

描述：计算给定值的自然对数。

签名：

```
Copied!1
LOG(Column e) -- 计算列e的自然对数
```

### LOG10

描述:计算给定值的以10为底的对数。

签名:

```
Copied!1
2
LOG10(Column e)
-- 计算列e中每个值的常用对数（以10为底）
```

### LOG1P

描述:计算给定值加一的自然对数。

签名:

```
Copied!1
LOG1P(Column e)
```

LOG1P是一个SQL函数，用于计算 1 加上指定列的自然对数（即ln(1 + e)）。这个函数在处理小数值时特别有用，因为直接计算对数可能导致精度问题。

### LOG2

描述:计算给定列的以2为底的对数。

签名:

```
Copied!1
LOG2(Column expr)
```

这个SQL函数LOG2用于计算给定列中每个值的以2为底的对数值。

### NEGATIVE

描述:一元负号（对表达式取负）。

签名:

```
Copied!1
NEGATIVE(Column e)  -- 计算列 e 的负值
```

### PMOD

描述：返回dividend模divisor的正值。

签名：

```
Copied!1
PMOD(Column dividend, Column divisor)
```

PMOD是一个SQL函数，用于计算被除数（dividend）除以除数（divisor）的非负模数。与传统的模运算不同的是，PMOD确保结果始终为非负数。

### POW

描述：返回第一个参数的值提升到第二个参数的幂。

签名：

```
Copied!1
2
3
4
-- 计算l的r次幂，支持不同类型的参数
POW(Column l, Column r) -- 使用两个列作为参数，计算l列的r列次幂
POW(Column l, double r) -- 使用一个列和一个double类型的数作为参数，计算l列的r次幂
POW(Column l, String rightName) -- 使用一个列和一个字符串（表示列名）作为参数，计算l列的指定列名的次幂
```

### RINT

描述:返回最接近参数值并等于数学整数的双精度值。

签名:

```
Copied!1
2
3
-- 可能是一个拼写错误，应该是 PRINT 而不是 RINT
-- PRINT 用于显示信息
PRINT(Column e)
```

### ROUND

描述:返回将列e的值四舍五入到0个小数位的结果。

签名:

```
Copied!1
2
3
-- ROUND 函数用于将数值列进行四舍五入。
-- ROUND(Column e): 将列 e 的数值进行四舍五入到整数。
-- ROUND(Column e, int scale): 将列 e 的数值四舍五入到指定的小数位数 scale。
```

### SHIFTLEFT

描述：将给定值向左移numBits位。

签名：

```
Copied!1
2
SHIFTLEFT(Column e, int numBits)
-- 将指定列 e 的每个值向左移动指定的位数 numBits
```

### SHIFTRIGHT

描述:将给定值向右移numBits位。

签名:

```
Copied!1
2
3
SHIFTRIGHT(Column e, int numBits)
-- 将列 e 中的数值右移 numBits 位
-- 这是一个位操作函数，将二进制数字右移指定的位数
```

### SHIFTRIGHTUNSIGNED

描述：无符号右移给定值numBits。

签名：

```
Copied!1
2
3
4
-- SHIFTRIGHTUNSIGNED 函数用于对指定的列进行无符号右移操作
-- Column e: 需要进行右移操作的列
-- int numBits: 指定右移的位数
SHIFTRIGHTUNSIGNED(Column e, int numBits)
```

### SIGNUM

描述:计算给定值的符号。

签名:

```
Copied!1
SIGNUM(Column e)
```

```
Copied!1
2
3
4
5
-- SIGNUM 函数返回给定列中每个值的符号。
-- 如果值为正数，返回 1；
-- 如果值为负数，返回 -1；
-- 如果值为零，返回 0。
-- 这个函数常用于判断数值的正负性。
```

### SIN

描述:计算给定值的正弦。

签名:

```
Copied!1
SIN(Column e) -- 计算列 e 中每个值的正弦值
```

### SINH

描述：计算给定值的双曲正弦。

签名：

```
Copied!1
SINH(Column e) -- 计算Column e中每个元素的双曲正弦值
```

### SQRT

描述：计算指定浮点值的平方根。

签名：

```
Copied!1
2
-- 计算列 e 的平方根
SQRT(Column e)
```

### TAN

描述：计算给定值的正切。

签名：

```
Copied!1
TAN(Column e) -- 计算列 e 中每个值的正切值
```

### TANH

描述:计算给定值的双曲正切。

签名:

```
Copied!1
2
TANH(Column e)
-- 计算列 e 的双曲正切值
```

### TODEGREES

描述:将以弧度测量的角度转换为大约等效的以度数测量的角度。

签名:

```
Copied!1
TODEGREES(Column e) -- 将弧度转换为角度
```

### TORADIANS

描述：将以度数测量的角度转换为近似等效的以弧度测量的角度。

签名：

```
Copied!1
2
TORADIANS(Column e)
-- 将列 e 中的角度值转换为弧度值
```

## 空值函数

| 函数 | 描述 |
| --- | --- |
| COALESCE | 返回第一个不为空的列，如果所有输入都为空，则返回空值。 |
| ISNULL | 当列为空时返回true。 |
| NULLIF | 如果两个参数相等则返回空值，否则返回第一个参数。 |

### COALESCE

描述:返回第一个不为空的列，如果所有输入都为空，则返回空值。

签名:

```
Copied!1
COALESCE(Column... e)
```

COALESCE是一个SQL函数，用于返回参数列表中的第一个非空值。此函数在处理可能包含NULL值的数据时非常有用。

### ISNULL

描述：当且仅当列为空时返回 true。

签名：

```
Copied!1
2
3
4
5
6
-- ISNULL 函数用于替换 NULL 值
-- 语法：ISNULL(expression, replacement_value)
-- 这里的 Column e 可能是一个错误或不完整的表达式
-- 如果你想检查某一列是否为 NULL 并替换它，可以使用下面的格式：
-- ISNULL(ColumnName, ReplacementValue)
-- 替换示例：ISNULL(ColumnName, 0)
```

### NULLIF

描述:如果两个参数相等，则返回null，否则返回第一个参数。

签名:

```
Copied!1
NULLIF(Column l, Column r)
```

NULLIF是一个 SQL 函数，用于比较两个表达式Column l和Column r。如果这两个表达式相等，则返回NULL；否则返回Column l的值。在数据处理和查询优化中，这个函数非常有用，可以避免除零错误或处理其他异常值。

## 集合函数

| 函数 | 描述 |
| --- | --- |
| ARRAY | 创建一个新的数组列。 |
| ARRAY_CONTAINS | 如果数组包含值，则返回true。 |
| EXPLODE | 为给定数组或映射列中的每个元素创建一个新行。 |
| MAP | 创建一个新的映射列。 |
| POSEXPLODE | 为给定数组或映射列中的每个带位置的元素创建一个新行。 |
| SIZE | 返回数组或映射的长度。 |
| SORT_ARRAY | 对给定列的输入数组进行升序/降序排序。 |
| STRUCT | 创建一个新的结构列。 |

### ARRAY

描述:创建一个新的数组列。

签名:

```
Copied!1
2
ARRAY(Column... cols)
-- 这个函数用于创建一个数组，由多个列组成。
```

### ARRAY_CONTAINS

描述:如果数组包含value则返回true。

签名:

```
Copied!1
ARRAY_CONTAINS(Column column, Object value)
```

ARRAY_CONTAINS函数用于检查数组列中是否包含指定的值。

- column: 要检查的数组列。
- value: 要搜索的对象值。
如果数组中包含该值，则返回true；否则返回false。

### EXPLODE

描述:为给定数组或映射列中的每个元素创建一个新行。

签名:

```
Copied!1
EXPLODE(Column e)
```

EXPLODE函数用于将数组或嵌套结构中的元素拆分成多行。Column e指定要被拆分的列。

### MAP

描述:创建一个新的映射列。

签名:

```
Copied!1
MAP(Column... cols)
```

MAP函数用于构建一个键值对的映射，其中cols是一组列。通常，cols的数量应该是偶数，键和值成对出现，例如(key1, value1, key2, value2, ...)。在数据库操作中，这样的映射可以用于存储和处理结构化的数据。

### POSEXPLODE

描述：为给定数组或映射列中的每个带位置的元素创建新行。

签名：

```
Copied!1
2
3
-- POSEXPLODE 函数用于将数组或映射类型的列展开，将每个元素与其位置一起输出
-- 参数 `Column e` 是要展开的列
POSEXPLODE(Column e)
```

### SIZE

描述：返回数组或映射的长度。

签名：

```
Copied!1
2
SIZE(Column e)
-- 返回指定列 e 的大小或元素数量
```

### SORT_ARRAY

描述:对给定列的输入数组进行排序，根据数组元素的自然顺序按升序/降序排列。排序默认按升序，除非将asc设置为false。

签名：

```
Copied!1
2
3
4
-- 对数组进行排序的函数
SORT_ARRAY(Column e)
-- 对数组进行升序或降序排序的函数，asc为true时升序，false时降序
SORT_ARRAY(Column e, boolean asc)
```

### STRUCT

描述：创建一个新的struct列。

签名：

```
Copied!1
STRUCT(Column... cols)
```

```
Copied!1
2
3
4
-- STRUCT 是一种 SQL 函数，用于创建一个结构体（类似于对象或记录），
-- 其中包含多个列（Column）。
-- 这个函数接收多个列作为参数，并将它们组合成一个结构体。
-- 结构体可以用于在 SQL 查询中返回复杂数据类型。
```

## 窗口函数

| 函数 | 描述 |
| --- | --- |
| LAG | 返回当前行之前偏移行数的值，如果当前行之前的行数少于偏移量，则返回null。 |
| LEAD | 返回当前行之后偏移行数的值，如果当前行之后的行数少于偏移量，则返回null。 |

### LAG

描述:窗口函数：返回当前行之前offset行数的值，如果当前行之前的行数少于offset，则返回null。例如，偏移量为一将在窗口分区的任何给定点返回前一行。

签名:

```
Copied!1
2
LAG(Column e, int offset)
LAG(Column e, int offset, Object defaultValue)
```

```
Copied!1
2
3
4
5
-- LAG 是一种窗口函数，用于获取当前行之前某个偏移量的行的值。
-- 第一个参数 e 是要获取值的列。
-- 第二个参数 offset 是偏移量，指定要获取的是当前行之前第几行的值。
-- 如果没有指定 offset，默认值为 1，即获取前一行的值。
-- 第三个参数 defaultValue 是可选的，当获取的行不存在时，返回的默认值。
```

### LEAD

描述:窗口函数：返回当前行之后offset行的值，如果当前行之后少于offset行，则返回null。

签名:

```
Copied!1
2
LEAD(Column e, int offset)
LEAD(Column e, int offset, Object defaultValue)
```

```
Copied!1
2
3
LEAD 函数用于从当前行向前查找相对于当前行偏移量为 offset 的行并返回该行中指定列 e 的值。
- 第一个形式 LEAD(Column e, int offset) 使用默认的 NULL 作为偏移行值缺失时的返回值。
- 第二个形式 LEAD(Column e, int offset, Object defaultValue) 则允许指定一个默认值 defaultValue，当偏移行的值缺失时返回该默认值。
```

## 其他函数

| 函数 | 描述 |
| --- | --- |
| CRC32 | 计算二进制列的循环冗余校验值，并将值返回为bigint。 |
| GREATEST | 返回值列表中的最大值，跳过空值。 |
| HASH | 计算给定列的哈希码，并将结果返回为int列。 |
| HEX | 计算给定列的十六进制值。 |
| ISNAN | 当且仅当列为NaN时返回true。 |
| LEAST | 返回值列表中的最小值，跳过空值。 |
| MD5 | 计算二进制列的MD5摘要，并将值返回为32字符的十六进制字符串。 |
| NANVL | 如果col1不是NaN，则返回col1，否则返回col2。 |
| NOT | 布尔表达式的反转。 |
| SHA1 | 计算二进制列的SHA-1摘要，并将值返回为40字符的十六进制字符串。 |
| SHA2 | 计算二进制列的SHA-2系列哈希函数，并将值返回为十六进制字符串。 |
| WHEN | 评估条件列表并返回多个可能结果表达式之一。 |

### CRC32

描述:计算二进制列的循环冗余校验值（CRC32），并将值返回为bigint。

签名:

```
Copied!1
CRC32(Column e)
```

CRC32(Column e)是一个 SQL 函数，用于计算列e中每个值的 CRC32 校验和。CRC32 是一种常用的错误检测算法，通常用于校验数据的完整性。它会返回一个无符号的 32 位整数作为结果。

### GREATEST

描述：返回值列表中的最大值，跳过空值。使用“>”运算符比较值。此函数至少需要2个参数。仅当所有参数均为空时才返回空值。

签名：

```
Copied!1
GREATEST(Column... exprs) -- 返回给定列或表达式中最大值的函数
```

### HASH

描述：计算给定列的哈希码，并将结果作为整数列返回。

签名：

```
Copied!1
2
3
4
HASH(Column... cols)
-- 该函数用于对一个或多个列进行哈希计算
-- 可以用于数据分布、数据去重、分区操作等场景
-- 传入的参数可以是一个或多个列，返回一个哈希值
```

### HEX

描述:计算给定列的十六进制值。如果column是整数或二进制类型，则返回数字的十六进制格式字符串。如果column是字符串类型，则将每个字符转换为其十六进制表示并返回生成的字符串。

签名:

```
Copied!1
HEX(Column column)
```

这个SQL函数用于将列中的数据转换为十六进制格式。

### ISNAN

描述:当且仅当列为NaN时返回true。

签名：

```
Copied!1
ISNAN(Column e) -- 检查列e中的值是否为NaN（不是一个数字）
```

### LEAST

描述：返回值列表中的最小值，跳过空值。使用“<”运算符比较值。此函数至少需要2个参数。仅当所有参数均为空时才会返回null。

签名：

```
Copied!1
LEAST(Column... exprs)
```

LEAST函数用于在给定的多个列或表达式中，返回最小的值。它比较所有输入的列或表达式，并输出其中的最小值。

### MD5

描述：计算二进制列的MD5摘要，并将值返回为32个字符的十六进制字符串。

签名：

```
Copied!1
MD5(Column e)
```

MD5是一种常用的哈希函数，用于对输入数据生成一个128位的哈希值。在这段代码中，MD5(Column e)的作用是对数据库中Column e列的内容进行MD5哈希计算。这个过程通常用于数据完整性验证或加密存储。

### NANVL

描述:如果col1不是NaN，则返回col1；如果col1是NaN，则返回col2。

签名:

```
Copied!1
NANVL(Column col1, Column col2)
```

NANVL是一个用于处理 SQL 中 NaN（Not a Number）值的函数。如果col1的值是 NaN，则返回col2的值；否则，返回col1的值。这在处理浮点数数据时非常有用，因为 NaN 是一个特殊的值，通常在计算中需要特别处理。

### NOT

描述:布尔表达式的取反（即NOT）。

签名:

```
Copied!1
2
3
4
-- 逻辑非运算符用于反转布尔值
-- 如果 Column e 的值为 TRUE，则 NOT(Column e) 的结果为 FALSE
-- 如果 Column e 的值为 FALSE，则 NOT(Column e) 的结果为 TRUE
NOT(Column e)
```

### SHA1

描述：计算二进制列的SHA-1摘要，并将值返回为40个字符的十六进制字符串。

签名：

```
Copied!1
2
3
SHA1(Column e)
-- 使用 SHA1 函数对列 e 的值进行哈希处理
-- SHA1 是一种加密哈希算法，会生成一个 160 位（20 字节）的哈希值
```

### SHA2

描述:计算二进制列的SHA-2系列哈希函数，并将值返回为十六进制字符串。

签名:

```
Copied!1
SHA2(Column e, int numBits)
```

```
Copied!1
2
3
-- SHA2 函数用于计算指定列的 SHA-2 哈希值。
-- Column e 表示要计算哈希的列。
-- int numBits 表示 SHA-2 算法的位数，例如 224、256、384 或 512。
```

### WHEN

描述:评估条件列表并返回多个可能结果表达式之一。

签名:

```
Copied!1
2
3
WHEN(Column condition, Object value)
-- 这个语法通常用于SQL的CASE语句中。
-- 当Column condition（列条件）为真时，返回Object value（对象值）。
```
