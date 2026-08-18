来源: https://palantir.com/docs/zh/foundry/transforms-java/transforms-examples/

# 示例

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 示例

## 高级变换

在Java中，数据变换通常涉及读取、处理和写入DataFrame对象。回忆一下，在Java API中，DataFrame由Dataset<Row>表示。如果您的数据变换依赖于DataFrame对象，可以定义一个高级变换。高级变换接受类型为Dataset<Row>的输入，并期望计算函数返回单个输出，类型为Dataset<Row>。或者，您可以定义一个更通用的低级变换，并显式调用asDataFrame()方法来访问包含输入数据集的Dataset<Row>。

要定义一个高级变换，您需要定义一个计算函数，该函数接受任意数量的类型为Dataset<Row>的输入，并返回一个类型为Dataset<Row>的单个输出。

### 自动注册

以下是如何通过在myproject.datasets包中创建一个名为HighLevelAutoTransform的类来定义变换的示例：

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
package myproject.datasets;

import com.palantir.transforms.lang.java.api.Compute;
import com.palantir.transforms.lang.java.api.Input;
import com.palantir.transforms.lang.java.api.Output;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;

/**
* 这是一个用于自动注册的示例高级转换（Transform）。
*/
public final class HighLevelAutoTransform {

   // 自动注册转换的类包含计算函数和有关输入/输出数据集的信息。
   // 自动注册需要使用 "@Input" 和 "@Output" 注解。
   @Compute
   @Output("/path/to/output/dataset") // 指定输出数据集的路径
   public Dataset<Row> myComputeFunction(@Input("/path/to/input/dataset") Dataset<Row> myInput) {
       // 高级转换的计算函数返回类型为 "Dataset<Row>" 的输出。
       return myInput.limit(10); // 返回输入数据集的前 10 条记录
   }
}
```

在这个代码示例中，HighLevelAutoTransform类被设计为自动注册的转换类。它采用注解机制，用@Input指定输入数据集的路径，@Output指定输出数据集的路径，@Compute标记计算函数。计算函数myComputeFunction对输入数据集进行处理，并返回前 10 条记录。
高级变换支持多个输入和单个输出。因此，每个输入参数必须使用@Input注解（其中包含输入数据集的完整路径），计算函数必须使用@Output注解（其中包含输出数据集的完整路径）。

现在，您可以通过在PipelineDefiner实现中调用Pipeline.autoBindFromPackage()方法，将此Transform添加到项目的Pipeline中：

### 手动注册

以下是如何通过在myproject.datasets包中创建一个名为HighLevelManualFunction的类来定义Transform的示例：

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

import com.palantir.transforms.lang.java.api.Compute;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;

/**
* 这是一个用于手动注册的高级Transform的示例计算函数。
*/
public final class HighLevelManualFunction {

   // 手动注册的Transform类仅包含计算函数。
   @Compute
   public Dataset<Row> myComputeFunction(Dataset<Row> myInput) {
       // 高级Transform的计算函数返回类型为 "Dataset<Row>" 的输出。
       return myInput.limit(10);
   }
}
```

现在，在您的PipelineDefiner实现中，您通过使用HighLevelTransform.builder()完成变换的定义，并通过调用Pipeline.register()将此变换添加到项目的Pipeline中：

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
package myproject;

import com.palantir.transforms.lang.java.api.Pipeline;
import com.palantir.transforms.lang.java.api.PipelineDefiner;

public final class MyPipelineDefiner implements PipelineDefiner {

    @Override
    public void define(Pipeline pipeline) {
        // 这是一个用于高级转换的手动注册示例。
        HighLevelTransform highLevelManualTransform = HighLevelTransform.builder()
                // 传入要使用的计算函数。这里，“HighLevelManualFunction”对应于高级转换的计算函数的类名。
                .computeFunctionInstance(new HighLevelManualFunction())
                // 传入要使用的输入数据集。
                // “myInput”对应于计算函数的输入参数。
                .putParameterToInputAlias("myInput", "/path/to/input/dataset")
                // 传入要使用的输出数据集。
                .returnedAlias("/path/to/output/dataset")
                .build();
        pipeline.register(highLevelManualTransform);
    }
}
```

高层变换支持多个输入和单个输出。每个计算函数的输入数据集应使用putParameterToInputAlias()提供——此方法需要一个对应于计算函数参数的输入名称，后跟输入数据集的完整路径。例如，在上述示例中，“myInput”是在my_compute_function()中的输入参数名称。使用returnedAlias()提供输出数据集的完整路径。

## 低层变换

如果您正在编写依赖于DataFrame对象或文件的数据变换，则可以使用低层变换。

### 自动注册

假设您正在使用自动注册。以下是如何通过在myproject.datasets包中定义一个名为LowLevelAutoTransform的类来创建变换对象的示例：

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
package myproject.datasets;

import com.palantir.transforms.lang.java.api.Compute;
import com.palantir.transforms.lang.java.api.FoundryInput;
import com.palantir.transforms.lang.java.api.FoundryOutput;
import com.palantir.transforms.lang.java.api.Input;
import com.palantir.transforms.lang.java.api.Output;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;

/**
 * 这是一个用于自动注册的低级Transform示例。
 */
public final class LowLevelAutoTransform {

   // 自动注册Transform的类包含compute函数和有关输入/输出数据集的信息。
   // 自动注册需要使用"@Input"和"@Output"注解。
   @Compute
   public void myComputeFunction(
           @Input("/path/to/input/dataset") FoundryInput myInput,
           @Output("/path/to/output/dataset") FoundryOutput myOutput) {
       Dataset<Row> limited = myInput.asDataFrame().read().limit(10);
       // 低级Transform的compute函数将结果写入输出数据集，而不是返回输出。
       myOutput.getDataFrameWriter(limited).write();
   }
}
```

