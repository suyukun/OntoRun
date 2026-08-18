来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/createStructV2/

# 创建结构体列

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 创建结构体列

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

将多个列合并为单个结构化列。

表达式类别: 结构体

## 声明的参数

- 结构体元素- 用于创建结构体的列列表。List<Expression<AnyType>>
输出类型:结构体

## 示例

### 示例 1: 基础案例

参数值:

- 结构体元素: [tail_number,id]
| tail_number | id | 输出 |
| --- | --- | --- |
| MT-112 | 1 | {id: 1,tail_number: MT-112,} |
| XB-123 | 2 | {id: 2,tail_number: XB-123,} |
| PA-654 | 3 | {id: 3,tail_number: PA-654,} |

### 示例 2: 基础案例

参数值:

- 结构体元素: [tail_number,id]
| tail_number | id | 输出 |
| --- | --- | --- |
| null | 1 | {id: 1,tail_number:null,} |
| XB-123 | null | {id:null,tail_number: XB-123,} |
| null | null | {id:null,tail_number:null,} |
