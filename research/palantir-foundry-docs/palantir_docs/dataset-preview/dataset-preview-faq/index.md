来源: https://palantir.com/docs/zh/foundry/dataset-preview/dataset-preview-faq/

# 数据集预览常见问题

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 数据集预览常见问题

以下是关于数据集预览的一些常见问题。

有关一般信息，请参阅数据集预览概述。

- CSV因引号字符不匹配而解析失败
- 数据集解析失败，因为一些底层CSV有更多列
- 为什么我下载的数据集在Microsoft Excel中打开时看起来很奇怪？
## CSV因引号字符不匹配而解析失败

当上传一个包含嵌套双引号和嵌入的换行符（\n）字符的CSV时，模式推断将失败，并且您无法使用模式编辑器创建一个有效的模式。

要进行故障排除，请执行以下步骤：

- 将CSV上传到数据集中并选择编辑模式。
- 设置列和引号属性。
- 忽略模式验证出错，并选择保存而不验证，该选项在保存并验证选项旁的下拉菜单中可用。这将创建一个具有正确列定义的模式。
- 在详情选项卡中，以编辑模式打开模式。
- 将dataFrameReaderClass更改为com.palantir.foundry.spark.input.DataSourceDataFrameReader。
- 在"customMetadata"Object中添加以下内容：
```
Copied!1
2
3
4
5
6
7
  "customMetadata": {
    "format": "csv",  // 文件格式为 CSV
    "options": {
      "header": true,  // CSV 文件中包含表头
      "multiLine": true  // 允许 CSV 文件中的字段占用多行
    }
  }
```

返回顶部

## 数据集解析失败因为某些底层CSV具有更多列

当一个数据集由多个CSV组成时（例如，通过数据连接APPEND事务），如果其中一些CSV包含更多列，模式推断将失败。一种选择是忽略不规则行（例如缺少某些列的行）。要做到这一点，请选择编辑模式，展开解析选项部分，并勾选忽略不规则行。

然而，如果您希望保留不规则行并为数据集指定一个标准化的模式，则适用此部分。如果您数据中符合下文假设部分中列出的条件，那么故障排除步骤将生成一个用户定义的标准模式的数据集，其中不规则行将自动填充缺少列为null。

解析失败的症状：

您可能会遇到这样的错误信息：“无法加载预览：解析输入CSV数据时出错。请确保所有数据格式正确。”

在选择编辑模式然后保存并验证后，您也可能会遇到以下错误信息：“您的数据集在x行上验证失败。”

假设：

- 您可以定义所需的模式，例如数据集应具备的所有列名和类型。
您可以定义所需的模式，例如数据集应具备的所有列名和类型。

- 您的模式强制严格的列顺序。例如，如果您希望数据集包含和显示列_{a, b, c}_，则底层CSV可以具有如下列结构：
您的模式强制严格的列顺序。例如，如果您希望数据集包含和显示列_{a, b, c}_，则底层CSV可以具有如下列结构：

- {a}
- {a, b}
但不能具有如下列结构：

- {b, a}
- 如果底层CSV具有第_(n+1)_ 列，则其必须具有所有前面的_n_列。例如，如果您希望数据集包含和显示列_{a, b, c, d}_，则底层CSV可以具有如下列结构：
- {a}
- {a, b}
- {a, b, c}
但不能具有如下列结构：

- {b, c, d}
- {a, c, d}
- {a, b, d}
以下是一个故障排除步骤适用且有用的案例示例：

通过APPEND事务定期将CSV添加到数据集中。某天，添加了一个新列，并成为CSV中的新最后一列。在数据集中，所有先前追加的CSV的行应该具有新列，字段值自动填充为null，而不是被视为不规则。

故障排除步骤不会复制mergeSchema选项的功能，该选项适用于原始Parquet数据集（这些数据集使用com.palantir.foundry.spark.input.ParquetDataFrameReader作为dataFrameReaderClass进行解析）。需要用户编写变换以在原始CSV数据集上复制此类功能。

