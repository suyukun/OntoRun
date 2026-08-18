来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/rollUpV1/

# 汇总

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 汇总

> 支持于: 批处理

支持于: 批处理

在不同粒度级别上对输入数据集执行指定的聚合，提供中间和超级聚合。

变换类别: 聚合

## 声明的参数

- 聚合- 在数据集上执行的聚合列表。List<Expression<AnyType>>
- 数据集- 要进行汇总的数据集。Table
- 汇总列- 在聚合时用于汇总数据集的列列表。如果为空，则不应用汇总。List<Column<AnyType>>
## 示例

### 示例 1: 基本情况

参数值:

- 聚合: [alias(alias: max_price,expression:max(expression:price,),)]
- 数据集: ri.foundry.main.dataset.rollupBaseCase
- 汇总列: [city]
输入:

| 城市 | 型号 | 价格 | 商店 |
| --- | --- | --- | --- |
| 伦敦 | 新手机 | 900.0 | MegaMart |
| 伦敦 | 新手机 | 850.75 | AA |
| 伦敦 | 新手机 | 870.75 | ABC Zone |
| 旧金山 | 新手机 | 1000.0 | Prescos |
| 旧金山 | 新手机 | 950.25 | XZY Force |
| 旧金山 | 新手机 | 1105.7 | Phone Mart |
| 伦敦 | forestX 20 | 750.1 | MegaMart |
| 伦敦 | forestX 20 | 690.0 | AA |
| 伦敦 | forestX 20 | 730.0 | ABC Zone |
| 旧金山 | forestX 20 | 890.4 | Prescos |
| 旧金山 | forestX 20 | 900.1 | XZY Force |
| 旧金山 | forestX 20 | 1050.75 | Phone Mart |

输出:

| 城市 | 最高价格 |
| --- | --- |
| 伦敦 | 900.0 |
| 旧金山 | 1105.7 |
| null | 1105.7 |

### 示例 2: 基本情况

参数值:

- 聚合: [alias(alias: mean_price,expression:mean(expression:price,),)]
- 数据集: ri.foundry.main.dataset.rollupBaseCase
- 汇总列: [city,model]
输入:

| 城市 | 型号 | 价格 | 商店 |
| --- | --- | --- | --- |
| 伦敦 | 新手机 | 900.0 | MegaMart |
| 伦敦 | 新手机 | 850.75 | AA |
| 伦敦 | 新手机 | 870.75 | ABC Zone |
| 旧金山 | 新手机 | 1000.0 | Prescos |
| 旧金山 | 新手机 | 950.25 | XZY Force |
| 旧金山 | 新手机 | 1105.7 | Phone Mart |
| 伦敦 | forestX 20 | 750.1 | MegaMart |
| 伦敦 | forestX 20 | 690.0 | AA |
| 伦敦 | forestX 20 | 730.0 | ABC Zone |
| 旧金山 | forestX 20 | 890.4 | Prescos |
| 旧金山 | forestX 20 | 900.1 | XZY Force |
| 旧金山 | forestX 20 | 1050.75 | Phone Mart |

输出:

| 城市 | 型号 | 平均价格 |
| --- | --- | --- |
| 伦敦 | 新手机 | 873.8333333333334 |
| 伦敦 | forestX 20 | 723.3666666666667 |
| 伦敦 | null | 798.6 |
| 旧金山 | 新手机 | 1018.65 |
| 旧金山 | forestX 20 | 947.0833333333334 |
| 旧金山 | null | 982.8666666666667 |
| null | null | 890.7333333333335 |

### 示例 3: 基本情况

参数值:

- 聚合: [alias(alias: max_price,expression:max(expression:plan_prices,),)]
- 数据集: ri.foundry.main.dataset.rollupComplexCase
- 汇总列: [model]
输入:

