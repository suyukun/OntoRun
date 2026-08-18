来源: https://palantir.com/docs/zh/foundry/slate/widgets-advanced/

# 高级

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 高级

高级微件类别包括以下微件：

- 代码沙盒
- 文件导入
- Iframe
## 代码沙盒

代码沙盒微件是一个安全的沙盒，用于实现您自己的自定义微件，以扩展Slate的功能。您可以搭建自己的自定义可视化，利用第三方JavaScript库，或搭建高级工作流交互。您可以定义渲染、微件模型和事件交互，以便您的微件与应用程序的其余部分集成。外部JavaScript库可以加载到您的项目文件夹中，并在您的微件中引用。

代码沙盒微件在您的Slate应用程序中解锁了高级的自定义开发能力。通过代码沙盒微件实现自定义功能时，应清楚理解所涉及的技术复杂性和成功开发所需的长期维护。微件开发完全由您自行决定和承担风险；不提供调试自定义代码的支持。

### 交互摘要

与Slate的交互及可用函数的摘要如下所示：

### JavaScript标签

此标签包含JavaScript字段，以及您可能希望加载的任何JavaScript库。

#### JavaScript

这是一个JavaScript字符串，当微件加载时将被执行。对该JavaScript的任何更改都将导致整个微件重新加载。此字段中的JavaScript将在库字段中的JavaScript之后执行。有关加载第三方库的说明，请参见JavaScript库部分。

不要在此处使用Handlebars。我们建议您通过Javascript标签传递数据以与交互标签中的状态进行交互。

在代码沙盒中不支持JavaScript、JavaScript库或HTML中的网络请求和引用（例如，fetch的使用）。任何网络请求必须通过SlateFunctions代理到配置的查询。

可用函数

可以调用以下本地函数来与Slate特定功能进行交互。这些函数允许您通过使用事件、操作和状态更改与Slate应用程序的其余部分进行交互。函数在微件内运行的JavaScript中暴露。更多信息和示例如下。

- SlateFunctions.onAction
- SlateFunctions.watch
- SlateFunctions.getState
- SlateFunctions.setState
- SlateFunctions.triggerEvent
#### JavaScript库

这是一个项目路径数组，将在微件中按顺序下载并执行，或一个符合CORS和CSP政策允许的URL数组（您可以混合使用）。

下载将使用浏览器，因此URL必须符合CORS和CSP政策。如果您希望在Foundry中托管库，可以将它们托管在Blobster中并使用cookie认证的API，或将脚本放在资产服务器中。对该字段的更改将导致整个微件重新加载和刷新。（库本身可以调用SlateFunctions以允许它们与Slate特定功能进行交互）。

导入的JavaScript库必须将其功能分配到一个全局可用的范围内，以便通过JavaScript标签引用（例如，打包为UMD模块，或将功能显式分配给window）。

##### 示例

要使用d3.min.js库，可以从https://d3js.org/d3.v5.min.js下载并通过拖放文件将其保存到Foundry目录中。文件上传后，复制其项目路径并粘贴到库数组中。

["/Users/admin/d3.min.js"]

您也可以选择使用资源的RID。例如：

["ri.blobster.main.code.7a4a12a8-e9f5-46ef-8008-5c3f4bbd4abc"]

您可以通过查看文件的目录来获取资源的项目路径/RID。或者，您可以在文件夹中右键单击该文件一次并复制位置/RID。

### HTML/CSS标签

#### HTML

这是一个HTML字符串，当微件加载时将被渲染。

不要在此处使用Handlebars。HTML标签<script>将不起作用，您需要将任何JavaScript提取到JavaScript标签中。

#### CSS

这是一个CSS字符串，当微件加载时将被渲染。

不要在此处使用Handlebars。指定的CSS将允许您覆盖在iframe边框中渲染的CSS，而不是在框架中。相同的边框样式也可以通过微件顶层样式标签中的附加CSS类和自定义样式应用。

