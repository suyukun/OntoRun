来源: https://palantir.com/docs/zh/foundry/slate/best-practices-user-interaction/

# 启用用户交互

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 启用用户交互

几乎每个应用程序都需要用户交互，而Slate提供了三种主要功能来启用交互性：

- 输入微件：简单的微件，提供常见的用户体验元素以捕获输入，例如下拉列表、文本字段、单选按钮等。
- 其他微件内的选择状态：大多数其他微件类型支持某种类型的选择。选择在每个微件中略有不同，因此您需要试验以了解可能的选择类型。
- 事件触发器：所有微件都有一组事件触发器，当微件状态发生变化或用户执行操作时会广播。查看事件文档以获取有关如何将事件合并到应用程序中的更多详细信息。
捕获用户输入的最简单模式是静态表单：添加输入微件并提供静态选项，然后可以在查询和函数中引用用户选择以提供动态视图。然而，通常存在“链式”输入的某种复杂性，其中一个或多个输入中的选择会影响下一组输入中的可用选项集。保持这些链短且易于理解非常重要——设置过多参数可能导致应用程序不直观且性能不佳。请参阅下面的“开放式探索”反模式。

在这种更复杂的依赖输入配置中，最佳实践是分离配置筛选的工作流和分析结果数据的工作流。简单来说，这意味着您应该将任何依赖这些用户输入的查询设置为manual，并为用户提供一个按钮微件来更新数据。这种模式确保您的应用程序不会因为每次筛选更改而重新运行所有查询而浪费资源（和用户时间）。这尤其重要，如果您有任何自由文本输入类型的微件——如文本字段或文本区域类型的微件——否则，像查询这样的下游依赖项会在每个用户击键时重新评估。

任何时候您的应用程序捕获用户输入以写回数据，您必须配置查询以手动运行，并在用户明确操作时触发查询。否则，您的持久化数据查询将在每次输入更改时运行，包括文本输入微件中的每个击键，导致极其意外的行为。

## 在会话之间维护用户选择

如果您的应用程序需要配置多个不同的输入才能获得有用的视图，用户通常希望有一种方式“保存”他们的配置，以便他们可以共享或稍后返回。

可以通过多种方式构建此功能的自定义版本 - 请参阅下面的持久化和恢复状态部分 - 然而，简单地指向内置的获取可共享视图链接更为容易，该链接位于查看应用程序时的操作下拉菜单中。

此内置功能生成一个带有自定义视图ID的应用程序URL，并将所有微件选择的状态存储在Slate数据库中。通过该URL查看应用程序将重新加载应用程序，并将这些选择设置为默认。

## 重置选择和管理默认值

另一种常见模式是为用户提供一个操作，以将所有字段重置为一组默认值。最简单的模式是定义一个v_defaults变量：

```
Copied!1
2
3
4
5
6
{
    "w_multiselectWidget_raw": ["a", "b"],  // 原始多选组件的值
    "w_multiselectWidget_display": ["Alpha", "Beta"],  // 多选组件的显示值
    "w_textInput": "default",  // 文本输入框的默认值
    ...
}
```

然后，在每个微件的配置中，在json定义（在</>图标下）中，您可以为所选值属性的特定版本创建模板。

对于任何具有显示值和原始值的微件，请确保同时模板化selectedValues和selectedDisplayValues：

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
{
    ...
    // selectedValues: 用于存储多选控件的原始选定值
    selectedValues: "{{v_defaults.w_multiselectWidget_raw}}",

    // selectedDisplayValues: 用于存储多选控件的显示选定值
    selectedDisplayValues: "{{v_defaults.w_multiselectWidget_display}}",
    ...
}
```

最后一步是配置一个事件以触发对v_defaults变量的更新，这将导致依赖图更新所有下游节点，其中将包括所有带有模板选择值的输入微件，并且选择将返回到默认。

这似乎足够简单，只需设置一个这样的事件：w_resetWidgetButton.click→v_defaults.set

```
Copied!1
2
// 将 v_defaults 设置为其自身
return {{v_defaults}}
```

如上面Slate中事件发生原因部分所讨论的，这里有一个细微之处，即使节点的解析值未更改，也需要“强制”依赖图重新评估。因此，我们需要添加一些“熵”，以便Slate理解这是一个新值。方法很简单：

```
Copied!1
2
3
4
5
6
7
8
// 获取默认值
const defaults = {{v_defaults}}

