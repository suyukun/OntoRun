来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/pdfTableOfContentsV1/

# PDF目录

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# PDF目录

> 支持于: 批处理

支持于: 批处理

表达式类别: 媒体

## 声明的参数

- 媒体引用- 包含媒体集中PDF文件的媒体引用的列。表达式<媒体引用>
输出类型:数组<结构<级别:整数, 标题:字符串, 页码:整数>>

## 示例

### 示例 1: 基本案例

参数值:

- 媒体引用:Media Reference
| 媒体引用 | 输出 |
| --- | --- |
| {"mimeType":"application/pdf","reference":{"type":"mediaSetItem","mediaSetItem":{"mediaSetRid":"ri.mio.test.media-set.1","mediaItemRid":"ri.mio.test.media-item.1"}}} | [ {级别: 0,页码: 2,标题: Chapter 1,}, {**l... |
