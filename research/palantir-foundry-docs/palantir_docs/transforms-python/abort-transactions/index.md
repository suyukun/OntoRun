来源: https://palantir.com/docs/zh/foundry/transforms-python/abort-transactions/

# 中止事务

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 中止事务

Python变换提供支持中止事务，以允许任务成功完成，如果输出数据集未更改（未写入新数据到数据集）。这是通过使用transform装饰器并在TransformOutput对象上调用.abort()来实现的。

如果您需要在某些条件下阻止输出数据集和下游数据集更新，可以使用中止事务。只要您的输出数据集更新，下游数据集将被视为过时（stale），它们将在下次搭建时更新（无论是手动还是通过计划搭建）。这提供了失败搭建的替代方案。这样可以更容易地识别实际出错的情况。

中止的事务将在数据集事务历史中显示为灰色的成功任务。这样您可以一目了然地分辨出成功搭建是否导致了提交事务。

可能需要中止事务的示例：

- 您有一个基于输入数据集内容更新数据集的自定义条件。
- 您的数据集需要强制搭建，因为它不会变得过时。一个例子是从API调用获取数据而不是输入数据集的数据集。
- 您有一个总是按计划更新的数据输出数据集（下面有详细示例）。
在一个总是更新但不总是导致更改输出的数据集之后添加一个使用abort()的验证数据集，通过避免不必要的下游更新来节省计算资源。

## 示例：假定的自定义条件

以下是一个简单的假定示例，我们可能希望确保只有当今天的数据到达我们的输入数据集时才更新数据集。

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
from transforms.api import transform, Input, Output
from datetime import date

@transform(
    holiday_trips=Input('/examples/trips'),
    processed=Output('/examples/trips_processed')
)
def update_daily_trips(holiday_trips, processed):
    holiday_trips_df = holiday_trips.dataframe()  # 获取 holiday_trips 的 DataFrame
    todays_trips_df = holiday_trips_df.filter(holiday_trips_df.trip_date == date.today())  # 过滤出今天的行程数据
    if (todays_trips_df.count() == 0):  # 如果今天没有行程数据
      processed.abort()  # 中止处理
    else:
      processed.write_dataframe(todays_trips_df)  # 写入今天的行程数据到 processed
```

使用if (len(todays_trips_df.head(1)) == 0)通常会比if (todays_trips_df.count() == 0)返回更快的结果，因为前者只检查是否存在至少一行，而不是不必要地计算所有行。

## 中止的事务与忽略的任务有何不同？

当一个任务被标记为“忽略”时，计算不会运行，因为 Foundry 确定任务规范没有过时。而当一个事务被中止时，任务确实运行并成功完成，但是输出数据集保持不变，且没有提交任何事务。

## 中止的事务与增量事务有何关系？

增量变换只使用已提交的事务读取输入和输出的数据集视图。这意味着在执行增量计算时，它们会忽略中止的事务。

当一个事务在增量变换的所有输出上被明确中止时，下次搭建将读取（并因此重新处理）输入，就像中止的事务从未发生过一样，从而能够增量运行。如果事务仅在部分输出上中止，则搭建将无法增量运行。对于具有中止事务的输出，输出任务规范将使用先前的输入事务范围，因为中止的事务被忽略。对于具有已提交事务的输出，输出任务规范将使用当前的输入事务范围。这种输入事务范围的不匹配意味着变换不能再增量运行。

在多输出增量变换中，如果在部分输出上明确中止一个事务，则下次搭建将作为快照运行，增量计算失败检查Provenance records for the previous build are inconsistent。如果设置了require_incremental=True，搭建将失败并出现错误InconsistentProvenanceRecords。这是因为当前的输出视图现在将由不同的输入事务生成。