#### CSS库

CSS库功能允许您加载CSS，以便您可以使用CSS样式（例如Blueprint）来创建自定义微件。您可以在微件的HTML/CSS标签中访问它。

CSS库的工作原理类似于代码沙盒的JavaScript库。CSS库接受一个项目路径数组，该数组将在微件中按顺序下载并渲染，或一个符合CORS和CSP政策允许的URL数组（您可以混合使用）。下载将使用浏览器，因此URL必须符合CORS和CSP政策。如果您希望在Foundry中托管CSS库，可以将它们托管在Blobster中并使用cookie认证的API，或将脚本放在资产服务器中。对该字段的更改将导致整个微件重新加载和刷新。

普通CSS足以用于CSS库文件的内容；请确保您没有在CSS样式周围使用HTML<style>标签。

### 交互标签

这是控制微件与Slate范式交互的工具。代码沙盒微件与Slate其余部分之间的所有交互应通过状态、事件或操作之一传递。

我们建议您仅通过此交互标签传递Handlebars。直接在JavaScript框中使用Handlebars仍然可以工作（例如，在不使用SlateFunctions.watch或SlateFunctions.getState的情况下传递一些状态），但不建议这样做，因为整个微件将在每次重新加载和刷新。

#### 状态

这是一个JSON blob，表示微件的当前配置。这类似于Slate中其他微件使用的状态，只是它被嵌套在此字段下以允许其他元字段。状态可以从微件内部或通过在状态中放置Handlebars的常规实践进行修改。

要从微件中修改状态，请在JavaScript中使用SlateFunctions.setState。传递状态给微件的其他Slate函数是SlateFunctions.watch和SlateFunctions.getState（见下面的示例）。

有某些方法可以使用此字段将额外的运行时代码加载到代码沙盒微件中（例如，将JavaScript传递到状态中并稍后加载）。但是，这些方法不推荐使用，因为该字段的目的是表示微件的状态。

#### 事件

这是一个字符串数组，表示此微件将能够触发的事件的名称。必须从微件内的JavaScript中显式调用这些触发器，使用下面提供的函数。事件将在事件标签中显示为custom.{event_name}。事件名称不需要单独键入在triggerEvent参数中。

要触发事件，请在JavaScript中使用SlateFunctions.triggerEvent(“event”)，如下例所示。

#### 操作

这是一个字符串数组，表示此微件将允许其他微件触发的操作名称。微件内的JavaScript应使用下面提供的函数监听操作。当操作在事件标签中显示时，将命名为custom.{action_name}。操作名称不需要单独键入在onAction参数中。

要让微件响应在Slate上下文中创建的操作，请在JavaScript中使用SlateFunctions.onAction(“action_name”,(value)=>{put JavaScript here})，如下例所示。

### Slate函数

这些本地函数允许您与Slate特定功能进行交互，并暴露给微件内运行的JavaScript。这些函数将允许您通过事件、操作和状态更改与Slate应用程序的其余部分进行交互。

#### onAction

数据方向：Slate上下文 → 微件

SlateFunctions.onAction允许您注册一个回调，当操作在您的微件上被调用时。它的参数是操作的名称和操作接收时要调用的函数。该函数将使用作为操作传递的“body”作为唯一参数进行调用。

然后，您需要在下面的交互标签中列出您的操作。

示例

此示例使用Slate复选框微件，当单击复选框微件时，会导致代码沙盒微件更新：

- 当单击复选框微件时，事件从复选框微件发出。
- 在Slate的事件面板中，此Slate事件已注册为在代码沙盒微件中触发操作（custom.checkbox）。
- 事件面板能够检测到此操作，因为该操作已在代码沙盒微件的交互操作框中注册。
JavaScript：

