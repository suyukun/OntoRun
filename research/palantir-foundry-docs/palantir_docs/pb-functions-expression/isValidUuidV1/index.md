来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/isValidUuidV1/

# 是否是有效的uuid

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 是否是有效的uuid

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

如果输入是有效的uuid，则返回true。

表达式类别: 布尔值

## 声明的参数

- 表达式- 表示uuid的字符串。Expression<字符串>
输出类型:布尔值

## 示例

### 示例 1: 基本情况

参数值:

- 表达式:uuid
| uuid | 输出 |
| --- | --- |
| 5c5622fe-e30e-4491-99b6-6213be506dec | true |
| 9daf08e9-d2e2-4172-86cc-9102c4c770b3 | true |
| 9DAF08E9-D2E2-4172-86CC-9102C4C770B3 | true |
| UUID with text before 9daf08e9-d2e2-4172-86cc-9102c4c770b3 | false |
| a1-a1-a1-a1-a1 | false |
| not a uuid | false |

### 示例 2: 空值情况

参数值:

- 表达式:uuid
| uuid | 输出 |
| --- | --- |
| null | false |
