来源: https://palantir.com/docs/zh/foundry/cross-app-interactivity/enrichment-tutorial/

# 实现 Foundry 和 Gotham 之间的拖放

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 实现 Foundry 和 Gotham 之间的拖放

要访问数据增强，您的注册必须同时拥有 Gotham 和 Foundry，并启用类型映射。如果您的应用程序仅在 Gotham 或仅在 Foundry 上执行拖放操作，则无需实现数据增强。

以下教程概述了实现数据增强所需的步骤。请注意，有添加增强到拖放区域的部分，但根据您的工作流程，增强只需要在拖区或放区发生。有关更多信息，请参阅增强指南。

## 拖放增强教程

步骤如下：

- 验证数据银行服务返回同义数据。
- 创建增强实用函数。
- 添加增强到拖区或添加增强到放区。
我们建议安装我们平台的最新版本，以增强您的应用程序与 Palantir 平台之间的拖放互操作性。

## 验证数据银行服务返回同义数据

要实现数据增强，您必须首先验证数据银行服务按预期返回同义数据。

### 支持的媒体类型

目前，数据银行服务支持增强以下列表中的媒体类型，目前可以使用Foundry 对象 RID媒体类型的数据增强Gotham 对象媒体类型的数据，反之亦然。

```
Copied!1
2
"application/x-vnd.palantir.rid.phonograph2-objects.object",
"application/x-vnd.palantir.rid.gotham.object",
```

这些代码行表示的是MIME类型字符串，用于描述两种不同类型的对象：

- application/x-vnd.palantir.rid.phonograph2-objects.object：表示Palantir的Phonograph2对象。
- application/x-vnd.palantir.rid.gotham.object：表示Palantir的Gotham对象。
这通常用于HTTP协议中，服务器和客户端通过MIME类型进行数据的交换和处理。

### 所需数据结构

以下是Data Bank Service请求所需的数据结构示例。请注意，JSON对象必须首先序列化以用于Data Bank Service请求；我们将在后续步骤中概述如何使用JSON.stringify↗。请求格式如下：

```
Copied!1
2
3
4
{
    "dataTransfers": [serializedData1, serializedData2, ...]
    // "dataTransfers" 是一个数组，包含多个序列化的数据对象（serializedData1, serializedData2 等）
}
```

上述代码片段中的serializedData指的是在序列化后发送到数据银行服务以进行丰富的数据。上面的dataTransfersObject不应与DataTransfer object混淆，它们名称相似但用途不同。上面的Object包含我们想要丰富的数据，而丰富可以在写入DataTransfer Object之前进行，也可以在DataTransfer Object被拖放到放置区域后进行。

每个serializedDataObject具有以下结构：

```
Copied!1
{<媒体类型>: <序列化数据>}
```

例如，如果您有Gotham Object标识符，并且想要以同义的Foundry数据丰富此数据，您的序列化数据表示将如下所示：

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
    "dataTransfers": [
        {
            // 数据传输格式为 "application/x-vnd.palantir.rid.gotham.object"
            // 包含多个资源标识符 (resource identifiers)
            "[\"application/x-vnd.palantir.rid.gotham.object\"]: [\"ri.gotham.XXXXXXXX\", \"ri.gotham.YYYYYYYY\", \"ri.gotham.ZZZZZZZZZZ\"]"
        }
    ]
}
```

在上述代码片段中，媒体类型为application/x-vnd.palantir.rid.gotham.object，后面跟随一个具有该媒体类型的数据数组。Data Bank Service将返回映射的同义媒体类型及其数据。注意，必须使用\转义引号（"），以正确格式化序列化数组。

在下面的curl请求中使用此请求格式，将application/x-vnd.palantir.rid.gotham.object媒体类型替换为您的媒体类型，并添加您计划丰富的数据。将<BEARER TOKEN>替换为您的词元，将<HOSTNAME>替换为您的注册主机名。注意，媒体类型的数据为字符串格式，并用\字符转义内部引号。

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
curl --location --request PUT "https://<HOSTNAME>/data-bank-service/api/data-transfer/batchEnrichDataTransfer" \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer <BEARER TOKEN>' \
--data '{
    "dataTransfers": [
        {
           "application/x-vnd.palantir.rid.gotham.object": "[\"ri.gotham.XXXXXXXX\", \"ri.gotham.YYYYYYYY\", \"ri.gotham.ZZZZZZZZZZ\"]"
        }
    ]
}'
```