```
Copied!1
2
3
4
5
6
7
SlateFunctions.onAction("checkbox", (value) => {
    var checkbox = document.createElement("div")
    // 将传入的值设置为新创建的div元素的HTML内容
    checkbox.innerHTML = value;
    // 将创建的div元素添加到文档的body中
    document.body.appendChild(checkbox);
});
```

```
Copied!1
2
3
[
    "checkbox" // 复选框
]
```

新事件-操作对已注册：

> 事件: Slate_微件.selectedValues.更改了操作: Code_Sandbox_微件.custom.checkbox

事件: Slate_微件.selectedValues.更改了

操作: Code_Sandbox_微件.custom.checkbox

#### 监测

数据方向: Slate 上下文 → 微件 (持续监测)

SlateFunctions.watch旨在帮助您检测状态字段的更改，类似于在 AngularJS 中的监测。SlateFunctions.watch接受一个字符串和一个函数作为参数。当由字符串表示的状态部分更改时，所提供的函数将与新状态和旧状态一起被调用。这可能是最有用的函数，也是您可以通过在交互选项卡中使用 Handlebars 传递数据到微件的方法（例如，"First Argument": "{{handlebars}}"）。

例如，如果您的状态有两个字段 - 高度和宽度 - 并且您想在高度变化时调用一个函数，您可以调用SlateFunctions.watch("height", <insert function here>)。如果初始字符串为空，那么函数将在任何状态变化时被调用。

示例

此示例使用了 Slate 的输入微件，该微件将状态传递到代码沙盒微件并显示：

- Slate 输入微件生成文本状态作为数据输出{{w_widget2.text}}
- 此状态已被输入到代码沙盒微件的交互状态框中，因此现在您可以在代码沙盒微件中使用该状态。您可以使用SlateFunctions.watch("State Name", (data) =>...在微件中使用该状态/数据。
JavaScript:

```
Copied!1
2
3
4
5
6
7
8
var el = document.createElement("div") // 创建一个新的 <div> 元素
el.id = "display" // 设置新元素的 id 为 "display"
document.body.appendChild(el); // 将新元素添加到文档的 <body> 中

// 监听 "Input State" 的变化，并在元素中显示相应的数据
SlateFunctions.watch("Input State", (data) => {
    el.innerHTML = "Code Sandbox widget: " + data; // 将数据更新到 div 元素的 HTML 内容中
});
```

```
Copied!1
2
3
{
  "Input State": "{{w_widget2.text}}" // 这里的 "Input State" 是一个键，其值为一个占位符 "{{w_widget2.text}}"，通常用于模板引擎中，表示将 w_widget2 的文本内容动态填充到此处。
}
```

#### getState

数据方向：Slate 上下文 → 微件（非连续，一次性'获取')

此函数返回微件的当前状态，该状态最初由状态字段填充。

SlateFunctions.getState返回微件当前状态的 JSON 对象，该状态最初由状态字段填充。您可以访问对象的不同属性（即不同的'状态'）。

SlateFunctions.getState将返回状态字段的 JSON 对象，您可以访问对象的不同属性（即不同的'状态'）。

SlateFunctions.getState仅在调用时获取状态。相比之下，SlateFunctions.watch将不断监测状态字段的更新。您可以在SlateFunctions.watch中使用此SlateFunctions.getState函数来获取完整状态对象的特定属性。

例如，如果您的状态是：

```
Copied!1
2
3
4
{
  "a": "cat",  // 字符串 "cat" 分配给键 "a"
  "b": "hat"   // 字符串 "hat" 分配给键 "b"
}
```

SlateFunctions.getState().a将返回cat。

示例

此示例使用了 Slate 的输入微件，该微件将状态传递给代码沙箱微件。通过使用getState函数（指派给 x），调用整个状态对象，然后显示该“整个状态”对象中的特定属性：在此示例中为 "a"。

JavaScript：

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
// 创建一个新的<div>元素
var el = document.createElement("div");
// 设置元素的id为"display"
el.id = "display";
// 将新创建的元素添加到文档的body中
document.body.appendChild(el);

