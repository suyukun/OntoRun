来源: https://palantir.com/docs/zh/foundry/ontology-sdk/create-a-new-osdk/

# 创建一个新的 Developer Console 应用程序

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 创建一个新的 Developer Console 应用程序

在此页面中，我们将逐步完成创建新 Developer Console 应用程序的以下过程：

- 向 SDK 应用程序添加 Object 类型、操作类型和其他 Ontology 资源。
- 添加用于访问平台 API 的操作和资源。
- 生成任意支持语言的包。
- 使用为您的特定应用程序 SDK 生成的自定义文档。
## 使用 Developer Console 创建应用程序

在您的 Foundry 实例中导航至 Developer Console，然后选择+ New application。

如果您没有看到+ New application按钮，您可能需要额外的权限。请参阅权限文档了解更多详情。

接下来，按照出现的创建向导中的步骤，并添加以下详细信息：

- 在Basic information页面，为您的应用程序添加一个图标；当用户看到同意屏幕时，该图标将用于识别应用程序。
- 在Application type页面，选择Client-facing application。
- 在Permissions页面的Authorization code grant部分，将重定向 URL 设置为http://localhost:8080/auth/callback。
按照配置 CORS中的说明将http://localhost:8080添加到 Control Panel 的 CORS 策略中。
如果您没有权限配置 CORS 且您的 Foundry 管理员无法为您配置 CORS，请将重定向 URL 设置为https://localhost:8080/auth/callback。

### 资源

- 在Resources页面，选择Yes, generate an Ontology SDK。
- 选择一个要使用的 Ontology。然后，选择您希望 Ontology SDK 包包含的 Object 类型和操作类型。在此练习中，选择任何可用的 Object 类型。
您选择的数据实体控制应用程序的两个方面：

- 生成的类型：基于所选实体创建特定语言的绑定。此外，集成的 API 文档将根据您的选择生成。
- 应用程序词元：默认情况下，通过 OAuth 2.0 流程获得的词元范围限定为所选实体集合。更多详情请参阅资源访问范围。
- 如果您需要使用应用程序进行平台 API 请求，请务必通过Platform SDK选项卡添加适当的资源和操作。
Client allowed operations表中授予的操作可能允许应用程序访问底层服务端点。

- 审核并确认您输入的信息，然后选择Create application来创建应用程序。
- 最后，您必须选择Generate first version以获取所创建包的第一个版本。
## Ontology 特定文档

Developer Console 基于您选择的 Ontology 实体生成文档。此文档适用于 TypeScript、Python 和 cURL；您可以使用 Console 右上角的下拉菜单在不同语言之间切换。

在上述示例中，每个 Object 类型、操作类型和函数都有文档说明。文档包括如何返回特定属性或如何使用参数的代码示例；您可以直接将这些示例复制并粘贴到您的代码中。
