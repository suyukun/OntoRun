来源: https://palantir.com/docs/zh/foundry/data-connection/optimize-jdbc-syncs/

# 优化 JDBC 同步

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 优化 JDBC 同步

本指南提供了提高 JDBC 同步速度和可靠性的方法。

如果您的同步已经可靠运行，则无需执行以下描述的操作。如果您正在设置新的同步，或者同步完成时间过长或无法可靠完成，建议您按照本指南进行操作。

加速 JDBC 同步主要有两种方法。我们建议首先使同步增量化，只有在增量同步不足时才并行化 SQL 查询：

- 使您的同步增量化
- 并行化 SQL 查询
## 增量同步

默认情况下，批量同步将同步目标表中所有匹配的行。增量同步则维护最近一次同步的状态，从而只吸收目标表中的新匹配行。对于拥有大量行的表，增量同步可以显著提高同步性能。增量同步通过将数据作为APPEND事务添加到同步的数据集中来工作。

以下是增量批量同步的示例配置：

执行以下步骤以设置增量批量同步：

- 导航到要转换的同步的配置页面，并确保预览正常工作。
导航到要转换的同步的配置页面，并确保预览正常工作。

- 将事务类型设置为APPEND。这是为了避免覆盖之前同步的行。
将事务类型设置为APPEND。这是为了避免覆盖之前同步的行。

- 在增量框中选择启用。确保预览已成功运行此同步。在预览正常工作的情况下，增量框将展开，允许您配置同步的初始增量状态。
在增量框中选择启用。确保预览已成功运行此同步。在预览正常工作的情况下，增量框将展开，允许您配置同步的初始增量状态。

- 配置同步的增量状态。该状态由一个增量列和一个初始值组成，可以在用户界面中配置。在设置这些值时，请牢记以下重要考虑事项：增量列在同步之间必须_严格递增_。如果您的行是不可变的（即现有行不能原地更新），任何持续递增的列（例如自动递增的ID，或表示行添加时间的时间戳）都将足够。如果您的行是可变的（即您的表允许更新现有行，而不仅仅是插入新行），您将需要一个每次数据变动时都会递增的列（例如update_time列）。为避免多次吸收同一行，增量列的初始值必须大于之前所有运行中同步的_所有行_的值。例如，如果最近的SNAPSHOT同步带入的行的整数id列值范围达到1999，则可以将初始值设置为2000。
配置同步的增量状态。该状态由一个增量列和一个初始值组成，可以在用户界面中配置。在设置这些值时，请牢记以下重要考虑事项：

- 增量列在同步之间必须_严格递增_。如果您的行是不可变的（即现有行不能原地更新），任何持续递增的列（例如自动递增的ID，或表示行添加时间的时间戳）都将足够。如果您的行是可变的（即您的表允许更新现有行，而不仅仅是插入新行），您将需要一个每次数据变动时都会递增的列（例如update_time列）。
- 为避免多次吸收同一行，增量列的初始值必须大于之前所有运行中同步的_所有行_的值。例如，如果最近的SNAPSHOT同步带入的行的整数id列值范围达到1999，则可以将初始值设置为2000。
当您吸收现有行的更新版本时，Foundry 数据集仍将包括该行的先前版本（记住，我们正在使用APPEND事务类型）。如果您只想要每行的_最新_版本，您需要使用 Foundry 中的其他工具，例如变换，来清理数据。有关更多信息，请参考增量管道指南。

- 最后，更新查询以使用通配符符号?。具体如何在查询中包含通配符取决于您的查询逻辑；以下是一个简单示例，请注意以下几点：在第一次增量运行中，此通配符将替换为我们在前一步中指定的初始值。在任何后续运行中，通配符将替换为上一次运行中增量列的_最大_同步值。
- 在第一次增量运行中，此通配符将替换为我们在前一步中指定的初始值。
- 在任何后续运行中，通配符将替换为上一次运行中增量列的_最大_同步值。
如上所述，增量状态界面仅在同步预览成功运行时有效。这意味着如果您从头开始创建增量同步或复制现有的增量同步，您需要在查询中不使用通配符?操作符运行预览。