// 生成一些随机性
defaults.entropy = Math.random() // 使用Math.random()生成0到1之间的随机数作为熵值

// 设置值
return defaults
```

使用此模式，您可以轻松地为用户提供一个按钮，以便在提交查询后重置默认值或重置它们。

您可以通过URL参数设置变量值，以进一步处理默认值。例如，您可能希望为从一个应用程序中通过链接进入的用户提供不同于直接进入应用程序的用户的默认值，并为在不同工具内的iframe中查看应用程序的用户提供另一组默认值。

要将其集成到上述模式中，而不是使用具有多个属性的单个复杂变量，您可以“展开”该变量，使每个默认值都有一个变量，因此您可以在URL中使用变量名称——请参阅变量以获取有关其工作原理的更多详细信息）。额外的变量将作为“熵”，并且您可以将它们全部组合在一个函数中，该函数返回一个对象，就像我们最初在单个变量中拥有的对象一样：

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
const defaults = {
    // 多选控件的原始值
    "w_multiselectWidget_raw": {{v_multiSelect_raw}},
    // 多选控件的显示值
    "w_multiselectWidget_display": {{v_multiSelect_raw}},
    // 文本输入的值
    "w_textInput": {{v_textInput}},
    // 熵值
    "entropy": {{v_entropy}}
    ...
}
```

每当您想恢复到默认设置时，只需让一个事件将v_entropy重置为一个随机值，默认设置就会重置。

## 验证用户输入

通常，您需要验证用户输入以禁用操作并提供用户反馈。在Slate中有多种方法可以做到这一点，但这里有一个常见的模式，可能在一般情况下会有所帮助。此函数收集所有用户输入，然后执行检查。每个检查都可以禁用表单和/或向用户提供反馈。

在此示例中，我们将验证一个用于收集项目信息的表单，包括标题、URL、联系人姓名、项目描述和项目状态。我们希望既检查用户输入的有效性（例如电子邮件地址格式正确），又确保项目不存在（例如主键尚未使用）。

最后，我们生成一个JSON输出，代表我们的验证结果，并且可以在整个应用程序中引用它来提供用户反馈和禁用某些操作。

f_validateInputs

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
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
// -----------------------------
// 收集验证输入
// -----------------------------

// 用户输入的值
var inputs = {
    Project_Title: {{i_projectTitle.text}},  // 项目标题
    Primary_URL: {{i_primaryUrl.text}},      // 主URL
    Contact: {{i_contact.text}},             // 联系人邮箱
    Project_Quote: {{i_projectQuote.text}},  // 项目描述
    Status: {{i_status.selectedValue}},      // 项目状态
}

// 用于验证的其他值
var uniqueTitle = {{q_searchDuplicateProject.result.[0].hits.length}} ? false : true // 检查标题是否唯一

// --------------------
// 初始化变量
// --------------------

// 用于确定是否应禁用操作的全局标志
var disable = false;

// 向用户显示的消息
var messages = [];

// 'Save' 按钮中显示的文本
var button_text = "Save " + (inputs.Project_Title ? inputs.Project_Title : "") // 如果有项目标题，则在按钮上显示

// --------------------------------
// 实现表单验证检查
// --------------------------------

// 对于所有新项目，检查 `title` 是否已被使用
if ({{i_newProjectToggle.selectedValue}} && !uniqueTitle){
    disable = true;
    messages.push(`Title must be unique. "${{{i_projectTitle.text}}}" already exists.`) // 如果标题不唯一，则禁用保存并显示信息
}

// 对于新项目，检查标题是否已为主键
if ({{i_newProjectToggle.selectedValue}} && {{q_checkUniquePrimaryKey.result.[0].rows.length}}){
    disable = true;
    messages.push(`This title conflicts with an existing project. The project was created as "${{{q_checkUniquePrimaryKey.result.[0].rows.[0].primaryKey.project_id}}}" and is now titled as
"${{{q_checkUniquePrimaryKey.result.[0].rows.[0].columns.title}}}"`) // 如果标题与现有项目冲突，则禁用保存并显示信息
}