该命令使用curl工具发送一个 HTTP PUT 请求。请求的详细信息如下：

- --location选项用于遵循请求重定向。
- --request PUT指定请求方法为 PUT。
- https://<HOSTNAME>/data-bank-service/api/data-transfer/batchEnrichDataTransfer是请求的目标 URL。请将<HOSTNAME>替换为实际的主机名。
- --header 'Content-Type: application/json'设置请求头，指定请求体的数据格式为 JSON。
- --header 'Authorization: Bearer <BEARER TOKEN>'设置请求头，用于携带认证令牌。请将<BEARER TOKEN>替换为实际的 Bearer 令牌。
- --data '{...}'指定请求的 JSON 数据体，其中包含一个dataTransfers数组。数组的每个元素是一个对象，包含一个键application/x-vnd.palantir.rid.gotham.object和其对应的值，这是一个包含多个对象标识符的 JSON 数组字符串。在实际使用中，请将标识符XXXXXXXX、YYYYYYYY和ZZZZZZZZZZ替换为实际的对象 ID。
如果您的数据具有同义词，您应该得到类似于以下的响应：
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
{
    "dataTransfers": [
        {
            "dataTransfer": {
                // 数据传输类型为Palantir定制的Gotham对象格式
                "application/x-vnd.palantir.rid.gotham.object": "[\"ri.gotham.XXXXXXXX\", \"ri.gotham.YYYYYYYY\", \"ri.gotham.ZZZZZZZZZZ\"]",
                // 数据传输类型为Palantir定制的Phonograph2对象格式
                "application/x-vnd.palantir.rid.phonograph2-objects.object": "[\"ri.phonograph2-objects.main.object.XXXXXXXX\", \"ri.phonograph2-objects.main.object.YYYYYYYY\", \"ri.phonograph2-objects.main.object.ZZZZZZZZZZ\"]",
            },
            "errors": [] // 没有错误信息
        }
    ]
}
```

请注意上面提到的dataTransfersObject、Gotham 媒体类型application/x-vnd.palantir.rid.gotham.object后跟随该媒体类型的数据，以及 Foundry 媒体类型application/x-vnd.palantir.rid.phonograph2-objects.object后跟随该媒体类型的数据。

如果您没有获得 Object 的同义词，请确认您的注册和 Ontology 启用了类型映射。如果您的 Ontology 确实启用了类型映射，请按照类型映射文档确认为您的 Object 类型启用了类型映射。我们还建议验证您发送的数据是否映射到预期的同义媒体类型，并且 Data Bank Service 支持它。

在本教程的其余部分中，我们将分解使用此请求的步骤，并向您展示如何使用响应来丰富您的拖放工作流。

既然您已经验证了 Data Bank Service 对您的数据具有同义词，请继续教程以在您的应用程序中添加丰富功能。

## 创建丰富功能函数

- 创建一个 Function，用于向 Data Bank Service 发出请求。以下是如何使用Fetch API ↗为 Data Bank Service 请求创建请求选项的示例。
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
// 创建一个函数，用于使用序列化数据生成请求选项对象
function getRequestOptions(
    bearerToken,
    // serializedData 是媒体类型到其数据序列化版本的映射
    serializedData
) {
    return {
        method: "PUT", // 请求方法为PUT
        headers: new Headers({
            "Authorization": bearerToken, // 认证信息，使用Bearer Token
            "Content-Type": "application/json" // 内容类型为JSON
        }),
        body: {
            "dataTransfers": [ serializedData ] // 请求主体，包含数据传输信息
        },
        redirect: "follow" // 重定向选项
    };
}

// 按如下方式使用此函数
// 将 <BEARER TOKEN> 替换为您的 Bearer Token
const requestOptions = getRequestOptions(
    "<BEARER TOKEN>",
    {
        ["application/x-vnd.palantir.rid.gotham.object"]:
        "[\"ri.gotham.XXXXXXXX\", \"ri.gotham.YYYYYYYY\", \"ri.gotham.ZZZZZZZZZZ\"]" // 序列化数据
    }
);
```

