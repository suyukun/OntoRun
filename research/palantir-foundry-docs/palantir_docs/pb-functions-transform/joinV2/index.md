来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/joinV2/

# 合并

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 合并

> 支持于：批处理，流处理

支持于：批处理，流处理

合并左侧和右侧的数据集输入。

变换类别：合并

## 声明的参数

- 合并键- 左侧和右侧输入中用于合并的列列表。List<Tuple<Column<AnyType>, Column<AnyType>>>
- 合并类型- 执行的合并类型。Enum<反合并, 交叉合并, 全外合并, 内合并, 左合并, 右合并, 半合并>
- 左侧数据集- 在合并中使用的左侧数据集。Table
- 右侧数据集- 在合并中使用的右侧数据集。Table