来源: https://palantir.com/docs/zh/foundry/carbon/modules-navigation/

# 配置模块间的导航

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 配置模块间的导航

Carbon 工作区的一个优势是能够执行跨越多个模块的工作流程。这为用户提供了一个统一的工作流程，而不是一组孤立和分散的应用。

在执行他们的工作流程时，用户不应该考虑特定的产品、模块或界面。相反，用户应该能够无缝地完成他们的工作。Carbon 提供了一个导航框架，使对象或对象集能够作为参数从一个模块传递到另一个模块。

## Carbon 中的导航简介

作为 Carbon 中的搭建者，您可以定义每个模块的输入和输出，以及当前可操作的对象或对象集。可操作的对象或对象集可以是列表中的选择、函数的结果、给定类型的所有对象，或任何其他可以使用 Ontology 基元编码的对象集。在接收端，另一个模块可以指定（具有适当的约束条件）其参数中的哪个可以接受上述描述的输出。

### 模块间的导航

如果用户决定执行从一个模块到另一个模块的导航操作（通常通过操作菜单中的按钮或由前端组件触发的其他操作），Carbon 将在新标签页中打开接收模块，允许用户逐步完成工作流程而不失去起始模块中保存的状态。

这有助于构建复杂的工作流程，因为它更容易将一个模块的结果分支到另一个模块的多个实例中。例如，Object Explorer 列表中的结果可以独立打开为 Object View 标签，并在不丢失原始结果列表的情况下进行检查。

### 多个导航步骤

模块间的导航操作次数没有限制。这意味着导航框架可以促进任意数量的工作流程步骤，因为每个后续模块的输出可以作为另一个模块的输入。同一模块甚至可以在一个工作流程中多次出现，如下所示，每次可能具有不同的输入。

#### 多个导航步骤的示例

在下面描述的工作流程中，我们希望使用 Carbon 工作区中可用的工具找到一个特定的单通道飞机，以便开始 Quiver 分析。

首先，我们搜索关键字aircraft；导航框架将我们带到以aircraft作为输入的搜索模块。

我们从搜索结果中选择Aircraft object type。导航框架将我们带到以Aircraft object type作为输入的 Object Explorer 模块。

现在，我们希望在Single Aisle AircraftsQuiver 模块中分析整个对象结果集。导航框架打开Single Aisle AircraftsQuiver 模块，并将 185 个Aircraft类型的对象作为输入。

在该模块中，我们选择Q-AGM飞机进行进一步检查。导航框架打开以Q-AGM Aircraft作为输入的 Object View 模块。

此时，我们决定需要对该对象进行进一步分析。例如，我们可能想要检查对象的链接或审查关联的时间序列数据。为此，导航框架再次用于打开Single Aisle AircraftsQuiver 模块，这次以Q-AGM Aircraft对象作为输入。

### Carbon 之外的导航

需要注意的是，尽管导航框架主要是为 Carbon 中的操作应用案例设计的，但导航框架也用于对象领域中的独立前端应用。在这些应用中工作时，导航操作会在新浏览器标签中打开接收应用（而不是在 Carbon 标签中打开），但所有优势仍然有效。因此，最终用户或搭建者无需在 Carbon 内外的应用案例之间进行区分。

## 在 Carbon 工作区中发现模块或使用集成模块

为了在 Carbon 中创建高质量的操作界面，搭建者必须能够指定哪些模块可用于导航，以便为最终用户工作流程的步骤量身定制工作区。

这些可用模块称为可发现模块，相应的导航操作在某些模块中（例如 Object Explorer 或 Object View）的Open in菜单中可访问（注意，只有满足约束条件的操作才会显示）。其他模块如 Workshop 允许搭建者指定在用户交互（如按钮点击）后触发的具体导航操作。您可以在下面的Carbon 模块的导航框架集成部分找到有关每种模块类型如何处理导航操作的详细信息和示例。

模块发现行为，即在Open in菜单中出现的选项，取决于用户是在 Carbon 中还是在 Carbon 工作区之外工作，这在下面的文档中进行了描述。

### 在 Carbon 配置编辑器中配置可发现模块

