来源: https://palantir.com/docs/zh/foundry/slate/widgets-platform/

# 平台

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 平台

平台微件类别包括以下微件：

- Object 卡片
- 资源选择器
- 时间序列
- 操作
## Object 卡片

Object 卡片微件以 ObjectRID 作为输入。它将按照在 Ontology 应用中定义的方式渲染迷你 object 视图（卡片）。这些 object 卡片将链接到它们的 Object Explorer object 视图。

### 表格格式

可以使用此微件与可重复容器结合填充 object 视图的表格。

例如，假设您有一个返回 RID 数组的 Slate 函数。您可以将 object 卡片微件插入重复容器中以创建“表格视图”。您需要使用可重复容器的索引对 Object 微件进行索引，因此在“Object RID”中，您将指定：{{lookup f_function1 w_repeating_container.index}}。

这会根据函数的 RID 和可重复容器的索引使用 lookup 内置函数设置卡片列表。

#### 获取 Object RID

要获得 ObjectRID 输入，您有几种选择：

选项1：Slate 提供了一个点击式 UI，即对象集 面板，在这里您可以进行 object 查询，而无需手动构建查询。

选项2：您可以通过导航到特定 object 的 Object View 并选择操作下拉菜单来获取该 object 的 ObjectRid。在剪贴板中，它将允许您复制 URL 链接。复制 URL 链接的最后一部分，即?objectId={ObjectRID}之后的部分（例如，如果 URL 是...?objectId=ri.phonograph2-objects.main.object.09d2e0e9-dd3c-49b2-8b96-0cb1bf005c1d，您的 ObjectRID =ri.phonograph2-objects.main.object.09d2e0e9-dd3c-49b2-8b96-0cb1bf005c1d）。

选项3：要从 ObjectTypeId 和 ObjectPrimaryKey 获得 ObjectRID，您需要使用Get Object by Locator端点。虽然 ObjectTypeId 和 ObjectPrimaryKey 可以在其他地方用于参数化 Object Explorer URL 链接，但它们需要在 Slate 中解析为 ObjectRIDs。您可以动态组合 ObjectTypeId 和 ObjectPrimaryKey 并将其传递到 Slate 查询中以检索 ObjectRID（前提是端点在您的实例上公开并且您已将其设置为数据源）。

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| cardStyles | 指示 Object 卡片是否应显示卡片样式（例如阴影和悬停样式） | 布尔值 | 是 | 直接编辑 |
| objectRid | 用于查找属性和渲染 object 卡片视图的 object 的 RID（资源 ID）。RID 是存储在 Foundry 平台上的 object 标识符（例如：ri.phonograph2-objects.main.object.f32b778d-b789-49e8-8041-ec14b4c5c5b9）。 | 字符串 | 是 | 直接编辑 |
| fixedHeader | 指示当内容溢出容器大小时，Object 卡片的标题是否应保持冻结。 | 布尔值 | 是 | 直接编辑 |

属性

描述

类型

必填

更改者

cardStyles

指示 Object 卡片是否应显示卡片样式（例如阴影和悬停样式）

布尔值

是

直接编辑

objectRid

用于查找属性和渲染 object 卡片视图的 object 的 RID（资源 ID）。RID 是存储在 Foundry 平台上的 object 标识符（例如：ri.phonograph2-objects.main.object.f32b778d-b789-49e8-8041-ec14b4c5c5b9）。

字符串

是

直接编辑

fixedHeader

指示当内容溢出容器大小时，Object 卡片的标题是否应保持冻结。

布尔值

是

直接编辑

## 资源选择器

此微件允许您选择资源。

## 时间序列

Slate 的时间序列微件提供了一种方便的方法来可视化时间序列图表。您可以使用系列 ID 将多个系列添加到同一图表中，或使用 Codex 查询从 Epoch2 提供的数据。您还可以通过以下方式配置可视化：

- 指定标题、单位和颜色，或禁用十字准线或图例。
- 动态定义时间范围以指定视图窗口。
- 开启数据的“流模式”。
## 操作

Slate 的操作微件允许 Slate 执行预配置的业务逻辑操作。在页面上添加微件后，您可以：

- 选择您有权限访问的 Foundry 操作，
- 直接或通过 Slate 的 handlebars 将默认参数传递到您的操作表单中，并且
- 通过Submit按钮直接提交操作表单，或通过 Slate 事件-操作对w_widget.submit间接提交。
此外，Slate 提供了以下与操作表单相关的 Slate 事件：

- 提交（w_widget.success/w_widget.failure）
- 验证状态（w_widget.ValidationSuccess/w_widget.ValidationFailure），以及
- 渲染更改（w_widget.transitioned和w_widget.cssClassesUpdated）。
最后，如果您需要从用户界面中抽象出 UI 并通过 Slate 事件触发提交，您还可以通过切换控制来防止显示操作表单。有关更多信息，请参阅Slate 事件。

在 Slate 中使用之前，需要先创建 Foundry 操作。有关更多信息，请参阅操作文档。

## 默认参数

可以由用户直接提供或通过使用默认参数以编程方式提供 Foundry 操作的参数，这些参数可以在微件的配置中设置。

### Object 定位器预填

要提供 object 引用，您可以使用以下代码片段。typeId和primaryKey的值可以在 Ontology 管理器中找到：typeID是 object 的 ID，primaryKey是 object 的主键的属性 ID。

```
Copied!1
2
3
4
5
6
{
  "typeId": "<object typeId here>",  // 对象的类型ID
  "primaryKey": {
    "<optional primary keys here>": "<values>"  // 可选的主键及其对应的值
  }
}
```

如果相关操作的Object参数支持多个输入，请提供对象定位器的_列表_作为默认值。

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
[{
  "typeId": "<object typeId here>", // 每个对象的类型标识符
  "primaryKey": {
    "<optional primary keys here>": "<values>" // 可选的主键及其对应的值
  }
},{
  "typeId": "<object typeId here>", // 每个对象的类型标识符
  "primaryKey": {
    "<optional primary keys here>": "<values>" // 可选的主键及其对应的值
  }
}]
```

上述JSON结构表示一个对象数组，其中每个对象包含两个主要属性：

- typeId: 用于标识对象类型的标识符。
- primaryKey: 一个可选的主键集合，用于唯一标识对象。主键是键值对的形式，其中键是主键名称，值是对应的值。
### 日期预填充

日期应为ISO 8601格式；例如，YYYY-MM-DD（例如1990-01-12）是一个有效的日期格式。

### 时间戳预填充

时间戳应遵循ISO 8601格式：YYYY-MM-DD[T]HH:mm:ss.SSS[Z]（例如1990-01-12T23:00:00.000Z）。
