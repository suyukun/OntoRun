来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/notV1/

# Not

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Not

> 支持于：批处理，流处理

支持于：批处理，流处理

返回布尔表达式的否定布尔值。

表达式类别：布尔

## 声明的参数

- 表达式-无描述Expression<Boolean>
输出类型：Boolean

## 例子

### 例子 1: 基本情况

参数值：

- 表达式:boolean
| boolean | 输出 |
| --- | --- |
| true | false |
| false | true |

### 例子 2: 空值情况

参数值：

- 表达式:null
输出：null
