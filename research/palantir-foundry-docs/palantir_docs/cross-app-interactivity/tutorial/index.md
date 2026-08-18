来源: https://palantir.com/docs/zh/foundry/cross-app-interactivity/tutorial/

# 创建拖放集成点

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 创建拖放集成点

以下教程仅涵盖在传输或接受相同媒体类型的拖放区域之间进行拖放。例如，如果您的拖动区域将Foundry object RID媒体类型数据添加到DataTransfer中，您只能将其拖动到接受Foundry object RID媒体类型的放置区域。如果您想支持在接受Gotham object媒体类型的放置区域上放置Foundry object RID数据，您需要为您的对象启用类型映射并在本教程后遵循丰富教程。

拖放允许用户在应用程序内和应用程序之间动态移动数据。以下教程将教您如何在您的应用程序和Palantir平台之间拖动数据，包括Gotham和Foundry。在您的应用程序中添加一个拖放集成点将允许用户在您的应用程序和Palantir平台之间无缝执行工作流。

实现拖放区域包括两个主要组件：

创建拖动区域：

- 使HTML元素可拖动
- 向DataTransfer中添加数据
创建放置区域：

- 启用项目在您的放置区域上放置
- 处理放置
- 设置您的放置区域样式
我们建议安装最新版本的平台，以增强您的应用程序与Palantir平台之间的拖放互操作性。

## 创建拖动区域

拖动区域是一个交互式的DOM元素，允许用户“抓取”数据并通过将其“放置”到放置区域来转移数据。拖动区域将数据写入DataTransfer对象，当用户拖动一个draggable元素时允许其传输。以下步骤详细说明了如何使元素draggable，将数据添加到DataTransfer对象，并处理拖动事件。有关这些概念的详细信息，请参阅拖动区域和DataTransfer对象。

### 使HTML元素可拖动

通过将draggable属性设置为true来使HTML元素成为拖动区域。要将数据附加到拖动事件，添加一个ondragstart处理程序，该处理程序将在DataTransfer上设置数据。

```
Copied!1
2
3
<p id="p1" draggable="true" ondragstart="handleDragStart(event)">
    Draggable Element
</p>
```

```
Copied!1
2
3
4
<!-- 这段代码定义了一个可拖拽的段落元素 -->
<!-- id="p1" 用于唯一标识这个段落 -->
<!-- draggable="true" 表示这个元素是可拖动的 -->
<!-- ondragstart="handleDragStart(event)" 是一个事件处理程序，当拖动开始时会调用 handleDragStart 函数 -->
```

### 向DataTransfer添加数据

要向拖动事件添加数据，请调用附加的DataTransfer的dataTransfer.setData方法。此方法以给定的媒体类型格式将数据添加到DataTransfer。有关更多信息，请参阅MDN DataTransfer文档 ↗。

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
function handleDragStart(event) {
    // 设置拖动数据到指定的媒体类型和数据
    event.dataTransfer.setData(
        <media type>, // 媒体类型，例如 "text/plain" 或 "text/html"
        <data> // 要传输的数据
    );

    // 设置允许的拖动效果为 "move"，表示移动操作
    event.dataTransfer.effectAllowed = "move";
}
```

将上述<media type>替换为拖拽数据的媒体类型，例如，Foundry对象RID的application/x-vnd.palantir.rid.phonograph2-objects.object。使用JSON.stringify将数据转换为字符串，以序列化版本替换<data>。请参考Palantir媒体类型文档以确定您的应用案例的正确媒体类型。

在将数据添加到您的DataTransfer时，请牢记安全问题。任何投放区域都可以访问此数据。

以下是Foundry对象RID的拖拽启动处理程序示例：

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
function handleDragStart(event) {
    // 定义一个数组，包含两个对象的资源标识符（RIDs）
    const foundryObjectRids = ["ri.phonograph2-objects.main.object.XXXXXXX", "ri.phonograph2-objects.main.object.YYYYYYY"];

    // 将资源标识符数组转换为JSON字符串，并设置为拖拽操作的数据
    event.dataTransfer.setData(
        "application/x-vnd.palantir.rid.phonograph2-objects.object",
        JSON.stringify(foundryObjectRids)
    );

    // 设置拖动效果为“移动”
    event.dataTransfer.effectAllowed = "move";
}
```

该处理程序将Foundry对象RID媒体类型添加到DataTransfer中。任何接受Foundry对象RID数据的投放区将能够在拖动的DataTransfer被放下时接收foundryObjectRids中的数据。

此时，您应该能够将数据从拖动区域拖到接受DataTransfer中媒体类型的投放区。请参阅Palantir媒体类型以查找根据媒体类型接受您拖动数据的投放区。

## 创建投放区

