来源: https://palantir.com/docs/zh/foundry/code-workspaces/data/

# 与数据交互

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 与数据交互

Code Workspaces允许您读取、探索、分析、变换和写回Foundry数据集。

Code Workspaces要求您为工作区中引用的每个Foundry数据集选择一个数据集别名。数据集别名作为特定数据集分支的引用，允许您在代码中读取和写入数据。

在数据选项卡中注册数据集时，Code Workspaces会在工作区的/home/user/repo/.foundry文件夹下的隐藏文件中创建所选数据集别名与Foundry数据集唯一标识符之间的映射。

## 数据集分支

默认情况下，Code Workspaces将从与工作区自身相同的分支加载数据集的数据，否则将退回到master分支。例如，当前在my-branch分支上的代码工作区将尝试读取数据集的my-branch版本，如果my-branch在数据集中不存在，则退回到master分支。

要为特定导入的数据集固定一个数据集分支，请在左侧边栏的数据选项卡中选择数据集旁的**•••图标。然后，选择固定数据集分支以进行读取**并选择要在代码工作区中使用的数据集分支。

## 导入数据

Code Workspaces允许您加载Foundry的表格和非表格数据集。

可以通过导入数据集按钮在数据选项卡中在代码工作区中注册一个新数据集。

选择所需数据集后，系统会提示您在表格或非表格数据集之间进行选择，并且可以非必填地修改工作区中数据集的别名。Code Workspaces使用这些设置生成相应加载数据集的代码片段。

- 即使在注册数据集之后，您也可以随时修改这些设置。
- 默认情况下，Code Workspaces将建议一个与数据集本身同名的数据集别名。
一旦设置了您的数据集别名，选择复制并注册数据集以在工作区中注册数据集，这也会将代码片段保存到您的剪贴板。

最后，将代码片段粘贴到您的工作区并执行代码，以将数据集加载到内存中。

### 示例代码片段

本页提供了表格数据集和非表格数据集的示例。

#### 表格数据集

以下代码片段为数据集别名为kittens的Cats表格数据集生成。注意在代码片段中没有任何地方引用“Cats”；在选择复制并注册数据集后，Code Workspaces会在您选择的数据集别名下隐式注册它。

在Jupyter®中：

```
Copied!1
2
3
4
5
6
from foundry.transforms import Dataset

# 从名为 "kittens" 的数据集中获取数据，并以 Arrow 格式读取
kittens = Dataset.get("kittens")\
  .read_table(format="arrow")\
  .to_pandas()  # 将数据转换为 Pandas DataFrame
```

请注意，上述read_table方法支持以下参数：

- arrow（推荐）：将数据集转换为 Apache Arrow 表，可以在其上执行高效的筛选。然后可以使用.to_pandas()将此表转换为 pandas dataframe。
- pandas或dataframe:将数据集转换为 pandas dataframe。
- polars:将数据集转换为 Polars dataframe。然后可以使用.to_pandas()将其转换为 pandas dataframe。
- lazy-polars:Polars dataframe 的惰性变体。无法在 lazy polars 上执行筛选。
- path:输出存储数据集的本地路径。
要使特定格式在read_table操作中可用，相应的包pyarrow、pandas和polars必须存在于环境中。这些包在默认的 Code Workspaces 环境中自动包含，但可能需要手动添加到您的自定义环境中。

在 RStudio® 中：

```
Copied!1
2
# 从数据集读取名为 "kittens" 的表格
kittens <- datasets.read_table("kittens")
```

上述语法加载数据集并自动将数据收集到R数据框中。

如果数据超过工作区的内存容量，可以应用下推筛选，以使用以下语法仅加载部分行或列：

```
Copied!1
2
3
4
5
library(dplyr) # 应该在 .Rprofile 中默认导入

kittens_df <- Dataset.get("kittens") %>%
  # （可选）在收集数据前应用其他转换
  collect()
```

#### 非表格数据集

