来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/selectV1/

# 选择列

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 选择列

> 支持于：批处理，流处理

支持于：批处理，流处理

从输入数据集中选择一组列。

变换类别：流行

## 声明的参数

- 要选择的列- 要选择的列列表。List<Column<AnyType>>
- 输入数据集- 包含要选择列的源数据集。Table