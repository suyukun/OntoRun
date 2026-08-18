来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/projectOnConditionV1/

# 项目条件

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 项目条件

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

通过选择列或将函数应用于列来变换输入数据集。

变换类别: 流行

## 声明的参数

- 条件以筛选列- 输入模式中的所有列将被测试以查看它们是否符合此条件。如果符合，给定表达式将应用于它们。ColumnPredicate
- 数据集- 要应用操作的数据集。Table
- 要应用的表达式- 每个符合条件的列应用一次的表达式。Expression<AnyType>
- 保留剩余列- 保留数据集中未投影的所有列。Literal<Boolean>
- 非必填保留匹配的列- 保留由条件匹配的原始列。如果投影列具有相同名称，原始列将被覆盖。Literal<Boolean>
## 示例

### 示例 1: 基本情况

描述: 根据正则表达式重命名匹配的列。参数值:

- 条件以筛选列:columnHasType(type: String,)
- 数据集: ri.foundry.main.dataset.a
- 要应用的表达式:dynamicAlias(expression:cast(expression:column,type: Integer,),transformer:columnNameRegexReplace(input:column,pattern: str,replace: int,),)
- 保留剩余列: true
- 保留匹配的列: false
输入:

| id | distance_str | factor_str |
| --- | --- | --- |
| 1 | 2000 | 1265 |

输出:

| distance_int | factor_int | id |
| --- | --- | --- |
| 2000 | 1265 | 1 |

### 示例 2: 边缘情况

描述: 您可以选择保留匹配和剩余列。参数值:

- 条件以筛选列:columnHasType(type: String,)
- 数据集: ri.foundry.main.dataset.a
- 要应用的表达式:dynamicAlias(expression:cast(expression:column,type: Integer,),transformer:columnNameConcat(inputs: [column,_as_integer],),)
- 保留剩余列: true
- 保留匹配的列: true
输入:

| id | distance |
| --- | --- |
| 1 | 2000 |

输出:

| distance_as_integer | id | distance |
| --- | --- | --- |
| 2000 | 1 | 2000 |

### 示例 3: 边缘情况

描述: 您可以选择保留条件匹配的列，以及创建的新列。参数值:

- 条件以筛选列:columnHasType(type: String,)
- 数据集: ri.foundry.main.dataset.a
- 要应用的表达式:dynamicAlias(expression:cast(expression:column,type: Integer,),transformer:columnNameConcat(inputs: [column,_as_integer],),)
- 保留剩余列: false
- 保留匹配的列: true
输入:

| id | distance |
| --- | --- |
| 1 | 2000 |

输出:

| distance_as_integer | distance |
| --- | --- |
| 2000 | 2000 |

### 示例 4: 边缘情况

描述: 当保留匹配列但投影列覆盖现有列时，匹配列将不会被保留。为了保留原始列，您必须将投影列重命名为新名称。参数值:

- 条件以筛选列:columnHasType(type: String,)
- 数据集: ri.foundry.main.dataset.a
- 要应用的表达式:cast(expression:column,type: Integer,)
- 保留剩余列: false
- 保留匹配的列: true
输入:

| id | distance |
| --- | --- |
| 1 | 2000 |

输出:

| distance |
| --- |
| 2000 |

### 示例 5: 边缘情况

描述: 您可以选择仅保留投影的列。参数值:

- 条件以筛选列:columnHasType(type: String,)
- 数据集: ri.foundry.main.dataset.a
- 要应用的表达式:dynamicAlias(expression:cast(expression:column,type: Integer,),transformer:columnNameConcat(inputs: [column,_as_integer],),)
- 保留剩余列: false
- 保留匹配的列: false
输入:

| id | distance |
| --- | --- |
| 1 | 2000 |

输出:

| distance_as_integer |
| --- |
| 2000 |

### 示例 6: 边缘情况

描述: 您可以选择仅保留未匹配条件的剩余列。参数值:

- 条件以筛选列:columnHasType(type: String,)
- 数据集: ri.foundry.main.dataset.a
- 要应用的表达式:cast(expression:column,type: Integer,)
- 保留剩余列: true
- 保留匹配的列: false
输入:

| id | distance |
| --- | --- |
| 1 | 2000 |

输出:

| distance | id |
| --- | --- |
| 2000 | 1 |