要进行故障排除，请执行以下步骤：

- 在详情选项卡中，打开模式选项卡，并选择编辑
- 修改fieldSchemaList以确保其包含数据集应具备的所有列。例如，如果数据集应具有列_{a, b, c}_，且全部为整数类型，则fieldSchemaList可能如下所示：
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
  "fieldSchemaList": [
    {
      "type": "INTEGER",  // 字段类型为整数
      "name": "a",  // 字段名称为a
      "nullable": null,  // 是否可为空，当前为null未指定
      "userDefinedTypeClass": null,  // 用户定义的类型类，当前为null未指定
      "customMetadata": {},  // 自定义元数据，当前为空对象
      "arraySubtype": null,  // 数组子类型，当前为null未指定
      "precision": null,  // 精度，当前为null未指定
      "scale": null,  // 标度，当前为null未指定
      "mapKeyType": null,  // 映射键类型，当前为null未指定
      "mapValueType": null,  // 映射值类型，当前为null未指定
      "subSchemas": null  // 子模式，当前为null未指定
    },
    {
      "type": "INTEGER",  // 字段类型为整数
      "name": "b",  // 字段名称为b
      "nullable": null,  // 是否可为空，当前为null未指定
      "userDefinedTypeClass": null,  // 用户定义的类型类，当前为null未指定
      "customMetadata": {},  // 自定义元数据，当前为空对象
      "arraySubtype": null,  // 数组子类型，当前为null未指定
      "precision": null,  // 精度，当前为null未指定
      "scale": null,  // 标度，当前为null未指定
      "mapKeyType": null,  // 映射键类型，当前为null未指定
      "mapValueType": null,  // 映射值类型，当前为null未指定
      "subSchemas": null  // 子模式，当前为null未指定
    },
    {
      "type": "INTEGER",  // 字段类型为整数
      "name": "c",  // 字段名称为c
      "nullable": null,  // 是否可为空，当前为null未指定
      "userDefinedTypeClass": null,  // 用户定义的类型类，当前为null未指定
      "customMetadata": {},  // 自定义元数据，当前为空对象
      "arraySubtype": null,  // 数组子类型，当前为null未指定
      "precision": null,  // 精度，当前为null未指定
      "scale": null,  // 标度，当前为null未指定
      "mapKeyType": null,  // 映射键类型，当前为null未指定
      "mapValueType": null,  // 映射值类型，当前为null未指定
      "subSchemas": null  // 子模式，当前为null未指定
    }
  ],
```

- 更改"dataFrameReaderClass"及其嵌套的customMetadataObject，使您的模式 JSON 的结尾看起来如下所示：
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
"dataFrameReaderClass": "com.palantir.foundry.spark.input.DataSourceDataFrameReader",
  "customMetadata": {
    "format": "csv",  // 指定数据格式为 CSV
    "options": {
      "multiLine": true,  // 支持多行数据
      "header": true,  // 第一行作为表头
      "mode": "PERMISSIVE"  // 解析模式为宽容模式，允许有错误的输入并尝试解析
    }
  }
}
```

- 选择保存。
返回顶部

## 为什么我下载的数据集在 Microsoft Excel 中打开时看起来很奇怪？

当从平台导出数据集时，有些文件在打开时可能会显得压缩。在某些地区观察到了这个问题，原因是 Excel 使用的默认分隔符。要解决此问题，您需要更改导出设置中的分隔符模式：

- 在 Excel 中打开文件。
- 选择功能区中的数据选项卡。
- 在数据工具组中选择分列选项。
- 在文本分列向导窗口中，选择分隔符号选项，然后点击下一步。
- 在分隔符部分，选择您想使用的分隔符（如逗号、分号、制表符）。
- 选择下一步然后完成以完成该过程。
返回顶部
