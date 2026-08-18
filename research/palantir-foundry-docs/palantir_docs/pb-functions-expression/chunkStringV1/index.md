来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/chunkStringV1/

# 分块字符串

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 分块字符串

> 支持于: 批处理

支持于: 批处理

将字符串分块为指定大小的块，并使用指定的分隔符。

表达式类别: 字符串

## 声明的参数

- 表达式- 包含要分块的文本文档的列。Expression<字符串>
- 非必填块重叠- 允许块在内容上重叠大约此数量。必须大于或等于0且小于所选块大小。Literal<Integer>
- 非必填块大小- 创建大小约为此数字的块。必须大于0。Literal<Integer>
- 非必填保留分隔符- 在输出块中包含分隔符。Literal<Boolean>
- 非必填分隔符- 使用这些提供的分隔符分块字符串。默认分隔符的效果是尽可能将所有段落、句子和单词保存在一起。List<Literal<字符串>>
输出类型:Array<字符串>

## 示例

### 示例 1: 基本情况

参数值:

- 表达式:string
- 块重叠:null
- 块大小: 10
- 保留分隔符:null
- 分隔符:null
| string | 输出 |
| --- | --- |
| hello | [ hello ] |
| hello world. the quick brown fox jumps over the fence. | [ hello, world., the quick, brown fox, jumps, over the, fence. ] |
| hello world.the quick brown foxjumps over the fence. | [ hello, world., the quick, brown fox, jumps, over the, fence. ] |
| hello world.the quick brown foxjumps over the fence. | [ hello, world., the quick, brown fox, jumps, over the, fence. ] |

### 示例 2: 基本情况

参数值:

- 表达式: A quick-brown-fox-jumps over the lazy dog
- 块重叠:null
- 块大小: 10
- 保留分隔符: false
- 分隔符: [,,  ]
输出:[ A, quick-brown-fox-jumps, over the, lazy dog ]

### 示例 3: 基本情况

参数值:

- 表达式: A quick brown fox jumps over the lazy dog
- 块重叠: 5
- 块大小: 10
- 保留分隔符:null
- 分隔符:null
输出:[ A quick, brown fox, fox jumps, over the, the lazy, lazy dog ]

### 示例 4: 基本情况

参数值:

- 表达式: Text1|Text2||Text3
- 块重叠:null
- 块大小: 10
- 保留分隔符: false
- 分隔符: [||, |]
输出:[ Text1, Text2, Text3 ]

### 示例 5: 基本情况

参数值:

- 表达式: Text1|Text2||Text3
- 块重叠:null
- 块大小: 10
- 保留分隔符:null
- 分隔符: [||, |]
输出:[ Text1, |Text2, ||Text3 ]

### 示例 6: 基本情况

参数值:

- 表达式: Text1, Text2Text3Text4
- 块重叠:null
- 块大小: 256
- 保留分隔符:null
- 分隔符:null
输出:[ Text1, Text2Text3Text4 ]

### 示例 7: 基本情况

参数值:

- 表达式: Text1 Text2Text3Text4
- 块重叠:null
- 块大小: 10
- 保留分隔符:null
- 分隔符:null
输出:[ Text1, Text2, Text3, Text4 ]
