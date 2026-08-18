来源: https://palantir.com/docs/zh/foundry/carbon/modules-discovery/

# 配置模块发现

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 配置模块发现

Object Explorer应用程序包括一个Open in按钮，该按钮使用户能够在一个平台应用程序中打开结果集到另一个平台应用程序中。Open in按钮的可用选项列表可以在 Carbon 编辑侧边栏的可发现模块部分进行配置。可在Open in菜单中包含的 "可发现" 选项包括：

- Workshop 模块
- Quiver 模板
- Slate 应用程序
- Vertex 图
模块发现行为——即出现在Open in菜单中的选项——取决于用户是在 Carbon 内还是在 Carbon 工作区外工作。了解更多关于在 Carbon 内部或外部的模块发现行为。

## Workshop 模块

通过Open in按钮使特定Workshop模块可发现需要在 Carbon 编辑侧边栏以及 Workshop 应用程序中进行配置。

### Carbon 编辑侧边栏

通过Open in按钮使 Workshop 模块可发现的第一步发生在 Carbon 编辑侧边栏。

- 在 Carbon 编辑器中，导航到General选项卡并将模块添加到Discoverable modules列表中。
- 选择Add item按钮以打开一个弹出窗口，提示输入Module Type。
- 在Module Type下拉菜单中选择Workshop module，然后选择Open Compass dialog来选择您希望使其可发现的特定 Workshop 模块。
### Workshop

在 Carbon 编辑侧边栏中的配置完成后，通过Open in按钮使 Workshop 模块可发现的下一步在 Workshop 工具本身中进行。

- 在Workshop中，打开您希望使其可发现的 Workshop 模块。
- 通过在变量Settings面板中添加一个外部 ID，为输入对象集创建一个模块接口变量。
- 为输入对象类型设置一个约束。
- 如果未设置任何约束，则该模块将对所有对象类型在Open in按钮上可发现。
## Quiver 模板

Quiver 模板也可以添加到Open in菜单中。该操作将出现在创建模板时的对象类型的探索中的Open in菜单中。

例如，如果您创建了此 Quiver 模板并将其添加为可发现模块，那么Open in Aircraft Template将出现在Aircraft对象类型的探索中。

## Slate 应用程序

如果您选择一个包含变量的Slate应用程序，它将在所有对象类型的探索中的Open in菜单中出现。

## Vertex 图

选择Vertex将在所有对象类型的探索中添加一个Open in Vertex graph选项。

## 在 Carbon 和 Carbon 外部的模块发现行为

模块发现行为——即出现在Open in菜单中的选项——取决于用户是在 Carbon 内部还是在 Carbon 界面外部工作。

在 Carbon 工作区中工作时，Open in按钮只会显示为当前选择的工作区配置的可发现模块。

在 Carbon 外部，Open in按钮将显示用户有权访问的所有提升的工作区中可发现模块的并集。了解更多关于提升的工作区。

以下示例说明了这种差异：

- Zayna 是两个不同的提升的 Carbon 工作区的成员：Claims 工作区Actuary 工作区
- Claims 工作区
- Actuary 工作区
- 在 Claims 工作区中，有两个不同的模块配置为可发现：Claim Alert ApplicationClaim Investigator Application
- Claim Alert Application
- Claim Investigator Application
- 在 Actuary 工作区中，有一个模块配置为可发现：Claim Cohorts Application
- Claim Cohorts Application
由于这种配置，Zayna 在不同位置工作时将在Open in按钮中看到不同的模块集合：

- 在 Claims 工作区中，Open in按钮将显示：Claim Alert ApplicationClaim Investigator Application
- Claim Alert Application
- Claim Investigator Application
- 在 Actuary 工作区中，Open in按钮将显示：Claim Cohorts Application
- Claim Cohorts Application
- 在 Carbon 外部，Open in按钮将显示：Claim Alert ApplicationClaim Investigator ApplicationClaim Cohorts Application
- Claim Alert Application
- Claim Investigator Application
- Claim Cohorts Application
了解更多关于模块之间导航的配置。
