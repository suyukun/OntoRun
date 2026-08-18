来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/arctanV1/

# Arctan

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Arctan

> 支持于: 批处理, 流式处理

支持于: 批处理, 流式处理

反正切函数。

表达式类别: 数值

## 声明的参数

- 角度单位- 输出角度单位，可以是度或弧度。Enum<Degrees, Radians>
- 值- 计算arctan的值。Expression<Double | Float>
输出类型:Double

## 示例

### 示例 1: 基本情况

参数值:

- 角度单位:degrees
- 值:angle
| angle | 输出 |
| --- | --- |
| -1.0 | -45.0 |
| 0.0 | 0.0 |
| 1.0 | 45.0 |

### 示例 2: 空值情况

参数值:

- 角度单位:radians
- 值:null
输出:null
