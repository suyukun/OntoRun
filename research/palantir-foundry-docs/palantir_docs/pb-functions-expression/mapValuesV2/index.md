来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/mapValuesV2/

# 映射值

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 映射值

> 支持于：批处理，流处理

支持于：批处理，流处理

将列中的一组值映射到新值。

表达式类别：数据准备

## 声明的参数

- Default- 如果值未被值映射映射，则选择此值。Expression<T2>
- Input- 要映射的值。Expression<T1>
- Value map- 要映射的值。Expression<Map<T1, T2>>
类型变量界限：T1 接受 ComparableType**T2 接受 AnyType

输出类型：T2

## 示例

### 示例 1: 基础案例

参数值：

- Default:null
- Input:country
- Value map: {Denmark -> DNK,United Kingdom -> UK,}
| country | Output |
| --- | --- |
| United Kingdom | UK |
| Denmark | DNK |
| United States of America | null |

### 示例 2: 基础案例

参数值：

- Default:country
- Input:country
- Value map: {Denmark -> DNK,United Kingdom ->null,}
| country | Output |
| --- | --- |
| United Kingdom | null |
| null | null |
