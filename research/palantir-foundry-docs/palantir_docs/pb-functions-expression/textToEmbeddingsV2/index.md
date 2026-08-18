来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/textToEmbeddingsV2/

# 文本到嵌入

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 文本到嵌入

> 支持于：批处理

支持于：批处理

将文本转换为嵌入。

表达式类别：字符串

## 声明参数

- 模型- 用于转换的嵌入模型。模型
- 文本列- 包含要使用给定模型转换为嵌入的文本的列。表达式<字符串>
- 非必填输出模式- 选择以简单输出或带错误输出。枚举<简单, 带错误>
输出类型：嵌入向量

## 示例

### 示例 1：基本情况

描述：'palantir'一词的示例嵌入。参数值：

- 模型：ada002Embedding()
- 文本列：text
- 输出模式：null
| text | 输出 |
| --- | --- |
| palantir | [ -0.019182289, -0.02127992, 0.009529043, -0.008066221, -0.0014429842, 0.019154688, -0.023556953, -0... |

### 示例 2：基本情况

描述：使用非 ADA 模型的'palantir'一词的示例嵌入。参数值：

- 模型：instructorLargeEmbedding()
- 文本列：text
- 输出模式：null
| text | 输出 |
| --- | --- |
| palantir | [ -0.019182289, -0.02127992, 0.009529043, -0.008066221, -0.0014429842, 0.019154688, -0.023556953, -0... |

### 示例 3：空值情况

描述：空值输入应有空值输出。参数值：

- 模型：ada002Embedding()
- 文本列：text
- 输出模式：null
| text | 输出 |
| --- | --- |
| null | null |

### 示例 4：边缘情况

描述：空输入字符串应有空值输出。参数值：

- 模型：ada002Embedding()
- 文本列：text
- 输出模式：null
| text | 输出 |
| --- | --- |
| empty string | null |

### 示例 5：边缘情况

描述：输入字符串超过 OpenAI Ada 的词元限制应有空值输出。参数值：

- 模型：ada002Embedding()
- 文本列：text
- 输出模式：null
| text | 输出 |
| --- | --- |
| a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a ... | null |

### 示例 6：边缘情况

描述：输入字符串超过 OpenAI Ada 的词元限制应有空值输出。参数值：

- 模型：instructorLargeEmbedding()
- 文本列：text
- 输出模式：SIMPLE
| text | 输出 |
| --- | --- |
| a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a ... | {出错: 超出上下文限制.,ok:null,} |
