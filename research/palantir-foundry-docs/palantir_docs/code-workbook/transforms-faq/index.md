来源: https://palantir.com/docs/zh/foundry/code-workbook/transforms-faq/

# 变换常见问题解答

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 变换常见问题解答

以下是一些关于变换的常见问题。

有关常规信息，请参阅我们的变换文档。

- 是否可以在transforms-python中保存CSV文件而不是保存Parquet文件？
- 我可以从一个Python变换中搭建多个输出数据集吗？
- 如何使用变换打开GZIP文件？
- 如何在Foundry管道中解压缩文件？是否可以并行解压？
## 是否可以在transforms-python中保存CSV文件而不是保存Parquet文件？

以下是如何在每种变换语言中执行此操作的示例：

Java

```
Copied!1
2
3
4
// 获取数据帧写入器并设置格式为CSV，然后写入
foundryOutput.getDataFrameWriter(dataFrame)
.setFormatSettings(DatasetFormatSettings.builder().format("csv").build())
.write();
```

> Python

Python

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
from transforms.api import transform, Input, Output

@transform(
  output=Output("/path/to/python_csv"),  # 指定输出路径
  my_input=Input("/path/to/input")       # 指定输入路径
)
def my_compute_function(output, my_input):
  # 将输入的数据框写入输出，并指定输出格式为CSV
  output.write_dataframe(my_input.dataframe(), output_format="csv")
```

SQL

```
Copied!1
2
CREATE TABLE `/path/to/sql_csv` USING CSV AS SELECT * FROM `/path/to/input`
-- 创建一个表位于 '/path/to/sql_csv'，使用CSV格式，并从 '/path/to/input' 中选择所有内容进行填充
```

返回顶部

## 我可以从一个Python变换搭建多个输出数据集吗？

如果你希望有多个变换/数据集，可以使用for循环创建它们：

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
from transforms.api import transforms_df, Input, Output

def transform_generator(sources):
	#type: (List[str]) -> List([transforms.api.Transform])
	transforms = []
		# 此示例使用多个输入数据集。你也可以从单个输入数据集中生成多个输出。
	for source in sources:
		@transforms_df(
			Output('/sources/{source}/output'.format(source=source)),
			my_input=Input('/sources/{source}/input'.format(source=source))
			)
		def compute_function(my_input, source=source):
			# 为了在函数中捕获 source 变量，你需要将其作为默认关键字参数传递。
			return my_input.filter(my_input.source == source)

		transforms.append(compute_function)

	return transforms

TRANSFORMS = transforms_generator(['src1', 'src2', 'src3'])
```

此代码定义了一个transform_generator函数，通过遍历给定的sources列表，为每个 source 创建一个数据转换函数compute_function。compute_function使用transforms_df装饰器，接收一个输入数据集，并根据source过滤数据，输出到对应的输出路径。最终，TRANSFORMS变量收集了所有生成的转换函数。
您现在可以导入模块的TRANSFORMS属性，并手动将每个变换添加到您的管道中：

```
Copied!1
2
3
4
import my_module

my_pipeline = Pipeline()  # 创建一个新的数据处理管道
my_pipeline.add_transforms(*my_module.TRANSFORMS)  # 从my_module中添加所有的转换操作到管道中
```

要在同一个搭建中使用单个变换以一个输入并输出多个数据集，您还可以按如下方式通过编程实现：

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
# 使用 `/examples/students_hair_eye_color` 数据集
students_input = foundry.input('/examples/students_hair_eye_color')
students_input.dataframe().sort('id').show(n=3)
+---+-----+-----+----+
| id| hair|  eye| sex|
+---+-----+-----+----+
|  1|Black|Brown|Male|
|  2|Brown|Brown|Male|
|  3|  Red|Brown|Male|
+---+-----+-----+----+
# 注意这个例子只显示了前三行。

from transforms.api import transform, Input, Output