### 示例

假设您正在吸收一个名为employees的表，事务类型设置为SNAPSHOT，并使用以下简单的 SQL 查询：

```
Copied!1
2
3
4
SELECT
    * -- 选择所有字段
FROM
    employees -- 从 employees 表中查询
```

在时间点T1，表格如下所示：

| id | name | surname | update_time | insert_time |
| --- | --- | --- | --- | --- |
| 1 | Jane | Smith | 1478862205 | 1478862205 |
| 2 | Erika | Mustermann | 1478862246 | 1478862246 |

假设这个表是可变的，因此在稍后的时间点T2，它看起来像这样：

| id | name | surname | update_time | insert_time |
| --- | --- | --- | --- | --- |
| 1 | Jane | Doe | 1478862452 | 1478862205 |
| 2 | Erika | Mustermann | 1478862246 | 1478862246 |
| 3 | Juan | Perez | 1478862438 | 1478862438 |

我们希望将此同步转换为增量同步，因此我们将事务类型更新为APPEND。

我们应该使用哪个作为增量列？重要的是要注意id或insert_time列都不适合作为增量列，因为它们会漏掉更新，比如Jane行中的surname列的更改。相反，我们应该使用update_time作为增量列。

我们选择的初始值取决于我们是否以前从此表同步过行。假设我们在时间点T1运行了一个SNAPSHOT同步，并且已经同步了update_time值高达1478862246的行；我们应该使用1478862247作为初始值以避免重复。如果我们从未从此表同步过任何行，我们可以使用0（或者如果设置日期，可以使用01/01/1970）作为初始值。

最后，我们将 SQL 查询更改为

```
Copied!1
2
3
4
5
6
SELECT
    *
FROM
    employees
WHERE
    update_time > ?  -- 查询条件：筛选出更新时间在某个时间点之后的员工数据。问号“?”为占位符，需在实际使用时替换为具体的时间值。
```

转换现已完成。请注意，在增量运行同步后，我们的数据集中将有多个Jane行（每次更新一个）。如前所述，我们必须在下游逻辑中处理这些重复项，例如在 Contour 或 变换 中。

如果您在增量 JDBC 同步中遇到问题，本节的故障排除指南可能会有所帮助。

## 并行化 SQL 查询

由于并行功能对目标数据库运行单独的查询，请仔细考虑实时更新表被略有不同时间的查询处理的情况。

并行功能允许您轻松地将 SQL 查询拆分为多个较小的查询，这些查询将由代理并行执行。

为了实现这种行为，您需要将 SQL 语句更改为以下结构：

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
SELECT
    /* FORCED_PARALLELISM_COLUMN({{column}}), FORCED_PARALLELISM_SIZE({{size}}) */
    /* 强制并行列和强制并行大小的设置 */
    column1,
    column2
FROM
    {{table_name}}
WHERE
    {{condition}}
    /* ALREADY_HAS_WHERE_CLAUSE(TRUE) */
    /* 已经有WHERE子句的标识 */
```

查询的关键部分包括：

- FORCED_PARALLELISM_COLUMN({{column}})这指定了表将被划分的列。它应该是一个数值列（或产生数值列的列表达式），其分布应尽可能均匀。
- 这指定了表将被划分的列。
- 它应该是一个数值列（或产生数值列的列表达式），其分布应尽可能均匀。
- FORCED_PARALLELISM_SIZE({{size}})指定并行度，例如4将导致五个同时查询：四个分割指定的并行列的值，以及一个针对并行列中NULL值的查询。
- 指定并行度，例如4将导致五个同时查询：四个分割指定的并行列的值，以及一个针对并行列中NULL值的查询。
- ALREADY_HAS_WHERE_CLAUSE(TRUE)这指定是否已经有WHERE子句或是否需要生成一个。如果这是FALSE，将WHERE column%size = X添加到每个生成的查询中。如果这是TRUE，该条件将通过AND附加。
- 这指定是否已经有WHERE子句或是否需要生成一个。如果这是FALSE，将WHERE column%size = X添加到每个生成的查询中。如果这是TRUE，该条件将通过AND附加。
### 示例

假设您正在同步一个名为employees的表，其中包含以下数据：

| id | name | surname |
| --- | --- | --- |
| 1 | Jane | Smith |
| 2 | Erika | Mustermann |
| 3 | Juan | Perez |
| NULL | Mary | Watts |

基本查询将如下所示：

```
Copied!1
2
3
4
SELECT
    id, name, surname -- 选择id、名字和姓氏
