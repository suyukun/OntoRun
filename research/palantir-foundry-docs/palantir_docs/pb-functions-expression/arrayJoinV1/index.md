来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/arrayJoinV1/

# 合并数组

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 合并数组

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

使用指定的分隔符合并数组。

表达式类别: 数组

## 声明的参数

- 要合并的数组-无描述表达式<数组<字符串>>
- 分隔符-无描述表达式<字符串>
输出类型:字符串

## 示例

### 示例 1: 基本情况

参数值:

- 要合并的数组: [ hello, world ]
- 分隔符: -
输出:hello-world

### 示例 2: 基本情况

参数值:

- 要合并的数组: [ hello, world ]
- 分隔符:
输出:helloworld

### 示例 3: 空值情况

参数值:

- 要合并的数组:array
- 分隔符:separator
| array | separator | 输出 |
| --- | --- | --- |
| [ hello, world ] | null | helloworld |
| null | - | null |
| null | null | null |
