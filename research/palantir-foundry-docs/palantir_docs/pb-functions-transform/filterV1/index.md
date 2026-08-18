来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/filterV1/

# 筛选

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 筛选

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

根据指定的筛选条件对输入数据集进行筛选。

变换类别: 常用

## 声明的参数

- 数据集- 需要筛选的数据集。表格
- 筛选条件- 用于筛选的条件。返回 true 的值将被保留，其他值将被移除。表达式<布尔>
## 示例

### 示例 1: 基本情况

参数值:

- 数据集: ri.foundry.main.dataset.a
- 筛选条件:recently_serviced
输入:

| recently_serviced | tail_number |
| --- | --- |
| true | KK-150 |
| false | XB-120 |
| true | MT-190 |

输出:

| recently_serviced | tail_number |
| --- | --- |
| true | KK-150 |
| true | MT-190 |

### 示例 2: 基本情况

描述: 空值被视为 false参数值:

- 数据集: ri.foundry.main.dataset.a
- 筛选条件:recently_serviced
输入:

| recently_serviced | tail_number |
| --- | --- |
| null | KK-150 |
| true | XB-120 |

输出:

| recently_serviced | tail_number |
| --- | --- |
| true | XB-120 |
