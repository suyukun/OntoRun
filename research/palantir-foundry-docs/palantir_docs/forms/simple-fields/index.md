来源: https://palantir.com/docs/zh/foundry/forms/simple-fields/

# 简单字段

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 简单字段

Foundry Forms 不再是 Foundry 上数据输入或数据输出工作流的推荐方法。相反，使用 Foundry Ontology 搭建用户输入工作流，将相关数据结构表示为对象类型，并通过操作配置数据输出交互。在Forms 概述文档中了解更多信息。

在表单中，简单字段以获取来自回应者的基本输入。此页面讨论了 Foundry Forms 中可用的不同类型的简单字段，不包括附件字段。

## 提示

提示字段强调对回应者重要的内容，并支持 Markdown 格式。用户可以配置以下选项：

- 创建引用其他字段值的内容。
- 设置标题、背景颜色和图标。
- 添加已上传到 Foundry 或从 Foundry 可访问的其他网站的图片。
提示字段的值永远不会写入到支持的对象类型或电子表格中。如果您需要使用写入不同字段的值来模板化一些文本，可以使用模板字段。

## 复选框

复选框字段将一组选项显示为复选框。用户可以配置以下选项：

- 提供可能的Values列表及其显示的Labels。
- 设置默认值。
- 将复选框水平或垂直显示。
## 日期选择器

日期选择器字段允许回应者输入日期或时间戳。用户可以配置以下选项：

- 设置时间精度（天、分钟、秒或毫秒）。
- 设置记录格式（默认是日期为YYYY-MM-DD，时间戳为YYYY-MM-DDTHH:mm:ss.SSSZZ）。
- 强制执行最小/最大日期。
- 禁用过去/未来的日期。
- 用填写日期预填字段。
默认的最小和最大日期是从当前日期起的25年，但可以通过更改其配置值进一步设置过去或未来的日期。例如，您可以通过在1900年设置一个最小日期来允许选择超过25年前的出生日期。

在日期选择器字段中，日期总是根据用户的时区选择和显示。然而，当日期值被写入到支持的电子表格或对象类型时，它们总是以UTC格式写入，以确保跨时区兼容。

## 下拉菜单

下拉菜单字段将一组选项显示为下拉菜单。用户可以配置以下选项：

- 提供可能的Values列表及其显示的Labels。
- 设置默认值。
- 允许多重选择。
- 如果只有一个值可用，则预填字段。
- 允许创建除了给定值之外的其他值。
- 设置占位符。
- 使用代码编辑器设置noResultsText: string。
## 地理编码选择器

地理编码选择器字段允许回应者输入地址。使用代码编辑器，用户可以设置placeholder: string。

## 地图选择器

地图选择器字段允许回应者输入坐标。使用代码编辑器，用户可以配置以下选项：

- 设置placeholder: string。
- 设置location: [double, double]。
- 设置initialZoom: double。
- 设置displayFormat: "latlng" | "mgrs"。
- 设置mapboxAccessToken: string。
- 设置mapboxStyles: list<string>（查看Mapbox 文档 ↗）。
## 数值

数值字段允许回应者输入数字。用户可以配置以下选项：

- 设置默认值。
- 设置单位标签（例如，kg或lbs）。
- 设置占位符。
- 显示增量/减量按钮并指定其位置。
- 使用代码编辑器:设置clampValueOnBlur: boolean。设置min: double。设置max: double。设置stepSize: double。设置minorStepSize: double。设置majorStepSize: double。
- 设置clampValueOnBlur: boolean。
- 设置min: double。
- 设置max: double。
- 设置stepSize: double。
- 设置minorStepSize: double。
- 设置majorStepSize: double。
## 单选按钮

单选按钮字段将一组选项显示为单选按钮。用户可以配置以下选项：

- 提供可能的Values列表及其显示的Labels。
- 设置默认值。
- 将单选按钮水平或垂直显示。
## 资源选择器

资源选择器字段允许回应者从 Foundry 内选择资源。用户可以指定是否允许回应者选择文件夹、数据集或任何资源类型。

## 滑块

滑块字段允许回应者选择一个数字。用户可以配置以下选项：

- 强制执行最小/最大值。
- 设置步长和标签步长。
- 设置单位标签（例如，kg或lbs）。
- 指定选定值如何标记。
- 使用代码编辑器:设置initialValue: double。设置labelPrecision: double。设置showTrackFill: boolean。
- 设置initialValue: double。
- 设置labelPrecision: double。
- 设置showTrackFill: boolean。
## 文本

文本字段允许回应者输入单行文本。用户可以配置以下选项：

- 设置默认值。
- 设置占位符。
## 文本区域

文本区域字段允许回应者输入多行文本。用户可以配置以下选项：

- 设置默认值。
- 设置占位符。
- 设置默认和最大行数。
## URL

URL字段允许回应者输入超链接。用户可以配置以下选项：

- 设置默认值。
- 设置占位符。
- 当格式无效时显示警告，并自定义显示的消息。