- 在 Carbon 编辑器（通过/workspace/carbon/edit访问）中，导航到General标签并将模块添加到Discoverable Modules列表中。
- 选择Add an element按钮以打开弹出窗口，提示选择Module Type。
- 在Module Type下拉菜单中选择所需的模块类型，然后选择Open Compass dialog以选择要使其可发现的特定模块。
## Carbon 内外的模块发现行为

模块发现行为，即在Open in菜单中出现的选项，取决于用户是在 Carbon 界面中还是在 Carbon 界面之外工作。

在 Carbon 工作区中工作时，Open in菜单将仅显示为当前选择的工作区配置的可发现模块。这样，每个工作区可以作为一个空间，提供旨在针对明确定义的操作工作流程的具体、精心策划的导航操作集合。

在 Carbon 之外工作时，Open in按钮将显示用户有访问权限的所有提升工作区中的所有可发现模块。这使得用户在特定 Carbon 工作区之外操作时能够充分利用 Foundry 的所有功能。所有可发现模块的集合由以下 UNION 操作确定：

- 首先，考虑用户有访问权限的所有组织，包括用户的主要组织和用户具有访客访问权限的所有组织。
- 对于每个组织，考虑该组织的所有提升工作区并对这些工作区的所有可发现模块进行并集。
- 将模块筛选为可以应用于显示Open in菜单的模块当前输出的模块。
以下示例说明了 Carbon 内外的模块发现之间的区别。

- Zayna 的主要组织是 Primary Org，她还具有 Guest Org 的访客访问权限。
Zayna 的主要组织是 Primary Org，她还具有 Guest Org 的访客访问权限。

- Zayna 是 Primary Org 中两个不同 Carbon 工作区的成员：Claims Workspace，配置了两个可发现模块（Claim Alert Application 和 Claim Investigator Application）。Actuary Workspace，配置了一个可发现模块（Claim Cohorts Application）。
Zayna 是 Primary Org 中两个不同 Carbon 工作区的成员：

- Claims Workspace，配置了两个可发现模块（Claim Alert Application 和 Claim Investigator Application）。
- Actuary Workspace，配置了一个可发现模块（Claim Cohorts Application）。
- Zayna 也是 Guest Org 中一个 Carbon 工作区的成员，即 Flight Workspace。Flight Workspace 配置了一个可发现模块（Flight Tracker）。
Zayna 也是 Guest Org 中一个 Carbon 工作区的成员，即 Flight Workspace。

- Flight Workspace 配置了一个可发现模块（Flight Tracker）。
由于这种配置，Zayna 将根据她工作的地方在Open in按钮中看到不同的模块集：

- 在 Claims Workspace 中，Open in按钮将显示 Claim Alert Application 和 Claim Investigator Application。
- 在 Actuary Workspace 中，Open in按钮将显示 Claim Cohorts Application。
- 在 Flight Workspace 中，Open in按钮将显示 Flight Tracker。
- 在 Carbon 之外，Open in按钮将显示四个模块：Claim Alert Application、Claim Investigator Application、Claim Cohorts Application 和 Flight Tracker。
## 设置导航当用户未直接访问 Carbon

在某些情况下，可能没有操作用户或 Carbon 工作区的应用案例。然而，您可能仍希望配置Open in操作以在独立对象应用之间导航，如之前在模块发现或在 Carbon 工作区中使用集成模块中描述的那样。

推荐的解决方案是创建一个 Carbon 工作区，使其可以被期望的用户集访问（最好通过项目级别权限），并在其中配置可发现模块集。工作区必须是提升工作区，以便其可发现模块可以在 Carbon 之外的Open in操作下显示。

我们建议确保可发现模块本身对用户可访问 - 最简单的方法是将它们放在与 Carbon 工作区本身相同的项目中。

以下示例演示了此过程：

- 创建一个新项目，其中包含工作区资源（Carbon）和模块资源（Workshop）。默认角色设置为 Viewer，以便为组织中的所有用户授予访问权限。请注意，工作区资源需要在 Carbon 内部创建并放置在项目中，因为无法直接从项目中创建工作区。
- 将My inbox模块添加到工作区的Discoverable modules列表中。
- 使工作区对于组织来说是重要的，以便导航框架在 Carbon 之外识别出可发现模块。
- 现在可以通过 Object Explorer 中的Open in菜单在 Carbon 之外访问My inbox模块。
## Carbon 模块的导航框架集成