投放区是DOM上的交互元素，用于接收从拖动区域“放下”的数据。投放区通过监听ondrop事件并在事件触发时从事件的DataTransfer中访问信息来工作。请参阅投放区和DataTransfer对象以了解更多信息。

您可以通过添加ondragover处理程序将HTML元素变成投放区，该处理程序会阻止默认事件行为。添加一个ondrop处理程序以处理放下的DataTransfer。

步骤如下：

- 启用项目可放置在您的投放区
- 处理放下操作
- 设置您的投放区样式
本教程涵盖了创建一个接受Foundry对象RID媒体类型的投放区，但您的实现可以用您选择的媒体类型替换。

### 启用项目可放置在您的投放区

- 编写函数以防止默认的dragover和dragenter事件处理。默认事件行为不接受放下的数据，因此我们取消此行为以允许元素接受放下的数据，这对于投放区是必要的。
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
// 为确保 drop 事件会触发
// 仅在拖拽数据被接受时才阻止默认行为

function handleDragOver(event){
    // 检查拖拽的数据类型是否包含指定类型
    if(event.dataTransfer?.types.includes("application/x-vnd.palantir.rid.phonograph2-objects.object")){
        // 阻止默认行为以允许 drop
        event.preventDefault();
    }
}

function handleDragEnter(event){
    // 同样检查拖拽的数据类型
   if(event.dataTransfer?.types.includes("application/x-vnd.palantir.rid.phonograph2-objects.object")){
        // 阻止默认行为以允许进入
        event.preventDefault();
    }
}
```

- 向你的放置区域添加handleDragOver事件处理程序
```
Copied!1
2
3
4
5
6
7
<div
  id="my-cool-drop-zone"
  ondragover="handleDragOver(event)"  <!-- 当拖动元素在目标元素上方时触发，通常用于防止默认行为 -->
  ondragenter="handleDragEnter(event)"  <!-- 当拖动元素进入目标元素时触发 -->
>
  Drop Zone
</div>
```

### 处理拖放

- 创建一个函数以处理拖放，通过访问已被拖放的数据中的DataTransfer，并阻止默认事件行为，即打开链接数据。调用DataTransfer的getData函数以字符串格式返回DataTransfer中的数据。如果DataTransfer没有数据或没有该媒体类型的数据，getData将返回一个空字符串。有关此方法的更多信息，请参阅MDN getData 文档↗。下面是一个ondrop回调的示例，用于从DataTransfer获取Foundry对象的RID。请将event.dataTransfer.getData调用中的媒体类型替换为反映您想要传输的数据类型的媒体类型。
创建一个函数以处理拖放，通过访问已被拖放的数据中的DataTransfer，并阻止默认事件行为，即打开链接数据。调用DataTransfer的getData函数以字符串格式返回DataTransfer中的数据。如果DataTransfer没有数据或没有该媒体类型的数据，getData将返回一个空字符串。有关此方法的更多信息，请参阅MDN getData 文档↗。

下面是一个ondrop回调的示例，用于从DataTransfer获取Foundry对象的RID。请将event.dataTransfer.getData调用中的媒体类型替换为反映您想要传输的数据类型的媒体类型。

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
function handleDrop(event) {
    // 阻止默认的打开链接行为
    event.preventDefault();

    // 获取 Foundry 对象的 RIDs 数据
    const data = event.dataTransfer.getData(
        "application/x-vnd.palantir.rid.phonograph2-objects.object"
    );

    try {
        if (data != null && data !== ""){
            // 尝试解析返回的数据
            const dataParsed = JSON.parse(data);

            // 打印解析后的数据
            console.log(dataParsed);

            // 使用解析后的 Foundry 对象数据进行一些操作
            doCoolThingWithFoundryObjects(dataParsed);
        }
    } catch (error) {
        console.error("无法解析数据", error)
    }
}
```

在这段代码中，handleDrop函数用于处理拖放事件。它首先阻止默认的打开链接行为，然后获取拖放事件中的 Foundry 对象 RIDs 数据。在成功解析数据后，它会打印并使用该数据进行进一步的操作。如果解析失败，则会在控制台输出错误信息。
2. 将handleDrop函数添加到您的拖放区域组件中，如下所示：

```
Copied!1
2
3
4
5
6
7
<div
  id="my-cool-drop-zone"
  ondrop="handleDrop(event)"  <!-- 当元素上有拖动元素放下时触发 handleDrop 函数 -->
  ondragover="handleDragOver(event)"  <!-- 当拖动元素在目标元素上移动时触发 handleDragOver 函数 -->
>
  Drop Zone
</div>
```

此时，您应该能够将数据拖放到您的投放区域。请参阅Palantir 媒体类型文档以查找可以投放到您投放区域的拖放区域。

