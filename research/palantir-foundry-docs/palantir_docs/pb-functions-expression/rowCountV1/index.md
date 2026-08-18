来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/rowCountV1/

# 行计数

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 行计数

> 支持于: 批处理, 流式处理

支持于: 批处理, 流式处理

计算组中非空行的数量。

表达式类别: 聚合

## 声明的参数

- 非必填表达式-无描述Expression<AnyType>
输出类型:Long

## 示例

### 示例 1: 基本情况

参数值:

- 表达式:values
给定输入表:

| values |
| --- |
| 2 |
| 4 |
| 3 |

输出:3

### 示例 2: 空值情况

参数值:

- 表达式:values
给定输入表:

| values |
| --- |
| 2 |
| null |
| 3 |

输出:2
