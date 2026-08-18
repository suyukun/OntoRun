来源: https://palantir.com/docs/zh/foundry/forms/integrate/

# 与其他 Foundry 应用集成

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 与其他 Foundry 应用集成

Foundry Forms 不再是 Foundry 上数据输入或数据输出工作流的推荐方法。相反，搭建用户输入工作流时应使用 Foundry Ontology，将相关数据结构表示为对象类型，并通过操作配置数据输出交互。请在Forms 概览文档中了解更多信息。

Forms 提供与其他 Foundry 应用的无缝集成。本页面讨论如何将 Foundry Forms 与Fusion、Slate和Object Explorer结合使用。

## Fusion

如果选择 Fusion 作为响应目标，Forms 将立即创建支持的电子表格。每次保存表单时，新需要的列会自动添加到表区域。

用户还可以通过选择插入选项卡并选择表单从 Fusion 中的现有表区域创建表单。

## Slate

两个 Slate 微件可以用于在 Slate 中嵌入表单：

- Foundry 表单
- iIframe
使用 iframe 时，可以使用以下 URL 参数自定义表单的显示：

- embedded=true：在 iframe 中嵌入表单时必须提供。
- noHeader=true：将移除表单中的标题。
- progressOnly=true：只将进度条作为标题渲染；当noHeader=true时被忽略。
- forceDarkMode=true：将在暗模式下渲染表单。
此外，用户可以使用代码编辑器为每个字段添加urlParam来预填值：

```
Copied!1
2
3
4
5
6
fields:
  - uri: display.Text  # URI字段，表示文本显示的路径
    name: Text  # 字段名称为“Text”
    type: Text  # 字段类型为“Text”
    urlParam: text  # URL参数名为“text”
    options: {}  # 选项为空，表示没有额外的配置选项
```

然后 URL 将显示为：workspace/fforms/f/new/<form-id>?embedded=true&progressOnly=true&text=prefilled。

## Object Explorer

三种部分微件可以被用于在Object视图中嵌入一个表单：

- 编辑对象表单
- 创建关联对象表单
- iframe
此外，Forms 支持通过一个对象支持的表单批量编辑多个对象。

### 编辑对象表单

要添加编辑对象表单部分：

- 创建一个与对象类型X关联的表单。
- 导航到X的Object视图，选择操作，然后选择编辑对象视图。
- 添加编辑对象表单部分。
默认表单 ID可以在 Forms URL 中找到：/workspace/fforms/v1/entry/<form-id>/new。

在预填值部分：

- 与字段关联的 URI 或 URL 参数可以使用代码编辑器找到。
- 值可以是静态的（2000-01-01）或取自当前对象的属性（{{start_date}}，其中start_date是对象类型X的属性 ID）。
条件表单部分可以用于根据某些属性的值渲染不同的表单。

### 创建关联对象表单

添加和配置此部分与编辑对象表单非常相似，但有两个显著区别：

- 该部分应添加到与X关联的Y的Object视图中。
- 表单可以基于最后的关联对象进行预填，并可以提供一个排序属性来自定义“最后”的定义。
### iframe

此部分可以按上述描述添加，并按Slate中描述进行配置。

### 批量编辑多个对象

默认情况下，此功能在对象支持的表单上是禁用的。通过在表单右侧的可视化编辑器中的设置标签中切换允许此表单批量编辑（在操作菜单中）来启用它。

启用后，按照以下步骤批量编辑多个对象：

- 导航到Object Explorer并选择要编辑的对象。
- 选择打开按钮并选择编辑 [选择对象数量] 个对象于 [表单名称]。
- 表单将在对话框中打开，允许您覆盖所有选定对象的属性。
批量编辑模式下的表单将覆盖所有选定对象中的所有属性。我们建议在此类表单中仅使用必填字段。使用required验证器确保在提交前填写值。

默认情况下，通过一个表单最多可以编辑 200 个对象。如果您的应用案例需要更大的限制，请联系您的 Palantir 代表。
