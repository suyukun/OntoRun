来源: https://palantir.com/docs/zh/foundry/cross-app-interactivity/enrichment-reference/

# 在 Foundry 和 Gotham 之间拖放

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 在 Foundry 和 Gotham 之间拖放

在某些情况下，您可能同时拥有一个 Foundry 和 Gotham 对同一现实世界对象的表示，将这些对象表示视为彼此的同义词。同义词是准确表示现实世界中同一对象的不同资源。这些同义词可以通过类型映射相互映射，建立它们之间的同义表示。

为了提高 Foundry 和 Gotham 之间的兼容性，您可以通过实施数据丰富来识别现有的同义词。拖放数据丰富通过发现跨 Foundry 和 Gotham 映射的同义表示来变换工作流程，从而提高您的应用程序与 Palantir 平台之间的互操作性。

要访问数据丰富，您的注册必须同时拥有 Gotham 和 Foundry，并启用类型映射。如果您的应用程序仅在 Gotham 或 Foundry 上执行拖放操作，则无需实现数据丰富。

在继续下面的教程之前，请确保您已查看概述和创建拖放集成点的教程，以对拖放概念和实现有基本了解。

## 通过数据丰富提高跨应用程序的互动性

作为一个示例应用案例，假设您的应用程序识别 Gotham 对象 ID，并且您希望创建一个工作流程，以便从您的应用程序中拖动 Gotham 对象 ID 数据到一个 Foundry 应用程序。您可能首先尝试使用下面的dragstart处理程序将 Gotham 对象 ID 写入 DataTransfer。请注意自定义 Palantir 媒体类型application/x-vnd.palantir.rid.gotham.object:

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
function handleDragStart(event) {
    // 使用 setData 方法将自定义格式的数据存储到拖放操作中
    event.dataTransfer.setData(
        "application/x-vnd.palantir.rid.gotham.object",
        JSON.stringify(["ri.gotham.XXXXXXXX", "ri.gotham.YYYYYYYY"...])
    );
    // 允许拖放操作的效果为 "move"，表示将拖动的元素移动到新位置
    event.dataTransfer.effectAllowed = "move";
}
```

你可能会注意到，当你试图将数据拖动到Foundry的投放区时，这些投放区不会“亮起”，这表明对于这些投放区而言，这不是有效的媒体类型。Foundry的投放区可能不会接受这些数据，因为DataTransfer包含了Gotham特定的媒体类型。你可以通过实施数据丰富来解决这个问题，以便Foundry能够识别并将Gotham对象的同义词添加到DataTransfer中。这样，Foundry就可以接受你拖放的数据，因为DataTransfer中现在包含了一个被接受的媒体类型的同义表示。请注意，这仅在你启用了类型映射并打算丰富的对象时有效。请参阅类型映射文档了解更多信息。

## 上下文和指南

以下部分提供了关于数据丰富工作的各个方面的背景信息。这包括使数据丰富成为可能的服务概述以及何时何地实施丰富。

### 在哪里添加数据丰富

数据丰富可以添加到拖动区或投放区。在拖放工作流中，不需要在拖动区和投放区都添加丰富。识别应用程序之间的数据流，以确定数据将从哪里来以及将去往哪里。

如果你的应用程序包含你希望用户将Gotham和Foundry数据拖动到的投放区，我们建议在拖动负载被投放后在投放区进行数据丰富。这样，你的应用程序就不需要同时识别Gotham和Foundry的概念。相反，你的应用程序可以接受Gotham或Foundry媒体类型，并在原始拖动负载不是接受的媒体类型时使用数据丰富的同义数据。

或者，如果你的应用程序中有你希望用户能够拖动到Foundry和Gotham投放区的拖动区，我们建议在将数据添加到DataTransfer之前进行数据丰富。这样，你的拖动负载将被丰富为同时包含Foundry和Gotham媒体类型，使Foundry和Gotham的投放区能够接受拖动负载。

### 请求丰富的数据

在实施数据丰富时，你必须向数据银行服务请求以获取同义数据。数据银行服务识别并返回Foundry和Gotham之间的同义对象标识符，实现跨平台的拖放。

向数据银行服务发出请求会产生轻微的性能成本，因为需要额外的调用。我们建议你注意添加到应用程序中的丰富拖动或投放区的数量以及相关的性能成本增加。联系你的Palantir代表以获取有关此服务的更多信息。

如果你的工作流涉及在Gotham和Foundry之间拖放数据，请按照丰富教程来利用Palantir媒体类型的强大功能。
