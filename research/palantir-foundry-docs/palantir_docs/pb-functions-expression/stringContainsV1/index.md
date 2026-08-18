来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/stringContainsV1/

# 字符串包含

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 字符串包含

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

表达式类别: 布尔, 字符串

## 声明的参数

- 表达式-无描述表达式<字符串>
- 忽略大小写- 布尔值决定比较是否区分大小写。文字<布尔>
- 值-无描述表达式<字符串>
输出类型:布尔

## 示例

### 示例 1: 基本情况

参数值:

- 表达式: ... Hello world
- 忽略大小写: false
- 值: hello
输出:false

### 示例 2: 基本情况

参数值:

- 表达式: ... Hello world
- 忽略大小写: false
- 值: Hello
输出:true

### 示例 3: 基本情况

参数值:

- 表达式: ... Hello world
- 忽略大小写: true
- 值: hello
输出:true

### 示例 4: 空情况

参数值:

- 表达式:null
- 忽略大小写: false
- 值:null
输出:false

### 示例 5: 空情况

参数值:

- 表达式:null
- 忽略大小写: false
- 值: Hello
输出:false

### 示例 6: 空情况

参数值:

- 表达式: hello world
- 忽略大小写: false
- 值:null
输出:false
