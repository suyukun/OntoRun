来源: https://palantir.com/docs/zh/foundry/slate/concepts-events-and-actions-index/

# 可用事件和操作

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 可用事件和操作

此页面列出了Slate中在查询、函数、变量、微件和应用程序级别的所有可用事件和操作。请参阅我们的附加文档了解如何配置和使用这些事件和操作。

## 全局事件

全局事件是指在应用程序级别发生的事件，不特定于单个组件或查询。

### slate.ready

slate.ready事件在页面框架加载完成且查询开始运行时触发。您希望在页面加载时立即触发的任何操作（例如，执行一些手动查询）应在此处发生。

### slate.resize

每当浏览器窗口调整大小时，slate.resize事件会触发。如果任何微件是基于浏览器窗口的大小进行调整的，它们也会被重新调整。然而，一些微件（如图表）有一个redraw操作，您可以触发它以确保即使在浏览器窗口大小更改时，微件也能重新绘制到正确的大小。

### slate.onNavigate[page_name]

每当用户导航到添加了此事件的页面时，slate.onNavigate[page_name]会被触发。

### slate.onPrint

每当用户关闭先前通过slate.print操作打开的打印模式时，slate.onPrint会被触发。

### slate.userStorageChanged

slate.userStorageChanged检测到用户存储通过slate.setUserStorage操作被更新时会触发。如果用户存储通过另一个浏览器标签页或窗口被更新，该事件也支持。

### slate.getMessage

slate.getMessage用于在其他应用程序（如Workshop）中的iframe内运行的Slate应用程序。每当Slate接收到来自父iframe的postMessage形式的消息时，slate.getMessage事件会触发。

```
Copied!1
2
3
4
{
  "target": "slate-parent-iframe-event",
  "message": <payload>
}
```

```
Copied!1
2
3
// 这是一个JSON对象，通常用于在iframe与其父页面之间通信。
// "target" 指定了事件的目标，这里是 "slate-parent-iframe-event"。
// "message" 是要传递的有效载荷 <payload>，可能是任何数据结构。
```

如果子窗口或父窗口发送一个包含以下目标属性设置的Object的postMessage，slate.getMessage事件也会被触发：

```
{"target": "SLATE_MESSAGING_SERVICE", ...<payload>}
```

在这段代码中，target是一个键，其值为SLATE_MESSAGING_SERVICE。这可能是一个消息服务的目标标识符。<payload>表示实际传递的数据内容，需要根据具体应用进行填充。
事件将被触发。然后，在此事件的JavaScript窗格内，<payload>将作为{{slEventValue}}可用，因此消息中的数据可以被适当使用。

发送到Slate的消息也可以执行操作，例如设置变量：

```
Copied!1
2
3
4
5
6
7
8
{
  "slateActionOption": {
    "type": "SET_VARIABLES", // 设置变量的操作类型
    "payload": {
      "v_variable": 123 // 变量 v_variable 的值被设置为 123
      }
    }
}
```

您也可以运行操作：

```
Copied!1
2
3
4
5
6
{
  "slateActionOption": {
    "type": "TRIGGER_ACTION",  // 动作类型为触发动作
    "payload": <payload for action>  // 动作的有效载荷
    }
}
```

### slate.getBroadcast

BroadcastChannel支持处于测试阶段。用于与事件和操作交互的API可能会更改。

slate.getBroadcast在 Slate 从已打开的BroadcastChannel接收到消息时触发。要打开一个BroadcastChannel，请使用slate.createBroadcastChannel操作。

消息负载将以{{slEventValue}}的形式提供，其结构如下：

```
Copied!1
2
3
4
{
  "channel": "channel_name", // 通道名称
  "data": <payload> // 负载数据
}
```

### slate.onCloseCheckpoint

slate.onCloseCheckpoint在用户关闭检查点时触发。它提供关于已关闭检查点的信息，该信息可通过{{slEventValue}}获取，结构如下：

```
Copied!1
2
3
4
5
{
    "slateCheckpointId": string,  // 检查点的唯一标识符
    "status": "cancelled" | "no-checkpoint" | "success",  // 检查点的状态：取消、无检查点或成功
    "interactionRid": string (optional - if Checkpoint was successful);  // 交互的唯一标识符，仅在检查点成功时存在
}
```