// 检查所有必填字段是否都有值
if (!(inputs.Project_Title &&
         inputs.Contact &&
         inputs.Primary_URL &&
         inputs.Project_Quote &&
         inputs.Status
        )){
    disable = true;
    messages.push("Complete all required fields."); // 如果有必填字段为空，则禁用保存并显示信息
}

const email_regex = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
if (inputs.Contact && !email_regex.test(inputs.Contact)){
    messages.push('Enter a valid email for "Contact Email"') // 如果联系人邮箱格式不正确，则禁用保存并显示信息
    disable = true;
}

// 检查项目描述字符数
if (inputs.Project_Quote && inputs.Project_Quote.length > 140){
    messages.push ("'Project Quote' must be less than 140 characters."); // 如果项目描述超过140字符，则禁用保存并显示信息
    disable = true;
}

// 动态调整按钮的保存或更新文本
if (inputs.Project_Title && uniqueTitle) {
    button_text = "Update " + inputs.Project_Title // 如果标题唯一，则按钮显示“更新”
}

return {
    inputs,
    disable,
    messages,
    button_text
}
```

我们可以使用此函数的输出将我们的w_submit按钮的disabled属性模板化为{{f_validate.disable}}。我们还可以有一个简单的文本微件，用于以红色警告显示错误消息：

```
Copied!1
2
3
4
5
{{#each f_validateForm.messages}}
    <!-- 遍历 f_validateForm.messages 中的每条消息 -->
    <div class='pt-tag pt-intent-danger pt-minimal'>{{this}}</div>
    <!-- 每个消息将被包装在一个带有特定样式类的 div 中 -->
{{/each}}
```

这是一个非常简单的例子，可以轻松扩展以包含特定于每个检查的消息，并显示在特定的微件旁边，或者提供类以应用于特定的微件以控制其显示 - 例如，您可以应用一个invalid类，该类具有将输入标题变红的 CSS。

## “动态输入”

有时您需要捕获看似不适合静态输入微件的输入。在许多情况下，您可以从另一个角度解决问题，并找到一个简单的解决方案，但假设您需要允许用户搭建一个更复杂的筛选器，或者您的应用案例似乎无法通过任何创造性使用静态输入来完成。

您可能会倾向于在此工作流中使用重复容器微件，然而这些微件仅限于显示。您可以在重复容器内使用输入微件，但它仅限于该容器，您将无法从容器内的其他微件引用该输入微件的任何实例。

相反，您可以拥有一个输入的单实例，但允许用户多次进行选择，方法是允许他们“保存”他们的选择。您可以在 HTML 微件中显示累积的选择，甚至内置功能以移除先前的选择。

要实现此模式，请使用变量v_userSelections设置为空数组 ([])。然后每次用户点击按钮保存他们的选择时，您可以更新此变量：

w_saveSelection.click→v_userSelections.set

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
// 获取现有的选择
const userSelections = {{v_userSelections}}

// 从当前输入组件的状态中获取新的选择
const newSelection = {
    primaryCategory = {{w_primaryCategory.selectedValue}}, // 主类别选择
    secondaryCategories = {{w_secondaryCategory.selectedValues}} // 次要类别选择
    ...
}

// 将新的选择与之前的选择合并
const userSelections.push(newSelection);

// 更新变量的值
return userSelections;
```

您可以实现更多事件，以允许用户操作其现有选择，最常见的是为每个选择提供一个“删除”操作，以便可以将其移除。

通过这种模式，您可以允许用户搭建任意复杂的输入标准集合。随着复杂性的增加，请谨慎处理，并在上面的事件部分中进一步了解事件密集型模式的注意事项。

通常，这种模式是下面详细讨论的通用有状态应用程序模式的特定案例。

依赖关系图的性质意味着您不能配置微件使其相互之间形成循环关系。输入微件之间的依赖关系需要“逐级传递”，而且您将无法搭建一个筛选集合，其中任何筛选的选择都会影响所有微件。