FROM
    employees -- 从employees表中查询
```

这将在数据库中执行一个查询，并尝试从表中检索所有记录。

为了利用并行机制，查询可以更改为以下内容：

```
Copied!1
2
3
4
5
6
7
8
SELECT
    /* FORCED_PARALLELISM_COLUMN(id), FORCED_PARALLELISM_SIZE(2) */
    -- 强制并行执行，基于id列进行并行化，设置并行度为2
    id, name, surname
FROM
    employees
 /* ALREADY_HAS_WHERE_CLAUSE(FALSE) */
 -- 表示当前查询语句还没有WHERE子句
```

这将并行执行以下三个查询：

```
Copied!1
2
3
4
5
6
SELECT
    id, name, surname
FROM
    employees
WHERE
    id % 2 = 1 -- 选择id为奇数的员工记录
```

提取：

| id | 名字 | 姓氏 |
| --- | --- | --- |
| 1 | Jane | Smith |
| 3 | Juan | Perez |

和

```
Copied!1
2
3
4
5
6
SELECT
    id, name, surname
FROM
    employees
WHERE
    id % 2 = 0  -- 选择员工表中ID为偶数的记录
```

提取：

| id | 名字 | 姓氏 |
| --- | --- | --- |
| 2 | Erika | Mustermann |

和

```
Copied!1
2
3
4
5
6
SELECT
    id, name, surname
FROM
    employees
WHERE
    id % 2 IS NULL -- 筛选出ID为偶数的员工记录，因为只有偶数对2取余为0
```

提取：

| id | name | surname |
| --- | --- | --- |
| NULL | Mary | Watts |

### 包含OR条件的WHERE子句的并行

当在包含OR条件的WHERE子句中使用并行时，应将条件用括号括起来以指示应如何评估条件。例如，查看下面提供的同步：

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
SELECT  /* FORCED_PARALLELISM_COLUMN(col1), FORCED_PARALLELISM_SIZE(32) */
-- 指定并行化列为 col1，强制并行化大小为 32
col1,
col2
FROM tbl
WHERE
condition1 = TRUE OR condition2 = TRUE
/* ALREADY_HAS_WHERE_CLAUSE(TRUE) */
-- 已经存在 WHERE 子句
```

此示例同步将被变换为以下内容：

```
Copied!1
2
3
4
condition1 = TRUE OR condition2 = TRUE AND col1 % X = 0
-- 请注意操作符的优先级问题：
-- AND 操作符比 OR 操作符的优先级高，因此上面的语句等同于：
-- condition1 = TRUE OR (condition2 = TRUE AND col1 % X = 0)
```

不过，该语句可能会被逻辑解释为condition1 = TRUE OR (condition2 = TRUE AND col1 % X = 0)，而不是期望的(condition1 = TRUE OR condition2 = TRUE) AND col1 % X = 0。您可以通过在整个WHERE子句外加括号来确保正确的解释。对于上面的例子，这意味着：

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
SELECT  /* FORCED_PARALLELISM_COLUMN(col1), FORCED_PARALLELISM_SIZE(32) */
-- 指定强制并行处理的列为 col1，并行度设置为 32
col1,
col2
FROM tbl
WHERE
(condition1 = TRUE OR condition2 = TRUE)
-- 判断条件 condition1 或 condition2 是否为真
/* ALREADY_HAS_WHERE_CLAUSE(TRUE) */
-- 表示此查询已经有 WHERE 子句
```