slateCheckpointId是一个用户定义的字符串，用于标识检查点。它在使用slate.showCheckpoint操作时定义。

您可以在检查点文档中阅读更多关于检查点的信息。

## 查询事件

查询事件是与 Slate 应用程序中的查询相关的事件，当查询完成或由于超时、格式错误的查询或其他服务器问题等原因导致查询未能成功完成时触发。每个查询都有其自己的事件实例。

### QUERY_NAME.success

每当QUERY_NAME指定的查询成功完成时，此事件触发。每个查询都有其自己的事件实例。

### QUERY_NAME.failure

每当QUERY_NAME指定的查询由于超时、格式错误的查询或其他服务器问题等原因未能成功完成时，此事件触发。每个查询都有其自己的事件实例。

## 函数事件

函数事件是与 Slate 函数执行相关的事件。每个函数都有其自己的事件实例。

### FUNCTION_NAME.ran

每当FUNCTION_NAME指定的函数完成运行时，此事件触发。每个函数都有其自己的事件实例。

## 变量事件

变量事件是与 Slate 变量交互相关的事件。每个变量都有其自己的事件实例。

### VARIABLE_NAME.changed

每当VARIABLE_NAME指定的变量更改时，此事件触发。更改后的值将作为{{slEventValue}}提供。每个变量都有其自己的事件实例。

## 微件事件

微件事件是用于在您的 Slate 应用程序中引发操作或活动的触发器。它们可以用于创建交互性并在您的应用程序中自动化流程。每个微件都有其自己的事件实例。

### WIDGET_ID.cssClassesUpdated

每当指定微件的WIDGET_ID所属的“附加 CSS 类”属性更改时，此事件触发。此事件在 DOM 更新后但在其被绘制之前触发；这意味着如果您使用 CSS 类更改不同微件的大小，使用此事件触发这些微件的redraw操作将按预期工作。每个微件都有其自己的事件实例。

### WIDGET_ID.transitionend

每当 JavaScripttransitioned事件直接发生在由WIDGET_ID指定的微件内时，此事件触发。在这种情况下，“直接”意味着不是来自子微件；每个transitioned只触发一个事件。更具体地说，您可以使用 CSS 过渡来为页面上的元素制作动画，例如使侧边栏滑入和滑出而不是弹出和弹出。每当这些过渡之一完成时，JavaScript 将触发一个transitioned事件，Slate 捕获并传递。这样，您可以在过渡完成时触发页面上发生其他更改，或提示对可能更改大小的微件进行resize操作。

每当此事件触发时，{{slEventValue}}是一个 JavaScript 对象，具有以下属性：

- elapsedTime: 过渡所花费的时间
- propertyName: 正在动画化的属性的名称
- targetId: 如果正在动画化的 DOM 元素具有 ID 属性，它将在此处可用
这些属性可能有助于区分具体的过渡；确保您的代码对正确的过渡作出响应。每个微件都有其自己的事件实例。

### WIDGET_ID.INTERACTION_PROPERTY.changed

每当属于指定微件WIDGET_ID的INTERACTION_PROPERTY属性更改时，此事件触发。更改后的值将作为{{slEventValue}}提供。请注意，此事件并非适用于每个微件的每一个属性，而仅适用于“交互属性”（即用户交互可更改的微件属性，例如selectedValue）。每个微件交互属性都有其自己的事件实例。

## 全局操作

全局操作控制应用程序级别的行为更改，例如页面或窗口修改、数据导出和跨应用程序消息。

### slate.navigateTo[page_name]

slate.navigateTo[page_name]操作将范围内的页面更改为page_name，并更新 URL 路由以指向目标页面。共享变量将在页面更改中保持其状态。

### slate.scrollToId

slate.scrollToId操作将页面（以及页面中任何其他可滚动的容器）滚动到具有给定 ID 的 DOM 元素（在事件面板的 JavaScript 代码中返回的 ID）。此操作可用于程序化地将页面滚动到特定元素或返回到可滚动表或列表中的记忆位置。

### slate.setWindowTitle

slate.setWindowTitle操作允许您重命名当前浏览器窗口的标题并更新选项卡名称。调用该操作并返回一个字符串以设置选项卡名称。如果在页面加载时未调用此操作，Slate 将默认将选项卡标题设置为文档名称。

