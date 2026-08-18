来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/parseJsonV1/

# 从JSON文件中提取行

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 从JSON文件中提取行

> 支持于: 批处理

支持于: 批处理

读取文件的数据集，并将每个JSON文件解析成行。

变换类别: 文件, 字符串, 结构

## 声明的参数

- 允许JSON值跨多行- 如果关闭，单个JSON记录必须完全在一行上。如果开启，单个JSON记录可以跨多行。Literal<Boolean>
- 数据集- 要处理的文件数据集。Files
- 模式- 解析JSON文件时使用的模式定义。Type<Struct>