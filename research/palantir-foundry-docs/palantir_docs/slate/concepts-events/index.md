来源: https://palantir.com/docs/zh/foundry/slate/concepts-events/

# 配置事件和操作

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 配置事件和操作

Slate中的事件面板允许应用构建者配置在特定事件发生时执行的操作。

操作是对应用行为的更改，包括打开或关闭对话框/通知，运行查询或设置变量值。

事件是触发器，比如用户与应用的互动（用户点击、值的更改或打开和关闭对话框）或数据加载状态（查询运行完成）来执行一个操作。

事件面板显示了在Slate应用中配置的所有事件/操作对。您也可以使用Handlebar引用和JavaScript为事件定义自定义逻辑，以控制发送到触发操作的值。就像使用函数一样，事件JavaScript无法访问DOM或Slate空间，并且不保存任何状态。

事件和操作比单独使用Handlebar引用允许更强大的应用行为控制。

事件编辑器不接受任何类型的助手。

- 示例示例1：在按钮点击时触发手动查询示例2：将变量设置为下拉菜单值的两倍示例3：跟踪一个变量中的对象列表，随着时间累积示例4：有条件地在按钮点击时触发手动查询
- 示例1：在按钮点击时触发手动查询
- 示例2：将变量设置为下拉菜单值的两倍
- 示例3：跟踪一个变量中的对象列表，随着时间累积
- 示例4：有条件地在按钮点击时触发手动查询
## 示例

### 示例1：在按钮点击时触发手动查询

此事件将在按钮被点击时运行查询：

打开事件面板并创建一个新事件：

选择w_button.click作为触发事件，选择q_query.run作为触发的操作，然后选择更新以持久化更改。此配对不需要JavaScript。

现在，每当按钮被点击时，查询将再次运行，为其他Slate函数和微件获取新数据。

### 示例2：将变量设置为下拉菜单值的两倍

此事件会将变量设置为下拉菜单中选择的值的两倍。注意：此示例仅供说明；通常这类事情应该使用Slate函数来完成。

假设有一个名为w_selectionDropdown的下拉微件，其中包含用户可以选择的各种数字，以及一个变量v_doubleSelection，旨在包含所选值的两倍。然后，为了创建这个，打开事件面板并创建一个新事件。选择w_selectionDropdown.selectedValue.changed作为事件，选择v_doubleSelection.set作为操作。然后在事件面板中填写如下代码：

```
Copied!1
2
var dropdownSelectionValue = {{slEventValue}}; // 获取下拉框选择的值
return 2 * dropdownSelectionValue; // 返回下拉框选择值的两倍
```

最终结果应如下所示

{{slEventValue}}是事件面板中的一个特殊 handlebars 值。如果触发的操作具有某个相关值，那么{{slEventValue}}就是该相关值。在.更改了操作的情况下，{{slEventValue}}是相关微件属性更改为的值。

因此，每当下拉菜单更改时，代码将获取下拉菜单更改后的值，将其加倍并返回。返回值由.set操作用于将变量设置为返回值。结果是，每当下拉菜单更改时，代码将获取下拉菜单的新值，将其加倍，并将变量设置为此加倍后的值。

### 示例 3：在变量中跟踪对象列表，随时间累积

此事件将记录用户在下拉菜单中选择的所有值的历史记录，以便该值列表可以在应用程序的其他地方以某种方式使用。

假设有一个名为w_selectionDropdown的下拉微件，用户可以在其中选择选项，还有一个变量v_selectionHistory用于包含选择历史记录。然后，为了创建此功能，打开事件面板并创建一个新事件。选择w_selectionDropdown.selectedValue.更改了作为事件，并选择v_selectionHistory.set作为操作。然后在事件面板中填写如下代码：

```
Copied!1
2
3
4
var history = {{v_selectionHistory}}; // 初始化历史记录变量，值来自模板变量 v_selectionHistory
var newValue = {{slEventValue}}; // 初始化新值变量，值来自模板变量 slEventValue
history.push(newValue); // 将新值添加到历史记录数组中
return history; // 返回更新后的历史记录
```

最终结果应如下所示

现在，每当用户从下拉菜单中选择某项时，事件将被触发。代码将获取v_selectionHistory中的当前值，并将通过{{slEventValue}}传入的新选择值添加到列表末尾，然后返回新的更新后的历史记录。由于操作是v_selectionHistory.set，变量v_selectionHistory将被设置为这个新数组，将新选择的项添加到累积的历史记录中。

### 示例4：条件触发按钮点击时的手动查询

此事件将在按钮被点击时运行查询——但只有当用户在需要的输入微件w_input1和w_input2中输入了数据时。

假设有两个输入微件（用户可输入的文本字段）名为w_input1和w_input2。另外，假设有一个名为w_buttonConditional的按钮和一个手动查询q_queryConditional。

进一步假设查询依赖于用户输入到输入框中的值，也就是说，w_input1.text和w_input2.text，如果这两个没有值，运行查询将毫无意义——因此，即使按钮被点击，我们也不想运行查询。如果这些是空白的，我们可以通过以下方式实现这一点。创建一个新事件，然后选择w_buttonConditional.click作为事件，选择q_queryConditional.run作为操作。然后在事件面板中填写代码如下：

```
Copied!1
2
3
4
5
6
7
var input1Text = {{w_input1.text}}; // 获取输入框1的文本内容
var input2Text = {{w_input2.text}}; // 获取输入框2的文本内容

// 如果输入框1或输入框2的内容为空，则返回禁用动作
if (input1Text === "" || input2Text === "") {
  return {{slDisableAction}};
}
```

最终结果应类似如下

{{slDisableAction}}是事件面板中的一个特殊 handlebars 值。从面板中的代码返回此值将禁用触发的操作。换句话说，如果w_input1或w_input2为空，将返回此特殊值，并且查询q_query不会运行。然而，如果这两个输入都有值，则不会返回任何内容，操作将照常进行。
