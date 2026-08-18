来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/isValidMediaReferenceV1/

# 是否为有效媒体引用

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 是否为有效媒体引用

> 支持于：批处理，流处理

支持于：批处理，流处理

如果输入是有效的Foundry媒体引用，则返回true。

表达式类别：布尔值

## 声明的参数

- 表达式- 代表媒体引用的字符串。表达式<字符串>
输出类型：布尔值

## 示例

### 示例 1：基本情况

参数值：

- 表达式：mediaRef
| mediaRef | 输出 |
| --- | --- |
| {"mimeType":"PDF","reference":{"type":"datasetFile","datasetFile":{"fileReference":{"datasetRid":"ri.foundry.main.dataset.a","ref":"master","logicalFilePath":"file.pdf"}}}} | true |
| {"mimeType":"PDF","reference":{"type":"mediaSetItem","mediaSetItem":{"mediaSetRid":"ri.mio.main.media-set.a", "mediaItemRid":"ri.mio.main.media-item.a"}}} | true |
| 不是媒体引用 | false |
