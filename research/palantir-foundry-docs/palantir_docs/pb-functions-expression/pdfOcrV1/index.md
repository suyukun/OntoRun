来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/pdfOcrV1/

# 从PDF提取文本（使用OCR）

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 从PDF提取文本（使用OCR）

> 支持于: 批量处理

支持于: 批量处理

在媒体集中的PDF文件上运行OCR以提取文本。

表达式类别: 媒体

## 声明的参数

- 要检测的语言- 要在输入文件中检测的语言。Set<Enum<南非语, 阿尔巴尼亚语, 阿姆哈拉语, 阿拉伯语, 亚美尼亚语, 阿萨姆语, 阿塞拜疆语, 阿塞拜疆语 - 西里尔文, 巴斯克语, 白俄罗斯语, 等...>>
- 媒体引用- 包含媒体集中PDF文件的媒体引用的列。Expression<媒体引用>
- OCR输出格式- 输出将是一个字符串数组。每个条目对应PDF的一页。Enum<文本, hOCR>
- 要检测的脚本- 要在输入文件中检测的脚本。Set<Enum<阿拉伯语, 亚美尼亚语, 孟加拉语, 加拿大土著语, 切罗基语, 西里尔文, 天城文, 埃塞俄比亚文, Fraktur, 格鲁吉亚语, 等...>>
- 非必填结束页- 页面范围结束，包含在内。默认为文档的最后一页。支持负索引。Expression<Integer>
- 非必填错误处理- 确定对处理失败的输入的管道行为。默认为快速失败。Enum<快速失败, 出错时为NULL>
- 非必填起始页- 页面范围起始，包含在内。默认为文档的第一页（1）。Expression<Integer>
输出类型:Array<字符串>

## 示例

### 示例 1: 基本情况

参数值:

- 要检测的语言: {ENG}
- 媒体引用:mediaReference
- OCR输出格式: {TEXT}
- 要检测的脚本: {ARABIC}
- 结束页:null
- 错误处理:FAIL_FAST
- 起始页:null
| mediaReference | 输出 |
| --- | --- |
| {"mimeType":"application/pdf","reference":{"type":"mediaSetItem","mediaSetItem":{"mediaSetRid":"ri.mio.main.media-set.a", "mediaItemRid":"ri.mio.main.media-item.a"}}} | [ This text came from the PDF document in the media set., So did this text. ] |
