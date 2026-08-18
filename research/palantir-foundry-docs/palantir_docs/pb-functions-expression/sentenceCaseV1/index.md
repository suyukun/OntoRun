来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/sentenceCaseV1/

# 句子大小写

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 句子大小写

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

将第一个单词的第一个字符转换为大写。

表达式类别: 字符串

## 声明的参数

- 表达式- 要应用句子大小写的字符串表达式。表达式<字符串>
输出类型:字符串

## 示例

### 示例 1: 基本情况

参数值:

- 表达式: hello world
输出:Hello world

### 示例 2: 基本情况

参数值:

- 表达式: this is a test. another test? yes, another test!
输出:This is a test. Another test? Yes, another test!

### 示例 3: 基本情况

参数值:

- 表达式:空字符串
输出:空字符串

### 示例 4: 基本情况

参数值:

- 表达式: hello world! how are you? have a nice day.
输出:Hello world! How are you? Have a nice day.

### 示例 5: 基本情况

参数值:

- 表达式: hELLO WORLD
输出:HELLO WORLD

### 示例 6: 基本情况

参数值:

- 表达式: how many people? 100 people!
输出:How many people? 100 people!

### 示例 7: 基本情况

参数值:

- 表达式: no punctuation
输出:No punctuation

### 示例 8: 空值情况

参数值:

- 表达式:空值
输出:空值
