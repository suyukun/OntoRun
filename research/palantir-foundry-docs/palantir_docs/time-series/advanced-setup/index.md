来源: https://palantir.com/docs/zh/foundry/time-series/advanced-setup/

# 高级设置

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 高级设置

我们建议按照时间序列设置页面中的说明，使用Pipeline Builder搭建您的时间序列管道。这样做将自动应用下面描述的变换优化。

在进行高级设置配置之前，请联系您的Palantir代表。

如果您需要低级变换控制或Pipeline Builder尚未提供的高级功能，本页将描述如何使用代码库手动设置您的时间序列管道以进行数据变换。

使用代码库设置时间序列，您必须完成以下步骤：

- 创建时间序列数据集。
- 优化时间序列数据集。
- 手动设置时间序列同步。
- 创建时间序列对象类型支持数据集。
- 设置时间序列对象类型。
## 1. 创建时间序列数据集

当您使用Pipeline Builder的时间序列输出创建时间序列同步时，时间序列数据集会自动生成，并且时间序列数据集和同步都会为您正确配置。当您手动设置管道时，必须明确生成包含您格式化的时间序列数据的时间序列数据集，这是创建时间序列同步所必需的。数据集必须包含Series ID、Value和Timestamp列，如术语表中所指定，以便它们可以在时间序列同步中映射。

一个系列ID的所有值应包含在同一数据集中。由于值是通过其系列ID获取的，单个时间序列数据集可以包含多个系列ID的所有值。例如：

```
+------------------------+---------------------+---------+
| series_id              | timestamp           | value   |
+------------------------+---------------------+---------+
| Machine123_temperature | 01/01/2023 12:00:00 | 100     |  // 机器123的温度在2023年1月1日12:00:00的读数为100
| Machine123_temperature | 01/01/2023 12:01:00 | 99      |  // 机器123的温度在2023年1月1日12:01:00的读数为99
| Machine123_temperature | 01/01/2023 12:02:00 | 101     |  // 机器123的温度在2023年1月1日12:02:00的读数为101
| Machine463_temperature | 01/01/2023 12:00:00 | 105     |  // 机器463的温度在2023年1月1日12:00:00的读数为105
| Machine123_pressure    | 01/01/2023 12:00:00 | 3       |  // 机器123的压力在2023年1月1日12:00:00的读数为3
| ...                    | ...                 | ...     |  // 省略其他数据
+------------------------+---------------------+---------+
```

时间序列数据集通常配置为在有实时数据时进行增量搭建。增量搭建可以节省计算成本，并在原始数据被摄取到最新数据可读取之间实现更短的延迟。

有关增量时间序列搭建的更多优点，请参阅常见问题文档。

## 2. 优化时间序列数据集

在代码中生成时间序列数据集时，请在写入之前按如下方式格式化数据集：

### Python

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
from transforms.api import transform, Input, Output

@transform(
    output_dataset=Output("/path/to/output/dataset"),
    input_dataset=Input("/path/to/input/dataset")
)
def my_compute_function(output_dataset, input_dataset):
    # 读取输入数据集并转换为DataFrame
    output_dataframe = (
        input_dataset
        .dataframe()
        # 按照'seriesId'字段对数据进行分区
        .repartitionByRange('seriesId')
        # 在每个分区内按照'seriesId'和'timestamp'排序
        .sortWithinPartitions('seriesId', 'timestamp')
    )

    # 将输出的DataFrame写入指定格式的输出数据集
    output_dataset.write_dataframe(output_dataframe, output_format='soho')
