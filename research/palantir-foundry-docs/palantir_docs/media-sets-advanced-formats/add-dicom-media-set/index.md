来源: https://palantir.com/docs/zh/foundry/media-sets-advanced-formats/add-dicom-media-set/

# 添加DICOM媒体集

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 添加DICOM媒体集

本指南将介绍如何将DICOM (.dcm) 文件导入到Foundry中作为媒体集。

## 第1部分：导入DICOM文件

首先，您需要创建一个新的媒体集，并将DICOM文件添加到媒体集中。

- 导航到要创建媒体集的文件夹中。选择新建 > 媒体集。
- 输入您的媒体集名称。选择DICOM作为媒体类型，选择批处理作为延迟。选择创建媒体集以创建DICOM媒体集。
- 接下来，向媒体集中添加一个或多个.dcm文件。DICOM媒体集类型包括如Patient ID和Study ID的元数据。
您可以选择一个DICOM文件，并通过左右或上下拖动来更改对比度和曝光。

## 第2部分：创建Object类型

接下来，您需要创建一个新的流水线，将媒体集变换为可以在Foundry中使用的Object类型。

了解有关为媒体集创建流水线的更多信息。

- 通过从所有操作下拉菜单中选择创建新流水线来创建流水线。
- 媒体集将自动添加到流水线中。选择变换以将媒体集转换为表。
- 选择将媒体集转换为表行，然后选择应用。在生成的表中，每一行代表媒体集中的一个DICOM文件。
- 通过从右侧面板的流水线输出菜单中选择添加流水线输出来创建一个Object类型。选择Object类型选项。
- 输入Object类型的名称，例如DICOM媒体集。您可以通过选择属性右侧的三点，然后选择设为主键来将Media Item Rid属性设置为主键。完成后，您可以保存并部署流水线。
流水线部署后，您可以在Object Explorer或Ontology Manager中查看Object类型。

## （非必填）第3部分：创建Workshop模块

您可以通过选择创建Workshop模块来打开Workshop。

Workshop将自动生成有用的微件，如Object表和预览。

了解有关在Workshop中创建微件的更多信息。