- （推荐）我们建议在从 DataTransfer 获取数据时尽可能使用运行时类型守卫/验证器。虽然媒体类型到媒体类型的数据连接作为合同存在，但添加类型守卫可确保接收到的数据遵循该合同。
请参阅以下文档以获取支持的 Palantir 媒体类型：

- Foundry 对象
- Foundry 对象集
- Gotham 对象
### 为您的投放区域设置样式

为您的投放区域应用样式至关重要，以便用户可以看到投放区域是否接受他们的拖动有效负载。否则，您的投放区域的可用性将不佳。我们建议根据拖动有效负载是否对投放区域有效，或者投放区域是否需要执行其他操作以确定其是否接受拖动有效负载来对投放区域应用不同的样式。投放区域的样式应在投放后清除，以下步骤中对此进行了说明。

在本教程结束时，如果投放区域接受拖动有效负载，它将“点亮”，但本教程不涉及实现设计指南中概述的“无效”和“加载”样式。我们建议实施这些附加样式，以实现更具凝聚力和用户友好的拖放交互。

完成步骤一至四后，当用户将有效负载拖到您的应用程序上且媒体类型被接受时，您的投放区域将“点亮”。完成步骤五至七后，当用户从您的应用程序内部开始拖动时，您的投放区域将“点亮”。完成步骤八后，下面图像中显示的悬停样式将应用于您的投放区域。

- 复制 CSS 类实现。为了为您的投放区域应用样式，请为您的样式创建一个 CSS 文件，并从设计指南中添加适当的投放区域样式类。请注意，我们根据您的投放区域的大小提供不同的样式建议。
复制 CSS 类实现。为了为您的投放区域应用样式，请为您的样式创建一个 CSS 文件，并从设计指南中添加适当的投放区域样式类。请注意，我们根据您的投放区域的大小提供不同的样式建议。

- 当您的投放区域接受拖动有效负载时，通过编写函数来有条件地添加样式，如果拖动有效负载包含被接受的媒体类型。此函数使用classlist ↗属性，如果投放区域接受拖动有效负载，则向我们的投放区域添加一个额外的类名。请参阅设计指南以获取 CSS 拖动悬停样式。
当您的投放区域接受拖动有效负载时，通过编写函数来有条件地添加样式，如果拖动有效负载包含被接受的媒体类型。此函数使用classlist ↗属性，如果投放区域接受拖动有效负载，则向我们的投放区域添加一个额外的类名。请参阅设计指南以获取 CSS 拖动悬停样式。

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
function conditionallyApplyStylingToDropZone(event, className){
    // 如果拖动的数据类型中包含 Foundry 对象 RIDs 的媒体类型，则我们的投放区接受该拖动数据
    if(event.dataTransfer?.types.includes("application/x-vnd.palantir.rid.phonograph2-objects.object")){
        const dropzone = document.getElementById("my-cool-drop-zone");
        if(dropzone != null){
            // 添加样式的类名
            dropzone.classList.add(className);
        }
    }
}
```

- 编写一个函数，使用classlist属性移除拖放区域的样式。
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
function removeStylingFromDropZone(){
    const dropzone = document.getElementById("my-cool-drop-zone");
    if(dropzone != null){
        dropzone.classList.remove(className);
    }
}

// 移除拖放区域的样式
function removeStylingFromDropZone(){
    // 获取拖放区域的元素
    const dropzone = document.getElementById("my-cool-drop-zone");
    if(dropzone != null){
        // 如果拖放区域元素存在，移除指定的样式
        dropzone.classList.remove(className);
    }
}
```

- 在数据从外部拖动区域拖动到放置区域上方时，通过添加dragenter和dragleave事件处理器来应用样式。注意，您需要在事件的capture阶段监听这些事件，以防止子元素阻止事件向上传播。有关更多信息，请参阅MDN 事件监听器捕获文档 ↗。在这里，我们需要本地跟踪每个事件触发的次数。这些事件将由页面上的所有子元素触发。
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
let dragInsideApplicationCount = 0;

function handleDragEnter(event){
    if(dragInsideApplicationCount === 0){
        // 如果是第一次拖拽进入，可能需要对放置区域应用有效样式
        maybeApplyValidStylingToDropZone(event, "valid-small");
    }

    dragInsideApplicationCount += 1;
}

function handleDragLeave(event){
    if(dragInsideApplicationCount === 1){
        // 如果是最后一次拖拽离开，移除放置区域的有效样式
        removeValidStylingFromDropZone("valid-small");
    }

    dragInsideApplicationCount -= 1;
}

