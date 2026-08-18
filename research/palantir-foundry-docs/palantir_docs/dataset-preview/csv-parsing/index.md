来源: https://palantir.com/docs/zh/foundry/dataset-preview/csv-parsing/

# CSV解析

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# CSV解析

Foundry支持CSV数据集。这些是包含CSV格式文件的数据集。

CSV格式可以使用不同的分隔符、引号字符和转义字符。为了解决这个问题，您可以定义控制CSV文件如何解析的参数。这些参数存储在数据集的模式中。Foundry将使用推断来建议一组合理的参数，但结果应进行验证并在必要时进行更改。

## 在Foundry中解析

Foundry的CSV数据集通常在模式中将TextDataFrameReader定义为它们的dataFrameReaderClass。这支持一组自定义参数，可以帮助有效地处理混乱的数据。在执行时，这委托给Spark CSV DataFrameReader ↗以获得最佳的性能和可靠性。

## 配置

在Foundry中，您可以通过导航到详情选项卡并选择模式，在数据集预览应用程序中查看任何数据集的模式。有关模式的更多详细信息，请参阅数据集文档。

可以在编辑模式UI中操作CSV模式，该UI可以从查看预览选项卡时的数据集预览中获得。这将有助于可视化可用的选项以及它们如何影响输出数据集。在CSV格式特别不规范的情况下，您可能需要手动编辑模式以获得所需的输出。

### TextDataFrameReader选项

要在模式中手动配置TextDataFrameReader选项，您可以导航到数据集预览的详情选项卡中的模式页面并选择编辑。在模式的底部，应该有如下的部分：

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
  "dataFrameReaderClass": "com.palantir.foundry.spark.input.TextDataFrameReader",
  // 指定数据框读取器类，用于读取文本数据

  "customMetadata": {
    "textParserParams": {
      "parser": "CSV_PARSER", // 使用CSV解析器
      "charsetName": "UTF-8", // 字符集为UTF-8
      "fieldDelimiter": ",", // 字段分隔符为逗号
      "recordDelimiter": "\n", // 记录分隔符为换行符
      "quoteCharacter": "\"", // 引号字符为双引号
      "dateFormat": {}, // 日期格式配置（当前为空）
      "skipLines": 1, // 跳过文件开头的1行
      "jaggedRowBehavior": "THROW_EXCEPTION", // 对于不规则行的处理方式为抛出异常
      "parseErrorBehavior": "THROW_EXCEPTION", // 解析错误时抛出异常
      "addFilePath": false, // 不添加文件路径
      "addFilePathInsteadOfUri": false, // 不用文件路径代替URI
      "addImportedAt": false, // 不添加导入时间
      "initialReadTimeout": "1 hour" // 初始读取超时时间设置为1小时
    }
  }
}
```

以下是TextDataFrameReader可用的选项：

| 属性 | 目的 | 接受的值 | 是否必需 | 支持的解析器 |
| --- | --- | --- | --- | --- |
| parser | 要使用的解析器类型。 | CSV_PARSER, MULTILINE_CSV_PARSER, SIMPLE_PARSER, SINGLE_COLUMN_PARSER | 是 | N/A |
| nullValues | 应解析为null的值。 | 一个字符串列表 | 是 | 全部 |
| fieldDelimiter | 用于将记录拆分为多个字段的分隔符字符。 | 一个字符的字符串 | 否，默认为 , (逗号) | CSV_PARSER, MULTILINE_CSV_PARSER, SIMPLE_PARSER |
| recordDelimiter | 用于将CSV文件拆分为多个记录的行尾符号。 | 以换行符结尾的字符串 | 否，默认为 \n (换行符) | CSV_PARSER, MULTILINE_CSV_PARSER |
| quoteCharacter | 用于CSV解析的引用字符。 | 一个字符的字符串 | 否，默认为 " (双引号) | CSV_PARSER, MULTILINE_CSV_PARSER |
| dateFormat | 用于某些列的日期解析格式字符串。 | 一个将列名映射到JodaTime DateTimeFormat模式的映射 | 否，默认为空映射 | CSV_PARSER, MULTILINE_CSV_PARSER, SIMPLE_PARSER |
| skipLines | 在解析每个文件的开始时跳过的行数。 | 一个非负数 | 否，默认为0 | 全部 |
| jaggedRowBehavior | 当列数多于或少于标题中指定的类型时的行为。 | THROW_EXCEPTION, DROP_ROW | 否，默认为THROW_EXCEPTION | N/A |
| parseErrorBehavior | 当值解析为标题中指定的请求类型失败时的行为。 | THROW_EXCEPTION, REPLACE_WITH_NULL | 否，默认为THROW_EXCEPTION | N/A |
| addFilePath | 每行都增加一个文件路径。 | 布尔值 | 否，默认为false | 全部 |
| addImportedAt | 每行都增加一个导入时间。 | 布尔值 | 否，默认为false | 全部 |
| initialReadTimeout | 限制解析器等待读取首行的时间。 | 人类可读的时长 | 否，默认为1小时 | 全部 |

### Spark CSV 选项

如果您已经熟悉Spark CSV DataFrameReader，可以在customMetadata中将dataFrameReaderClass配置为DataSourceDataFrameReader，并将format配置为csv。

请参阅Spark CSV DataFrameReader 文档 ↗以获取支持的选项列表。您可以像这样添加配置为键值对：

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
  "dataFrameReaderClass": "com.palantir.foundry.spark.input.DataSourceDataFrameReader", // 用于指定DataFrame读取类
  "customMetadata": {
    "format": "csv", // 指定文件格式为CSV
    "options": {
      "unescapedQuoteHandling": "STOP_AT_DELIMITER", // 指定引号处理方式为在分隔符处停止
      "multiline": true, // 允许多行记录
      ...
    }
  }
```

请注意，上述模式选项仅适用于由CSV文件构建的数据集。
