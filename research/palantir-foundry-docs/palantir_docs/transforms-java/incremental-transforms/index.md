来源: https://palantir.com/docs/zh/foundry/transforms-java/incremental-transforms/

# 增量变换

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 增量变换

增量计算是一个高级功能。确保您在使用此功能之前了解用户指南的其他部分。

到目前为止在用户指南中展示的变换每次运行时都会重新计算它们的整个输出数据集。这可能导致很多不必要的工作。考虑以下示例：

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
package myproject.datasets;

import com.palantir.transforms.lang.java.api.*;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;

public final class FilterTransform {

   @Compute
   public void myComputeFunction(
           @Input("/examples/students_hair_eye_color") FoundryInput myInput,
           @Output("/examples/students_hair_eye_color_filtered") FoundryOutput myOutput) {
       // 读取输入数据集并转换为DataFrame
       Dataset<Row> inputDf = myInput.asDataFrame().read();
       // 过滤出眼睛颜色为棕色的数据，并写入输出
       myOutput.getDataFrameWriter(inputDf.filter("eye = 'Brown'")).write();
   }
}
```

该代码片段定义了一个名为FilterTransform的类，该类包含一个计算函数myComputeFunction。这个函数从指定路径读取输入数据集，将其转换为DataFrame，并过滤出眼睛颜色为棕色的记录，最后将过滤后的结果写入到指定的输出路径。
如果在/examples/students_hair_eye_color输入数据集中添加了任何新数据，filter()将对整个输入进行操作，而不仅仅是对添加的新数据进行操作。这在计算资源和时间上是浪费的。

如果一个变换能够了解其搭建历史，它就可以更智能地计算其输出。更具体地说，它可以利用对输入所做的更改来修改输出数据集。这种在重新实现表时使用已实现数据的过程称为增量计算。没有增量计算，输出数据集总是被变换的最新输出替换。

让我们回到上面显示的变换示例。变换对students数据集执行filter()操作，以输出棕色头发的学生。有了增量计算，如果有两个新学生的数据被追加到students中，变换可以利用其搭建历史的信息，仅将新的棕色头发的学生追加到输出中：

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
RAW                              DERIVED
+---+-----+-----+                  +---+-----+-----+
| id| hair|  eye|                  | id| hair|  eye|
+---+-----+-----+     Build 1      +---+-----+-----+
| 17|Black|Brown|    --------->    | 18|Brown|Brown|  // 在第一次构建中，选择了id为18的数据
| 18|Brown|Brown|                  +---+-----+-----+
| 19|  Red|Brown|
+---+-----+-----+                            ...
   ...
+---+-----+-----+     Build 2      +---+-----+-----+
| 20|Brown|Brown|    --------->    | 20|Brown|Brown|  // 在第二次构建中，选择了id为20的数据
| 21|Black|Blue |                  +---+-----+-----+
+---+-----+-----+
```

在这个示例中，原始数据（RAW）经过两次构建（Build 1 和 Build 2）后，产生了派生数据集（DERIVED）。每次构建都会选择特定的记录并将其包括在派生数据集中。首次构建选择了id为 18 的记录，而第二次构建选择了id为 20 的记录。

## 编写增量变换

我们将逐步指导您如何使用transforms-java编写增量变换。与transforms-python不同，transforms-java不使用注解来自动验证增量并以增量方式应用变换。在Java中编写增量变换的过程更多地由用户直接控制，用户可以明确决定在何种情况下变换应以增量方式进行，何时不进行。通过解释输入数据集的更改方式，用户可以决定是以增量方式还是以快照方式更新输出数据集。

### 解释您的输入

第一步涉及对输入的解释。输入数据集可能以多种方式被修改，我们只能在某些特定情况下应用增量变换。DataFrameModificationType（或FilesModificationType）表达了数据集可以被修改的不同方式。不同模式包括：

- APPENDED
- UPDATED
- NEW_VIEW
- UNCHANGED
基于输入的更改方式，我们可以决定从输入数据集中读取什么以及向输出数据集写入什么。

### 读取输入

了解输入的修改方式可以让我们相应地读取它。如果一个事务仅追加了数据，我们可以安全地以增量方式操作并仅读取已修改的内容。如果我们对输入数据集进行了更改，包括修改了已存在的行，我们可能需要重新读取整个视图。Transforms-JavaAPI 通过readForRange()方法支持输入数据集的不同读取模式。
ReadRange 公开了可能的读取范围。不同模式包括：