以下代码片段是为别名为puppies的非表格数据集Dogs生成的。注意，Dogs在代码片段中没有被引用；在选择复制并注册数据集后，Code Workspaces会自动以您选择的名称注册它。与表格数据集不同，这会让您通过puppies_files变量访问数据集中的文件，而不是在数据框中插入值。

在Jupyter®中：

```
Copied!1
2
3
4
5
6
from foundry.transforms import Dataset

# 获取名为 "puppies" 的数据集
puppies = Dataset.get("puppies")
# 下载数据集中的所有文件
puppies_files = puppies.files().download()
```

```
Copied!1
2
3
4
5
puppies_files <- datasets.list_files("puppies")
# 列出数据集 "puppies" 中的所有文件

puppies_local_files <- datasets.download_files("puppies", puppies_files)
# 下载数据集 "puppies" 中的所有文件到本地
```

### 安全性

应用于数据集的数据安全权限标记在Code Workspaces中被遵循。此外，工作区会继承所有已加载数据集的权限标记。这意味着，为了访问代码工作区，用户还必须拥有对工作区中包含的所有数据集和其他输入的必要权限。如果您失去对工作区某个输入的访问权限，您将无法访问整个工作区。

### 数据集大小限制

与Foundry中的其他工具不同，Code Workspaces默认不在Spark上运行。Code Workspaces被设计用于快速探索性分析，而不是处理非常大的数据集。考虑在加载数据集之前使用筛选来减少数据集的大小，以防止与配置工作区的内存或CPU限制相关的问题。

## 筛选数据集文件

Code Workspaces使您能够下载支持任何数据集的文件，无论它们是表格形式（即，它们有一个模式）还是非表格形式。可以选择要下载的文件子集，无论是按名称，还是通过对文件元数据（路径、字节大小、事务RID和更新时间）应用筛选逻辑。

在Jupyter®中：

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
from foundry.transforms import Dataset

# 下载数据集中的所有文件
downloaded_files = Dataset.get("my_alias").files().download()
local_file = downloaded_files["file.pdf"]

# 下载单个文件
local_file = Dataset.get("my_alias").files().get("file.pdf").download()

# 下载数据集中所有小于1MB的PDF文件
downloaded_files = my_dataset.files()\
    .filter(lambda f: f.path.endswith(".pdf") and f.size_bytes < 1024 * 1024)
    .download()
```

在下载多个文件时，我们建议使用筛选语法，而不是按名称单独下载文件，以利用并行下载。

在RStudio®中：

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
# 下载数据集中的所有文件
all_files <- datasets.list_files("my_alias")  # 获取数据集中所有文件的列表
downloaded_files <- datasets.download_files("my_alias", all_files)  # 下载所有文件
local_file <- downloaded_files$`file.pdf`  # 获取下载的文件中的特定文件

# 按名称下载文件
downloaded_files <- datasets.download_files("my_alias", c("file1.pdf", "file2.pdf"))  # 下载指定名称的文件

# 下载数据集中小于1MB的所有PDF文件
all_files <- datasets.list_files("my_alias")  # 获取数据集中所有文件的列表
pdf_files <- all_files[sapply(all_files, function(f) f.endswith(".pdf") && f$sizeBytes < 1024*1024)]  # 过滤出小于1MB的PDF文件
downloaded_files <- datasets.download_files("my_alias", pdf_files)  # 下载过滤后的PDF文件
```

在这两种情况下，downloaded_files将是一个映射，映射从当前数据集视图中定义的文件名（可能包含斜杠）到文件下载到的本地路径。请注意，此本地路径可能会更改，因此建议依赖于映射的键。

## 筛选表格数据集

Code Workspaces 使您能够在将数据集加载到内存之前应用筛选。这有效地减少了导入工作区的数据帧的内存消耗，使您能够专注于分析所需的数据子集。Code Workspaces 提供了处理列、行或两者选择的灵活性。

### 何时使用表格数据集的筛选

