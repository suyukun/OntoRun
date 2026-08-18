来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/cosineV1/

# Cosine

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Cosine

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

计算一个角度的余弦值。

表达式类别: 数值

## 声明的参数

- 角度单位- 角度单位，可以是度或弧度。Enum<Degrees, Radians>
- 角度值- 角度值，可以是弧度或度。Expression<DefiniteNumeric>
输出类型:Double

## 例子

### 例子 1: 基本情况

参数值:

- 角度单位:degrees
- 角度值:angle
| angle | 输出 |
| --- | --- |
| 0.0 | 1.0 |
| 90.0 | 0.0 |
| 180.0 | -1.0 |

### 例子 2: 空值情况

参数值:

- 角度单位:radians
- 角度值:null
输出:null
