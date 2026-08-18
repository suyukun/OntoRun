来源: https://palantir.com/docs/zh/foundry/transforms-python/pyspark-window/

# 窗口

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 窗口

窗口函数允许用户在不丢失未参与聚合的列的情况下，将聚合和其他值附加到数据帧中的行。

## 激励示例

假设您有一个transactions数据集，其中包含每个customer的交易记录，并且您想计算每个客户的average_spend并将其附加到每个交易中。要使用合并执行此操作，您需要执行一个分组以获得平均值，然后合并回原始表：

```
Copied!1
2
3
4
5
6
averages = transactions\
	.groupBy('customer')\
	.agg(
		F.avg('spend').alias('average_spend')  # 计算每个客户的平均消费，并命名为 'average_spend'
	)
transactions = transactions.join(averages, ['customer'], 'left_outer')  # 将平均消费数据通过左外连接合并回原始交易数据
```

如果您想获取最大支出，此逻辑会变得更加复杂，因为现在您必须计算最大值而不是平均值，然后再合并回最大值：

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
maximums = transactions\
	.groupBy('customer')\
	.max(
		F.avg('spend').alias('max_spend')
	)
# 计算每位顾客的平均支出，并找到每位顾客的最大平均支出，结果保存在 maximums 中

transactions = transactions\
	.join(
		averages,
		(transactions.customer == maximums.customer) &\
		(transactions.spend == maximums.max_spend),
		'left_outer'
	).drop(maximums.customer)
# 将 transactions 数据与 maximums 数据进行左外连接，条件是顾客相同且支出等于最大支出，连接后删除 maximums 中的顾客列
```

然而，窗口函数允许您通过先定义窗口，然后计算“在”窗口上的聚合来简化此代码：

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
from pyspark.sql.window import Window

# 定义一个窗口函数
window = Window()\
	.partitionBy('customer')\  # 按照'customer'进行分组
	.orderBy('spend')          # 按照'spend'进行排序

# 为每个事务添加新的列
transactions = transactions\
	.withColumn('average_spend', F.avg('spend').over(window))  # 计算每个顾客的平均消费
	.withColumn('max_spend', F.max('spend').over(window))      # 计算每个顾客的最大消费
```

此外，还有一些只能在窗口中使用的函数。这些称为窗口函数，将在下一节中描述。

## 窗口函数

#### dense_rank()

#### lag(col, count=1, default=None)

#### lead(col, count=1, default=None)

#### ntile(n)

#### percent_rank()

#### rank()

#### row_number()

#### window(timeColumn, windowDuration, slideDuration=None, startTime=None)