@transform(
	hair_eye_color=Input('/examples/students_hair_eye_color'),
	males=Output('/examples/hair_eye_color_males'),
	females=Output('examples/hair_eye_color_females'),
)
def brown_hair_by_sex(hair_eye_color, males, females):
	# type: (TransformInput, TransformOutput, TransformOutput) -> None
	# 过滤出头发颜色为棕色的学生数据
	brown_hair_df = hair_eye_color.dataframe().filter(hair_eye_color.dataframe().hair == 'Brown')

	# 将男性学生数据写入 'males' 输出
	males.write_dataframe(brown_hair_df.filter(brown_hair_df.sex == 'Male'))
	# 将女性学生数据写入 'females' 输出
	females.write_dataframe(brown_hair_df.filter(brown_hair_df.sex == 'Female'))
```

此代码的功能是从学生的头发和眼睛颜色数据集中提取出头发为棕色的学生，并根据性别将这些学生分别写入不同的输出数据集中。

有关变换的更多帮助和信息，请查阅以下文档：

- Python 变换
- Java 变换
- Spark SQL 变换
返回顶部

## 如何通过变换打开GZIP文件？

由于变换的输入是由流支持的类似文件的对象，您可以将其作为文件进行处理。这意味着您无需担心将整个文件读入内存或将其复制到磁盘，从而允许使用更大的文件。

使用Python 3中包含的gzip和io包：

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
import gzip, io

def process_file(file_stauts):
    # 获取输入数据集的文件系统
	fs = input_dataset.filesystem()
	# 以二进制读取文件
	with fs.open(file_status.path, 'rb') as f:
		# 解压gzip文件
		gz = gzip.GzipFile(fileobj=f)
		# 创建一个缓冲读取器
		br = io.BufferedReader(gz)
```

如果您希望读取返回字符串，可以将其包装：

```
Copied!1
tw = io.TextIOWrapper(br)  # 使用TextIOWrapper将字节流br包装为文本流tw，以便进行文本处理
```

如果您的文件有编码，可以指定它：

```
Copied!1
tw = io.TextIOWrapper(br, encoding='CP500')  # 创建一个TextIOWrapper对象，将br包装成文本流，使用CP500编码
```

如需有关变换的更多帮助和信息，请查看以下文档：

- Python变换
- Java变换
- Spark SQL变换
返回顶部

## 如何在Foundry管道中解压文件？可以并行进行吗？

这使用Java和Spark以并行方式解压缩zip存档中的每个文件。如果您想在单个压缩文件内并行化解压缩，请使用可分割的文件格式，例如.bz2。

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
package com.palantir.transforms.java.examples;

import com.google.common.io.ByteStreams;
import com.palantir.transforms.lang.java.api.Compute;
import com.palantir.transforms.lang.java.api.FoundryInput;
import com.palantir.transforms.lang.java.api.FoundryOutput;
import com.palantir.transforms.lang.java.api.ReadOnlyLogicalFileSystem;
import com.palantir.transforms.lang.java.api.WriteOnlyLogicalFileSystem;
import com.palantir.util.syntacticpath.Paths;
import java.io.IOException;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

/**
 * 这是一个使用 Spark 并行解压文件的示例。
 * <p>
 * 任务分配给执行器。
 */
public final class UnzipWithSpark {

    @Compute
    public void compute(FoundryInput zipFiles, FoundryOutput output) throws IOException {
        ReadOnlyLogicalFileSystem inputFileSystem = zipFiles.asFiles().getFileSystem();
        WriteOnlyLogicalFileSystem outputFileSystem = output.getFileSystem();

        inputFileSystem.filesAsDataset().foreach(portableFile -> {
            // "processWith" 提供给定输入文件的 InputStream。
            portableFile.processWithThenClose(stream -> {
                try (ZipInputStream zis = new ZipInputStream(stream)) {
                    ZipEntry entry;
                    // 对于压缩文件中的每个文件，将其写入到输出文件系统。
                    while ((entry = zis.getNextEntry()) != null) {
                        outputFileSystem.writeTo(
                                Paths.get(entry.getName()),
                                outputStream -> ByteStreams.copy(zis, outputStream));
                    }
                    return null;
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }
            });
        });
    }
}
```

有关变换的更多帮助和信息，请查看以下文档：

- Python 变换
- Java 变换
- Spark SQL 变换
返回顶部