- 访问Data Bank服务增强端点，以获取用于增强拖放区域的其他同义媒体类型和该媒体类型的数据：
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
// 将 <HOSTNAME> 替换为您的注册主机名
const batchEnrichDataTransferURL =
    "https://<HOSTNAME>/data-bank-service/api/data-transfer/batchEnrichDataTransfer";

// bearerToken 类型为字符串
// serializedData 类型为 {[mediaType: string]: string}
function getEnrichedData(
    bearerToken,
    serializedData
){
    // 调用在步骤1中定义的函数，获取请求选项
    const requestOptions = getRequestOptions(bearerToken, serializedData);

    // 使用 fetch API 请求批量丰富数据传输的URL
    const enrichedData =
        await fetch(batchEnrichDataTransferURL, requestOptions)
            .then((response) => response.json()) // 解析响应为 JSON 格式
            .catch((error) => console.error(error)); // 捕获并打印错误

    // 由于我们只丰富一个数据传输，获取第一个条目
    const enrichedFirstDataTransfer = enrichedData.dataTransfers?.[0]?.dataTransfer;
    return enrichedFirstDataTransfer;
}
```

此端点返回一个序列化的对象列表，每个对象包含已解析的丰富数据和与该丰富相关的潜在出错列表。此端点以以下格式返回数据：

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
    {
        "dataTransfers":
            [
                {
                    "dataTransfer": {"<media type>": "<serialized data>"}, // 数据传输对象，包含媒体类型和序列化数据
                    "errors": "[<error1>, <error2>...]" // 错误信息列表，记录数据传输过程中出现的错误
                },
                {
                    "dataTransfer": {"<media type>": "<serialized data>"}, // 数据传输对象
                    "errors": "[<error1>, <error2>...]" // 错误信息列表
                },
            ...
            ]
    }
```

一个需要注意的潜在出错是请求媒体类型不被Data Bank Service支持。

## 为拖动区域添加补充

请注意，补充只需要添加到拖动或放置区域。请查阅补充指南以确定本教程的此部分是否与您的工作流程相关。

- 为了在您的拖动区域添加补充，从上一节的第二步调用getEnrichedData函数。补充应在页面或组件挂载时发生，而不是在dragstart处理程序中。这是因为您无法在dragstart处理程序中进行昂贵的阻塞调用。返回的补充数据将包含您请求中的原始数据以及其他同义数据。
为了在您的拖动区域添加补充，从上一节的第二步调用getEnrichedData函数。补充应在页面或组件挂载时发生，而不是在dragstart处理程序中。这是因为您无法在dragstart处理程序中进行昂贵的阻塞调用。返回的补充数据将包含您请求中的原始数据以及其他同义数据。

- 在dragstart处理程序中，将获得的补充数据添加到拖动事件的DataTransfer中。当这些数据被添加到拖动事件的DataTransfer中时，如果补充成功，用户将能够将此数据包拖动到Foundry和Gotham的放置区域中。下面的代码展示了如何使用Gotham对象ID请求补充数据，并使用JSON.stringify↗将数据以字符串格式放入。
在dragstart处理程序中，将获得的补充数据添加到拖动事件的DataTransfer中。当这些数据被添加到拖动事件的DataTransfer中时，如果补充成功，用户将能够将此数据包拖动到Foundry和Gotham的放置区域中。下面的代码展示了如何使用Gotham对象ID请求补充数据，并使用JSON.stringify↗将数据以字符串格式放入。

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
const gothamObjectIds = ["ri.gotham.XXXXXXXX", "ri.gotham.YYYYYYYY", "ri.gotham.ZZZZZZZZZZ"];

async function getEnrichedFoundryData(){
    // 调用异步函数获取丰富的数据信息
    const enrichedData = await getEnrichedData(
        "<BEARER TOKEN>",
        {"application/x-vnd.palantir.rid.gotham.object": JSON.stringify(gothamObjectIds)}
    );

    // 提取特定格式的丰富数据
    const enrichedFoundryIdData = enrichedData?.["application/x-vnd.palantir.rid.phonograph2-objects.object"]

    if (enrichedFoundryIdData != null){
        try {
            // 尝试解析 JSON 数据
            return JSON.parse(enrichedFoundryIdData);
        } catch (error) {
            // 如果解析失败，输出错误信息
            console.error(error);
            return undefined;
        }
    }
}

