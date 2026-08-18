来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/pdfTextExtractionV1/

# 从PDF中提取文本

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 从PDF中提取文本

> 支持于: 批处理

支持于: 批处理

从PDF文件中的页面提取原始文本。

表达式类别: 媒体

## 声明的参数

- 媒体引用- 包含媒体集中PDF文件的媒体引用的列。表达式<媒体引用>
- 非必填结束页- 页范围的结束，包括在内。默认为文档中的最后一页。支持负索引。表达式<整数>
- 非必填起始页- 页范围的开始，包括在内。默认为文档中的第一页（1）。表达式<整数>
输出类型:数组<字符串>

## 示例

### 示例 1: 基本情况

参数值:

- 媒体引用:Media Reference
- 结束页:End Page
- 起始页:Start Page
| 媒体引用 | 起始页 | 结束页 | 输出 |
| --- | --- | --- | --- |
| {"mimeType":"application/pdf","reference":{"type":"mediaSetItem","mediaSetItem":{"mediaSetRid":"ri.mio.test.media-set.1","mediaItemRid":"ri.mio.test.media-item.1"}}} | 1 | 2 | [ 第一页, 第二页 ] |