// 监听拖拽进入事件
document.addEventListener("drag-enter", handleDragEnter, {capture: true});
// 监听拖拽离开事件
document.addEventListener("drag-leave", handleDragLeave, {capture: true});
```

上述代码片段仅当拖动是从外部应用程序或窗口上的拖动区域启动时才会使放置区亮起。如果您希望放置区在来自您的应用程序的拖动负载时亮起，您需要添加一个dragstart监听器，具体如下所述。

此时，如果放置区接受拖动负载，您应该能够从外部应用程序或窗口拖动负载并使放置区亮起。请参阅Palantir媒体类型文档以查找可以拖动到放置区的拖动区域。请注意，拖动负载放下后，样式仍将应用于您的放置区；有关放下时移除样式的说明将在后续步骤中提供。

- 编写一个全局dragstart事件监听器，当放置区接受拖动负载时应用样式。此事件监听器将在用户从同一页面的拖动区域启动拖动时触发。此样式表示您的放置区接受拖动负载。有关更多信息，请参见MDN拖动启动文档 ↗。
```
Copied!1
2
document.addEventListener("dragstart", maybeApplyValidDropStylingToDropZone, {capture: true});
// 监听拖动开始事件，并在捕获阶段调用 maybeApplyValidDropStylingToDropZone 函数，可能会将有效的拖拽样式应用到放置区域
```

- 更改拖放区域的样式，当其被拖拽经过时。为了向用户展示当拖拽的内容位于拖放区域上方时的视觉更改，向您的拖放区域添加drag-enter和drag-leave处理器，以应用和移除这些样式。这与上面的全局drag-enter和drag-leave事件监听器不同，因为这些事件仅会由拖放区域上的dragenter和dragleave事件触发。
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
let dropHoveringOverDropZoneCount = 0;

function handleDragEnter(event){
    // 如果当前悬停计数为0，并且拖拽的数据类型包含指定类型，则允许放置并应用样式
    if (dropHoveringOverDropZoneCount === 0 && event.dataTransfer?.types.includes("application/x-vnd.palantir.rid.phonograph2-objects.object")){
        // 允许放置并应用样式，如果放置区接受拖拽的有效负载
        event.preventDefault();
        conditionallyApplyStylingToDropZone(event, "valid-small-hover");
    }
    dropHoveringOverDropZoneCount += 1;
}

function handleDragLeave(event){
    // 如果当前悬停计数为1，则移除样式
    if (dropHoveringOverDropZoneCount === 1){
        removeStylingFromDropZone("valid-small-hover");
    }
    dropHoveringOverDropZoneCount -= 1;
}
```

- 将handleDragEnter和handleDragLeave拖动事件处理程序添加到您的拖放区域组件中：
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
<div
  id="my-cool-drop-zone"
  ondragover="handleDragOver(event)" <!-- 当元素被拖动到目标区域上方时触发 -->
  ondrop="handleDrop(event)" <!-- 当元素在目标区域内被释放时触发 -->
  ondragenter="handleDragEnter(event)" <!-- 当拖动的元素进入目标区域时触发 -->
  ondragleave="handleDragLeave(event)" <!-- 当拖动的元素离开目标区域时触发 -->
>
  Drop Zone
</div>
```

- 更新投放区域以执行样式清理。当数据被投放后，从投放区域移除投放样式的CSS类。这是必要的，以便投放区域不会停留在“点亮”阶段。同时重置拖动计数器，以便从头处理新的拖动事件。
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
function handleDrop(event) {
    // 阻止默认的打开链接行为
    event.preventDefault();

    // 执行一些样式清理
    // 移除CSS类，因为现在没有活动的拖拽数据
    removeStylingFromDropZone("valid-small-hover");
    removeStylingFromDropZone("valid-small");

    // 重置计数器
    dropHoveringOverDropZoneCount = 0;
    dragInsideApplicationCount = 0;

    // 获取 Foundry 对象 RIDs 数据
    const data = event.dataTransfer.getData(
        "application/x-vnd.palantir.rid.phonograph2-objects.object"
    );

    try {
        if (data != null && data !== ""){
            // 尝试解析返回的数据
            const dataParsed = JSON.parse(data);

            // 打印数据
            console.log("dropped data: ", dataParsed);

            // 对数据进行一些操作
            doCoolThingWithFoundryObjects(dataParsed);
        }
    } catch (error) {
        console.error("无法解析数据", error);
    }
}
```

完成此步骤后，您应该拥有一个可用的放置区域。当放置区域接受拖动负载中的数据时，它应该会亮起，并且在拖动负载被放下后，数据应该打印在控制台中。您的放置区域还应该在拖动负载被放下后移除样式。

如果您的工作流程涉及在Gotham和Foundry之间传输数据，请遵循数据增强教程以实现此功能。