本节包含有关每种 Carbon 模块类型如何与导航框架集成的信息。您将找到有关在每种模块类型的上下文中，什么被视为导航操作的输出的信息，以及如何使 Carbon 参数成为导航操作的输入的信息。

对于没有关联 Foundry 资源的模块（Object View、Object Explorer、Search），输入和输出是预定义的，不能更改或配置。例如，Object View 将始终接受任何单一对象作为其输入，而 Object Explorer 的输出设置为用户探索的当前结果。我们称这些模块为内建模块；内建模块不需要显式使其可发现。

可以由搭建者创建的模块（例如 Workshop、Slate、Quiver 或 Map）具有更复杂和强大的输入和输出指定方式，通常通过在此类模块的上下文中定义的变量或参数。我们称这些模块为动态模块，它们必须显式使其可发现。

### Object View（内建）

#### Object View：通过模块发现输入

Object View 模块支持任何对象类型的单个对象作为其输入。打开 Object View 模块的导航操作默认存在于大多数与单个选定对象相关的上下文或操作菜单中。无法禁用此导航操作或在工作区配置编辑器中将 Object View 模块配置为可发现。

#### Object View：通过 UI 元素输入

在动态模块中，可以创建 UI 元素以触发到 Object View 的导航操作：

- 在 Workshop 中，您可以定义Open Object view类型的事件；有关 Workshop 模块输出的更多详细信息，请参阅Workshop 模块的输出文档。
- 在 Slate 中，通过到独立 Object View 应用的常规 HTML 链接进行的导航将被 Carbon 拦截，并且会打开一个新的 Object View 模块，其中包含链接中存在的对象 RID。有关更多详细信息，请参阅Slate 模块文档。
#### Object View：输出

Object View 中当前显示的对象是模块的输出。

### Object Explorer

#### Object Explorer：通过模块发现输入

Object Explorer 模块支持单个对象集（版本化或非版本化）作为其输入。打开 Object Explorer 模块的导航操作存在于大多数与单个选定对象集相关的上下文或操作菜单中，或者存在对象集链接的地方（请参阅下图中对象属性呈现为对象集链接的示例）。无法禁用此操作或在工作区配置编辑器中将 Object Explorer 模块配置为可发现。

还可以通过多种方式从搜索模块导航到 Object Explorer 模块，例如：

- 打开已保存的探索，
- 打开已保存的对象列表，
- 开始对对象类型的探索，以及
- 打开模块的快捷方式。
#### Object Explorer：通过 UI 元素输入

在动态模块中，可以创建 UI 元素以触发到 Object Exploration 的导航操作：

- 在 Workshop 中，您可以定义Open Object explorer类型的事件。有关 Workshop 模块输出的更多详细信息，请参阅Workshop 模块的输出文档。
- 在 Slate 中，通过到独立 Object Explorer 应用的常规 HTML 链接进行的导航将被 Carbon 拦截，并且会打开一个新的 Object Explorer 模块，其中包含链接中存在的对象集 RID。有关更多详细信息，请参阅Slate 模块文档。
#### Object Explorer：输出

Object Explorer 中当前选择的对象集是模块的输出。

### Search（内建）

搜索模块是打开各种 Ontology 工件的入口，提供了使用关键字筛选对象类型及其属性的能力，并浏览资源列表，如 Explorations、Lists 和 Modules。

#### Search：通过模块发现输入

搜索模块只能通过工作区中的模块快捷方式或通过 Carbon 首页模块的搜索栏直接访问。

#### Search：通过 UI 元素输入

可以配置 Carbon 首页模块以显示一个搜索栏。搜索栏中输入的查询成为用于打开搜索模块的参数值。

#### Search：输出

当用户在搜索模块中对特定资源进行操作时，相应的模块将在 Carbon 中的新标签页中打开。除了模块工件（仅选择的模块会打开）外，Object Explorer 将接收输入对象集：

