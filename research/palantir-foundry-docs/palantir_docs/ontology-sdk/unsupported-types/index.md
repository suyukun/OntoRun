来源: https://palantir.com/docs/zh/foundry/ontology-sdk/unsupported-types/

# Ontology SDK 不支持的类型

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Ontology SDK 不支持的类型

## 概述

Ontology SDK 为 TypeScript 和 Python 包生成客户端代码；此代码表示来自 Ontology 的 Object 类型、操作类型和函数。目前并非所有数据类型都在 Ontology SDK 中得到支持；此页面列出了尚未在 Ontology SDK 中支持的数据类型。

## Object 类型：不支持的属性类型

如果您使用的 Object 类型包含一种在下方列出的属性类型，代码生成器将跳过该属性并记录出错。

### Typescript SDK

以下 Typescript SDK 属性类型不受支持：

- Cipher
- Markings
- Media
- Vectors
### Python SDK

以下 Python SDK 属性类型不受支持：

- 时间序列属性
- Cipher
- Geohash
- Geoshape
- Marking
- Media
- Vector
### Java SDK

以下 Java SDK 属性类型不受支持：

- 时间序列属性
- Cipher
- Marking
- MarkingList
- Media
- Vector
## 操作类型：不支持的参数类型

如果您使用的操作类型包含一种在下方提到的参数类型，代码生成器将无法创建您的包。为解决此问题，您必须从 SDK 应用程序中移除该操作类型，直到为该类型添加支持。

### Python SDK

以下 Python SDK 参数类型不受支持：

- ObjectSet
- Marking
- MarkingList
### Java SDK

以下 Java SDK 参数类型不受支持：

- Marking
- MarkingList
## 操作类型：不支持的 webhook 类型

使用使用 OAuth 2.0 进行身份验证的 webhooks的操作类型不受支持。这是因为用户将无法通过 SDK 应用程序使用这些操作类型，除非首先通过 Foundry 授权出站应用程序（例如，通过首先在 Workshop 应用程序中调用操作）。

## 函数：不支持的输入参数类型和输出类型

如果您使用的函数包含一种在下方列出的输入或输出类型，代码生成器将无法生成您的包。为解决此问题，您必须从 SDK 应用程序中移除该函数，直到添加支持。

### Typescript SDK

#### 函数输出类型

以下 Typescript SDK 函数输出类型不受支持：

- Principal
- User
- Notification
- OntologyEdit
- ClassificationMarking
### Python SDK

#### 函数输入参数类型

以下 Python SDK 函数输入类型不受支持：

- ObjectSet
- AnonymousCustomType
- ClassificationMarking
- CustomType
- GeoShape
- Group
- MandatoryControl
- ModelGraph
- Notification
- OntologyEdit
- Principal
- Range
- StringFunctionDateType_ThreeDimensionalAggregation
- TimeSeries
- TwoDimensionalAggregation
- User
#### 函数输出类型

以下 Python SDK 函数输出类型不受支持：

- ObjectSet
- AnonymousCustomType
- ClassificationMarking
- CustomType
- GeoShape
- Group
- MandatoryControl
- ModelGraph
- Notification
- OntologyEdit
- Principal
- Range
- StringFunctionDateType_ThreeDimensionalAggregation
- TimeSeries
- TwoDimensionalAggregation
- User
### Java SDK

#### 函数输入参数类型

以下 Java SDK 函数输入类型不受支持：

- AnonymousCustomType
- ClassificationMarking
- CustomType
- GeoShape
- Group
- MandatoryControl
- ModelGraph
- Notification
- OntologyEdit
- Principal
- Range
- StringFunctionDateType_ThreeDimensionalAggregation
- TimeSeries
- TwoDimensionalAggregation
- User
#### 函数输出类型

以下 Java SDK 函数输出类型不受支持：

- AnonymousCustomType
- ClassificationMarking
- CustomType
- GeoShape
- Group
- MandatoryControl
- ModelGraph
- Notification
- OntologyEdit
- Principal
- Range
- StringFunctionDateType_ThreeDimensionalAggregation
- TimeSeries
- TwoDimensionalAggregation
- User