如数据集大小限制所述，Code Workspaces 最适合用于快速探索和迭代周期，而不是处理极大的数据集。我们建议在决定如何将数据加载到工作区时遵循以下指南：

- 对于适合工作区内存的未压缩数据，我们建议在不使用筛选的情况下加载数据集，并在内存中应用数据变换以实现最大效率。
对于适合工作区内存的未压缩数据，我们建议在不使用筛选的情况下加载数据集，并在内存中应用数据变换以实现最大效率。

- 如果未压缩数据超过了工作区的内存容量，我们建议使用其他 Foundry 工具，如 Pipeline Builder 来预处理数据，或使用行限制加载有限数量的行。还可以使用列和行筛选将数据子集加载到内存中。这些下推筛选在数据加载到工作区内存之前应用，从而减少导入数据的内存占用。但是，根据数据的规模和分区，这些筛选可能需要很长时间运行。
如果未压缩数据超过了工作区的内存容量，我们建议使用其他 Foundry 工具，如 Pipeline Builder 来预处理数据，或使用行限制加载有限数量的行。还可以使用列和行筛选将数据子集加载到内存中。这些下推筛选在数据加载到工作区内存之前应用，从而减少导入数据的内存占用。但是，根据数据的规模和分区，这些筛选可能需要很长时间运行。

- 如果您经常加载相同的数据子集或在多个工作区中使用它，我们建议将该子集持久化为其自己的数据集，以便可以不使用筛选加载该子集。数据集的 parquet 文件只会下载一次，而每次数据加载到工作区时都会发生筛选开销。
如果您经常加载相同的数据子集或在多个工作区中使用它，我们建议将该子集持久化为其自己的数据集，以便可以不使用筛选加载该子集。数据集的 parquet 文件只会下载一次，而每次数据加载到工作区时都会发生筛选开销。

- 对于更复杂的数据加载需求，您可以使用非表格数据集语法下载支持数据集的文件，并使用本地python或R包来处理文件内容。
对于更复杂的数据加载需求，您可以使用非表格数据集语法下载支持数据集的文件，并使用本地python或R包来处理文件内容。

### 行限制

可以仅从数据集中加载有限数量的行。

在 Jupyter® 中：

```
Copied!1
2
3
4
5
6
from foundry.transforms import Dataset

# 获取名为“dogs”的数据集，并限制读取1000条记录
dogs_subset = Dataset.get("dogs")\
  .limit(1000)\
  .read_table(format="pandas")  # 以pandas格式读取数据表
```

```
Copied!1
2
3
4
5
6
library(dplyr) # 应该在.Rprofile中默认导入

# 从数据集中获取“dogs”数据，并选择前1000行，收集到数据框中
dogs_subset <- Dataset.get("dogs") %>%
  head(1000) %>%
  collect()
```

### 列筛选

所有表格数据集都可以加载到一个工作区中，并只包含部分列。以下是一个数据集的示例：

| name | weight | color | age | breed |
| --- | --- | --- | --- | --- |
| Bella | 60 | Brown | 4 | Labrador |
| Max | 75 | Black | 7 | German Shepherd |
| Daisy | 30 | White | 2 | Poodle |

您可能只想使用以下语法加载此数据集的breed和age列，假设dogs数据集已正确注册到工作区：

在 Jupyter® 中：

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
from foundry.transforms import Dataset, Column

# 仅加载“breed”和“age”列
columns_to_load = ["breed", "age"]
breed_and_age_only = Dataset.get("dogs")\
  .select(*columns_to_load)\
  .read_table(format="pandas")  # 读取数据并以pandas格式返回

# 仅加载“weight”和“color”列
weight_and_color_only = Dataset.get("dogs")\
  .select("weight", "color")\
  .read_table(format="pandas")  # 读取数据并以pandas格式返回
```

```
Copied!1
2
3
4
5
6
library(dplyr) # 通常在 .Rprofile 文件中默认导入 dplyr 库

# 仅加载 "weight" 和 "color" 列
weight_and_color_only <- Dataset.get("dogs") %>%
  select(weight, color) %>% # 选择数据集中的 "weight" 和 "color" 列
  collect() # 收集并返回结果
