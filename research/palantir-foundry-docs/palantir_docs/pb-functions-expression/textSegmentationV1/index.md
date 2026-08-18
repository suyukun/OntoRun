来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/textSegmentationV1/

# 文本分割

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 文本分割

> 支持：批处理，流处理

支持：批处理，流处理

使用滑动窗口分割提取一系列文本段。

表达式类别: 字符串

## 声明的参数

- Expression- 要分割的文本主体。Expression<字符串>
- Length- 文本将被分割成的段的词数。Expression<Integer>
- 非必填Overflow- 一个段可以与另一个段共享的单词数量。Expression<Integer>
输出类型:Array<字符串>

## 示例

### 示例 1: 基本情况

描述: 此测试展示了变换正确分割一小段文本的能力，其中结尾也将是一个独立的段。参数值:

- Expression:string
- Length: 3
- Overflow: 1
| string | 输出 |
| --- | --- |
| hello world this is a test string | [ hello world this, this is a, a test string, string ] |

### 示例 2: 基本情况

描述: 使用负溢出的测试。参数值:

- Expression:string
- Length:length
- Overflow:overflow
| string | length | overflow | 输出 |
| --- | --- | --- | --- |
| She sells sea shells by | 2 | -1 | [ She sells, shells by ] |

### 示例 3: 基本情况

描述: 一个带有溢出和结尾较小段的较大测试。参数值:

- Expression:string
- Length:length
- Overflow:overflow
| string | length | overflow | 输出 |
| --- | --- | --- | --- |
| hello world this is a larger test with overlap, the nature of the human spirit is strange as such i ... | 10 | 3 | [ hello world this is a larger test with overlap, the, with overlap, the nature of the human spirit ... |

### 示例 4: 基本情况

描述: 测试一个溢出设置为0的字符串，最后一个段小于完整长度。参数值:

- Expression:string
- Length: 3
- Overflow:null
| string | 输出 |
| --- | --- |
| hello world this is a test string | [ hello world this, is a test, string ] |

### 示例 5: 基本情况

描述: 在没有溢出的情况下测试，段被完美地按长度划分。参数值:

- Expression:string
- Length:length
- Overflow:overflow
| string | length | overflow | 输出 |
| --- | --- | --- | --- |
| hello world this is a test string without overlap | 3 | 0 | [ hello world this, is a test, string without overlap ] |

### 示例 6: 空情况

描述: 在没有溢出的情况下测试，段被完美地按长度划分。参数值:

- Expression:string
- Length:length
- Overflow:overflow
| string | length | overflow | 输出 |
| --- | --- | --- | --- |
| null | null | null | null |

### 示例 7: 空情况

描述: 在没有溢出的情况下测试，段被完美地按长度划分。参数值:

- Expression:string
- Length:length
- Overflow:overflow
| string | length | overflow | 输出 |
| --- | --- | --- | --- |
| null | 1 | null | null |

### 示例 8: 空情况

描述: 在没有溢出的情况下测试，段被完美地按长度划分。参数值:

- Expression:string
- Length:length
- Overflow:overflow
| string | length | overflow | 输出 |
| --- | --- | --- | --- |
| Hello world | null | null | null |