let enrichedFoundryIdData = null;

// 异步更新丰富的数据
// 这是必要的，因为我们不能在拖动开始的处理程序中实现数据丰富，否则会导致阻塞
getEnrichedFoundryData().then((data) => {
    enrichedFoundryIdData = data;
});

async function handleDragStart(event) {
    // 设置拖动数据，包含原始的 Gotham 对象媒体类型数据
    event.dataTransfer.setData("application/x-vnd.palantir.rid.gotham.object", JSON.stringify(gothamObjectIds));

    if(enrichedFoundryIdData != null){
        // 如果丰富的数据不为空，设置附加的数据
        event.dataTransfer.setData("application/x-vnd.palantir.rid.phonograph2-objects.object", enrichedFoundryIdData)
    }

    // 现在 event.dataTransfer 包含了原始的 Gotham 对象数据以及相关的 Foundry 数据
    event.dataTransfer.effectAllowed = "move";
}
```

使用上述代码，如果您有包含Foundry同义词的Gotham对象ID，您可以将同义数据添加到您的DataTransfer中，以便您的拖动有效载荷可以被Gotham和Foundry的放置区接受。

完成此步骤后，您应该能够将拖动区域拖动到Gotham和Foundry的放置区。请参考Palantir媒体类型文档找到可以接受您拖动区域的放置区。

## 向放置区添加增强

请注意，增强只需添加到拖动或放置区。请查阅增强指南以确定本教程的这一部分是否与您的工作流程相关。

要向您的放置区添加增强，您需要从事件的DataTransfer中增强数据。在下面的代码片段中，代码期望Gotham对象ID，但如果DataTransfer上没有Gotham对象媒体类型，可以从DataTransfer中增强数据。为简单起见，假设下面的放置处理程序首先尝试直接从DataTransfer中访问Gotham对象数据，并在失败后，继续进行下面代码块中的增强。

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
function handleDrop(event) {
    // 防止默认的打开链接行为
    event.preventDefault();

    // 执行一些样式清理
    removeStylingFromDropZone("valid-small-hover");
    removeStylingFromDropZone("valid-small");
    dropHoveringOverDropZoneCount = 0;
    dragInsideApplicationCount = 0;

    // <尝试从DataTransfer中访问Gotham对象数据，如果成功则提前返回，否则继续>

    // Foundry对象RID的媒体类型数据可以被丰富为Gotham对象的媒体类型数据
    const foundryData = event.dataTransfer.getData(
        "application/x-vnd.palantir.rid.phonograph2-objects.object"
    );

    try {
        if(foundryData != null && foundryData !== ""){
            // 尝试解析返回的数据并发送丰富请求，
            // 如果无法解析数据，则说明数据格式错误
            const foundryDataParsed = JSON.parse(foundryData);

            const serializedData = {
                ["application/x-vnd.palantir.rid.phonograph2-objects.object"]: foundryDataParsed
            }

            const enrichedData = await getEnrichedData(
                "<BEARER TOKEN>",
                serializedData
            );

            if(enrichedData?.["application/x-vnd.palantir.rid.gotham.object"] != null){
                doCoolThingWithGothamObjectIds(
                    enrichedData["application/x-vnd.palantir.rid.gotham.object"]
                );
            }
        }
    } catch (error) {
        console.error("无法解析数据", error)
    }
}
```

添加了中文注释，以帮助理解代码的功能和逻辑。

在这一点上，您的拖放区域应该能够接受Gotham和Foundry数据。请参阅Palantir媒体类型文档，以找到可以拖动到您的拖放区域的拖放区域。

### 结论

使用上述代码片段，您可以向Data Bank Service端点发送请求，以丰富您的数据，使其包含在Gotham和Foundry中兼容的同义词。这使得可拖动数据可以被Gotham和Foundry的拖放区域接受，并且可以使拖放区域接受Foundry和Gotham数据。
