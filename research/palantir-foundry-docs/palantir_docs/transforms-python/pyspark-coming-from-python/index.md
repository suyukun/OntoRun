来源: https://palantir.com/docs/zh/foundry/transforms-python/pyspark-coming-from-python/

# 来自 Python

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 来自 Python

如果您有 Python 的经验，您可能习惯于以过程性或命令性的方式处理数据：提供将数据从一个状态变换到另一个状态所需的确切步骤。与此相反，SQL 是声明性的，这意味着您描述您所寻找的结果，软件会处理生成该结果。PySpark 是一个用于通过 Python 方便地搭建复杂 SQL 查询的库：它试图在 Python 的过程语法中提供对 SQL 概念的访问。这利用了 Python 的灵活性、SQL 的便利性和 Spark 的并行处理能力。

将您的概念模型发展到从整体上思考数据集，并基于列而不是行处理数据会很有帮助。我们不是直接使用变量、列表、字典、循环等操作数据，而是以 DataFrame 为单位工作。这意味着我们将不再使用 Python 的原语和操作符，而是使用 Spark 内置的在分布式环境中处理 DataFrame 的操作符。

### 示例

假设您在 Python 中有一个数字列表，并且您想为每个数字加上5。

```
Copied!1
2
3
4
5
6
7
old_list = [1,2,3]
new_list = []
for i in old_list:
    added_number = i + 5  # 将列表中的每个元素加5
    new_list.append(added_number)  # 将结果添加到新的列表中
print new_list
>>> [6,7,8]  # 输出结果为每个元素加5后的新列表
```

在PySpark中，这将类似于

```
Copied!1
2
3
# 创建一个新的数据帧，在原数据帧的基础上添加一列 'added_number'
# 该列的值是原数据帧中 'number' 列的值加上 5
new_dataframe = old_dataframe.withColumn('added_number', old_dataframe.number + 5)
```

new_dataframe现在代表以下内容，

| number | added_number |
| --- | --- |
| 1 | 6 |
| 2 | 7 |
| 3 | 8 |

有趣的是，DataFrameObject 实际上并不在内存中包含您的数据：它是对 Spark 中数据的引用。DataFrame 是惰性计算的。当我们要求 Spark 实际上对 DataFrame 执行某些操作时（例如将其写入 Foundry），它会遍历我们创建的所有中间 DataFrame，生成一个优化的查询计划，并在 Spark 集群上执行它。这使得 Foundry 能够扩展到超出单台服务器或您的笔记本电脑内存所能容纳的数据量。
