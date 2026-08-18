来源: https://palantir.com/docs/zh/foundry/contour/expressions-arrays/

# 数组函数

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 数组函数

本主题重点介绍您可能希望在Contour中的表达式中使用的数组函数。

## 关于Contour中的数组

您应该注意，数组仅在Contour的表达式面板中支持。在列表达式中使用数组后，您应该使用array_join将结果数组转换为字符串，以便您可以在其他Contour面板中使用它。

## 数组长度

您可以使用array_length函数来获取数组的长度。这在筛选时可能很有帮助。例如，如果您有一个数组列items_array，可以使用筛选表达式面板与array_length函数一起获取数组的长度，如下所示。

```
Copied!1
2
array_length(items_array) > 0
# 检查数组 items_array 是否为空，返回 True 表示数组中至少有一个元素。
```

## 合并值

您可以使用array_agg函数来合并列中的值。
假设您有一个购买记录的表。您想要创建一个新列，其中包含特定客户购买的所有商品的数组。
如果您的表格如下所示：

| customer_id | item |
| --- | --- |
| 123 | bread |
| 123 | eggs |
| 444 | milk |
| 444 | bananas |
| 444 | bread |

您可以使用以下函数创建一个带有合并值的新列：

```
Copied!1
2
3
array_join( array_agg("item") OVER (PARTITION BY "customer_id"), ', ' )
-- 这个SQL函数组合用于根据"customer_id"对数据进行分区，并将属于同一客户的"item"聚合成一个数组。
-- 然后，使用array_join函数，将该数组中的元素用', '分隔符连接成一个字符串。
```

将其分解为以下部分：

- array_agg返回给定列中所有值的数组。我们为其提供了一个窗口函数作为列参数。因此，不是
```
array_agg("item")
```

这将聚合列中的所有值，我们有

```
array_agg("item") OVER (PARTITION BY "customer_id")
```

这将按customer_id聚合值。

- array_agg_distinct返回给定列中所有不同值的数组。与array_agg不同，此函数确保每个值在结果数组中仅出现一次。
array_agg_distinct返回给定列中所有不同值的数组。与array_agg不同，此函数确保每个值在结果数组中仅出现一次。

- array_join是一个变换函数，将数组中的项目连接成一个字符串，以分隔符分隔。通常，这看起来像：
array_join是一个变换函数，将数组中的项目连接成一个字符串，以分隔符分隔。通常，这看起来像：

```
array_join(<array>, <delimiter>)
```

因此，[milk, bananas, bread]变为"milk, bananas, bread"。

生成的列items_array将如下所示：

| customer_id | items_array |
| --- | --- |
| 123 | eggs, bread |
| 444 | milk, bananas, bread |

## 拆分数组

如果您已经有一个将主键映射到值数组的列，可以使用explode函数将这些值拆分出来，这将为数组中的每个值创建一个新行，因此给定：

| customer_id | items_array |
| --- | --- |
| 123 | eggs, bread |
| 444 | milk, bananas, bread |

打开表达式编辑器并选择“替换列”。代码explode(items_array)将产生如下表格：

| customer_id | items_array |
| --- | --- |
| 123 | eggs |
| 123 | bread |
| 444 | milk |
| 444 | bananas |
| 444 | bread |

请注意，explode函数会删除空值。要保留空值，请使用explode_outer函数。