```

### 行筛选

表格数据集也可以加载到工作区中，其中包含满足某些条件的行的子集。

行筛选仅适用于Parquet格式的数据集。其他格式，如CSV，允许进行列筛选，但不支持行筛选。借助Foundry变换，大多数表格数据集可以轻松转换为Parquet格式。

回顾之前提到的dogs数据集：

| name | weight | color | age | breed |
| --- | --- | --- | --- | --- |
| Bella | 60 | Brown | 4 | Labrador |
| Max | 75 | Black | 7 | German Shepherd |
| Daisy | 30 | White | 2 | Poodle |
| Buddy | 65 | Yellow | 3 | Labrador |
| Gizmo | 18 | Brown | 1 | Pug |

#### Jupyter®中的行筛选语法

以下语法可用于在Jupyter®中以行级别筛选数据集。

您可以使用以下语法仅从dogs数据集中加载棕色的狗：

```
Copied!1
2
3
4
5
6
from foundry.transforms import Dataset, Column

# 仅加载颜色为“Brown”的狗
brown_dogs = Dataset.get("dogs")\
  .where(Column.get("color") == "Brown")\  # 过滤条件：颜色为“Brown”
  .read_table(format="pandas")  # 将结果读取为pandas格式的表格
```

请注意使用.where、select或.limit来预先筛选数据集，然后再将其加载到工作区。这些语句可以链接在一起以一次应用多个条件：

```
Copied!1
2
3
4
5
# 仅加载颜色为“Brown”且品种为“Labrador”的狗的数据集
golden_dogs = Dataset.get("dogs")\
  .where(Column.get("color") == "Brown")\  # 筛选颜色为“Brown”的狗
  .where(Column.get("breed") == "Labrador")\  # 筛选品种为“Labrador”的狗
  .read_table(format="pandas")  # 读取数据并格式化为pandas表格
```

以下是Jupyter® Code Workspaces中支持的行筛选语法示例：

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
# 仅保留等于某个值的行
.where(Column.get("column_name") == value)

# 仅保留不等于某个值的行
.where(Column.get("column_name") != value)

# 使用 ~ 操作符进行不等判断
.where(~Column.get("column_name") == value)

# 仅保留其值可与另一个值比较的行
.where(Column.get("column_name") > value)
.where(Column.get("column_name") >= value)
.where(Column.get("column_name") < value)
.where(Column.get("column_name") <= value)

# OR / AND 操作符
.where((Column.get("column_name") == value1) | (Column.get("column_name") == value2))
.where((Column.get("column_name1") == value1) & (Column.get("column_name2") == value2))

# 仅保留值不为 null 的行
.where(~Column.get("column_name").isnull())

# 仅保留值属于给定列表的行
.where(Column.get("column_name").isin([value1, value2, value3]))

# 仅保留日期在两个给定边界之间（包含）的行
.where(Column.get("date_column_name").between('lower_bound_incl', 'upper_bound_incl'))

# 仅保留前 N 行，其中 N 是一个数字。这将在其他过滤器之前应用
.limit(N)

# 选择子集列
.select("column_name1", "column_name2", "column_name3")
```

#### RStudio® 中的行级筛选语法

下面的语法可用于在 RStudio® 中对数据集进行行级筛选。

RStudio 筛选通过使用dplyr库实现，并实现了标准方法filter、select和head。这些筛选是下推的，这意味着它们在数据加载到工作区的内存之前被应用。

您可以使用以下语法从dogs数据集中仅加载棕色的狗：

```
Copied!1
2
3
4
5
6
library(dplyr) # 默认应在 .Rprofile 中导入

# 仅加载颜色为“Brown”的狗
brown_dogs <- Dataset.get("dogs") %>%
  foundry::filter(color == "Brown") %>% # 过滤出颜色为“Brown”的狗
  collect() # 收集过滤后的数据
```