- 对于对象类型，将打开基于该类型的新探索。
- 对于探索，将打开基于探索所支持的版本化对象集的新探索。
- 对于列表，将打开基于列表中包含的对象的新探索。
- 对于比较，将打开基于比较视图的比较模式新探索。
### Workshop

#### Workshop：通过模块发现输入

任何至少具有一个对象集类型模块界面变量的 Workshop 模块都可以配置为可发现模块，如配置模块发现，Workshop 模块部分所述。

#### Workshop：通过 UI 元素输入

在动态模块中，可以创建 UI 元素以触发到 Workshop 模块的导航操作：

- 在 Workshop 中，您可以定义Open Workshop类型的事件；有关 Workshop 模块输出的更多详细信息，请参阅Workshop 模块的输出文档。
在 Workshop 中，您可以定义Open Workshop类型的事件；有关 Workshop 模块输出的更多详细信息，请参阅Workshop 模块的输出文档。

- 在 Slate 中，通过到独立 Workshop 应用的常规 HTML 链接进行的导航将被 Carbon 拦截，并且会打开一个新的 Workshop 模块，其中包含链接中存在的对象集 RID。有关更多详细信息，请参阅Slate 的文档。
在 Slate 中，通过到独立 Workshop 应用的常规 HTML 链接进行的导航将被 Carbon 拦截，并且会打开一个新的 Workshop 模块，其中包含链接中存在的对象集 RID。有关更多详细信息，请参阅Slate 的文档。

#### Workshop：模块界面

可以通过在变量Settings面板中设置外部 ID 来将Workshop 变量添加到模块界面，以启用 Workshop 模块的参数化。模块界面变量的值可以通过 URL 传递到独立 Workshop 应用，或者通过参数传递到 Carbon Workshop 模块。

##### 通过 URL

要通过 URL 将参数传递到 Carbon 模块中的 Workshop 应用，您必须在 URL 中的参数前添加param.variable.。

示例：workspace/carbon/ri.carbon.main.workspace.../ri.workshop.main.module...?param.variable.flight_id=1000,1001&param.variable.route=100,200

##### 通过参数

当用作 Carbon 参数时（例如，在顶部栏模块快捷方式中），参数名称必须是以字符串variable.（包括点）作为前缀的变量外部 ID。

##### 限制

目前，Carbon 导航不支持以下类型的模块界面变量：

- 具有空对象集作为其值的对象集变量。
- 值为NaN（不是数字）的数字变量。
- 对象集筛选变量；作为替代方案，请考虑使用其他变量类型，如数字或字符串，它们可以在 Workshop 模块中定义的对象集筛选器中使用。
- 时间序列集变量。
- 场景变量。
#### Workshop：事件

在 Workshop 模块中，可能会有多个对象集通过上述变量概念同时被操作。可以将任何此类对象集作为导航操作的输入传递给许多其他类型的模块，使用Open Application类型的Workshop 事件。

目前支持以下类型的模块：

- Workshop
- Object View
- Object Explorer
- Notepad（只读）
- Vertex exploration
一旦选择了要打开的应用或模块类型（在动态模块的情况下，通过资源选择器选择一个模块），可以选择一个特定变量作为输入。

当在 Workshop 模块中触发配置的事件时，将使用所选变量的当前值构建导航操作，并打开一个新的 Carbon 标签。

### Slate

#### 配置 Slate 文档以用作 Carbon 模块

Carbon 可以在内联框架（iframes）中显示 Slate 模块。Slate 使用一个文档 API 来保存其微件的状态，例如记住下拉菜单中选择的值，或某个复选框是否被选中。

保存 Slate 微件的状态需要 Carbon 和 Slate 模块之间的通信。当用户在 Carbon 中从 Slate 模块导航离开时，Carbon 将向 Slate 模块的 iframe 发送一个 POST 消息，以通知底层 Slate 文档保存其状态并将相应的标识符报告给 Carbon。此标识符会被转换为 Carbon 模块参数。为了使 Slate 模块能够理解来自 Carbon 的 POST 消息并在导航期间成功保存状态，必须在支持模块的 Slate 文档中添加两个小事件，如下所列：

