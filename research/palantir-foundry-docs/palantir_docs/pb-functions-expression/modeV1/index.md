来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/modeV1/

# 模式

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 模式

> 支持于: 批处理

支持于: 批处理

计算列中值的众数。

表达式类别: 聚合

## 声明的参数

- 表达式- 计算众数的列。Expression<字符串>
类型变量界限:字符串接受字符串

输出类型:字符串

## 示例

### 示例 1: 基本情况

参数值:

- 表达式:values
给定输入表:

| values |
| --- |
| a |
| b |
| b |
| b |
| c |
| c |
| d |

输出:b

### 示例 2: 空情况

参数值:

- 表达式:values
给定输入表:

| values |
| --- |

输出:null

### 示例 3: 空情况

参数值:

- 表达式:values
给定输入表:

| values |
| --- |
| a |
| null |
| null |
| null |
| c |
| c |
| d |

输出:c
