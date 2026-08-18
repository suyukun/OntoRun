来源: https://palantir.com/docs/zh/foundry/slate/concepts-variables/

# 在变量中存储值

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 在变量中存储值

在变量编辑器中定义的变量可在整个 Slate 应用中访问。您可以在查询和微件中引用它们，甚至可以通过事件或 URL 设置其值。

变量的有效类型为Number、字符串、Boolean、Array、Object和Null。

## 创建变量

要创建变量，请按照以下说明操作：

- 选择变量以打开变量编辑器。
- 选择添加新变量。
- 选择变量页面范围——共享（在每个页面上可访问）或本地（仅在创建变量时编辑的页面上可访问）。
- 选择名称列中的文本并输入变量的新名称。
Slate 会检测变量名称冲突的情况，并在输入有效名称之前阻止用户保存变量。
共享变量名称必须在所有页面、微件、事件、查询和函数中唯一。
本地变量名称在页面内必须唯一，并且不能与环境变量名称冲突。

- 输入变量的默认值。Slate 将根据输入的值推断变量类型。
变量的值不会在页面加载之间持久化。当 Slate 应用重新加载时，它将使用默认的变量值。
要使变量值在页面加载之间持久化，请使用用户存储变量。

变量编辑器不仅显示每个变量的页面范围、名称和默认值，还提供变量当前值的只读视图，以防它通过事件或直接从 URL 更改。

## 通过事件更新变量

事件可用于设置变量的新值。每个变量自动提供一个.set事件。要更新变量的值，只需在事件内容中返回一个新的合法值。事件逻辑也可以使用变量的当前值作为输入。您还可以在更新变量值时更改其类型（例如，从字符串到数字）；但是，这可能会破坏变量的依赖关系。

在下面的示例中，每当用户点击w_button_next_page按钮时，v_page_number变量都会更新：

## URL 中的变量

您可以在 URL 查询参数中使用变量（附加到 URL 的附加信息，以帮助设置 Slate 页面的状态）。URL 参数始终覆盖默认参数。

通常，使用以下语法将变量添加到 URL：

- 单个变量：?variableName=value
- 多个变量：?variableName=value&otherVariableName=otherValue
请注意，查询参数区分大小写。此外，从 URL 查询参数检索到的变量值将是字符串，即使传递的值是数字、布尔值或对象。这些值可以使用Handlebar helpers或通过函数转换为所需的类型。

## 示例：在微件中使用变量

以下示例在下拉微件中使用变量，并假定一个关于小行星的概念性数据集。

- 创建一个名为Dropdown variables example的新应用。
- 创建一个名为asteroidNames的新查询，将数据源设置为asteroids，并输入以下查询语句：
```
Copied!1
2
SELECT name FROM allnamed;
-- 从表“allnamed”中选择“name”列的数据
```

- 选择更新以保存查询。
选择更新以保存查询。

- 打开变量编辑器并添加一个新变量。将其命名为astro并给予默认变量""（一个空字符串）。
打开变量编辑器并添加一个新变量。将其命名为astro并给予默认变量""（一个空字符串）。

- 向您的应用程序添加一个下拉微件。
向您的应用程序添加一个下拉微件。

- 通过从刚刚编写的查询中提取小行星的名称来填充下拉菜单：
通过从刚刚编写的查询中提取小行星的名称来填充下拉菜单：

- 通过选择按钮</>切换到原始选项卡，并将selectedValue的值从null更新为"{{astro}}"。请注意，由于selectedValue被指派给了astro变量，而该变量目前是一个空字符串，因此下拉菜单最初不显示任何值。
通过选择按钮</>切换到原始选项卡，并将selectedValue的值从null更新为"{{astro}}"。请注意，由于selectedValue被指派给了astro变量，而该变量目前是一个空字符串，因此下拉菜单最初不显示任何值。

- 保存应用程序。
保存应用程序。

- 要为下拉菜单指定一个起始的selectedValue，我们可以在URL中为变量astro设置一个值。在URL后面添加?astro=Flora并使用Enter键。请注意，小行星名称是区分大小写的。现在URL看起来像https://<HOSTNAME>:<PORT>/edit/documents/dropdown-global-variables?astro=Flora，下拉菜单现在初始显示“Flora”。
要为下拉菜单指定一个起始的selectedValue，我们可以在URL中为变量astro设置一个值。在URL后面添加?astro=Flora并使用Enter键。请注意，小行星名称是区分大小写的。现在URL看起来像https://<HOSTNAME>:<PORT>/edit/documents/dropdown-global-variables?astro=Flora，下拉菜单现在初始显示“Flora”。

## Slate系统变量

Slate提供两种类型的系统变量：

- 环境变量。
- 用户存储变量。
系统变量具有特殊行为，无法通过URL设置。

### 环境变量

$global变量提供访问特定环境信息的功能。

| 属性 | 描述 |
| --- | --- |
| locale | 返回用户会话的语言区域。 |
| app.isEditMode | 如果应用程序处于编辑模式则返回true，如果处于查看模式则返回false。 |
| app.rid | 返回Slate文档的RID。 |
| user.domain | 返回用户的认证域。 |
| user.email | 返回用户的电子邮件地址。 |
| user.familyName | 返回用户的姓氏。 |
| user.firstName | 返回用户的名字。 |
| user.groups | 返回用户所属的所有认证组的列表。 |
| user.id | 返回用户的唯一标识符。 |
| user.username | 返回用户的用户名。 |
| window.origin | 返回当前URL的来源。 |

#### 示例：在函数中使用环境变量

以下示例使用$global变量的不同属性以合适的语言向用户问候：

```
// 'de' 表示德语区域设置
// 英语是默认语言
if ({{$global.locale}} == 'de') {
    return "Willkommen " + {{$global.user.firstName}} // 返回德语欢迎信息
} else {
    return "Welcome " + {{$global.user.firstName}} // 返回英语欢迎信息
}
```

### 用户存储变量

Slate 中的sl_user_storage变量在应用加载时为每个用户保持其值，与其他变量在页面加载时重置为默认值不同。

用户存储变量允许应用构建者在应用上下文中为各个用户存储信息，例如特定应用上的用户偏好。

通过事件，可以将值存储在用户存储中，这些值可以在应用中的多个会话中访问。用户存储限制为 10 kB，可以通过slate.setUserStorage操作进行设置。当用户在多个浏览器标签页或窗口中使用应用时，可以调用slate.refreshUserStorage。在一个标签页或窗口中将存储设置为新值时，可以通过调用刷新操作将此值提取到其他窗口中。

#### 示例：更新用户存储变量中的用户偏好

在下面的示例中，用户偏好的目的地被写入一个userPreferencesJSON 对象中。然后在应用加载期间加载用户偏好，以便在应用默认位置向用户展示其个人偏好的目的地。