### slate.print

slate.print操作将打开浏览器的打印对话框，以允许用户选择打印机选项然后进行打印。

### slate.downloadBlob

slate.downloadBlob操作允许您在遵循 Slate 的导出限制的同时下载任意数据 blob。要使用此操作，请添加如下的 return 语句：

```
Copied!1
2
3
4
return {
    fileName: "my_file.txt", // 文件名为"my_file.txt"
    blob: new Blob(["Hello, world!"], {type: "text/plain;charset=utf-8"}) // 创建一个包含"Hello, world!"文本的Blob对象，类型为"text/plain"，字符编码为"utf-8"
}
```

一个应用案例是通过在函数选项卡中使用像 ExcelJS 这样的库下载带有条件格式的 Excel 文件，然后发送到slate.downloadBlob以供用户下载。有关 Blobs 的更多信息，请参见MDN web docs ↗。

### slate.exportWidget

slate.exportWidget操作允许您将微件以PNG或PDF文件格式导出。要使用此操作，请添加如下所示的返回语句：

```
Copied!1
2
3
4
5
6
return {
    widgetId: "my_chart", // 小部件ID
    exportType: "download", // 导出类型
    outputType: "png", // 输出类型
    fileName: "exported_chart", // 文件名
}
```

### slate.sendMessage

slate.sendMessage操作被用于在嵌入在其他应用程序中的Slate应用程序中。具体来说，此操作将获取传递给它的值（从面板中的JavaScript代码返回）并向父iframe发送如下形式的postMessage：

```
Copied!1
{"source": "slate-parent-iframe-action", "message": <payload>}
```

<payload>是面板中JavaScript代码返回的值。

slate.sendMessage操作也可以被用于在不在iframe内的情况下向其他窗口发送消息。

例如，您可以使用slate.redirectToUrl在新标签页或浏览器窗口中打开子窗口，并为该窗口设置ID。

然后，您可以使用slate.sendMessage操作向特定窗口发送消息：

```
Copied!1
2
3
4
5
6
7
return {
        "targetOptions": {
          "targetWindow": "child" | "opener" | "parent", // 指定消息目标窗口，可以是子窗口（child），打开窗口（opener），或父窗口（parent）
          "children": ["child-id1", "child-id2"] // （可选）指定子窗口的ID
        },
        "message": <payload> // 消息内容
        }
```

如果目标窗口设置为child，您可以提供一个数组，其中包含使用slate.redirectToUrl时设置的子窗口ID。如果未提供，将向所有子窗口发送消息。

opener和parent的targetWindow将分别对window.opener和window.parent执行 postMessage。

### slate.createBroadcastChannel

BroadcastChannel支持处于beta阶段。用于与事件和操作交互的API可能会更改。

slate.createBroadcastChannel操作将创建一个具有指定名称的BroadcastChannel。此频道可以用于向/从所有具有相同频道名称的广播频道发送/接收消息。

要使用此操作，请添加如下所示的返回语句：

```
Copied!1
2
3
4
return {
    channel: "my_new_channel"
    // 返回一个对象，其中包含一个键 "channel"，其值为 "my_new_channel"
};
```

有关BroadcastChannel的更多信息，请参见MDN web docs ↗。

### slate.closeBroadcastChannel

BroadcastChannel支持处于测试阶段。用于与事件和操作交互的API可能会更改。

slate.closeBroadcastChannel操作将关闭并删除具有指定名称的BroadcastChannel。

要使用此操作，请添加如下所示的return语句：

```
Copied!1
2
3
return {
    channel: "channel_to_close" // 指定要关闭的通道名称
};
```

### slate.broadcastMessage

BroadcastChannel 支持处于测试阶段。用于与事件和操作交互的API可能会更改。

slate.broadcastMessage操作将向具有指定名称的广播频道发布一条消息。

要使用此操作，请添加如下的返回语句：

```
Copied!1
2
3
4
return {
    channel: "my_channel", // 指定要发送消息的通道名称
    message: <payload> // 消息的内容，<payload> 是一个占位符，代表实际的消息数据
};
```

### slate.showCheckpoint

