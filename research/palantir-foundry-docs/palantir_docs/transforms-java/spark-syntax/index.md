来源: https://palantir.com/docs/zh/foundry/transforms-java/spark-syntax/

# 语法速查表

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 语法速查表

Java Spark SQL中最常用的模式和函数的快速参考指南。

有关Java Spark的更多信息，请参见Java Spark官方文档 ↗。

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
8
9
10
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MyClass {
    // 创建一个Logger实例，用于记录日志
    private static final Logger LOG = LoggerFactory.getLogger(MyClass.class);

    // 记录一条信息级别的日志
    LOG.info("example log output");
}
```

#### 导入数据集、行、函数和类型

```
Copied!1
2
3
4
import org.apache.spark.sql.Dataset; // 导入Spark SQL的Dataset类
import org.apache.spark.sql.Row; // 导入Spark SQL的Row类
import static org.apache.spark.sql.functions.*; // 导入Spark SQL函数的静态方法
import org.apache.spark.sql.types.DataTypes; // 导入Spark SQL数据类型
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
16
17
18
// 根据等于条件进行过滤
df = df.filter(col("is_adult").equalTo("Y"));

// 根据 >, <, >=, <= 条件进行过滤
df = df.filter(col("age").gt(25));  // 大于25
df = df.filter(col("age").lt(25));  // 小于25
df = df.filter(col("age").geq(25)); // 大于等于25
df = df.filter(col("age").leq(25)); // 小于等于25

// 多个条件组合过滤
df = df.filter(col("age").gt(25).and(col("is_adult").equalTo("Y")));

// 根据允许值列表进行过滤
df = df.filter(col("first_name").isin(List.of(3, 4, 7)));

// 排序结果
df = df.orderBy(col("age").asc());  // 按年龄升序排序
df = df.orderBy(col("age").desc()); // 按年龄降序排序
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
24
25
// 在另一个数据集上进行左连接
df = df.join(personLookupTable, col("person_id"), "left");

// 在另一个数据集上进行左反连接（返回左数据集中未匹配的行）
df = df.join(personLookupTable, col("person_id"), "leftanti");

// 在左、右数据集中使用不同的列进行匹配
df = df.join(otherTable, col("id").equalTo(col("person_id")), "left");

// 在多个列上进行匹配
df = df.join(otherTable, col("first_name").equalTo(col("name")).and(
             col("last_name").equalTo(col("family_name"))), "left");

// 用于单行查找代码连接的有用方法
public Dataset<Row> lookupAndReplace(Dataset<Row> df1, Dataset<Row> df2,
    String df1Key, String df2Key, String df2Value) {

    return df1.join(df2.select(col(df2Key), col(df2Value)),
                    col(df1Key).equalTo(col(df2Key)), "left")
              .withColumn(df1Key, coalesce(col(df2Value), col(df1Key)))
              .drop(df2Key, df2Value);
}

// 使用lookupAndReplace方法进行查找和替换
Dataset<Row> df = lookupAndReplace(people, payCodes, id, payCodeId, payCodeDesc);
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
28
29
30
31
32
33
34
35
36
37
38
39
// 添加一个新的静态列
df = df.withColumn("status", lit("PASS"));

// 构建一个新的动态列
df = df.withColumn("full_name", when(
    (col("fname").isNotNull().or(col("lname").isNotNull())),
    concat_ws(" ", col("fname"), col("lname")))
    .otherwise(lit(null))); // 如果姓或名不为空，则连接它们，否则为null

// 选择保留的列，并可选地重命名一些列
df = df.select(
    col("name"),
    col("age"),
    col("dob").alias("date_of_birth") // 将dob列重命名为date_of_birth
);

// 删除列
df = df.drop("mod_dt", "mod_username");

// 重命名某一列
df = df.withColumnRenamed("dob", "date_of_birth");

// 保留在另一个数据集中也出现的所有列
import org.apache.spark.sql.Column;
import scala.collection.JavaConversions;

List<Column> columnsToSelect = new ArrayList<Column>();
List<String> df2Columns = Arrays.asList(df2.columns());
for (String c : df.columns()) {
  if (df2Columns.contains(c)) {
    columnsToSelect.add(col(c)); // 如果df2中也有该列，则添加到选择列表
  }
}
df = df.select(JavaConversions.asScalaBuffer(columnsToSelect));

