来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/repartitionV1/

# 重新分区数据

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 重新分区数据

> 支持于: 批处理

支持于: 批处理

基于非必填提供的分区列和结果分区数量强制对数据进行重新洗牌。如果未提供，将自动确定分区。

变换类别: 其他

## 声明参数

- 数据集- 执行聚合的目标数据集。表格
- 非必填分区数量- 要重新洗牌的分区数量。Literal<Integer>
- 非必填分区列- 指定用于重新分区的列列表。List<Column<AnyType>>