请注意使用foundry::filter以预先筛选数据集，然后再将其加载到工作区中。从技术上讲，foundry::前缀不是必需的，但我们建议使用它以避免与环境中其他包中类似命名的筛选函数发生潜在冲突。这些筛选语句可以使用dplyr库中的%>%运算符链接在一起，以一次应用多个条件。此库应在 RStudio 工作区的.Rprofile文件中默认导入。

```
Copied!1
2
3
4
5
6
7
library(dplyr) # 应该在 .Rprofile 中默认导入

# 仅加载颜色为“棕色”且品种为“拉布拉多”的狗
brown_labradors <- Dataset.get("dogs") %>%
  foundry::filter(color == "Brown") %>% # 过滤出颜色为“棕色”的狗
  foundry::filter(breed == "Labrador") %>% # 过滤出品种为“拉布拉多”的狗
  collect() # 收集过滤后的结果
```

以下是RStudio® Code Workspaces中支持的行筛选语法的更多示例。列名必须在传递给foundry::filter函数时不加引号。

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
# 仅保留等于某个值的行
foundry::filter(column_name == "string_value") %>%
foundry::filter(integer_column_name == 4) %>%

# 仅保留不等于某个值的行
foundry::filter(column_name != value) %>%

# 使用 ! 操作符进行不等判断
foundry::filter(!(column_name == value)) %>%

# 仅保留值可与另一个值进行比较的行
foundry::filter(column_name > value) %>%
foundry::filter(column_name >= value) %>%
foundry::filter(column_name < value) %>%
foundry::filter(column_name <= value) %>%

# OR / AND 运算符
foundry::filter(column_name == value1 | column_name == value2) %>%
foundry::filter(column_name == value1 & column_name == value2) %>%

# 仅保留值是给定列表的一部分的行
foundry::filter(column_name %in% c("value1", "value2")) %>%

# 仅保留值不是空值的行
foundry::filter(!is.na(column_name)) %>%

# 仅保留值在两个给定边界之间（包含）的行
foundry::filter(between(age, 2, 4)) %>%

# 选择一部分列
select(column_name1, column_name2) %>% # 如果设置，必须包括在 `filter` 子句中使用的所有列

# 仅保留前 N 行，其中 N 是一个数字。这将在应用其他过滤器之前执行
head(N) %>%
```

此外，您可以通过将数据临时收集为Arrow表来执行高级数据变换，例如group_by：

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
library(dplyr) # 应该在 .Rprofile 中默认导入

grouped_dogs <- Dataset.get("alias") %>%
  # 简单的过滤可以下推
  foundry::filter(age > 2) %>%
  collect(as_data_frame = FALSE) %>% # 暂时将数据收集为 Arrow 表
  # 复杂的转换需要在 Arrow 表上应用
  group_by(breed) %>%
  collect()
```

### 列筛选和行筛选结合使用

列筛选和行筛选可以结合使用，以加载包含其列和行子集的数据集。使用前面提到的dogs数据集：

| name | weight | color | age | breed |
| --- | --- | --- | --- | --- |
| Bella | 60 | Brown | 4 | Labrador |
| Max | 75 | Black | 7 | German Shepherd |
| Daisy | 30 | White | 2 | Poodle |
| Buddy | 65 | Yellow | 3 | Labrador |
| Gizmo | 18 | Brown | 1 | Pug |

可以使用下面的语法获取超过给定体重的棕色狗的名称、品种和颜色的数据集。

在 Jupyter® 中：

