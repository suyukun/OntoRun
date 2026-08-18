来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/getImageryMetadataV1/

# 提取图像元数据

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 提取图像元数据

> 支持于: 批处理

支持于: 批处理

从图像的媒体引用中提取元数据字段。

表达式类别: 媒体

## 声明的参数

- 要包含的图像元数据信息- 要包含的附加元数据列。Set<Enum<Attributes, Bands, Bytes, Dimensions, Format, Geographic Metadata, ICC Profile>>
- 媒体引用- 包含媒体集中图像媒体引用的列。Expression<Media reference>
输出类型:Struct

## 示例

### 示例 1: 基本情况

参数值:

- 要包含的图像元数据信息: [Attributes,Bands,Bytes,Dimensions,Format,Geographic Metadata,ICC Profile]
- 媒体引用:Media Reference
| 媒体引用 | 输出 |
| --- | --- |
| {"mimeType":"image/tiff","reference":{"type":"mediaSetItem","mediaSetItem":{"mediaSetRid":"ri.mio.test.media-set.1","mediaItemRid":"ri.mio.test.media-item.1"}}} | {attributes: {outer_key1 -> {inner_key1 -> inner_value1,},... |

### 示例 2: 基本情况

参数值:

- 要包含的图像元数据信息: [Bands,Dimensions,Geographic Metadata]
- 媒体引用:Media Reference
| 媒体引用 | 输出 |
| --- | --- |
| {"mimeType":"image/tiff","reference":{"type":"mediaSetItem","mediaSetItem":{"mediaSetRid":"ri.mio.test.media-set.1","mediaItemRid":"ri.mio.test.media-item.1"}}} | {bands: [ {color_interpretation: RED,type: BYTE,}, {<b... |

### 示例 3: 基本情况

参数值:

- 要包含的图像元数据信息: [ICC Profile]
- 媒体引用:Media Reference
| 媒体引用 | 输出 |
| --- | --- |
| {"mimeType":"image/tiff","reference":{"type":"mediaSetItem","mediaSetItem":{"mediaSetRid":"ri.mio.test.media-set.1","mediaItemRid":"ri.mio.test.media-item.1"}}} | {icc_profile: some-icc-profile,} |
