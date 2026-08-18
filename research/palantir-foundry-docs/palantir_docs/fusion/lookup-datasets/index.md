来源: https://palantir.com/docs/zh/foundry/fusion/lookup-datasets/

# 查找数据集

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 查找数据集

Foundry 数据集通过lookup公式导入到 Fusion 中。这些公式类似于微软的 VLOOKUP 函数，但用于从 Foundry 数据集中引入实时数据，而不是电子表格。

您可以使用查找和使用数据面板搜索数据并生成这些公式 - 更多详情请参见查找和使用数据。您也可以自行编写这些公式，并在其他公式中嵌套使用它们。

以下是现有的lookup公式：

- lookup: 从数据集列中返回一组带有非必填筛选的值。单个结果作为一个值返回，而多个结果返回为一个数组。例如，=lookup(dataset_name, column_name, filter_column_1, filter_value_1, filter_column_2, filter_value_2)。
- lookup_array: 与lookup相同，除单个结果返回为一个长度为1的数组。
- lookup_distinct: 返回数据集列中的不重复值集合，带有非必填筛选。
- lookup_dropdown: 返回一个下拉菜单，其中可选值为查找的结果。
- lookup_sorted: 返回按数据集列升序或降序排序的一组值。
- lookup_schema: 返回数据集模式的数组。
您可以在函数库中找到关于这些特定公式的更多详情。

查找（例如sum(lookup(...))）限制为 2,000 个结果。如果您的工作流程需要更多元素，您应首先在 Contour 中进行聚合或透视，然后将结果表保存为可以在 Fusion 中索引的数据集。

lookup中的任何参数都可以是电子表格中的单元格引用。这允许您创建依赖于用户输入、派生单元格或其他查找的动态查找。

要展开lookup结果的数组，可以Shift+拖动该单元格到单个单元格中。

带有单元格引用的lookup调用可以拖动或复制/粘贴到电子表格的其他部分以获得特定上下文的结果。