// 批量重命名/清理列
for (String c in df.columns()) {
  df = df.withColumnRenamed(c, c.toLowerCase().replace(" ", "_").replace("-", "_")); // 将列名转换为小写并替换空格和破折号为下划线
}
```

#### 转换和合并空值及重复值

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
import org.apache.spark.sql.types.DataTypes;

// 将列转换为不同的数据类型（两种方式等效）
df = df.withColumn("price", col("price").cast(DataTypes.DoubleType));
df = df.withColumn("price", col("price").cast("double"));

// 创建一个全为空值的列并转换为特定类型
df = df.withColumn("name", lit(null).cast(DataTypes.StringType));
df = df.withColumn("name", lit(null).cast("string"));

// 用特定值替换所有的空值
df = df.na().fill(ImmutableMap.of("first_name", "Tom", "age", 0));

// 取第一个非空值
df = df.withColumn("last_name", coalesce(col("last_name"), col("surname"), lit("N/A")));

// 删除数据集中重复的行（与 distinct() 相同）
df = df.dropDuplicates()

// 删除重复的行，但只考虑特定的列
df = df.dropDuplicates("name", "height");
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
24
25
26
27
28
29
30
31
// 包含 - col.contains(string)
// 过滤出"name"列中包含字母"o"的行
df = df.filter(col("name").contains("o"));

// 以...开头 - col.startsWith(string)
// 过滤出"name"列以"Al"开头的行
df = df.filter(col("name").startsWith("Al"));

// 以...结尾 - col.endsWith(string)
// 过滤出"name"列以"ice"结尾的行
df = df.filter(col("name").endsWith("ice"));

// 为空 - col.isNull()
// 过滤出"is_adult"列为空的行
df = df.filter(col("is_adult").isNull());

// 不为空 - col.isNotNull()
// 过滤出"first_name"列不为空的行
df = df.filter(col("first_name").isNotNull());

// 类似 - col.like(string_with_sql_wildcards)
// 过滤出"name"列以"Al"开头的行（使用SQL通配符）
df = df.filter(col("name").like("Al%"));

// 正则表达式匹配 - col.rlike(regex)
// 使用正则表达式过滤出"name"列以任意大写字母开头并以"ice"结尾的行
df = df.filter(col("name").rlike("[A-Z]*ice$"));

// 在列表中 - col.isin(Object... values)
// 过滤出"name"列值为"Bob"或"Mike"的行
df = df.filter(col("name").isin("Bob", "Mike"));
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
// Substring - col.substr(startPos, length) (1-based indexing)
// 子字符串 - col.substr(startPos, length)（基于1的索引）
df = df.withColumn("short_id", col("id").substr(1, 10));

// Trim - trim(col)
// 去除字符串两端的空格 - trim(col)
df = df.withColumn("name", trim(col("name")));

// Left Pad - lpad(col, len, pad)
// 左填充 - lpad(col, len, pad)
df = df.withColumn("id", lpad(col("id"), 4, "0"));

// Left Trim - ltrim(col)
// 去除字符串左侧的空格 - ltrim(col)
df = df.withColumn("id", ltrim(col("id")));

// Right Trim - rtrim(col)
// 去除字符串右侧的空格 - rtrim(col)
df = df.withColumn("id", rtrim(col("id")));

// Concatenate - concat(Column... cols) (null if any column null)
// 连接字符串 - concat(Column... cols)（如果任何列为null，则结果为null）
df = df.withColumn("full_name", concat(col("fname"), lit(" "), col("lname")));

// Concatenate with Delimiter - concat_ws(delim, Column... cols) (ignores nulls)
// 带分隔符连接字符串 - concat_ws(delim, Column... cols)（忽略null值）
df = df.withColumn("full_name", concat_ws("-", "fname", "lname"));

// Regex Replace - regexp_replace(col, pattern, replacement)
// 正则表达式替换 - regexp_replace(col, pattern, replacement)
df = df.withColumn("id", regexp_replace(col("id"), "0F1(.*)", "1F1-$1"));

// Regex Extract - regexp_extract(str, pattern, idx)
// 正则表达式提取 - regexp_extract(str, pattern, idx)
df = df.withColumn("id", regexp_extract(col("id"), "[0-9]*", 0));
```

## 数字操作

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
// Round - round(col, scale=0)
// 四舍五入 - round(col, scale=0)
df = df.withColumn("price", round(col("price"), 0));

// Floor - floor(col)
// 向下取整 - floor(col)
df = df.withColumn("price", floor(col("price")));

// Ceiling - ceil(col)
// 向上取整 - ceil(col)
df = df.withColumn("price", ceil(col("price")));

// Absolute Value - abs(col)
// 绝对值 - abs(col)
df = df.withColumn("price", abs(col("price")));

// X raised to power Y – pow(X, Y)
// X 的 Y 次方 - pow(X, Y)
df = df.withColumn("exponential_growth", pow(col("x"), 2.0));

// Select smallest value out of multiple columns – least(Column... cols)
// 选择多个列中的最小值 - least(Column... cols)
df = df.withColumn("least", least(col("subtotal"), col("total")));

// Select largest value out of multiple columns – greatest(Column... cols)
// 选择多个列中的最大值 - greatest(Column... cols)
df = df.withColumn("greatest", greatest(col("subtotal"), col("total")));
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
// 将已知格式的字符串转换为日期（不包括时间信息）
df = df.withColumn("date_of_birth", to_date(col("date_of_birth"), "yyyy-MM-dd"));

