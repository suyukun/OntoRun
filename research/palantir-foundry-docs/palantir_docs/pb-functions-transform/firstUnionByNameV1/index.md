来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/firstUnionByNameV1/

# 按名称首次合并

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 按名称首次合并

> 支持于: 批处理

支持于: 批处理

将一组数据集按第一个数据集的列合并在一起，当缺少列时添加空值。第一个数据集中不存在的列将被移除。

变换类别: 合并

## 声明的参数

- 要合并的数据集- 被合并在一起的数据集。List<Table>
## 示例

### 示例 1: 基本案例

参数值:

- 要合并的数据集: [ri.foundry.main.dataset.a, ri.foundry.main.dataset.b]
输入:ri.foundry.main.dataset.a

| recently_serviced | tail_number | airline_code |
| --- | --- | --- |
| true | KK-150 | KK |
| false | XB-120 | XB |
| true | MT-190 | MT |

ri.foundry.main.dataset.b

| recently_serviced | tail_number | home_country |
| --- | --- | --- |
| true | AA-200 | US |
| true | BN-435 | UK |
| true | BN-111 | UK |

输出:

| recently_serviced | tail_number | airline_code |
| --- | --- | --- |
| true | KK-150 | KK |
| false | XB-120 | XB |
| true | MT-190 | MT |
| true | AA-200 | null |
| true | BN-435 | null |
| true | BN-111 | null |

### 示例 2: 基本案例

参数值:

- 要合并的数据集: [ri.foundry.main.dataset.a, ri.foundry.main.dataset.b, ri.foundry.main.dataset.c]
输入:ri.foundry.main.dataset.a

| recently_serviced | tail_number | airline_code |
| --- | --- | --- |
| true | KK-150 | KK |
| false | XB-120 | XB |
| true | MT-190 | MT |

ri.foundry.main.dataset.b

| home_country | tail_number | recently_serviced |
| --- | --- | --- |
| US | AA-200 | true |
| UK | BN-435 | true |
| UK | BN-111 | true |

ri.foundry.main.dataset.c

| home_country | tail_number |
| --- | --- |
| DK | SK-908 |
| CH | LX-17 |
| IN | AI-144 |

输出:

| recently_serviced | tail_number | airline_code |
| --- | --- | --- |
| true | KK-150 | KK |
| false | XB-120 | XB |
| true | MT-190 | MT |
| true | AA-200 | null |
| true | BN-435 | null |
| true | BN-111 | null |
| null | SK-908 | null |
| null | LX-17 | null |
| null | AI-144 | null |

### 示例 3: 基本案例

参数值:

- 要合并的数据集: [ri.foundry.main.dataset.a, ri.foundry.main.dataset.b]
输入:ri.foundry.main.dataset.a

| recently_serviced | tail_number | airline_code |
| --- | --- | --- |
| true | KK-150 | KK |
| false | XB-120 | XB |
| true | MT-190 | MT |

ri.foundry.main.dataset.b

|
|

输出:

| recently_serviced | tail_number | airline_code |
| --- | --- | --- |
| true | KK-150 | KK |
| false | XB-120 | XB |
| true | MT-190 | MT |

### 示例 4: 空案例

参数值:

- 要合并的数据集: [ri.foundry.main.dataset.a, ri.foundry.main.dataset.b]
输入:ri.foundry.main.dataset.a

| recently_serviced | tail_number | airline_code |
| --- | --- | --- |
| null | null | null |

ri.foundry.main.dataset.b

| recently_serviced | tail_number | home_country |
| --- | --- | --- |
| null | null | null |

输出:

| recently_serviced | tail_number | airline_code |
| --- | --- | --- |
| null | null | null |
| null | null | null |

### 示例 5: 边缘案例

参数值:

- 要合并的数据集: [ri.foundry.main.dataset.a, ri.foundry.main.dataset.b]
输入:ri.foundry.main.dataset.a

| recently_serviced | tail_number | airline_code |
| --- | --- | --- |

ri.foundry.main.dataset.b

| recently_serviced | tail_number | home_country |
| --- | --- | --- |

输出:

| recently_serviced | tail_number | airline_code |
| --- | --- | --- |

### 示例 6: 边缘案例

参数值:

- 要合并的数据集: [ri.foundry.main.dataset.a]
输入:

| recently_serviced | tail_number | airline_code |
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
