来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/getDocumentMetadataV1/

# 提取文档元数据

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 提取文档元数据

> 支持于: 批处理

支持于: 批处理

从文档的媒体引用中提取元数据字段。

表达式类别: 媒体

## 声明的参数

- 要包含的文档元数据信息- 额外要包含的元数据列。Set<Enum<Bytes, Document Author, Document Title, Page Count>>
- 媒体引用- 包含媒体集合中PDF文件媒体引用的列。Expression<Media reference>
输出类型:Struct

## 示例

### 示例 1: 基本案例

参数值:

- 要包含的文档元数据信息: [Document Author,Page Count,Document Title]
- 媒体引用:Media Reference
| 媒体引用 | 输出 |
| --- | --- |
| {"mimeType":"application/pdf","reference":{"type":"mediaSetItem","mediaSetItem":{"mediaSetRid":"ri.mio.test.media-set.1","mediaItemRid":"ri.mio.test.media-item.1"}}} | {author: Jane Doe,page_count: 23,title: Document Title,} |

### 示例 2: 基本案例

参数值:

- 要包含的文档元数据信息: [Document Title]
- 媒体引用:Media Reference
| 媒体引用 | 输出 |
| --- | --- |
| {"mimeType":"application/pdf","reference":{"type":"mediaSetItem","mediaSetItem":{"mediaSetRid":"ri.mio.test.media-set.1","mediaItemRid":"ri.mio.test.media-item.1"}}} | {title: Who Framed Roger Rabbit - Final Script,} |

### 示例 3: 基本案例

参数值:

- 要包含的文档元数据信息: [Document Author,Page Count]
- 媒体引用:Media Reference
| 媒体引用 | 输出 |
| --- | --- |
| {"mimeType":"application/pdf","reference":{"type":"mediaSetItem","mediaSetItem":{"mediaSetRid":"ri.mio.test.media-set.1","mediaItemRid":"ri.mio.test.media-item.1"}}} | {author: John Smith,page_count: 78,} |

### 示例 4: 空案例

参数值:

- 要包含的文档元数据信息: []
- 媒体引用:Media Reference
| 媒体引用 | 输出 |
| --- | --- |
| {"mimeType":"application/pdf","reference":{"type":"mediaSetItem","mediaSetItem":{"mediaSetRid":"ri.mio.test.media-set.1","mediaItemRid":"ri.mio.test.media-item.1"}}} | null |
