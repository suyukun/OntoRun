来源: https://palantir.com/docs/zh/foundry/transforms-python/incremental-overview/

# 概述

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 概述

增量计算是一种执行变换以生成输出数据集的高效方法。通过利用变换的搭建历史，增量计算避免了每次运行变换时重新计算整个输出数据集的需求。

有关如何创建和管理增量管道的端到端指导，请参阅搭建管道部分。

## 示例：非增量和增量变换

在本节中，我们通过首先考虑一个不使用增量变换的代码示例来研究增量变换的好处：

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
from transforms.api import transform, Input, Output

@transform(
    students=Input('/examples/students_hair_eye_color'),
    processed=Output('/examples/hair_eye_color_processed')
)
def filter_hair_color(students, processed):
    # type: (TransformInput, TransformOutput) -> None
    students_df = students.dataframe()

    # 这个方法效率不高，因为过滤操作是在整个输入数据上执行的，而不是只在新的数据上执行
    processed.write_dataframe(students_df.filter(students_df.hair == 'Brown'))
```

如果在/examples/students_hair_eye_color输入数据集中添加了任何新数据，filter()将对整个输入执行，而不仅仅是对添加到输入中的新数据执行。这既浪费计算资源又浪费时间。

如果一个变换能够了解其搭建历史，就可以更智能地计算其输出。更具体地说，它可以利用对输入所做的更改来修改输出数据集。这个在重新物化表时使用已经物化的数据的过程称为增量计算。没有增量计算，输出数据集总是被变换的最新输出替换。

让我们回到上面显示的变换示例。变换对students数据集执行filter()以写出棕色头发的学生。通过增量计算，如果有关于两个新学生的数据追加到students中，变换可以利用其搭建历史信息仅将新的棕色头发学生追加到输出中：

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
+---+-----+-----+------+                  +---+-----+-----+------+
| id| hair|  eye|   sex|                  | id| hair|  eye|   sex|
+---+-----+-----+------+     Build 1      +---+-----+-----+------+
| 17|Black|Green|Female|    --------->    | 18|Brown|Green|Female|
| 18|Brown|Green|Female|                  +---+-----+-----+------+
| 19|  Red|Black|Female|
+---+-----+-----+------+
        ...                                         ...
+---+-----+-----+------+     Build 2      +---+-----+-----+------+
| 20|Brown|Amber|Female|    --------->    | 20|Brown|Amber|Female|
| 21|Black|Blue |Male  |                  +---+-----+-----+------+
+---+-----+-----+------+
```

这段代码展示了两个数据集的构建过程。其中：

- Build 1中，数据集的转换操作将某些行进行了替换。例如，id为 17 的行被id为 18 的行替换。
- Build 2中，数据集保持不变，没有行替换。
这可能用于说明数据处理或数据清理的步骤。
因此，上述示例变换可以使用增量逻辑并通过以下语法重写：

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
from transforms.api import transform, incremental, Input, Output

@incremental()
@transform(
    students=Input('/examples/students_hair_eye_color'),
    processed=Output('/examples/hair_eye_color_processed')
)
def filter_hair_color(students, processed):
    # type: (IncrementalTransformInput, IncrementalTransformOutput) -> None
    # 从输入数据集中获取增量的学生数据
    students_df = students.dataframe('added')
    # 过滤出头发颜色为棕色的学生，并写入输出数据集
    processed.write_dataframe(students_df.filter(students_df.hair == 'Brown'))
```

有关增量变换和@incremental装饰器的更多信息，请访问增量变换参考。

当其中一个数据集是完全读取的参考表，而另一个是增量读取的增量数据集时，进行合并是安全的。然而，增量读取参与合并的两个数据集需要特殊处理，参见示例利用增量变换合并大型数据集。

### 与轻量级变换一起使用

增量计算现已支持轻量级变换。查看下面的示例轻量级增量变换。
