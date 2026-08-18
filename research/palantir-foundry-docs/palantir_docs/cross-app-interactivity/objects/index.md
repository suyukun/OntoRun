来源: https://palantir.com/docs/zh/foundry/cross-app-interactivity/objects/

# Object

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Object

Object媒体类型描述了将对象元数据附加到拖动负载的契约。Palantir平台接受这些媒体类型，因此将它们添加到您的拖动负载中可以使相关的投放区域接收包含此媒体类型的数据。使用这些媒体类型创建投放区域意味着您可以将负载从Palantir平台中的相关拖动区域拖动到您的投放区域。有关更多信息，请参见媒体类型和Palantir媒体类型。

## Foundry

这些是主要用于Foundry中的数据的媒体类型，并由Foundry概念支持。

### Foundry对象资源标识符

媒体类型:"application/x-vnd.palantir.rid.phonograph2-objects.object"

数据形状:string[]

此媒体类型可用于在DataTransfer上传输Foundry对象资源标识符（RID）。

请参阅拖放区域教程，了解如何使用此媒体类型实现应用程序的拖放功能。有关如何使用这些ID获取对象数据的信息，请参阅Ontology概览文档，并查看对象RID文档，以获取有关Foundry对象RID的更多信息。

#### 用法

此媒体类型可以如下写入DataTransfer：

```
Copied!1
2
3
4
5
6
7
8
const foundryObjectRids = ["ri.phonograph2-objects.main.object.XXXXXXX", "ri.phonograph2-objects.main.object.YYYYYYY"]
// 将一组对象RID存储在一个数组中

event.dataTransfer.setData(
    "application/x-vnd.palantir.rid.phonograph2-objects.object",
    JSON.stringify(foundryObjectRids)
    // 将对象RID数组转换为JSON字符串并设置为拖放操作的数据
);
```

#### 示例

在Object Explorer视图中，对象图标是一个拖动区域，用于将Foundry对象RID媒体类型添加到拖动负载中。

然后可以将此拖动负载放到Vertex图上。

## Gotham

这些是主要用于Gotham的媒体类型，并由Gotham概念支持。

### Gotham对象标识符

媒体类型:"application/x-vnd.palantir.rid.gotham.object"

数据形状:字符串[]

这种媒体类型可用于在DataTransfer上传输Gotham对象标识符。Gotham标识符，也称为GIDs，用于标识Gotham中的数据和其他概念。

查看拖放教程以获取有关如何使用此媒体类型在您的应用程序中实现拖放的指导。

#### 用法

这种媒体类型可以如下写入DataTransfer：

```
Copied!1
2
3
4
5
6
7
8
// 定义一个包含两个字符串的数组，代表 Gotham 对象的 ID
const gothamObjectIds = ["ri.gotham.XXXXXXXX", "ri.gotham.YYYYYYYYY"]

// 将 gothamObjectIds 数组转换为 JSON 字符串，并将其存储在 dataTransfer 对象中，使用自定义的 MIME 类型 "application/x-vnd.palantir.rid.gotham.object"
event.dataTransfer.setData(
    "application/x-vnd.palantir.rid.gotham.object",
    JSON.stringify(gothamObjectIds)
);
```

#### 示例

在下图中，每个卡片都是一个Gotham Object拖拽区域。

以下地图放置区域接受Gotham Object拖拽负载。
