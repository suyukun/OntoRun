来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/approximatePercentileV1/

# 近似百分位数

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 近似百分位数

> 支持于: 批处理

支持于: 批处理

返回表达式的近似百分位数，该值是排序表达式值（从小到大排序）中最小的值，使得不超过指定百分比的表达式值小于或等于该值。

表达式类别: 聚合

## 声明的参数

- Expression- 输入表达式。Expression<Numeric>
- Percentiles- 要计算的百分位数，如果给定单个值，输出将是双精度数，如果提供多个值，输出将是表示每个百分位数的双精度数数组。必须在0到1之间。List<Literal<Double>>
- 非必填Accuracy- 精度参数（默认: 10000）是一个正整数，它以内存为代价控制近似精度。更高的精度值产生更好的精度，1.0/精度是近似的相对误差。Literal<Integer>
输出类型:Array<Numeric> | Byte | Decimal | Double | Float | Integer | Long | Short

## 例子

### 例子 1: 基本情况

参数值:

- Expression:values
- Percentiles: [0.5]
- Accuracy:null
给定输入表:

| values |
| --- |
| 2 |
| 4 |
| 3 |

输出:3

### 例子 2: 基本情况

参数值:

- Expression:values
- Percentiles: [0.33, 0.5, 0.66]
- Accuracy:null
给定输入表:

| values |
| --- |
| 2 |
| 4 |
| 3 |
| 5 |
| 1 |

输出:[ 2, 3, 4 ]

### 例子 3: 空值情况

参数值:

- Expression:values
- Percentiles: [0.5]
- Accuracy:null
给定输入表:

| values |
| --- |
| null |
| null |
| null |

输出:null

### 例子 4: 空值情况

参数值:

- Expression:values
- Percentiles: [0.5]
- Accuracy:null
给定输入表:

| values |
| --- |
| null |
| 1 |
| 3 |

输出:1