slate.showCheckpoint操作将打开指定的Checkpoint模态窗口。您可以在Checkpoints文档中阅读更多关于Checkpoints的信息。

要使用此操作，请添加如下的return语句：

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
return {
    slateCheckpointId: string; // 定义石板检查点的ID，类型为字符串
    checkpointType: CheckpointTypeV1; // 检查点类型，使用CheckpointTypeV1枚举
    primaryCheckpointedItemId?: { // 可选的主要检查点项ID
        id: string; // 项目ID，类型为字符串
        type: CheckpointedItemIdType; // 项目ID类型，使用CheckpointedItemIdType枚举
    };
    additionalCheckpointedItemIds?: { // 可选的附加检查点项ID列表
        id: string; // 项目ID，类型为字符串
        type: CheckpointedItemIdType; // 项目ID类型，使用CheckpointedItemIdType枚举
    }[];
};
```

slateCheckpointId是用户定义的字符串，用于标识 Checkpoint，并在onCloseCheckpoint事件的响应中返回。

checkpointType应为配置的 Checkpoint 类型。查看 Checkpoint 类型。

#### 导出配置

| 名称 | 类型 | 描述 |
| --- | --- | --- |
| widgetId | 字符串 | 要导出的微件的 ID（如微件列表中所示）。 |
| exportType | "copy" | "download" | 将微件下载为文件或保存到剪贴板。 |
| outputType | "png" | "pdf" | 将微件导出为 PNG 或 PDF 文件。 |
| fileName | 字符串 (非必填) | 如果exportType为"download"，则为下载文件的名称。 |

#### 不支持的微件

iframe、代码沙盒和多选框微件，以及包含任何前述微件的容器，无法导出。

### slate.openAppsPortal

slate.openAppsPortal操作将打开应用程序门户。您可以通过非必填参数来指定要导航到的应用程序门户部分。参数必须符合以下形式：

| 应用程序门户部分 | 参数 |
| --- | --- |
| 无指定 | 无参数 |
| 所有应用程序 | { type: "allResultsNavItem" } |
| 平台应用程序 | { type: "platformAppsNavItem" } |
| 推广应用程序 | { type: "promotedAppsNavItem" } |
| 指定类别的平台应用程序 | { type: "platformAppsCategoryNavItem", title: 字符串 } |
| 指定集合的推广应用程序 | { type: "promotedAppsCollectionNavItem", title: 字符串, rid: 字符串 } |

### slate.askAIPAssist

slate.askAIPAssist操作将打开AIP Assist支持工具。您可以指定一个非必填的prompt字符串参数，该参数将作为用户在 AIP Assist 聊天中的消息发送。prompt可以从当前用户在应用程序中的状态派生，以便向 AIP Assist 提出针对性的问题。

```
Copied!1
2
3
4
return {
  // 提示用户如何在 Slate 中与小部件交互
  "prompt": "How do I interact with widgets in Slate?"
};
```

### slate.logout

slate.logout操作将打开一个浏览器对话框以确认用户是否想要退出登录。如果用户确认，他们将会退出Foundry。

### slate.copyToClipboard

slate.copyToClipboard操作会将面板中JavaScript代码返回的值复制到用户的剪贴板。

### slate.redirectToUrl

slate.redirectToUrl操作会将用户重定向到传递给操作的URL。我们不建议将此操作与slate.ready事件一起使用，因为这样做会在页面加载时立即重定向用户，从而使编辑变得困难。如果您的应用案例确实需要将slate.redirectToUrl操作与slate.ready事件一起使用，我们建议添加一个查询参数以禁用该操作。

您还可以控制重定向的目标。要使用此功能，创建操作并返回具有以下属性的Object：

```
Copied!1
2
3
4
return {
  "url": "https://www.palantir.com/",
  "target": "_blank" // (可选) 指定链接在新窗口或标签页中打开
};
```

如果您希望发送或接收来自您打开的子窗口的postMessages，您可以添加windowSharingOptions字段，并为子窗口提供一个唯一ID：

```
Copied!1
2
3
4
5
6
7
return {
  "url": "https://www.palantir.com/", // 指定要打开的网址
  "target": "_blank" (optional), // (可选) 指定在新窗口或标签页中打开链接
  "windowSharingOptions": {
    "id": "child-window-id1" // 子窗口的唯一标识符
  }
};
```

您可以使用slate.sendMessage操作与此窗口进行通信。

## 查询操作

查询操作作用于特定查询或其结果集。它们使应用程序构建者能够在特定事件触发时运行查询或以文件格式导出查询结果集。

### QUERY_NAME.run

此操作将立即运行由QUERY_NAME指定的查询。无论查询是手动还是自动，此操作均可工作。每个查询都有此操作的独立实例。

### QUERY_NAME.export, QUERY_NAME.exportXlsx, QUERY_NAME.exportCsv

QUERY_NAME.export将以 .xlsx 格式导出由QUERY_NAME指定的查询结果。它将在服务器上运行查询，生成文件，并将其下载到用户的计算机上。每个查询都有此操作的独立实例。

可以从Queries选项卡中的Export on下拉菜单中添加QUERY_NAME.export操作为事件的触发器。

默认情况下，文件将命名为QUERY_NAME.xlsx。要更改此名称，请导航到Events选项卡并选择QUERY_NAME.export。然后可以添加返回语句以配置文件名。例如，return "january_data"或return {fileName: "january_data"}将下载一个名为january_data.xlsx的 .xlsx 文件。有效的文件名不应为空且只能包含字母、数字、下划线或空格。如果返回语句中的文件名无效，将使用查询的名称作为文件名。

您可以从Events选项卡中的Actions下拉菜单中选择QUERY_NAME.exportXlsx或QUERY_NAME.exportCsv操作。然后，您可以添加返回语句以将文件名更改为有效的文件名。

### QUERY_NAME.exportCsv, QUERY_NAME.exportXlsx

这些操作将由QUERY_NAME指定的查询输出下载到用户的本地机器。结果可以下载为 CSV 或 Excel 文件。默认情况下，文件将采用查询的名称，尽管您可以通过在事件中返回{ fileName: <<custom_string>> }对象来自定义名称。

## 函数操作

函数操作作用于特定函数或其结果集。它们使应用程序构建者能够在特定事件触发时运行函数或以文件格式导出函数结果集。

### FUNCTION_NAME.run

此操作将立即运行由FUNCTION_NAME指定的函数。每个函数都有此操作的独立实例。

#### FUNCTION_NAME.export, FUNCTION_NAME.exportXlsx, FUNCTION_NAME.exportCsv

FUNCTION_NAME.export将以 .xlsx 格式导出由FUNCTION_NAME指定的函数结果。它将运行函数，将结果发送到服务器，生成文件，并将其下载到用户的计算机上。每个函数都有此操作的独立实例。

可以从Functions选项卡中的Export on下拉菜单中添加FUNCTION_NAME.export操作为事件的触发器。

默认情况下，文件将命名为FUNCTION_NAME.xlsx。要更改此名称，请导航到Events选项卡并选择FUNCTION_NAME.export。然后可以添加返回语句以配置文件名。例如，return "january_data"或return {fileName: "january_data"}将下载一个名为january_data.xlsx的 .xlsx 文件。有效的文件名不应为空且只能包含字母、数字、下划线或空格。如果返回语句中的文件名无效，将使用函数的名称作为文件名。

您可以从Events选项卡中的Actions下拉菜单中选择FUNCTION_NAME.exportXlsx或FUNCTION_NAME.exportCsv操作。然后，您可以添加返回语句以将文件名更改为有效的文件名。

为了使函数导出工作，函数必须返回一个对象，其中每个属性代表一个列名，每个属性值是一个等长的数组，代表该列中每个单元格的值。这意味着如果您正在处理查询结果，必须删除查询中的._results属性；该属性由 Slate 添加，以提供查询是否成功运行的信息，但它会阻止函数的导出。

## 变量操作

变量操作作用于特定变量。它们使应用程序构建者能够在特定事件触发时修改变量的值。

### VARIABLE_NAME.set

此操作将指定的变量VARIABLE_NAME设置为操作传递的任何值（Action面板中的 JavaScript 代码的返回值）。请注意，变量的旧/当前值仍可作为{{VARIABLE_NAME}}使用，允许您使用先前的值来确定要设置的新值。每个变量都有此操作的独立实例。
