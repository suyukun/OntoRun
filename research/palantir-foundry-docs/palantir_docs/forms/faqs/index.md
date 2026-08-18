来源: https://palantir.com/docs/zh/foundry/forms/faqs/

# 常见问题解答

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 常见问题解答

本页讨论了一些常见问题和调试步骤，这些可能在使用 Foundry Forms 时作为参考有所帮助。

## 我可以用什么替代 Foundry Forms？

Foundry Forms 已不再是 Foundry 上数据输入或数据输出工作流的推荐方法。相反，请使用 Foundry Ontology 搭建用户输入工作流，将相关数据结构表示为 Object 类型，并通过操作配置数据输出交互。

操作提供了对添加、编辑和删除数据的权限进行更强大和细粒度控制的能力，包括遵循限制视图和配置复杂条件权限。此外，操作可以由Foundry 函数支持，从而实现更具表现力的数据输出逻辑。

除了操作配置中的内置表单搭建器外，操作在 Workshop 和 Slate 中也被本地支持，在这些地方可以使用完整的应用搭建工具套件来打造复杂的数据输入用户体验。

操作还会自动为 Foundry API 生成 API 绑定，外部应用程序可以通过此 API 将数据写入 Foundry，并通过 webhooks 接口，操作可以将数据写入外部数据系统或触发其他下游效果。

目前尚无废弃 Foundry Forms 的时间表，现有使用 Foundry Forms 的实现将继续受到支持。强烈建议新的工作流使用基于 Ontology 的方法，预计 Foundry Forms 不会接收新功能、增强或非安全相关的修复。

## 如何存储多个值？

各种字段类型允许响应者选择多个值（例如，checkboxes、dropdown和list）。在 Fusion 表中，值会自动存储在单个单元格中作为数组。使用 Object 类型时，需要进行一些额外设置：

- 在源数据集和数据输出数据集的模式中，相关列必须具有类型Array<X>，其中X是一个基本类型，如字符串或Integer。
- 在 Ontology 配置中，相关属性必须具有相同的基本类型X，并且必须选中允许多个值选项。
## 如何在目标数据集中将多个值转换为多行？

在配置字段以存储多个值之后，可以使用explode↗函数将每个值分离到其自己的行中。此函数可在数据集的 SQL/Python 变换或 Contour 表达式中使用。

## 如何生成一个字段，该字段是其他字段的串联？

使用模板字段进行以下配置：

```
Copied!1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
- uri: display.Text1
  name: Text 1
  type: Text
  tag: X
- uri: display.Text2
  name: Text 2
  type: Text
  tag: Y
- uri: display.Template
  name: Text 1_Text 2
  type: Template
  options:
    inputs:
      a: X  # 输入变量 'a' 对应标签 'X'
      b: Y  # 输入变量 'b' 对应标签 'Y'
    template: '{{a}}_{{b}}'  # 模板将使用 'a' 和 'b' 的值，以格式 'a_b' 进行拼接
```

此代码定义了三个对象。前两个对象是文本类型，分别标记为X和Y。第三个对象是一个模板，它将X和Y的值结合在一起，格式为'a_b'。

## 如何调试失败的提交？

当保存一个基于Object的表单时，您可能会看到这个出错信息：Submitting failed! Please try again or contact your Palantir support.。

要进行进一步调试，请按照以下步骤操作：

- 右键点击页面并选择检查。然后，打开控制台标签。
- 找到以Submitting failed! Reason ...开头的消息。
- 展开标题为e和body的消息组。最常见的errorName是FormEntries:PhonographEntryParseError，这可能是由于表单与数据集模式/Ontology配置之间的不一致引起的。
- 最常见的errorName是FormEntries:PhonographEntryParseError，这可能是由于表单与数据集模式/Ontology配置之间的不一致引起的。
- 展开标题为parameters的消息组。在FormEntries:PhonographEntryParseError的具体例子中，这将突出显示问题字段（PropertyId）。
- 在FormEntries:PhonographEntryParseError的具体例子中，这将突出显示问题字段（PropertyId）。
例如，如果一个类型为字符串的列/属性与允许多值的字段配对，用户需要将类型更改为Array<String>或更新字段以仅允许单一值。

## 移动设备提交是否支持？

Forms具有响应式网页设计，可以在移动设备上运行；然而，Forms并非专为移动设备设计，因此不提供官方支持。
