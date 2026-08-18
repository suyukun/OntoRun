来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/audioTranscriptionV1/

# 将音频转录为文本

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 将音频转录为文本

> 支持于：批处理

支持于：批处理

将音频文件转录为文本。

表达式类别: 媒体

## 声明的参数

- 媒体引用- 包含媒体集中音频文件的媒体引用的列。Expression<Media reference>
- 非必填语言- 要检测输入文件的语言。如果未提供语言，将从音频的前30秒推断。Enum<Afrikaans, Albanian, Amharic, Arabic, Armenian, Assamese, Azerbaijani, Bashkir, Basque, Belarusian, 等等 ...>
- 非必填输出模式- 选择输出为简单输出，其中输出是输出类型参数的类型，错误返回为null，或输出一个包含输出类型和错误作为字段的结构。Enum<Simple, With errors>
- 非必填性能模式- 运行转录时使用的性能模式。如果未提供模式，我们将默认为更经济的选项。Enum<More economical, More performant>
输出类型:字符串 | Struct<ok:字符串, error:字符串>

## 例子

### 例子 1: 基本情况

描述: 转录音频文件参数值:

- 媒体引用:mediaReference
- 语言:null
- 输出模式:null
- 性能模式:null
| mediaReference | 输出 |
| --- | --- |
| {"mimeType":"audio/mpeg","reference":{"type":"mediaSetItem","mediaSetItem":{"mediaSetRid":"ri.mio.main.media-set.a", "mediaItemRid":"ri.mio.main.media-item.a"}}} | This is an example transcription from Whisper |

### 例子 2: 空值情况

参数值:

- 媒体引用:Media Reference
- 语言:null
- 输出模式:null
- 性能模式:null
| mediaReference | 输出 |
| --- | --- |
| null | null |
