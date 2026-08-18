来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/narrowUnionByNameV1/

# 按名称缩小合并

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 按名称缩小合并

> 支持于: 批量

支持于: 批量

将一组数据集按其列名的交集合并在一起，所有输入数据集中不存在的列将被移除。

变换类别: 合并

## 声明的参数

- 要合并的数据集- 被合并在一起的数据集。List<Table>
## 示例

### 示例 1: 基本情况

参数值:

- 要合并的数据集: [ri.foundry.main.dataset.a, ri.foundry.main.dataset.b]
输入:ri.foundry.main.dataset.a

| recently_serviced | tail_number |
| --- | --- |
| true | KK-150 |
| false | XB-120 |
| true | MT-190 |

ri.foundry.main.dataset.b

| recently_serviced | tail_number | airline_code |
| --- | --- | --- |
| true | AA-200 | AA |
| true | BN-435 | BN |
| true | BN-111 | BN |

输出:

| recently_serviced | tail_number |
| --- | --- |
| true | KK-150 |
| false | XB-120 |
| true | MT-190 |
| true | AA-200 |
| true | BN-435 |
| true | BN-111 |
