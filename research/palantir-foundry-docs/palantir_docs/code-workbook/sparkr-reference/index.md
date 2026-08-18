来源: https://palantir.com/docs/zh/foundry/code-workbook/sparkr-reference/

# SparkR 参考

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# SparkR 参考

## SparkR 简介

Code Workbook 允许用户同时使用 Spark R 和原生 R。Spark R 提供了一种分布式数据框实现，支持对大型数据集进行选择、筛选和聚合等操作。虽然用户可能对原生 R 更加熟悉，但建议用户首先使用 SparkR 以筛选大型数据集，然后再使用原生 R。

## 常见 SparkR 操作

阅读完整的API 文档 ↗以查看所有可能的操作。下面，我们概述了常见操作的语法。

### 筛选

筛选表达式可以是一个作为字符串传递的类似 SQL 的 WHERE 子句。

```
Copied!1
2
df_filtered <- SparkR::filter(df, "numeric_col > 10")
# 使用 SparkR 的 filter 函数过滤数据框 df，只保留 numeric_col 大于 10 的行
```

您也可以使用类似于标准R语法的列表达式。

```
Copied!1
2
# 使用 SparkR 的 filter 函数过滤数据框中的行，条件是 numeric_col 列的值大于 10
df_filtered <- SparkR::filter(df, df$numeric_col > 10)
```

您也可以使用SparkR::where，语法类似。

```
Copied!1
2
# 使用SparkR库的where函数过滤数据框df，条件是'numeric_col'列的值大于10
df_filtered <- SparkR::where(df, "numeric_col > 10")
```

### 列操作

使用SparkR::select()筛选列。

```
Copied!1
2
# 从数据框 df 中选择指定的列 "column1", "column2", "column3"
df_subset <- SparkR::select(df, "column1", "column2", "column3")
```

使用SparkR::withColumnRenamed()重命名列。

```
Copied!1
2
# 将数据框 df 中的 "old_column_name" 列重命名为 "new_column_name"
df <- SparkR::withColumnRenamed(df, "old_column_name", "new_column_name")
```

使用SparkR::withColumn()添加新列。

```
Copied!1
2
3
4
5
# 添加两列的和，创建新列 'col1_plus_col2'
df <- SparkR::withColumn(df, 'col1_plus_col2', df$col1 + df$col2)

# 将列乘以常数 60，创建新列 'col1_times_60'
df <- SparkR::withColumn(df, 'col1_times_60', df$col1 * 60)
```

### 聚合

使用SparkR::groupBy和SparkR::agg来计算聚合。调用SparkR::groupBy将创建一个分组对象。将分组对象传递给SparkR::agg以获取聚合的数据框。

```
Copied!1
2
3
4
5
# 使用 SparkR 对数据框 df 进行分组操作，按 group_col1 和 group_col2 列进行分组
df_grouped <- SparkR::groupBy(df, "group_col1", "group_col2")

# 对分组后的数据进行聚合操作，计算 col1 列的平均值和最大值
df_agg <- SparkR::agg(df_grouped, average_col1=avg(df$col1), max_col=max(df$col1))
```
