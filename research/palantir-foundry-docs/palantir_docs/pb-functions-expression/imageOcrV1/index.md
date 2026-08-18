来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/imageOcrV1/

# 从图像中提取文本（使用OCR）

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 从图像中提取文本（使用OCR）

> 支持于: 批处理

支持于: 批处理

对媒体集中的图像文件运行OCR以提取文本。

表达式类别: 媒体

## 声明的参数

- 检测语言- 要在输入文件中检测的语言。Set<Enum<南非语, 阿尔巴尼亚语, 阿姆哈拉语, 阿拉伯语, 亚美尼亚语, 阿萨姆语, 阿塞拜疆语, 阿塞拜疆语 - 西里尔文, 巴斯克语, 白俄罗斯语, 以及更多...>>
- 媒体引用- 包含媒体集中图像文件的媒体引用的列。Expression<媒体引用>
- OCR输出格式- 输出将是一个字符串。Enum<文本, hOCR>
- 检测脚本- 要在输入文件中检测的脚本。Set<Enum<阿拉伯语, 亚美尼亚语, 孟加拉语, 加拿大土著语, 切罗基语, 西里尔文, 天城文, 埃塞俄比亚语, Fraktur, 格鲁吉亚语, 以及更多...>>
- 非必填错误处理- 决定对于处理失败的输入，流水线的行为。默认情况下快速失败。Enum<快速失败, 出错时返回NULL>
输出类型:字符串

## 示例

### 示例 1: 基本情况

参数值:

- 检测语言: {ENG}
- 媒体引用:mediaReference
- OCR输出格式: {TEXT}
- 检测脚本: {ARABIC}
- 错误处理:FAIL_FAST
| mediaReference | 输出 |
| --- | --- |
| {"mimeType":"image/png","reference":{"type":"mediaSetItem","mediaSetItem":{"mediaSetRid":"ri.mio.main.media-set.a", "mediaItemRid":"ri.mio.main.media-item.a"}}} | 这段文本来自媒体集中的图像。 |
