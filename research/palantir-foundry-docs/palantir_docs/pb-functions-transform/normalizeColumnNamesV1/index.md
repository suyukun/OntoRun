来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/normalizeColumnNamesV1/

# 标准化列名

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 标准化列名

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

标准化列名为lower_snake_case格式。

变换类别: 数据准备

## 声明的参数

- Dataset- 需要标准化列名的数据集。Table
- 非必填移除特殊字符- 移除列名中的所有@~`!#$%^&=*+':"/?><字符。Literal<Boolean>
## 示例

### 示例 1: 基本情况

参数值:

- Dataset: ri.foundry.main.dataset.a
- 移除特殊字符:null
输入:

| recentlyServiced | tailNumber | _airlineCode |
| --- | --- | --- |
| true | KK-150 | KK |
| false | XB-120 | XB |
| true | MT-190 | MT |

输出:

| recently_serviced | tail_number | airline_code |
| --- | --- | --- |
| true | KK-150 | KK |
| false | XB-120 | XB |
| true | MT-190 | MT |

### 示例 2: 基本情况

参数值:

- Dataset: ri.foundry.main.dataset.a
- 移除特殊字符: true
输入:

| recently^Serviced | tail@Number$ | !airline*Code |
| --- | --- | --- |
| true | KK-150 | KK |
| false | XB-120 | XB |
| true | MT-190 | MT |

输出:

| recently_serviced | tail_number | airline_code |
| --- | --- | --- |
| true | KK-150 | KK |
| false | XB-120 | XB |
| true | MT-190 | MT |

### 示例 3: 边界情况

参数值:

- Dataset: ri.foundry.main.dataset.a
- 移除特殊字符:null
输入:

| columnA. | columnB() | column!C | column,;{}    D | column()e |
| --- | --- | --- | --- | --- |
| foo | bar | fooBar | foo | bar |

输出:

| column_a | column_b | column!_c | column_d | column_e |
| --- | --- | --- | --- | --- |
| foo | bar | fooBar | foo | bar |
