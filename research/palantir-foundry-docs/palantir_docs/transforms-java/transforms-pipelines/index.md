来源: https://palantir.com/docs/zh/foundry/transforms-java/transforms-pipelines/

# 变换和管道

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 变换和管道

所有变换当前默认以事务类型SNAPSHOT。

Transform是描述如何计算数据集的描述。它描述了以下内容：

- 输入和输出数据集，
- 用于将输入数据集变换为输出数据集的代码（我们将其称为计算函数），以及
- 任何其他配置（例如在运行时使用的自定义变换配置文件）。
输入和输出数据集，以及变换代码，在Transform对象中指定，然后注册到Pipeline。如何定义Transform取决于两个因素：

- 您是在定义高层次还是低层次变换，以及
- 您是使用自动还是手动注册来将变换添加到项目的Pipeline中。
### 变换类型

数据变换可以用DataFrame对象以及文件来表达。这些DataFrame对象仅仅指代常规的Spark DataFrames。在Spark Scala/Java API中，DataFrame由Dataset表示。因此，作为用户，您直接与数据变换代码中的Dataset对象交互。
有关使用Spark的更多信息，您可以参考在线提供的Java API for Spark 文档 ↗。

对于依赖于DataFrame对象的变换，您可以：

- 定义一个高层次变换，支持输入和输出类型为Dataset<Row>，或
- 定义一个低层次变换并显式调用方法以访问包含输入数据集的Dataset<Row>。
对于依赖于文件的变换，您必须定义一个低层次变换，然后访问数据集中的文件。

以下是两种类型变换的关键区别总结：

| 描述 | 高层次变换 | 低层次变换 |
| --- | --- | --- |
| 允许依赖于DataFrame对象的数据变换 | ✓ * | ✓ |
| 允许依赖于文件访问的数据变换 |  | ✓ |
| 支持多个输入数据集 | ✓ | ✓ |
| 支持多个输出数据集 |  | ✓ |
| 计算函数必须返回DataFrame值 | ✓ |  |
| 计算函数写入输出，而不是返回值 |  | ✓ |

* 我们建议对依赖于DataFrame对象的数据变换使用高层次变换。

对于两种Transform类型，您需要创建一个包含计算函数的类。在此类中，您的计算函数必须是一个公共的、非静态的方法，并带有@Compute注解。没有此注解，您的数据变换代码将无法正确注册。

## 注册类型

每个仓库中的变换Java子项目都会暴露一个Pipeline对象。此Pipeline对象用于：

- 在Foundry中注册数据集，并提供搭建它们的说明，以及
- 在Foundry搭建期间定位并执行负责搭建给定数据集的Transform对象。
### 入口点

负责执行Java变换的运行时需要能够找到项目的Pipeline。请注意，变换Java使用用于服务加载的标准Java设施 ↗。

为了定义与项目关联的Pipeline对象，您必须实现一个PipelineDefiner对象。在此PipelineDefiner对象中，您可以将变换添加到项目的Pipeline中。具体来说，要求每个Java子项目实现一个PipelineDefiner对象：

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
package myproject;

import com.palantir.transforms.lang.java.api.Pipeline;
import com.palantir.transforms.lang.java.api.PipelineDefiner;

public final class MyPipelineDefiner implements PipelineDefiner {