事件以在 Carbon 请求时保存视图

```
Copied!1
2
3
4
5
6
Event: slate.getMessage
Action: slate.saveView
const type = {{slEventValue}}['type']; // 从事件值中提取类型
if (type !== "carbon-save-view-request") { // 检查类型是否为“carbon-save-view-request”
  return {{slDisableAction}}; // 如果不是，禁用该操作
}
```

事件以将保存的视图标识符传递给iframe父级（Carbon）

```
Copied!1
2
3
4
5
6
Event: slate.viewSaved
Action: slate.sendMessage
return {
  type: "viewSaved", // 返回的数据类型为 "viewSaved"
  payload: {{slEventValue}} // 负载数据来自 slEventValue
};
```

#### Slate变量和Carbon参数

Slate模块输入使用Slate变量，这些变量被转换为Carbon模块参数，以指定诸如菜单栏项目等Carbon功能。以下部分包含有关如何将Slate变量转换为Carbon接受的格式和类型的更多信息。

Slate变量：

Slate菜单栏项目：

Slate参数

Slate变量的Carbon参数类型确定

Slate变量是无类型的；没有机制可以声明给定变量是字符串、数字还是对象。因此，Carbon会检查变量的默认值以确定其类型。在上面的截图中，v_var3具有一个对象RID作为其默认值。这让我们可以将对象指定为相应Carbon参数的值。如果您的Slate文档的变量没有默认值是合理的，Carbon会自动为两个变量名称进行类型化：

```
Copied!1
2
  v_objectSetPassedFromCarbon # 自动类型化为 objectSet
  v_objectPassedFromCarbon    # 自动类型化为 object
```

如果在Slate文档中定义了这些变量，它们将始终如上所述进行类型化，而不考虑其默认值。这在您希望使您的Slate模块可发现并通过Carbon参数从另一个模块或类似Object Explorer的应用程序传递对象（或单个对象）的情况下特别有用。

#### Slate：通过模块发现输入

Slate模块支持单个对象或单个对象集（有版本或无版本）作为其输入。确保Carbon能够准确地将Slate文档中的一个变量转换为Carbon参数并识别为这种类型非常重要，否则将无法提供相应的导航操作。

#### Slate：通过UI元素输入

目前，不支持通过UI元素导航到Slate模块，除了从另一个Slate模块导航（请参阅下面的输出部分）。

#### Slate：输出

Slate模块以特定方式与导航框架集成。每当Slate文档中发生导航时（例如，通过点击链接），Carbon会拦截此类导航并尝试解释它。如果导航所到达的地址可以被识别为独立的前端应用程序，并且该应用程序有相应的Carbon模块，该模块将在新的Carbon标签页中打开。例如：

- 链接到workspace/hubble/objects/ri.phonograph2-objects.main.object.4202d614-bb6e-471d-80d2-2cf9c735caf3将被解释为打开Object View模块，使用对象RIDri.phonograph2-objects.main.object.4202d614-bb6e-471d-80d2-2cf9c735caf3。
- 链接到workspace/module/view/latest/ri.workshop.main.module.25b772f5-a095-48c6-a889-a960eeb93ce1?orderInput=ri.object-set.main.object-set.63417288-3e8d-4b34-a995-d6c2c6054e27将被解释为打开Workshop模块，使用模块RIDri.workshop.main.module.a1838b32-448d-43f6-beff-3c9e40a34929和参数orderInput等于ri.object-set.main.object-set.63417288-3e8d-4b34-a995-d6c2c6054e27。
- 链接到workspace/slate/documents/another-slate-doc将被解释为打开Slate模块，使用与Slate永久链接another-slate-doc对应的模块RID。
- 链接到workspace/quiver/template/view/ri.quiver.main.artifact.b5597828-d4a2-4fec-964f-304a3ad7f1a9将被解释为打开Quiver Template模块，使用模块RIDri.quiver.main.artifact.b5597828-d4a2-4fec-964f-304a3ad7f1a9。
- 链接到workspace/hubble/exploration/saved/ri.object-set.main.versioned-object-set.ba21a7b3-3407-4bb1-ae9f-aae3d70c4a40将被解释为打开Object Explorer模块，使用对象集RIDri.object-set.main.versioned-object-set.ba21a7b3-3407-4bb1-ae9f-aae3d70c4a40。
因此，Slate模块没有特定的输出基于Slate文档中微件的状态；每个导航操作都是用户操作的结果，输出基于该操作确定。

