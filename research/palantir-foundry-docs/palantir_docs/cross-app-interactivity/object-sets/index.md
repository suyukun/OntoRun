来源: https://palantir.com/docs/zh/foundry/cross-app-interactivity/object-sets/

# 对象集

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 对象集

对象集表示单一媒体类型的无序对象集合。有关更多信息，请参见媒体类型和Palantir媒体类型。

## Foundry

这些是主要用于在Foundry中传输数据的媒体类型，并由Foundry概念支持。

### Foundry对象集

媒体类型："application/x-vnd.palantir.rid.object-set.temporary-object-set"

数据形态：字符串[]

此媒体类型可用于在DataTransfer上传输Foundry对象集RID。有关更多信息，请参见对象集。

请参考拖放区域教程，以获取有关如何使用此媒体类型实现应用程序拖放的指导。

#### 用法

此媒体类型可以如下写入DataTransfer：

```
Copied!1
2
3
4
5
const objectSetRids = ["ri.object-set.main.temporary-object-set.XXXXXXXX", "ri.object-set.main.temporary-object-set.YYYYYYYYY"]
event.dataTransfer.setData(
    "application/x-vnd.palantir.rid.object-set.temporary-object-set",
    JSON.stringify(objectSetRids)
);
```

```
Copied!1
2
3
4
5
6
7
8
// 定义了一个包含两个对象集 RID 的数组
const objectSetRids = ["ri.object-set.main.temporary-object-set.XXXXXXXX", "ri.object-set.main.temporary-object-set.YYYYYYYYY"]

// 将对象集 RID 数组转换为 JSON 字符串，并通过 dataTransfer 接口设置数据
event.dataTransfer.setData(
    "application/x-vnd.palantir.rid.object-set.temporary-object-set", // 数据类型
    JSON.stringify(objectSetRids) // 数据内容
);
```

```
#### 示例

如果您的Workshop部分标题可以拖动，它将成为一个拖动区域，将对象集媒体类型添加到拖动负载中。

<img src="../../foundry-docs/cross-app-interactivity/media/drag.png" width=600 alt="Foundry 可拖动的Workshop部分标题">

然后可以将此拖动负载放到Vertex图表上。

<img src="../../foundry-docs/cross-app-interactivity/media/vertex-graph.png" width=600 alt="Foundry Vertex图表">
```