- UNPROCESSED
- PROCESSED
- ENTIRE_VIEW
通过解释输入修改类型，我们可以决定如何读取数据，如下例所示。

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
private ReadRange getReadRange(FoundryInput input) {
     switch (input.asDataFrame().modificationType()) {
         case UNCHANGED:
             // 如果输入数据集没有变化，则只读取未处理的部分
             LOG.info("No changes in input dataset, read only unprocessed");
             return ReadRange.UNPROCESSED;
         case APPENDED:
             // 如果输入数据集仅追加了数据，则只读取未处理的部分
             LOG.info("Append-only changes in input dataset, read only unprocessed");
             return ReadRange.UNPROCESSED;
         case UPDATED:
             // 如果输入数据集有更新，则读取整个视图
             LOG.info("Update-type changes in input dataset, read entire view");
             return ReadRange.ENTIRE_VIEW;
         case NEW_VIEW:
             // 如果输入数据集是新的视图，则读取整个视图
             LOG.info("New view in input dataset, read entire view");
             return ReadRange.ENTIRE_VIEW;
         default:
             // 如果遇到未知的修改类型，则抛出异常
             throw new IllegalArgumentException("Unknown ModificationType for input dataset "
                 + input.asDataFrame().modificationType());
     }
}
```

接下来我们可以相应地修改我们的compute方法。

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
@Compute
public void myComputeFunction(
        @Input("/examples/students_hair_eye_color") FoundryInput myInput,
        @Output("/examples/students_hair_eye_color_filtered") FoundryOutput myOutput) {
    // 从输入中读取数据集，并将其转换为DataFrame格式
    Dataset<Row> inputDf = myInput.asDataFrame().readForRange(getReadRange(myInput));
    // 过滤出眼睛颜色为棕色的记录，并写入输出
    myOutput.getDataFrameWriter(inputDf.filter("eye = 'Brown'")).write();
}
```

此时我们仅在读取输入数据集的不同部分，但在输出数据集上没有进行不同的操作。运行本示例中的代码到此步骤时，无论读取输入的哪个部分，都会在输出上产生一个快照事务。在应用增量变换之前，请继续进行本教程，了解如何正确修改输出数据集。

### 变换数据

在此步骤中，用户需要应用所需的数据变换。请记住，取决于输入的更改，读取的数据会有所不同。在我们的例子中，变换是一个简单的筛选棕色眼睛的操作，我们可以将其隔离为：

```
Copied!1
inputDf = inputDf.filter("eye = 'Brown'"); // 过滤条件：选择眼睛颜色为棕色的记录
```

### 写入输出

一旦我们解释了输入数据集中的修改，读取了所需的输入部分，并根据我们的变换逻辑变换了数据，我们就可以相应地写入我们的输出。WriteMode 提供了不同的写入模式。不同的模式包括：

- SNAPSHOT
- UPDATE
例如，在我们的情况下，我们可以根据输入的修改类型选择输出类型。

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
private WriteMode getWriteMode(FoundryInput input) {
     // 根据输入的修改类型确定写入模式
     switch (input.asDataFrame().modificationType()) {
         case UNCHANGED:
             // 如果输入数据集没有变化，使用更新模式写入
             LOG.info("No changes in input dataset, writing in update mode");
             return WriteMode.UPDATE;
         case APPENDED:
             // 如果输入数据集仅有追加变化，使用更新模式写入
             LOG.info("Append-only changes in input dataset, writing in update mode");
             return WriteMode.UPDATE;
         case UPDATED:
             // 如果输入数据集有更新变化，使用快照模式写入
             LOG.info("Update-type changes in input dataset, writing in snapshot mode");
             return WriteMode.SNAPSHOT;
         case NEW_VIEW:
             // 如果输入数据集是一个新视图，使用快照模式写入
             LOG.info("new view in input dataset, writing in snapshot mode");
             return WriteMode.SNAPSHOT;
         default:
             // 如果输入的数据集的修改类型未知，抛出异常
             throw new IllegalArgumentException("Unknown ModificationType for input dataset " + input.asDataFrame().modificationType());
     }
 }
```

不要混淆WriteMode.UPDATE和DataFrameModificationType.UPDATED。前者会导致输出数据集的增量修改，并将导致下游数据集的DataFrameModificationType.APPENDED。后者是对输入数据集的修改，包括追加和现有行的修改。

最后，可以更改write()函数以包含写入模式：

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
@Compute
public void myComputeFunction(
        @Input("/examples/students_hair_eye_color") FoundryInput myInput,
        @Output("/examples/students_hair_eye_color_filtered") FoundryOutput myOutput) {
    // 将输入数据转换为DataFrame，并根据范围读取数据
    Dataset<Row> inputDf = myInput.asDataFrame().readForRange(getReadRange(myInput));
    // 过滤眼睛颜色为“Brown”的记录，并将结果写入输出
    myOutput.getDataFrameWriter(inputDf.filter("eye = 'Brown'")).write(getWriteMode(myInput));
}
```

