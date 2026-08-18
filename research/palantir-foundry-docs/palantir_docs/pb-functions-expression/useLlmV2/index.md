来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/useLlmV2/

# 使用LLM

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 使用LLM

> 支持于: 批量

支持于: 批量

使用可配置的提示调用LLM。

表达式类别: 字符串

## 声明的参数

- Model- 要使用的LLM模型。模型
- Prompt- 传递给LLM模型的用户提示。List<Expression<AnyType>>
- 非必填Output mode- 选择输出为简单输出，输出为输出类型参数的类型，出错返回null，或输出一个结构，其中输出为输出类型和错误为字段。Enum<Simple, With errors>
- 非必填Output type- LLM响应应遵循的输出类型。Type<Array<AnyType> | Boolean | Date | Decimal | Double | Float | Integer | Long | Short | String | Struct | Timestamp>
- 非必填System prompt- 传递给LLM模型的系统提示。Literal<String>
输出类型:Array<AnyType> | Boolean | Date | Decimal | Double | Float | Integer | Long | Short | String | Struct | Struct<ok<AnyType> | Boolean | Date | Decimal | Double | Float | Integer | Long | Short | String | Struct | Timestamp, error> | Timestamp

## 示例

### 示例 1: 基本情况

参数值:

- Model:gpt4ChatModel(temperature: 0.0,)
- Prompt:prompt
- Output mode:null
- Output type:null
- System prompt: 在一个食品配送应用的背景下，您的任务是根据以下用户提示评估评论...
| prompt | 输出 |
| --- | --- |
| The food was great! | 5 |

### 示例 2: 基本情况

参数值:

- Model:gpt4ChatModel(temperature: 0.0,)
- Prompt: [prompt,mediaRef]
- Output mode:null
- Output type:null
- System prompt: 您是一个高度先进的AI，旨在通过解读医学影像来协助医疗专业人员...
| prompt | mediaRef | 输出 |
| --- | --- | --- |
| Patient: John Doe, Age: 45, Symptoms: Persistent cough, shortness of breath, and chest pain. Please analyze the attached chest X-ray for any signs of pneumonia or other abnormalities. | {"mimeType":"image/jpeg","reference":{"type":"mediaSetViewItem","mediaSetViewItem":{"mediaSetRid":"r... | Diagnostic Report:Patient: John DoeAge: 45Symptoms: Persistent cough, shortness of b... |

### 示例 3: 空情况

参数值:

- Model:gpt4ChatModel(temperature: 0.0,)
- Prompt:prompt
- Output mode:null
- Output type:null
- System prompt:null
| prompt | 输出 |
| --- | --- |
| null | null |

### 示例 4: 空情况

描述: 只有MediaSet引用，没有提示，应该有一个空输出。参数值:

- Model:gpt4ChatModel(temperature: 0.0,)
- Prompt:mediaRef
- Output mode:null
- Output type:null
- System prompt:null
| mediaRef | 输出 |
| --- | --- |
| {"mimeType":"image/jpeg","reference":{"type":"mediaSetViewItem","mediaSetViewItem":{"mediaSetRid":"r... | null |

### 示例 5: 边缘情况

描述: 空输入字符串应有一个空输出。参数值:

- Model:gpt4ChatModel(temperature: 0.0,)
- Prompt:prompt
- Output mode:null
- Output type:null
- System prompt:null
| prompt | 输出 |
| --- | --- |
| empty string | null |

### 示例 6: 边缘情况

描述: 输入提示超出模型限制应有一个空输出。参数值:

- Model:gpt4ChatModel(temperature: 0.0,)
- Prompt:prompt
- Output mode:null
- Output type:WITH_ERRORS
- System prompt:null
| prompt | 输出 |
| --- | --- |
| What is the capital of France? | {error:null,ok: Paris,} |
| a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a ... | {error: Context limit exceeded.,ok:null,} |

### 示例 7: 边缘情况

描述: 输入提示超出模型限制应有一个空输出。参数值:

- Model:gpt4ChatModel(temperature: 0.0,)
- Prompt:prompt
- Output mode:null
- Output type:null
- System prompt:null
| prompt | 输出 |
| --- | --- |
| a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a ... | null |
