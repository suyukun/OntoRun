来源: https://palantir.com/docs/zh/foundry/contour/convert-to-pipeline-builder/

# 以Pipeline Builder格式导出Contour逻辑

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 以Pipeline Builder格式导出Contour逻辑

在Foundry中，您可以将复杂的Contour分析导出其基础逻辑到Pipeline Builder。虽然Contour是进行探索性分析和深入研究特定问题的理想工具，但它不太适合生产管道的维护。如果您的分析逻辑不会经常更改以您的应用案例，我们建议以Pipeline Builder格式导出以获得更多的灵活性和生产管道维护配置。

以下指南提供了在选择导出Contour分析时需要考虑的要点，以及如何轻松将您的逻辑导出到Pipeline Builder的引导式演练。

Contour到Pipeline Builder工具不能保证您的逻辑在导出后保持不变。对于依赖于严格逻辑的敏感应用案例，我们建议进行您自己的验证。

## 考虑因素

在决定将Contour逻辑导出到Pipeline Builder之前，请查看以下预期的好处、不支持的功能和可能的重大更改。

### 好处

Pipeline Builder是大多数应用案例中搭建和维护管道的推荐Foundry工具。当您开始使用稳态管道并且有下游应用或用户依赖于一致的模式时，您可能会发现Pipeline Builder是一个更灵活和可配置的管道维护和性能工具，提供以下各种生产质量的实用程序：

- 使用分支和拉取请求轻松协作。
- 安全、一致的模式。
- 广泛的类型安全函数。
- 自定义的强大计算配置文件。
- 增量变换模式以避免重建相同数据。
### 不支持的功能

转换器目前不支持SPLIT函数或透视转换。透视看板中的聚合将按预期工作。

除了上述不支持的配置外，其他函数可能由于各种原因不被支持。在这些情况下，转换器应返回一个解释失败的出错信息。如果您仍然希望将不支持的逻辑移至Pipeline Builder，请移除不支持的面板，直到转换成功。然后，将逻辑添加到Pipeline Builder图中的适当位置。

在尝试将Contour逻辑转换为Pipeline Builder时，可能会发生以下重大更改：

- Contour极其灵活的类型系统可能与Pipeline Builder使用的强类型不匹配。在大多数情况下，转换应失败并显示修复类型出错的信息。在某些边缘情况下，Pipeline Builder可能会为您的模式选择不同的输出类型。
- Contour中的某些参数无法转换为Pipeline Builder参数。如果发生这种情况，转换器将创建一个空白参数供您填写。
- 在Pipeline Builder中，时区可能与Contour中的处理方式不同。请务必在转换分析后确认时区行为。
## 将Contour分析转换为Pipeline Builder

按照以下步骤将您的Contour分析转换为Pipeline Builder：

- 导航到Foundry中的Contour分析。
导航到Foundry中的Contour分析。

- 滚动到分析底部，然后选择Convert to Pipeline Builder。
滚动到分析底部，然后选择Convert to Pipeline Builder。

- 在出现的对话框中，选择新管道的目标文件夹并选择Save。
在出现的对话框中，选择新管道的目标文件夹并选择Save。

- 一旦进入Pipeline Builder，预览并搭建您的管道。
一旦进入Pipeline Builder，预览并搭建您的管道。

## 故障排除

### 分析转换失败

在大多数情况下，当您的分析转换失败时，您将收到一个明确的出错信息。这意味着该行为是已知的缺陷。如果解除此问题对您的应用案例至关重要，请联系Palantir客服支持以查看此问题是否可以解决。

当出错未知或意外时，您将收到一个尽力而为的信息，告知您可能出错的操作类型，并重申Pipeline Builder的类型检查比Contour更严格（这可能是您出错的根本原因）。