#### 从Slate模块中的嵌套iframe导航

Slate具有在文档中嵌入iframe的功能。通过此类iframe内的链接进行的任何导航将属于以下类别之一：

- 导航在iframe内发生：iframe将更改自己的源URL。例如，iframe可以被视为子视图，内容更改保持在iframe内。
- 导航在iframe外发生：当点击iframe中的链接时，将打开一个新的Carbon标签页。例如，当iframe中的链接指向一个对象时，点击链接将在新标签页中打开该对象。
在后一种情况下，为了使Slate模块的输出部分中描述的机制生效，嵌套iframe中的链接必须指定最外层的Slate iframe（Carbon显示顶级Slate模块的iframe）作为其target。Carbon将该iframe的名称设置为carbon-navigation-target。下面可以找到一个链接的HTML代码片段示例：

```
Copied!1
2
3
4
5
6
<a
  href="/workspace/hubble/objects/ri.phonograph2-objects.main.object.4202d614-bb6e-471d-80d2-2cf9c735caf3"
  target="carbon-navigation-target" <!-- 设置链接的打开方式 -->
>
  Link to an object with target="carbon-navigation-target"
</a>
```

这段HTML代码创建了一个链接 (<a>标签)，该链接指向一个特定的对象。href属性指定了链接的目标URL。target="carbon-navigation-target"属性定义了链接的打开方式，通常用于指定在新的浏览上下文（如新窗口或标签页）中打开链接。
这种方法可以正确处理任何深度的 iframe 嵌套。例如，您可以在第二个 iframe 内嵌入第三个 iframe，并将其嵌入由 Carbon 创建的顶级 Slate 模块 iframe 中。

### Quiver

在 Quiver 工件中，只有 Quiver 模板可以用作 Carbon 模块。请参阅在 Quiver 文档中创建和嵌入模板了解模板和分析之间的区别，以及如何创建模板。

Quiver 模板可以是对象模板或对象集模板。

在这两种情况下，都必须选择一种对象类型作为模板的基础。这是为了确保无论何时将参数——对象或对象集——传入模板，所有定义的变换都能正常工作（例如，总是会考虑相同的对象属性和 Ontology 链接集）。

因此，模板所基于的对象类型会转换为对可能输入的约束。有关约束如何影响导航操作可用性的更多详细信息，请参阅模块发现或在 Carbon 工作区中使用集成模块。

例如，假设Single Aisle Aircrafts模板基于Aircraft对象类型。

导航操作的推断约束是对象集输入必须仅包含Aircraft对象。在 Carbon 工作区中，Single Aisle Aircrafts模块被添加到可发现模块配置部分。

在对象浏览器模块中检查Aircraft对象类型的一组结果时，由于操作的约束得到满足（因为对象集中包含Aircraft类型的对象），导航操作会显示在打开方式菜单中：

在对象浏览器模块中检查Order对象类型的一组结果时，由于对象集包含与Aircraft不同类型的对象且导航操作的约束不满足，导航操作不会出现在打开方式菜单中：

#### Quiver：通过模块发现输入

任何非空的 Quiver 模板模块都可以配置为可发现的，如前几节所述。

#### Quiver：通过 UI 元素输入

目前，在动态模块中，可以通过 Slate 中的 UI 元素打开 Quiver 模板模块。在 Slate 模块中，通过常规 HTML 链接到独立的 Quiver 应用程序的导航将被 Carbon 拦截，并会打开一个新的 Quiver 模板模块。有关详细信息，请参阅Slate 模块文档。

#### Quiver：输出

Quiver 模板在输出端与导航框架提供了非常基本的集成。卡片中显示的每个对象都可以在弹出窗口中进行检查，并可以从那里触发到对象视图的导航操作。
