来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/isNaNV1/

# 判断是否为NaN

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 判断是否为NaN

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

如果输入为nan，则返回true，否则返回false。

表达式类别: 布尔

## 声明的参数

- 表达式- 表达式检查数值表达式是否为nan。表达式<Double | Float>
输出类型:布尔

## 示例

### 示例 1: 基础案例

参数值:

- 表达式: NaN
输出:true

### 示例 2: 基础案例

参数值:

- 表达式: 12.57
输出:false

### 示例 3: 空值案例

参数值:

- 表达式:null
输出:false

### 示例 4: 边缘案例

参数值:

- 表达式:numbers
| numbers | 输出 |
| --- | --- |
| NaN | true |
