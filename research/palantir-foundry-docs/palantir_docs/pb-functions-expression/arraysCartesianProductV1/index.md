来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/arraysCartesianProductV1/

# 数组笛卡尔积

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 数组笛卡尔积

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

计算数组的笛卡尔积。

表达式类别: 数组

## 声明的参数

- 表达式- 要转换的列。List<Expression<Array<AnyType>>>
输出类型:Array<Struct>

## 示例

### 示例 1: 基本案例

参数值:

- 表达式: [first,second]
| first | second | 输出 |
| --- | --- | --- |
| [ [ {s1: 1,}, {s1: 2,} ], [ {s1: 3,} ] ] | [ [ {s2: 4,}, {s2: 5,} ], [ {s2: 6,} ] ] | [ {first: [ {s1: 1,}, {s1: 2,} ],second: ... |

### 示例 2: 基本案例

参数值:

- 表达式: [first,second]
| first | second | 输出 |
| --- | --- | --- |
| [ 1, 2 ] | [ 3, 4 ] | [ {first: 1,second: 3,}, {first: 1,second: ... |

### 示例 3: 基本案例

参数值:

- 表达式: [first,second,third]
| first | second | third | 输出 |
| --- | --- | --- | --- |
| [ 1, 2 ] | [ word, a ] | [ {s1: 1,}, {s1: 2,} ] | [ {first: 1,second: word,third: {s1: 1,}... |

### 示例 4: 空值案例

参数值:

- 表达式: [first,second]
| first | second | 输出 |
| --- | --- | --- |
| [ 1,null] | [null, 4 ] | [ {first: 1,second:null,}, {first: 1,second: ... |
| [ 1, 2 ] | null | [  ] |
| [  ] | [  ] | [  ] |
| null | null | [  ] |
