来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/renameColumnsV1/

# 重命名列

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 重命名列

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

重命名一组列。

变换类别: 数据准备, 流行

## 声明的参数

- 输入数据集- 包含要重命名列的源数据集。Table
- 重命名- 从现有列名重命名为新名称。List<Tuple<Column<AnyType>, Literal<字符串>>>
## 示例

### 示例 1: 基本案例

参数值:

- 输入数据集: ri.foundry.main.dataset.a
- 重命名: [(recently_serviced, does_not_require_service)]
输入:

| recently_serviced | tail_number | airline_code |
| --- | --- | --- |
| true | KK-150 | KK |
| false | XB-120 | XB |
| true | MT-190 | MT |

输出:

| does_not_require_service | tail_number | airline_code |
| --- | --- | --- |
| true | KK-150 | KK |
| false | XB-120 | XB |
| true | MT-190 | MT |
