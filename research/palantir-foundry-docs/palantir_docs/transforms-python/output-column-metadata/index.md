来源: https://palantir.com/docs/zh/foundry/transforms-python/output-column-metadata/

# 输出列元数据

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 输出列元数据

您可以在代码库变换中读取和写入输出数据集的列描述和列类型类。

## 在代码库变换中更新列描述

您可以通过向TransformOutput的write_dataframe()函数提供非必填的column_descriptions参数，以添加输出列描述到您的输出数据集中。

- 该参数应为一个字典 ↗，其中键为列名，值为列描述。列描述的长度限制为800个字符。
- 代码将自动计算在您的DataFrame ↗上可用的列名和您提供的字典 ↗中的键的交集，因此不会尝试在不存在的列上放置描述。
### 示例：在代码库变换中写入列描述

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
from transforms.api import transform, Input, Output

# 装饰器 `@transform` 用于定义一个数据转换函数
# `my_output` 和 `my_input` 分别表示输出和输入的数据路径
@transform(
    my_output=Output("/my/output"),
    my_input=Input("/my/input"),
)
def my_compute_function(my_input, my_output):
    # 将输入数据框写入输出路径，同时可以为列提供描述信息
    my_output.write_dataframe(
        my_input.dataframe(),  # 从输入中获取数据框
        column_descriptions={
            "col_1": "col 1 description"  # 为列 "col_1" 添加描述
        }
    )
```

## 列类型类

column_typeclasses属性返回一个结构化的Dict<str, List<Dict<str, str>>>，它将列名称映射到它们的列类型类。

- List中的每个类型类是一个Dict[str, str]对象。这个Dict对象只能使用键"name"和"kind"。这些键映射到用户想要的对应字符串。
- 这个Dict对象只能使用键"name"和"kind"。这些键映射到用户想要的对应字符串。
一个示例column_typeclasses值是{"my_column": [{"name": "my_typeclass_name", "kind": "my_typeclass_kind"}]}。

### 示例：在代码库变换中读取和写入列描述和类型类

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
from transforms.api import transform, Input, Output

# 定义一个转换函数，使用装饰器@transform来指定输入和输出数据集
@transform(
    my_output=Output("ri.foundry.main.dataset.my-output-dataset"),  # 输出数据集的标识符
    my_input=Input("ri.foundry.main.dataset.my-input-dataset"),     # 输入数据集的标识符
)
def my_compute_function(my_input, my_output):
    # 从输入数据集中获取前10行数据
    recent = my_input.dataframe().limit(10)

    # 获取输入数据集的列类型和列描述
    existing_typeclasses = my_input.column_typeclasses
    existing_descriptions = my_input.column_descriptions

    # 将前10行数据写入输出数据集，并保留原有的列描述和列类型
    my_output.write_dataframe(
        recent,
        column_descriptions=existing_descriptions,
        column_typeclasses=existing_typeclasses
    )
```