```
Copied!1
2
3
4
5
6
7
8
# 仅加载颜色为“棕色”且体重超过62的狗
# 仅加载“name”、“breed”和“color”列
heavy_brown_dogs = Dataset.get("dogs")\
  .where(Column.get("weight") > 62)\  # 过滤条件：体重大于62
  .where(Column.get("color") == "Brown")\  # 过滤条件：颜色为“棕色”
  .select("name", "breed", "color")\  # 选择需要的列
  .read_table(format="arrow")\  # 读取数据表，格式为“arrow”
  .to_pandas()  # 将数据转换为Pandas DataFrame
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
library(dplyr) # 应该在 .Rprofile 中默认导入

# 只加载颜色为“Brown”且体重超过62的狗
# 只加载“name”、“breed”和“color”列
heavy_brown_dogs <- Dataset.get("dogs") %>%
  foundry::filter(weight > 62) %>%  # 过滤体重大于62的狗
  foundry::filter(color == "Brown") %>%  # 过滤颜色为“Brown”的狗
  select("name", "breed", "color") %>%  # 选择需要的列
  collect()  # 收集结果
```

## 写入数据

要安排您的数据变换、查看数据沿袭或增量写入。您可以将代码转换为Jupyter®或RStudio变换。

您可以通过以下步骤，使用Code Workspaces交互式地写入Foundry数据集。

- 打开数据选项卡并选择保存到数据集选项（位于导入数据集右侧），创建目标输出数据集。
- 为输出数据集选择一个名称以及保存数据集的位置。
- 选择保存。
- 一个新的数据集将出现在数据选项卡中。默认情况下，保存到数据集选项将被选中，输出数据集应保留此设置。
- 系统还会提示您指定数据集别名，该别名将成为工作区内输出数据集的名称，类似于导入数据时的别名。
- 对于表格输出数据集，系统还会提示您指定填充数据集的数据框变量。
- 对于非表格数据集，您需要指定要上传到数据集的本地文件或文件夹路径。
- 一旦设置了数据集类型、数据集别名和数据框变量，选择复制并注册数据集以在工作区中注册数据集，同时将代码片段保存到剪贴板。
- 将代码片段粘贴到您的工作区中，根据需要替换变量，并执行代码以写入输出数据集。
### 事务类型

在交互式写回时，每个SDK函数调用将对应一个事务：

- 写回表格数据时将创建一个SNAPSHOT事务（在Python中为output_dataset_tabular.write_table(df_variable)或在R中为datasets.write_table(df_variable, "output_dataset_tabular")）。
- 写回文件时将创建一个UPDATE事务（在Python中为output_dataset_non_tabular.write_file(path_to_file_variable)或在R中为datasets.upload_files(path_to_file_variable, "output_dataset_non_tabular")）。
一旦脚本被注册为变换，交互式调用将开始写入以code-workspace-sandbox/为前缀的分支，而当前分支将在变换运行时更新。在这种情况下，即使有多个SDK函数调用，也将为整个脚本执行创建一个事务：

- 默认情况下，事务类型为SNAPSHOT。
- 如果已配置增量设置，事务类型将为APPEND。
### 示例代码片段

按照上述说明，假设创建了两个名为output_dataset_tabular和output_dataset_non_tabular的数据集，并在工作区中注册。Code Workspaces将根据您选择的变量为每个数据集生成以下代码片段：

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
# 表格数据片段
from foundry.transforms import Dataset

# 获取名为 "output_dataset_tabular" 的表格数据集
output_dataset_tabular = Dataset.get("output_dataset_tabular")
# 将 df_variable 写入表格数据集中
output_dataset_tabular.write_table(df_variable)

# 非表格数据片段
from foundry.transforms import Dataset

# 获取名为 "output_dataset_non_tabular" 的非表格数据集
output_dataset_non_tabular = Dataset.get("output_dataset_non_tabular")
# 将 path_to_file_variable 指定的文件写入非表格数据集中
output_dataset_non_tabular.upload_directory(path_to_file_variable)
```

```
Copied!1
2
3
4
5
6
7
# 表格数据片段
datasets.write_table(df_variable, "output_dataset_tabular")
# 将数据帧 df_variable 写入到一个表格格式的数据集 "output_dataset_tabular" 中

# 非表格数据片段
datasets.upload_files(path_to_file_variable, "output_dataset_non_tabular")
# 上传文件 path_to_file_variable 到一个非表格格式的数据集 "output_dataset_non_tabular"
```
