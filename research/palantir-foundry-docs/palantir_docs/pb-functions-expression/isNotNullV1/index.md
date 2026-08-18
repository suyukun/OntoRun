来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/isNotNullV1/

# Is not null

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Is not null

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

如果输入不为null，则返回true，可以选择性地将空字符串视为null。

表达式类别: 布尔值

## 声明的参数

- Expression-无描述Expression<AnyType>
- 非必填将空字符串视为null-无描述Literal<Boolean>
输出类型:布尔值

## 示例

### 示例 1: 基本情况

参数值:

- Expression:空字符串
- 将空字符串视为null: true
输出:false

### 示例 2: 基本情况

参数值:

- Expression:null
- 将空字符串视为null:null
输出:false

### 示例 3: 基本情况

参数值:

- Expression: 1
- 将空字符串视为null:null
输出:true

### 示例 4: 基本情况

参数值:

- Expression: hello
- 将空字符串视为null:null
输出:true