| 城市 | 型号 | 计划价格 | 商店 |
| --- | --- | --- | --- |
| 伦敦 | 新手机 | [ 900.0, 1080.23, 899.99 ] | MegaMart |
| 伦敦 | 新手机 | [ 850.75, 800.78, 999.99 ] | AA |
| 伦敦 | 新手机 | [ 870.75, 775.0, 804.48 ] | ABC Zone |
| 旧金山 | 新手机 | [ 910.0, 1030.23, 1100.5 ] | Prescos |
| 旧金山 | 新手机 | [ 1020.0, 989.99, 1130.0 ] | XZY Force |
| 旧金山 | 新手机 | [ 1020.0, 1065.25, 1110.99 ] | Phone Mart |
| 伦敦 | forestX 20 | [ 738.5, 701.25, 834.0 ] | MegaMart |
| 伦敦 | forestX 20 | [ 703.75, 821.0, 712.5 ] | AA |
| 伦敦 | forestX 20 | [ 692.0, 787.5, 841.75 ] | ABC Zone |
| 旧金山 | forestX 20 | [ 1003.25, 997.75, 893.5 ] | Prescos |
| 旧金山 | forestX 20 | [ 981.5, 872.25, 1035.0 ] | XZY Force |
| 旧金山 | forestX 20 | [ 928.0, 995.25, 1098.5 ] | Phone Mart |

输出:

| 型号 | 最高价格 |
| --- | --- |
| 新手机 | [ 1020.0, 1065.25, 1110.99 ] |
| forestX 20 | [ 1003.25, 997.75, 893.5 ] |
| null | [ 1020.0, 1065.25, 1110.99 ] |

### 示例 4: 空值情况

参数值:

- 聚合: [alias(alias: max_price,expression:max(expression:price,),)]
- 数据集: ri.foundry.main.dataset.rollupNullCase
- 汇总列: [city,model]
输入:

| 城市 | 型号 | 价格 | 商店 |
| --- | --- | --- | --- |
| 伦敦 | 新手机 | null | MegaMart |
| 伦敦 | 新手机 | 850.75 | AA |
| 伦敦 | 新手机 | 870.75 | ABC Zone |
| 旧金山 | 新手机 | null | Prescos |
| 旧金山 | 新手机 | null | XZY Force |
| 旧金山 | 新手机 | null | Phone Mart |
| 伦敦 | forestX 20 | 750.1 | MegaMart |
| 伦敦 | forestX 20 | 690.0 | AA |
| 伦敦 | forestX 20 | null | ABC Zone |
| 旧金山 | forestX 20 | 890.4 | Prescos |
| 旧金山 | forestX 20 | null | XZY Force |
| 旧金山 | forestX 20 | 1050.75 | Phone Mart |

输出:

| 城市 | 型号 | 最高价格 |
| --- | --- | --- |
| 伦敦 | 新手机 | 870.75 |
| 伦敦 | forestX 20 | 750.1 |
| 伦敦 | null | 870.75 |
| 旧金山 | 新手机 | null |
| 旧金山 | forestX 20 | 1050.75 |
| 旧金山 | null | 1050.75 |
| null | null | 1050.75 |

### 示例 5: 边界情况

参数值:

- 聚合: [alias(alias: mean_price,expression:mean(expression:price,),)]
- 数据集: ri.foundry.main.dataset.rollupBaseCase
- 汇总列: []
输入:

| 城市 | 型号 | 价格 | 商店 |
| --- | --- | --- | --- |
| 伦敦 | 新手机 | 900.0 | MegaMart |
| 伦敦 | 新手机 | 850.75 | AA |
| 伦敦 | 新手机 | 870.75 | ABC Zone |
| 旧金山 | 新手机 | 1000.0 | Prescos |
| 旧金山 | 新手机 | 950.25 | XZY Force |
| 旧金山 | 新手机 | 1105.7 | Phone Mart |
| 伦敦 | forestX 20 | 750.1 | MegaMart |
| 伦敦 | forestX 20 | 690.0 | AA |
| 伦敦 | forestX 20 | 730.0 | ABC Zone |
| 旧金山 | forestX 20 | 890.4 | Prescos |
| 旧金山 | forestX 20 | 900.1 | XZY Force |
| 旧金山 | forestX 20 | 1050.75 | Phone Mart |

输出:

| 平均价格 |
| --- |
| 890.7333333333335 |

### 示例 6: 边界情况

参数值:

- 聚合: [alias(alias: max_price,expression:max(expression:price,),)]
- 数据集: ri.foundry.main.dataset.rollupEmptyCase
- 汇总列: [city,model]
输入:

| 城市 | 型号 | 价格 | 商店 |
| --- | --- | --- | --- |

输出:

| 城市 | 型号 | 最高价格 |
| --- | --- | --- |
