来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/concatStringsV1/

# 拼接字符串

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 拼接字符串

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

使用指定的分隔符拼接字符串列表。

表达式类别: 字符串

## 声明的参数

- 表达式- 要拼接的字符串列表。List<Expression<字符串>>
- 非必填分隔符- 要添加在字符串之间的分隔符。Literal<字符串>
输出类型:字符串

## 示例

### 示例 1: 基本情况

参数值:

- 表达式: [hello, world]
- 分隔符: _
输出:hello_world

### 示例 2: 空值情况

参数值:

- 表达式: [hello,null, world, !]
- 分隔符: --
输出:hello--world--!
