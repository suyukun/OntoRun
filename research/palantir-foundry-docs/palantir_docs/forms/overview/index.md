来源: https://palantir.com/docs/zh/foundry/forms/overview/

# Forms

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Forms

我们不建议使用 Foundry Forms，因为它不再更新，并将逐步停用。相反，对于在 Foundry 上的数据输入或数据输出工作流程，我们建议使用 Foundry Ontology 搭建用户输入工作流程。使用 Ontology，可以将相关的数据结构表示为 Object 类型，并使用操作配置数据输出交互。

操作提供了更强大和细粒度的控制权限，涉及添加、编辑和删除数据，包括对受限视图的尊重和配置复杂的条件权限。此外，操作可以由Foundry 函数支持，允许更具表达性的写回逻辑。

除了操作配置中的内置表单构建器外，操作还在 Workshop 和 Slate 中原生支持，在这里可以使用完整的应用程序搭建工具套件来打造复杂的数据输入用户体验。

操作还会自动为 Foundry API 生成 API 绑定，外部应用程序可以通过该 API 将数据写入 Foundry，并与 webhooks 接口，操作可以通过 webhooks 将数据写入外部数据系统或触发其他下游效果。

目前没有弃用 Foundry Forms 的时间表，现有的使用 Foundry Forms 的实现将得到支持。强烈建议新工作流程使用基于本体的方法，并且预计 Foundry Forms 不会接收新功能、增强功能或非安全相关的修复。

## 什么是 Foundry Forms？

Foundry Forms是一个无缝集成到其他 Foundry 应用程序中的表单构建界面。Foundry Forms提供了直观的体验，同时不牺牲复杂的可配置性。

使用 Forms，用户即使没有编程经验，也可以创建和管理定制的数据输入和存储解决方案。用户可以使用 Forms 配置各种工作流程，包括：

- 定义动态字段以引导来自响应者的数据。
- 将表单嵌入到Object Explorer和Slate中的部分。
- 将收集的信息存储在Fusion中。
通过学习如何创建表单或查看和编辑表单响应来开始使用 Forms。
