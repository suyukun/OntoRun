来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/unpivotV1/

# 反透视

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 反透视

> 支持于：批处理，流处理

支持于：批处理，流处理

执行与透视相反的操作...

变换类别: 聚合, 流行

## 声明参数

- 要反透视的列- 要反透视的列列表。List<Column<T>>
- 数据集- 要执行反透视的数据集。Table
- 输出反透视列名- 提供给包含反透视列的输出列的列名。Literal<字符串>
- 反透视值输出列名- 提供给包含反透视值的输出列的列名。Literal<字符串>
类型变量界限:T 接受 AnyType

## 示例

### 示例 1: 基本情况

参数值:

- 要反透视的列: [new_york_miles,london_miles]
- 数据集: ri.foundry.main.dataset.a
- 输出反透视列名: city
- 反透视值输出列名: miles
输入:

| airline | new_york_miles | london_miles |
| --- | --- | --- |
| foundry airways | 1000 | 6000 |
| new air | null | 8000 |

输出:

| city | miles | airline |
| --- | --- | --- |
| new_york_miles | 1000 | foundry airways |
| london_miles | 6000 | foundry airways |
| new_york_miles | null | new air |
| london_miles | 8000 | new air |
