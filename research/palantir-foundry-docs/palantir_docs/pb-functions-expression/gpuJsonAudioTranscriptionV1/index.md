来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/gpuJsonAudioTranscriptionV1/

# 使用GPU将音频转录为json

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 使用GPU将音频转录为json

> 支持于: 批处理

支持于: 批处理

使用GPU将音频文件转录为json。

表达类别: 媒体

## 声明的参数

- 媒体引用- 包含媒体集中音频文件的媒体引用的列。表达<媒体引用>
- 非必填语言- 要检测的输入文件中的语言。如果未提供语言，将从音频的前30秒推断。枚举<南非语, 阿尔巴尼亚语, 阿姆哈拉语, 阿拉伯语, 亚美尼亚语, 阿萨姆语, 阿塞拜疆语, 巴什基尔语, 巴斯克语, 白俄罗斯语, 以及更多 ...>
输出类型:字符串

## 示例

### 示例 1: 基本情况

描述: 转录音频文件参数值:

- 媒体引用:mediaReference
- 语言:null
| mediaReference | 输出 |
| --- | --- |
| {"mimeType":"audio/mpeg","reference":{"type":"mediaSetItem","mediaSetItem":{"mediaSetRid":"ri.mio.main.media-set.a", "mediaItemRid":"ri.mio.main.media-item.a"}}} | {"version":1,"segments":[{"id":"a1f69f02-f780-465b-94da-0930e2e2e7d2","channel":"1d38a2f7-e234-419e-... |

### 示例 2: 基本情况

描述: 转录音频文件参数值:

- 媒体引用:mediaReference
- 语言:null
| mediaReference | 输出 |
| --- | --- |
| {"mimeType":"audio/mpeg","reference":{"type":"mediaSetItem","mediaSetItem":{"mediaSetRid":"ri.mio.main.media-set.a", "mediaItemRid":"ri.mio.main.media-item.a"}}} | {"version":1,"segments":[{"id":"a1f69f02-f780-465b-94da-0930e2e2e7d2","channel":"1d38a2f7-e234-419e-... |

### 示例 3: 空情况

参数值:

- 媒体引用:Media Reference
- 语言:null
| mediaReference | 输出 |
| --- | --- |
| null | null |