// 获取SlateFunctions的状态
var x = SlateFunctions.getState();
// 将获取的状态中的属性a的值显示在<div>元素中
el.innerHTML = "Code Sandbox widget: " + x.a;
```

交互操作：

```
Copied!1
2
3
  "a": "{{w_widget2.text}}",  // 将w_widget2的文本值插入到键"a"中
  "b": "random_state"         // 键"b"的值是字符串"random_state"
}
```

#### setState

数据方向：微件 → Slate 上下文。

SlateFunctions.setState更改微件的状态，既适用于使用 Handlebars 引用该微件状态的外部微件，也适用于未来的getState调用。它需要两个参数：表示要更改的状态部分的字符串和表示该部分新值的 JSON blob。

例如，如果您希望将微件的视图高度设置为 4，但保留所有其他属性，您可以调用SlateFunctions.setState("view.height", 4)。如果您想覆盖整个状态（而不仅仅是高度），可以将第一个参数传递为空字符串""，而不是"view.height"。

示例

此示例使用代码沙盒微件中生成的按钮，将 Slate "HTML 微件" 的状态从 "初始微件状态" 更新为 "更新后的微件状态"。

- 当单击按钮时，与代码沙盒微件的交互触发SlateFunctions.setState。这将 "outval" 的状态从 "初始微件状态" 更新为 "更改后的微件状态"。
- 由于状态已在代码沙盒微件的交互 "state" 中注册，因此此更新后的状态可以在 Slate 中被检测到。
JavaScript:

```
Copied!1
2
3
4
5
6
7
8
var button1 =  document.createElement("button"); // 创建一个按钮元素
button1.innerHTML = "button1"; // 设置按钮的文本内容

button1.onclick = () => {
    SlateFunctions.setState("outval", "Updated widget state"); // 当按钮被点击时，更新小部件的状态
};

document.body.appendChild(button1); // 将按钮添加到页面的主体中
```

交互状态：

```
Copied!1
2
3
{
  "outval": "Initial Widget State" // 初始组件状态
}
```

#### triggerEvent

数据方向: 微件 → Slate 上下文。

SlateFunctions.triggerEvent触发一个事件。两个参数是要触发的事件名称和作为事件主体传递的消息。

示例

在此示例中，当通过单击按钮与代码沙箱微件进行交互时，会在Slate上下文中启动一个Slate Toast微件。

- 当按钮被点击时，函数launchToast.onclick运行，并触发SlateFunctions.triggerEvent。
- 事件从代码沙箱微件发出，因为此事件已在代码沙箱微件的交互“事件”中进一步注册。
- 在Slate的事件面板中，此代码沙箱微件事件已注册为触发Slate微件中的操作 (Slate_widget.open)。
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
// 创建一个按钮元素
var launchToast =  document.createElement("button");
// 设置按钮文本为“launch toast”
launchToast.innerHTML = "launch toast";

// 为按钮添加点击事件
launchToast.onclick = () => {
    // 触发名为“toast”的事件
    SlateFunctions.triggerEvent("toast");
};

// 将按钮添加到文档主体中
document.body.appendChild(launchToast);
```

交互事件：

```
Copied!1
2
3
[
  "toast" // 这是一个简单的JSON数组，包含一个字符串元素"toast"
]
```

新事件已注册：

> 事件：Code_Sandbox_widget.custom.toast操作：Slate_widget.open

事件：Code_Sandbox_widget.custom.toast

操作：Slate_widget.open

### 加载顺序

Code Sandbox 微件按以下顺序加载：