  @Override
  public void define(Pipeline pipeline) {
    // 在这里通过自动或手动注册将转换添加到项目的管道中。
    // 此方法用于定义数据管道中的转换步骤。
  }
}
```

一旦创建Java包并实现一个PipelineDefinerObject，您必须更新resources/META-INF/services/com.palantir.transforms.lang.java.api.PipelineDefiner以指向您的PipelineDefiner实现：

```
Copied!1
2
3
// 将此替换为你的 "PipelineDefiner" 实现的类名。
// 由于每个 Java 子项目只实现一个 "PipelineDefiner"，因此此文件只能包含一个条目。
myproject.MyPipelineDefiner
```

MyPipelineDefiner指的是PipelineDefiner实现的类名。

### 向管道添加变换

一旦与项目的Pipeline关联的Transform声明了一个数据集作为输出，您可以在Foundry中搭建这个数据集。向Pipeline添加Transform对象的两种推荐方法是手动注册和自动注册。

如果您有更高级的工作流和/或希望明确地将每个Transform对象添加到项目的Pipeline中，可以使用手动注册。例如，如果您希望元编程地将相同的数据变换逻辑应用于多个输入和输出数据集组合，使用手动注册将非常有用。

否则，强烈建议使用自动注册，以确保您的注册代码简洁且集中。通过自动注册，Pipeline.autoBindFromPackage()会发现包中的任何Transform定义（前提是这些对象具有所需的@Input和@Output注解）。

#### 自动注册

随着项目复杂度的增加，手动向Pipeline添加Transform对象可能变得笨拙。因此，Pipeline对象提供了autoBindFromPackage()方法，以发现Java包内的所有Transform对象。要使用自动注册，您必须执行以下操作：

- 定义一个与您的Transform对应的类。通过自动注册，您定义一个包含有关输入和输出数据集以及计算函数信息的类。
- 添加足够的@Input和@Output注解。
- 调用Pipeline.autoBindFromPackage()方法，以注册您提供的Java包中的任何Transform定义。autoBindFromPackage()方法只会注册具有所需注解的Transform定义。任何没有所需注解的Transform将不会被添加到项目的Pipeline中，即使这些Transform在您提供给autoBindFromPackage()方法的Java包中。
#### 手动注册

可以使用Pipeline.register()方法手动将Transform对象添加到Pipeline中。每次调用此方法可以注册一个Transform。为了使用手动注册Transforms，您必须执行以下操作：

- 定义一个包含计算函数的类，用于您的Transform对象。与自动注册不同，通过手动注册，您在PipelineDefiner实现中提供有关输入和输出数据集的信息。
- 使用HighLevelTransform.builder()或LowLevelTransform.builder()来指定要使用的计算函数以及提供您的输入和输出数据集。
- 调用Pipeline.register()方法，将您的Transform定义明确地添加到项目的Pipeline中。
请注意，诸如@StopProgagating和@StopRequiring的注解仅支持自动注册的Java变换。

## 变换上下文

在某些情况下，数据变换可能依赖于其输入数据集之外的其他内容。例如，可能需要访问当前的Spark会话或访问jobSpec中的变换参数。在这种情况下，您可以向变换中注入TransformContext对象。为此，您的计算函数必须接受一个类型为TransformContext的参数。TransformContext包含变换的authHeader、Spark会话、变换参数和一个ServiceDiscovery对象。ServiceDiscovery类公开已发现的Foundry服务的服务URI。

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
package myproject.datasets;

import com.palantir.transforms.lang.java.api.Compute;
import com.palantir.transforms.lang.java.api.Input;
import com.palantir.transforms.lang.java.api.Output;
import com.palantir.transforms.lang.java.api.TransformContext;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;

/**
* 这是一个访问 TransformContext 的高级 Transform 示例
*/
@Compute
public Dataset<Row> myComputeFunction(Dataset<Row> myInput, TransformContext context) {
    // 从 context 中获取参数 "limit" 的值，并将其转换为 int 类型
    int limit = (int) context.parameters().get("limit");
    // 返回限定行数的 Dataset
    return myInput.limit(limit);
}
```

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
package myproject.datasets;

import com.palantir.transforms.lang.java.api.Compute;
import com.palantir.transforms.lang.java.api.Input;
import com.palantir.transforms.lang.java.api.Output;
import com.palantir.transforms.lang.java.api.TransformContext;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;

/**
* 这是一个示例的低级转换，演示如何访问 TransformContext
*/
@Compute
public void compute(FoundryInput input, FoundryOutput output, TransformContext context) {
    // 从上下文参数中获取“limit”值，并将其转换为整数
    int limit = (int) context.parameters().get("limit");
    // 读取输入数据集，将其限制到指定的行数，然后写入输出
    output.getDataFrameWriter(input.asDataFrame().read().limit(limit)).write();
}
```
