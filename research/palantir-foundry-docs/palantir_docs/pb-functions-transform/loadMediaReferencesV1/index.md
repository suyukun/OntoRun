来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/loadMediaReferencesV1/

# 获取媒体引用（数据集）

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 获取媒体引用（数据集）

> 支持于：批处理

支持于：批处理

生成一个包含媒体引用和文件基本元数据的数据集。

变换类别：文件

## 声明参数

- 数据集- 要加载媒体引用的文件数据集。文件
- 非必填强制指定MIME类型- 为每个媒体引用强制指定MIME类型值。如果未设置，则每个文件将被读取以检测MIME类型。枚举<BMP, CSV, FLAC, H264, JP2K, JPEG, JSON, MP4, MP4_AUDIO, MPEG, 等等...>