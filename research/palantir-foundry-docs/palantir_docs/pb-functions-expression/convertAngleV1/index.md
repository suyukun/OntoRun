来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/convertAngleV1/

# 转换角度单位

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 转换角度单位

> 支持于: 批处理, 流式处理

支持于: 批处理, 流式处理

表达式类别: 地理空间, 数值

## 声明的参数

- 当前单位的数量-无描述Expression<DefiniteNumeric>
- 当前单位- 转换前的单位。Enum<Degrees, Minutes, Radians, Seconds>
- 目标单位- 转换后的期望单位。Enum<Degrees, Minutes, Radians, Seconds>
输出类型:Double

## 示例

### 示例 1: 基本情况

参数值:

- 当前单位的数量:degrees
- 当前单位:degrees
- 目标单位:radians
| degrees | 输出 |
| --- | --- |
| 180 | 3.141592653589793 |

### 示例 2: 基本情况

参数值:

- 当前单位的数量:radians
- 当前单位:radians
- 目标单位:degrees
| radians | 输出 |
| --- | --- |
| 3.141592653589793 | 180.0 |

### 示例 3: 空值情况

参数值:

- 当前单位的数量:radians
- 当前单位:radians
- 目标单位:degrees
| radians | 输出 |
| --- | --- |
| null | null |
