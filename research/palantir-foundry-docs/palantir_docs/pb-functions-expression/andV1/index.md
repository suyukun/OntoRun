来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/andV1/

# And

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# And

> 支持于：批处理，流处理

支持于：批处理，流处理

如果所有指定条件都为true，则返回true。空值被视为false。

表达式类别：布尔

## 声明的参数

- 条件- 用于计算输出的条件列表。List<Expression<Boolean>>
输出类型：Boolean

## 示例

### 示例 1: 基本情况

参数值：

- 条件: [left_boolean,right_boolean]
| left_boolean | right_boolean | 输出 |
| --- | --- | --- |
| true | true | true |
| true | false | false |
| false | true | false |
| false | false | false |

### 示例 2: 空值情况

参数值：

- 条件: [null, true]
输出：false