### 整合所有内容

我们可以通过将各个部分组合起来搭建一个简单的增量筛选变换。

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
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
package myproject.datasets;

import com.palantir.transforms.lang.java.api.*;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public final class FilterTransform {

    private static final Logger LOG = LoggerFactory.getLogger(FilterTransform.class);

    // 计算函数
    @Compute
    public void myComputeFunction(
            @Input("/examples/students_hair_eye_color") FoundryInput myInput, // 输入数据集
            @Output("/examples/students_hair_eye_color_filtered") FoundryOutput myOutput) { // 输出数据集
        // 将输入数据集转换为DataFrame并读取指定范围的数据
        Dataset<Row> inputDf = myInput.asDataFrame().readForRange(getReadRange(myInput));
        // 过滤出眼睛颜色为棕色的数据，并写入输出数据集
        myOutput.getDataFrameWriter(inputDf.filter("eye = 'Brown'")).write(getWriteMode(myInput));
    }

    // 获取读取范围，根据输入数据集的修改类型决定读取策略
    private ReadRange getReadRange(FoundryInput input) {
        switch (input.asDataFrame().modificationType()) {
            case UNCHANGED:
                LOG.info("No changes in input dataset, read only unprocessed");
                return ReadRange.UNPROCESSED; // 无变化，仅读取未处理的部分
            case APPENDED:
                LOG.info("Append-only changes in input dataset, read only unprocessed");
                return ReadRange.UNPROCESSED; // 仅追加变化，仅读取未处理的部分
            case UPDATED:
                LOG.info("Update-type changes in input dataset, read entire view");
                return ReadRange.ENTIRE_VIEW; // 更新类型变化，读取整个视图
            case NEW_VIEW:
                LOG.info("New view in input dataset, read entire view");
                return ReadRange.ENTIRE_VIEW; // 新视图，读取整个视图
            default:
                throw new IllegalArgumentException("Unknown ModificationType for input dataset "
                    + input.asDataFrame().modificationType()); // 未知的修改类型
        }
    }

    // 获取写入模式，根据输入数据集的修改类型决定写入策略
    private WriteMode getWriteMode(FoundryInput input) {
        switch (input.asDataFrame().modificationType()) {
            case UNCHANGED:
                LOG.info("No changes in input dataset, writing in update mode");
                return WriteMode.UPDATE; // 无变化，更新模式写入
            case APPENDED:
                LOG.info("Append-only changes in input dataset, writing in update mode");
                return WriteMode.UPDATE; // 仅追加变化，更新模式写入
            case UPDATED:
                LOG.info("Update-type changes in input dataset, writing in snapshot mode");
                return WriteMode.SNAPSHOT; // 更新类型变化，快照模式写入
            case NEW_VIEW:
                LOG.info("new view in input dataset, writing in snapshot mode");
                return WriteMode.SNAPSHOT; // 新视图，快照模式写入
            default:
                throw new IllegalArgumentException("Unknown ModificationType for input dataset " + input.asDataFrame().modificationType()); // 未知的修改类型
        }
    }
}
```

如上所述，我们评估输入修改类型并相应地读取输入。然后我们决定是增量更新输出数据集还是启动一个新的快照事务。

## 最佳实践

### 在快照和增量之间切换

假设您希望主要运行增量变换，但有时需要重新运行数据集的快照。

为了避免手动硬编码所需结果，您可以添加一个新的输入，以便在此输入更改时使用SNAPSHOT写入模式生成输出。这个新输入实际上将作为快照触发数据集。请注意，您需要根据这个新快照触发数据集的修改类型来调整变换的其他输入的读取范围。

也可以通过创建一个没有来源的空追加事务来强制外部快照。然而，transforms-java不提供此类功能，因此超出了本指南的范围。

## 高级特性

本节中的高级特性如果使用不当可能会产生严重的负面影响。如果您不完全确定其影响，请不要使用这些特性。如果运行时没有适当的谨慎和小心，存在产生不良后果的高风险。如有任何疑问，请联系您的Palantir代表。

高级特性通常包含在@Compute函数顶部的注释中。然而，如果您的变换是手动注册的，您将需要将属性添加到Transform Builder中。

### 忽略增量删除

如果增量搭建依赖于无限增长的仅追加数据集，并且没有足够的磁盘空间容纳这种增长，则可能需要删除部分上游数据集。
然而，这可能会破坏增量性，因为原始数据集的更改将不会导致APPENDED修改类型。IncrementalOptions.IGNORE_INCREMENTAL_DELETES将避免这种情况，并且不会将上游数据集中的删除视为破坏性更改。

只有在低级变换中才可以忽略增量删除。

```
Copied!1
2
3
4
5
6
    @Compute
    @UseIncrementalOptions(IncrementalOptions.IGNORE_INCREMENTAL_DELETES)
    public void myComputeFunction(
           @Input("/Users/admin/students_data") FoundryInput myInput, // 输入数据路径
           @Output("/Users/admin/students_data_filtered") FoundryOutput myOutput) { // 输出数据路径
    ...
```

```
Copied!1
2
3
4
5
6
    LowLevelTransform lowLevelManualTransform = LowLevelTransform.builder()
               .computeFunctionInstance(new MyLowLevelManualFunction()) // 创建一个自定义的低级计算函数实例
               .putParameterToInputAlias("myInput", "/path/to/input/dataset") // 设置输入数据集路径的别名
               .putParameterToOutputAlias("myOutput", "/path/to/output/dataset") // 设置输出数据集路径的别名
               .ignoreIncrementalDeletes(true) // 忽略增量删除操作
               .build(); // 构建LowLevelTransform对象
```

### 忽略模式更改

请注意，当输入数据集的模式修改与增量变换结合使用时，可能会产生意外后果。

请阅读以下所有文档，确保您了解所有潜在影响后再使用此功能。

仅在低级变换中可以忽略模式更改。

如果增量搭建所依赖的数据集的模式发生更改，该更改将导致DataFrameModificationType.NEW_VIEW，可能破坏增量性。

然而，如果设置了IncrementalOptions.USE_SCHEMA_MODIFICATION_TYPE选项，则模式更改不会导致新视图。
相反，输入数据集中的模式更改将被解释为DataFrameModificationType.UNCHANGED，并将设置一个模式更改类型标志SchemaModificationType.NEW_SCHEMA，允许用户明确处理此特殊情况。

```
Copied!1
2
3
4
5
6
7
        @Compute
        @UseIncrementalOptions(IncrementalOptions.USE_SCHEMA_MODIFICATION_TYPE)
        public void myComputeFunction(
               @Input("/Users/admin/students_data") FoundryInput myInput, // 输入数据路径
               @Output("/Users/admin/students_data_filtered") FoundryOutput myOutput) { // 输出数据路径
        ...
        }
```

以上代码是一个Java方法的定义，带有注解@Compute，表示这是一个计算函数。@UseIncrementalOptions注解指定使用增量选项，可能与数据的模式变化相关。myComputeFunction方法接受一个输入和一个输出，分别通过@Input和@Output注解指定数据路径。
如果您的变换是手动注册的，请将属性添加到构建器中，如以下代码块所示。

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
    // 创建一个LowLevelTransform对象，使用建造者模式进行配置
    LowLevelTransform lowLevelManualTransform = LowLevelTransform.builder()
               // 设置计算函数实例
               .computeFunctionInstance(new MyLowLevelManualFunction())
               // 设置输入数据集的参数别名
               .putParameterToInputAlias("myInput", "/path/to/input/dataset")
               // 设置输出数据集的参数别名
               .putParameterToOutputAlias("myOutput", "/path/to/output/dataset")
               // 启用模式修改类型
               .useSchemaModificationType(true)
               // 构建LowLevelTransform对象
               .build();
```

与变换相关的搭建将会成功或失败，取决于变换如何依赖于输入数据集。更确切地说，如果变换依赖于涉及模式更改的列，对这些列的修改将导致增量变换失败。在这些情况下，需要一个新的快照才能再次使用增量变换。

如果变换依赖于某个特定列：

- 它包含明确依赖于该列的修改（例如，如果我们有filter("eye = 'Brown'")，并且在原始数据集中将列eye重命名或删除，那么如果我们重新触发FilterTransform，增量更新将失败）。
- 修改后的列出现在输出数据集中（例如，如果我们在示例原始数据集中删除列hair，我们的FilterTransform将失败）。
如果变换不依赖于模式更改，则增量搭建将会成功。

例如，如果我们首先在变换中为id和eye添加一个select语句，并从原始数据集中触发一个初始快照搭建，然后在原始数据集中删除列hair，增量搭建将会成功，模式更改不会对增量变换产生任何影响。在模式的附加更改（例如添加新列）的情况下，搭建也将始终成功。