### 代码说明

- 包和导入：代码位于myproject.datasets包中，并导入了Palantir Foundry的相关API和Spark SQL的类。
包和导入：代码位于myproject.datasets包中，并导入了Palantir Foundry的相关API和Spark SQL的类。

- 类注释：LowLevelAutoTransform类是一个低级的Transform示例，旨在展示自动注册功能。
类注释：LowLevelAutoTransform类是一个低级的Transform示例，旨在展示自动注册功能。

- @Compute注解：标记myComputeFunction方法为计算函数。
@Compute注解：标记myComputeFunction方法为计算函数。

- 输入输出注解：@Input和@Output注解用于指定输入和输出数据集的路径。这是自动注册所需的。
输入输出注解：@Input和@Output注解用于指定输入和输出数据集的路径。这是自动注册所需的。

- 数据处理：使用Spark SQL的Dataset<Row>来读取输入数据集，并限制结果为前10行。
数据处理：使用Spark SQL的Dataset<Row>来读取输入数据集，并限制结果为前10行。

- 写入输出：通过FoundryOutput的getDataFrameWriter方法，将处理后的数据写入指定的输出数据集路径。
低级变换支持多个输入和输出数据集。因此，每个输入参数必须使用@Input进行注解（其中包含输入数据集的完整路径），每个输出参数必须使用@Output进行注解（其中包含输出数据集的完整路径）。
写入输出：通过FoundryOutput的getDataFrameWriter方法，将处理后的数据写入指定的输出数据集路径。
低级变换支持多个输入和输出数据集。因此，每个输入参数必须使用@Input进行注解（其中包含输入数据集的完整路径），每个输出参数必须使用@Output进行注解（其中包含输出数据集的完整路径）。

现在，您可以通过在PipelineDefiner实现中调用Pipeline.autoBindFromPackage()方法，将此Transform添加到项目的Pipeline中：

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
package myproject;

import com.palantir.transforms.lang.java.api.Pipeline;
import com.palantir.transforms.lang.java.api.PipelineDefiner;

public final class MyPipelineDefiner implements PipelineDefiner {

  @Override
  public void define(Pipeline pipeline) {
    // 提供包含任何要自动注册的转换的Java包。
    // 这里自动绑定来自“myproject.datasets”包中的转换。
    pipeline.autoBindFromPackage("myproject.datasets");
  }
}
```

### 手动注册

现在，假设您正在使用手动注册。在这种情况下，您将定义一个仅包含计算函数的类。以下是在myproject.datasets包中定义一个名为LowLevelManualFunction类的示例：

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
package myproject.datasets;

import com.palantir.transforms.lang.java.api.Compute;
import com.palantir.transforms.lang.java.api.FoundryInput;
import com.palantir.transforms.lang.java.api.FoundryOutput;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;

/**
* 这是一个用于手动注册的低级 Transform 示例计算函数。
*/
public final class LowLevelManualFunction {

    // 手动注册的 Transform 类仅包含计算函数。
    @Compute
    public void myComputeFunction(FoundryInput myInput, FoundryOutput myOutput) {
        Dataset<Row> limited = myInput.asDataFrame().read().limit(10);
        // 低级 Transform 的计算函数将结果写入输出数据集，
        // 而不是返回输出结果。
        myOutput.getDataFrameWriter(limited).write();
    }
}
```

现在，在您的PipelineDefiner实现中，您可以使用LowLevelTransform.builder()创建实际的Transform对象，并通过调用Pipeline.register()将此Transform添加到项目的Pipeline中：

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
package myproject;

import com.palantir.transforms.lang.java.api.Pipeline;
import com.palantir.transforms.lang.java.api.PipelineDefiner;

public final class MyPipelineDefiner implements PipelineDefiner {

    @Override
    public void define(Pipeline pipeline) {
        // 这是一个低级转换（Transform）的示例手动注册。
        LowLevelTransform lowLevelManualTransform = LowLevelTransform.builder()
                // 传入要使用的计算函数。这里，“LowLevelManualFunction”对应于低级转换的计算函数的类名。
                .computeFunctionInstance(new LowLevelManualFunction())
                // 传入要使用的输入数据集。
                // “myInput”对应于计算函数的输入参数。
                .putParameterToInputAlias("myInput", "/path/to/input/dataset")
                // 传入要使用的输出数据集。
                // “myOutput”对应于计算函数的输入参数。
                .putParameterToOutputAlias("myOutput", "/path/to/output/dataset")
                .build();
        pipeline.register(lowLevelManualTransform);
    }
}
```

低级变换支持多个输入和输出数据集。每个用于计算函数的输入数据集应使用putParameterToInputAlias()提供，而每个输出数据集应使用putParameterToOutputAlias()提供。这些方法需要一个对应于计算函数参数的输入/输出名称以及输入/输出数据集的完整路径。例如，在上述示例中，“myInput”和“myOutput”是my_compute_function()中的输入参数名称。请记住，低级变换的计算函数写入输出数据集，并且不返回值。这就是为什么您的输入/输出数据集作为参数传递给计算函数。