```

### Java

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
package myproject.datasets;

import com.palantir.transforms.lang.java.api.Compute;
import com.palantir.transforms.lang.java.api.FoundryInput;
import com.palantir.transforms.lang.java.api.FoundryOutput;
import com.palantir.transforms.lang.java.api.Input;
import com.palantir.transforms.lang.java.api.Output;
import com.palantir.foundry.spark.api.DatasetFormatSettings;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;

import java.util.Collections;

public final class TimeSeriesWriter {
    @Compute
    public void writePartitioned(
            @Input("/path/to/input/dataset") FoundryInput inputDataset, // 输入数据集路径
            @Output("/path/to/output/dataset") FoundryOutput outputDataset) { // 输出数据集路径
        Dataset<Row> inputDataframe = inputDataset.asDataFrame().read(); // 读取输入数据集到DataFrame

        Dataset<Row> outputDataframe = inputDataframe
            .repartitionByRange(inputDataframe.col('seriesId')) // 通过seriesId列进行范围分区
            .sortWithinPartitions('seriesId', 'timestamp'); // 在分区内根据seriesId和timestamp排序

        outputDataset.getDataFrameWriter(outputDataframe)
            .setFormatSettings(DatasetFormatSettings.builder()
                .format('soho') // 设置数据集格式为'soho'
                .build())
            .write(); // 写入输出数据集
    }
}
```

在这段代码中，我们定义了一个名为TimeSeriesWriter的 Java 类，用于处理时间序列数据集的分区和排序。通过 Spark 的 DataFrame API，我们首先读取输入数据集，然后根据seriesId列对数据集进行范围分区，并在每个分区内依据seriesId和timestamp进行排序。最终，我们将处理好的数据集写入到指定的输出路径，并设置数据格式为soho。
运行此重新分区和排序将优化您的数据集，以便作为时间序列高效使用。至少，您的数据集还应按_Soho_格式化（如所示），以便在尚未投影时，新数据能够索引到时间序列数据库中。您还应根据以下指南，为您的管道配置由repartitionByRange()↗写入的分区数量：

- 尽量写入尽可能少的分区。
- 分区应大于128 MB。
- 一般来说，分区应少于50亿行。
您可以写入的最少分区数量的限制是由写入足够小的分区来决定的，这些分区适合执行器，但分区数量足够多以使您的任务能够充分并行化，达到所需的管道延迟。写入更多分区会导致分区较小且任务更快，但不如较大分区那样最优。

## 3. 手动设置时间序列同步

要创建新的时间序列同步，直接导航到https://<domain>/workspace/time-series-catalog-app/new。系统会提示您选择保存同步的位置，该位置必须位于包含您的时间序列数据集的项目中或将其作为引用导入。

选择您的时间序列数据集作为输入，然后完成将数据集列映射到时间序列同步的系列ID、值和时间戳。如果您的时间戳列是Long类型，请指定它是SECONDS、MILLISECONDS、MICROSECONDS还是NANOSECONDS单位。

当时间序列同步构建时，它会同步时间序列数据集的元数据，使Foundry能够按需索引您的时间序列数据到其时间序列数据库中。

### 使用受限视图支持的对象类型

受限视图将数据集访问限制为用户有权限查看的行。当使用受限视图支持的对象类型时，您必须配置您的时间序列同步以停止继承权限标记。

通过选择权限标记旁的停止继承来停止继承时间序列数据集上的每个权限标记。

完成后，选择页面顶部的保存。

### 高级时间序列同步配置

虽然可以为时间序列同步构建配置Spark配置文件，但这很少是必要的。

默认情况下，当输入时间序列数据集更新时，同步将计划运行。我们建议使用此设置以确保您的时间序列数据保持最新。

如果您在另一个时间序列同步中写入了相交的系列ID，并希望用新的同步替换该同步，您可以在显示高级选项>覆盖其他数据集支持的其他同步中的系列中指定旧同步。这样做会导致旧同步失败，然后应将其移至回收站。

## 4. 创建时间序列对象类型支持的数据集

您可以通过首选的方法生成时间序列对象类型支持的数据集，并且它应符合术语表中指定的模式。

要自动生成时间序列对象类型支持的数据集，您可以在与时间序列数据集相同的变换中生成它，您可以在其中获取系列ID的不同集合并从中提取/映射元数据。在增量管道中，您可以使用合并和追加模式来实现这一点。

## 5. 设置时间序列对象类型

按照标准流程在您的时间序列对象类型支持的数据集上创建对象类型。还可以通过在数据集预览中选择所有操作>创建对象类型，直接从数据集中生成对象类型。创建对象类型时，通过指定哪些属性应为时间序列属性来配置它以用于时间序列。
