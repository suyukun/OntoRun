来源: https://palantir.com/docs/zh/foundry/quiver/dashboards-workshop/

# 在 Workshop 模块中嵌入

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 在 Workshop 模块中嵌入

您可以在Workshop 模块中嵌入已发布的 Quiver 仪表盘。

输入和输出的主要目的是在嵌入仪表盘的应用程序中传递数据。例如，嵌入的仪表盘中的图表可以根据应用程序中的对象集选择进行更新，或者 Workshop 指标卡片可以突出显示嵌入仪表盘中计算的值。

在下面的示例中，我们为具有高优先级维护问题的飞机筛选 WorkshopAircraft对象集。嵌入的 Quiver 仪表盘会自动更新，显示按当前位置的飞机条形图和旁边的对象列表。当我们从条形图中仅选择位于DFW和DEN的飞机时，顶部的 Workshop 指标卡片会相应更新，以显示 Quiver 条形图选择中的对象计数。

## 嵌入仪表盘

在 Workshop 中，选择添加微件，然后从菜单中选择Quiver 仪表盘。

在微件编辑器中，选择您要嵌入的仪表盘。列表显示您有权访问的所有已发布仪表盘。将鼠标悬停在每个仪表盘旁边的信息提示上以获取更多信息，或在新标签页中打开。

## 配置输入和输出

您可以为仪表盘定义多个输入和输出。

如果所选仪表盘已配置输入或输出，Workshop 会提示您将它们映射到 Workshop 变量。
Quiver 仪表盘输入和输出可以根据以下映射表映射到 Workshop 变量：

| Quiver 数据类型 | Workshop 变量类型 |
| --- | --- |
| Boolean | Boolean |
| Number | Numeric |
| String | String |
| Time | Timestamp, Date |
| Time Range | String (因为 Workshop 没有范围变量类型，请将范围起始和范围结束作为字符串传递) |
| Time Series | Object (因为 Workshop 没有时间序列变量类型，请传递时间序列对象) |
| Object | Object |
| Object Set | 对象集 |

最后，请确保选择了正确的仪表盘版本。如果您希望仪表盘自动显示最新版本，请启用自动更新切换。
