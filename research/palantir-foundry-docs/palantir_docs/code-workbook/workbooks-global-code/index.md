来源: https://palantir.com/docs/zh/foundry/code-workbook/workbooks-global-code/

# 全局代码

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 全局代码

全局代码窗格位于工作簿界面的右侧，允许你定义的变量和函数在该语言的所有代码变换中都可以使用。例如，你可以使用全局代码定义将在多个变换中使用的常量，或定义你希望重复使用的辅助函数。

## 示例

在此示例中，我们将基于titanic_dataset编写一个简单的函数，该函数将接收乘客的年龄并返回其年龄段。

首先，在页面右侧打开Python全局代码面板，如下图所示：

一旦打开全局代码面板，将以下代码复制粘贴到面板中：

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
def return_age_bracket(age):
  if age is None:
    return 'Not specified'  # 未指定
  elif (age <= 12):
    return '12 and under'  # 12岁及以下
  elif (age >= 13 and age < 19):
    return 'Between 13 and 19'  # 13到19岁之间
  elif (age >= 19 and age < 65):
    return 'Between 19 and 65'  # 19到65岁之间
  elif (age >= 65):
    return '65 and over'  # 65岁及以上
  else: return 'N/A'  # 不适用
```

要使用此全局函数，请创建一个新的Python变换，来源于titanic_dataset，并将以下代码粘贴到变换中：

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
def passengers_by_age_bracket_udf(titanic_dataset):
  from pyspark.sql.functions import udf

  input_df = titanic_dataset

  # 定义一个用户自定义函数(UDF)，用于根据年龄返回年龄段
  age_bracket_udf = udf(return_age_bracket)

  # 使用withColumn方法将新的年龄段列添加到DataFrame中
  output_df = input_df.withColumn("age_bracket", age_bracket_udf(input_df.Age))
  # 选择需要的列，即乘客的名字和他们的年龄段
  output_df = output_df.select(output_df.Name, output_df.age_bracket)

  return output_df
```

这段代码定义了一个函数passengers_by_age_bracket_udf，它接收一个Titanic数据集，并使用用户自定义函数(UDF)根据乘客的年龄为每个乘客添加一个新的列age_bracket，然后返回只有乘客名字和年龄段的DataFrame。
现在运行代码。您将看到以下输出：

由于用户定义函数 (UDF)，特别是带有循环的函数，可能经常效率低下，因此此代码可能需要一些时间来运行。使用全局定义的函数并不总是最佳实践。在此示例中，pyspark.functions提供了一种更简单的方法：when((condition), result).otherwise(result)。

让我们尝试在不使用 UDF 的情况下获得与上面相同的结果：

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
def passengers_by_age_bracket(titanic_dataset):
  from pyspark.sql import functions as F

  input_df = titanic_dataset
  output_df = input_df.withColumn("age_bracket",
                                  F.when(input_df.Age.isNull(), 'Not specified')  # 如果年龄为空，标记为 'Not specified'
                                   .when(input_df.Age <= 12, '12 and under')  # 如果年龄小于等于12岁，标记为 '12 and under'
                                   .when((input_df.Age >= 13) & (input_df.Age < 19), 'Between 13 and 19')  # 如果年龄在13到19岁之间，标记为 'Between 13 and 19'
                                   .when((input_df.Age >= 19) & (input_df.Age < 65), 'Between 19 and 65')  # 如果年龄在19到65岁之间，标记为 'Between 19 and 65'
                                   .when(input_df.Age >= 65, '65 and over')  # 如果年龄大于等于65岁，标记为 '65 and over'
                                   .otherwise('N/A'))  # 如果不符合以上条件，标记为 'N/A'
  output_df = output_df.select('Name', 'age_bracket')  # 选择输出的列为 'Name' 和 'age_bracket'

  return output_df
```

这段代码使用 PySpark 对 Titanic 数据集中的乘客进行年龄分段。通过withColumn方法，代码创建了一个新的列age_bracket，该列根据乘客年龄的不同范围进行分类。最后，代码返回只包含乘客姓名和年龄段的 DataFrame。
在大多数情况下，上述变换应在几秒钟内运行，而使用 UDF 则需要几分钟。

## 关于可重复性的注意事项

请注意，为了确保结果具有可重复性，全局代码中的可变变量和函数不会传播到其他变换中。例如，在 Python 中，如果您在全局代码中定义一个列表，如下所示：

```
Copied!1
my_list = [1,2,3,4]  # 定义一个包含四个整数元素的列表
```

然后在您的变换中更新列表：

```
Copied!1
2
3
4
5
def my_transform(input_df):
    # 尝试在函数内部访问未定义的变量 my_list，会导致 NameError
    # 可以考虑在函数内部定义 my_list 或者将其作为参数传入
    my_list.append(5)
    print(my_list)
```

运行my_transform将打印[1,2,3,4,5]，但其他变换仍将接收到[1,2,3,4]的值。
