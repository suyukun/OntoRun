来源: https://palantir.com/docs/zh/foundry/workshop/widgets-markdown/

# Markdown

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Markdown

Markdown微件支持使用 Markdown 格式渲染文本。此外，高级功能允许 Markdown 文本引用 Ontology 对象并支持点击事件。模块搭建者配置 Markdown 微件时可以使用以下功能：

- 基本的 Markdown 文本格式，如加粗、斜体、删除线和高亮
- 更高级的 Markdown 格式，如标题、表格、块样式、代码样式和 URL
- 从特定高亮锚文本到 Ontology 对象的嵌入引用
- 由特定高亮锚文本触发点击 Workshop 事件
下图显示了一个配置的 Markdown 微件示例，包括对象引用，其中附有 Ontology 对象引用的文本锚显示为下划线且可选择：

## 配置选项

下图显示了未配置的 Markdown 微件的初始状态及其初始配置面板。

对于 Markdown 微件，核心配置选项如下：

- 输入数据：文本 / 变量文本：如果选择文本选项，搭建者可以直接在配置面板中输入他们想要显示的 Markdown 文本。变量：如果选择变量选项，可以选择一个字符串变量作为要显示的 Markdown 文本输入。
- 文本：如果选择文本选项，搭建者可以直接在配置面板中输入他们想要显示的 Markdown 文本。
- 变量：如果选择变量选项，可以选择一个字符串变量作为要显示的 Markdown 文本输入。
- 显示选项：标准 Markdown/对象引用标准 Markdown：默认情况下启用此选项，并以标准 Markdown 格式显示输入。对象引用：如果启用，可以在文本中嵌入对 Ontology 对象的引用和触发点击的 Workshop 事件。这是 Markdown 语法的自定义扩展；有关此高级功能的更多信息，请参见下文中的文档。
- 标准 Markdown：默认情况下启用此选项，并以标准 Markdown 格式显示输入。
- 对象引用：如果启用，可以在文本中嵌入对 Ontology 对象的引用和触发点击的 Workshop 事件。这是 Markdown 语法的自定义扩展；有关此高级功能的更多信息，请参见下文中的文档。
## Markdown 微件中的对象引用

作为一项高级功能，Markdown 微件允许搭建者标记 Markdown 文本的子集（“锚”），然后使用这些锚链接到特定的 Ontology 对象并触发 Workshop 点击事件。

创建这些锚点的格式如下：

```
Copied!1
2
3
4
5
6
:objectreference[$text_to_display]{objectType="$object_type_id" primaryKey="$object_primary_key"}

# 这是一个自定义语法的示例，可能用于某种模板或标记语言。
# - $text_to_display: 需要显示的文本。
# - $object_type_id: 对象的类型标识符。
# - $object_primary_key: 对象的主键，用于唯一标识对象。
```

让我们通过一个示例来演示如何在一个句子中引用两个Flight Alerts对象。首先，让我们看看希望在屏幕上为用户显示的最终状态。注意：下面引用的每个Flight Alert对象都可以由用户单独选择，然后成为Markdown微件的输出选定对象集。

为了实现上述效果，支持的Markdown输入如下：

纽瓦克机场在五月__*很少*__出现航班问题，但有两个高优先级延误：:objectreference[Alert A00150]{objectType="flight-alert" primaryKey="A00150"} 和 :objectreference[Alert A00182]{objectType="flight-alert" primaryKey="A00182"}

除了上述Markdown输入的语法外，搭建者还可以配置以下选项以用于对象引用：

- 选定对象集：使用对象引用所需。这是Markdown微件的输出对象集。当用户在Markdown微件中选择一个对象引用时，该对象将被输出到此对象集变量中。
- 对象类型：使用对象引用所需。搭建者应选择将在Markdown微件中引用的所有对象类型。一旦添加了对象类型，搭建者可以在内部配置面板中额外配置条件格式规则。如果Markdown微件中引用了一个对象类型但未在此列表中配置，该对象引用将不会出现在Markdown微件中。对象类型：指定对象类型以进一步配置颜色和事件选项。高亮颜色：选择一种静态颜色，从具有Ontology格式的属性继承颜色，或定义自定义规则以确定颜色。选择时覆盖事件：配置在Workshop中触发指定对象类型的事件。这些事件将覆盖选择时的其他事件。
- 对象类型：指定对象类型以进一步配置颜色和事件选项。
- 高亮颜色：选择一种静态颜色，从具有Ontology格式的属性继承颜色，或定义自定义规则以确定颜色。
- 选择时覆盖事件：配置在Workshop中触发指定对象类型的事件。这些事件将覆盖选择时的其他事件。
- 选择行为：控制Markdown微件内的选择行为。如果选择无高亮，在Markdown微件中选择一个对象引用不会导致选择状态。如果选择高亮最后选择的，在Markdown微件中选择一个对象引用将导致最近选择的锚文本被高亮。如果选择高亮选定引用，在Markdown微件中的高亮基于选定对象集的内容。此选项在Markdown中的对象引用与另一个微件中的对象1:1匹配，并且两个微件的选定对象集相同时效果最佳。
- 如果选择无高亮，在Markdown微件中选择一个对象引用不会导致选择状态。
- 如果选择高亮最后选择的，在Markdown微件中选择一个对象引用将导致最近选择的锚文本被高亮。
- 如果选择高亮选定引用，在Markdown微件中的高亮基于选定对象集的内容。此选项在Markdown中的对象引用与另一个微件中的对象1:1匹配，并且两个微件的选定对象集相同时效果最佳。
- 选择时的事件：此选项使模块搭建者能够配置在Markdown微件中选择对象引用时触发的Workshop事件（例如，导致一个包含更详细对象视图的抽屉式导航出现）。
Markdown中的对象引用也可以应用标准的Markdown格式。下面的截图包含了各种Markdown格式的示例，如嵌入对象的标题和表格。
