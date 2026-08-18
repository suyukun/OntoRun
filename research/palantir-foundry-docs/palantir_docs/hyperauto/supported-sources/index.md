来源: https://palantir.com/docs/zh/foundry/hyperauto/supported-sources/

# HyperAuto V2 支持的来源

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# HyperAuto V2 支持的来源

本页描述了HyperAuto V2 支持的数据连接来源类型。

## SAP

### 来源连接

HyperAuto V2 支持来自Foundry SAP 来源的数据。SAP ECC 和 S/4HANA 均被支持，无论是否有对应的 SLT 复制服务器（流式传输需要 SLT）。为了支持来源，必须满足以下最低要求：

- SAP 管理来源 (magritte-sap-source) 版本：1.25.0
- Palantir Foundry SAP 连接器版本：SP26 (2.26.0)
有关如何在 Foundry 中设置 SAP 的更多信息，请查看SAP 附加组件安装指南。

### 基于文件夹的数据

HyperAuto V2 也可以从 SAP 数据的静态切片中工作，而无需直接连接。在这种情况下，您需要将以下数据字典表上传为数据集：

- DD02L (SAP 表)
- DD02T (SAP DD: SAP 表文本)
- DD03L (表字段)
- DD04T (R-3 DD: 数据元素文本)
- DD05S (外键字段)
- DD08L (R-3 DD: 关系定义)
所有后续需使用 HyperAuto 处理的表都需要作为 Foundry 数据集上传到单个文件夹中。

有关 HyperAuto 如何处理静态数据的更多信息，请查看基于文件夹的 SAP 管道文档。
