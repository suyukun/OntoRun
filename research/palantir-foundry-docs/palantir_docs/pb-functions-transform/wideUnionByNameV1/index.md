来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/wideUnionByNameV1/

# 按名称宽合并

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 按名称宽合并

> 支持于：批处理，流处理

支持于：批处理，流处理

在其列名的超集上将一组数据集合并在一起，当缺少列时添加空值。

变换类别：合并

## 声明的参数

- 要合并的数据集- 被合并在一起的数据集。List<Table>
## 示例

### 示例 1: 基本案例

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

| recently_serviced | tail_number | airline_code |
| --- | --- | --- |
| true | KK-150 | null |
| false | XB-120 | null |
| true | MT-190 | null |
| true | AA-200 | AA |
| true | BN-435 | BN |
| true | BN-111 | BN |
