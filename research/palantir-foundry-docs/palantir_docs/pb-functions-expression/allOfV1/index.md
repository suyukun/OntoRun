来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/allOfV1/

# 全部

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 全部

> 支持于: 批处理

支持于: 批处理

计算一个聚合的布尔值'和'。空值被视为false。

表达式类别: 聚合

## 声明的参数

- 表达式- 计算'all'的列。Expression<Boolean>
输出类型:Boolean

## 示例

### 示例 1: 基本情况

参数值:

- 表达式:values
给定输入表:

| values |
| --- |
| true |
| false |
| true |

输出:false

### 示例 2: 空值情况

参数值:

- 表达式:values
给定输入表:

| values |
| --- |
| true |
| true |
| null |

输出:false