- Slate（包含微件的父框架上下文）加载，然后微件 iframe 加载。
- Slate 将微件“状态”发送到微件（有关更多详细信息，请参见下面的交互），接着加载 CSS、HTML、库和 JavaScript。
- iframe 接收并设置以下内容：CSS 和 HTML 被附加。库被执行。JavaScript 被执行。适当的“SlateFunctions”被触发（输入）。
- CSS 和 HTML 被附加。
- 库被执行。
- JavaScript 被执行。
- 适当的“SlateFunctions”被触发（输入）。
- 用户与微件框架交互（更新状态、触发事件、创建操作等）。这些交互可以修改或生成从微件发送到父 Slate 框架的“SlateFunctions”。如果指定为交互（输出），这些微件输出可以在 Slate 的其他部分使用。
### 安全性

此微件的安全模型与 Slate 函数的安全模型非常相似。代码将在沙盒化的 iframe 中执行，输入和输出通过 postMessage 传输。这使我们能够安全地执行不受信任的 JavaScript 代码。唯一的修改是 iframe 在页面上可见，但这并不改变安全模型。

### 调试技巧

在 Chrome 控制台中，您可以选择默认位于顶部的下拉菜单，然后选择 codeSandboxIframe.html。这将导致您在控制台中键入的任何 JavaScript 在微件的环境中执行。当您试图弄清楚如何让微件工作时，这可能很有用，因为对 JavaScript 字段的更改将强制重新加载微件。

### 第三方代码

使用第三方代码时，我们建议遵循以下通用方法：

- 检查许可证以确保您可以使用它。
- 通过找到具有尽可能少的独立 JavaScript 块的示例来最小化代码复杂性。
- 如果 JavaScript 使用任何库，请从源下载 .js 文件，并将上传文件的 Foundry 项目路径放入库部分。您也可以直接链接 URL，并在之后测试以确保它不会与 CSP 或 CORS 策略冲突。
- 确保所有 HTML <script> </script> 标签中的 JavaScript 都被重构并放入 JavaScript 部分。
- 使用 Slate 函数进行交互：使用SlateFunctions.getState将所需数据传递到自定义 Code Sandbox。要在微件中传达一个交互给 Slate 的其余部分，可以将SlateFunctions.triggerEvent标记到该函数。要使微件响应来自 Slate 其他部分的操作，可以将SlateFunctions.onAction标记到该函数。
- 使用SlateFunctions.getState将所需数据传递到自定义 Code Sandbox。
- 要在微件中传达一个交互给 Slate 的其余部分，可以将SlateFunctions.triggerEvent标记到该函数。
- 要使微件响应来自 Slate 其他部分的操作，可以将SlateFunctions.onAction标记到该函数。
## 文件导入

下表提供了有关文件导入微件的属性的使用详情。

### 属性

| 属性 | 描述 | 类型 | 必需 | 更改者 |
| --- | --- | --- | --- | --- |
| buttonCssClasses | 应用于浏览按钮的 CSS 类 | string[] | 是 | 直接编辑 |
| buttonText | 浏览按钮的文本 | string | 是 | 直接编辑 |
| message | 在上传面板中显示的消息 | string | 是 | 直接编辑 |
| fileContent | 用户导入的文件内容 | string | 是 | 用户交互 |
| fileName | 用户导入的文件名称 | string | 是 | 用户交互 |
| fileType | 用户导入的文件的 MIME 类型 | string | 是 | 用户交互 |

## Iframe

下表提供了有关 iframe 微件的属性的使用详情。表格后面有几个示例。

如果您正在嵌入通过工作区加载的内容，需要在 URL 末尾添加?embedded=true

### 属性

| 属性 | 描述 | 类型 | 必需 | 更改者 |
| --- | --- | --- | --- | --- |
| uri | iframe 的 src URI | string | 否 | 直接编辑 |

操作

| 操作名称 | 描述 |
| --- | --- |
| sendMessage | 触发此操作会导致微件以格式{ source: ‘slate-iframe-action’, message: {…}向内部 iframe 发送消息。 |

事件

| 事件名称 | 描述 |
| --- | --- |
| getMessage | 当微件的内部 iframe 以格式{ target: ‘slate-iframe-event’, message: {…}向 Slate 发送消息时，触发此事件。 |
