来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/getManyStructFieldsV1/

# 提取多个结构字段

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 提取多个结构字段

> 支持于: 批处理

支持于: 批处理

从结构中提取多个字段。原始结构将被删除。

变换类别: 结构

## 声明的参数

- Dataset- 包含结构列的数据集。表
- Locators- 用于访问结构中字段的定位器。列表<元组<结构定位器, 字面量<字符串>>>
- Struct- 输入结构。列<结构>
## 示例

### 示例 1: 基本情况

参数值:

- Dataset: ri.foundry.main.dataset.a
- Locators: [(airline.name, airline), (tail_no, tail_number)]
- Struct:raw
输入:

| raw |
| --- |
| {airline: {id: NA,name: new air,},tail_no: NA-123,} |
| {airline: {id: FA,name: foundry airways,},tail_no: FA-123,} |

输出:

| airline | tail_number |
| --- | --- |
| new air | NA-123 |
| foundry airways | FA-123 |