// 将已知格式的字符串转换为时间戳（包括时间信息）
df = df.withColumn("time_of_birth", to_timestamp(col("time_of_birth"), "yyyy-MM-dd HH:mm:ss"));

// 从日期中获取年份：      year(col)
// 从日期中获取月份：      month(col)
// 从日期中获取日期：      dayofmonth(col)
// 从日期中获取小时：      hour(col)
// 从日期中获取分钟：      minute(col)
// 从日期中获取秒：        second(col)
df = df.filter(year(col("date_of_birth")).equalTo("2017"));

// 增加和减少天数
df = df.withColumn("three_days_after", date_add(col("date_of_birth"), 3));
df = df.withColumn("three_days_before", date_sub(col("date_of_birth"), 3));

// 增加和减少月份
df = df.withColumn("next_month", add_months(col("date_of_birth"), 1));
df = df.withColumn("previous_month", add_months(col("date_of_birth"), -1));

// 获取两个日期之间的天数
df = df.withColumn("days_between", datediff(col("end"), col("start")));

// 获取两个日期之间的月份数
df = df.withColumn("months_between", months_between(col("end"), col("start")));

// 仅保留date_of_birth在2017-05-10和2018-07-21之间的行
df = df.filter(
    (col("date_of_birth").geq("2017-05-10")).and(
    (col("date_of_birth").leq("2018-07-21")))
);
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
// 从现有列创建数组或结构体列
df = df.withColumn("guardians", array(col("guardian_1"), col("guardian_2"))); // 创建一个包含guardian_1和guardian_2的数组列
df = df.withColumn("properties", struct(col("hair_color"), col("eye_color"))); // 创建一个包含hair_color和eye_color的结构体列

// 通过索引或键从数组或结构体列中提取数据（若无效则为null）
df = df.withColumn("primary_guardian", col("guardians").getItem(0)); // 提取guardians数组中的第一个元素
df = df.withColumn("hair_color", col("properties").getItem("hair_color")); // 从properties结构体中提取hair_color键对应的值

// 将数组或结构体列拆分为多行
df = df.select(col("child_name"), explode(col("guardians"))); // 将guardians数组拆分为多行
df = df.select(col("child_name"), explode(col("properties"))); // 将properties结构体拆分为多行（通常explode不适用于结构体）

// 将结构体列拆分为多个列
df = df.select(col("child_name"), col("properties.*")); // 将properties结构体列展开为多个独立的列
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
16
17
18
19
// 行计数：                count(col), countDistinct(col)
// 组中行的总和：          sum(col)
// 组中行的平均值：        mean(col)
// 组中行的最大值：        max(col)
// 组中行的最小值：        min(col)
// 组中第一行：            first(col, ignoreNulls)

// 按照"address"列进行分组，并聚合操作
df = df.groupBy(col("address")).agg(
  count(col("uuid")).alias("num_residents"),   // 计算每个组中"uuid"的数量，别名为"num_residents"
  max(col("age")).alias("oldest_age"),         // 找出每个组中"age"的最大值，别名为"oldest_age"
  first(col("city"), true).alias("city")       // 获取每个组中第一个"city"的值，忽略空值，别名为"city"
);

// 收集组中所有行的集合：       collect_set(col)
// 收集组中所有行的列表：       collect_list(col)

// 按照"address"列进行分组，并聚合操作，收集每个组中所有"resident_names"
df = df.groupBy(col("address")).agg(collect_set("name").alias("resident_names"));
```

## 高级操作

#### 重新分区

```
Copied!1
2
3
// 重新分区 – df.repartition(num_output_partitions)
// 将数据帧重新分区为1个输出分区
df = df.repartition(1);
```

#### UDF（用户定义函数）

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
import org.apache.spark.sql.expressions.UserDefinedFunction;
import org.apache.spark.sql.types.DecimalType;
import static org.apache.spark.sql.functions.col;
import static org.apache.spark.sql.functions.udf;
import java.math.BigDecimal;

/**
 * 以下示例创建了一个Java UDF（用户自定义函数），用于将两个Spark类型为"Decimal"的列相加。
 * Spark使用java.math.BigDecimal来表示DecimalType，因此我们使用此类。
 * 其他Spark类型将由其他Java类型表示，具体定义请参阅https://spark.apache.org/docs/3.0.0/sql-ref-datatypes.html
 */

public final class HighLevelAutoTransform {
    @Compute
    @Output("...")
    public Dataset<Row> myComputeFunction(@Input("...") Dataset<Row> df) {
        UserDefinedFunction addsUDF = udf((BigDecimal i, BigDecimal j) -> {
            if (i == null || j == null) { // 始终处理空值情况
                return null;
            }

            return i.add(j);
        }, new DecimalType()); // 这是UDF结果的Spark数据类型

        return df.withColumn("a_plus_b", addsUDF.apply(col("a"), col("b")));
    }
}
```
