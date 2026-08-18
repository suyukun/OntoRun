来源: https://palantir.com/docs/zh/foundry/slate/public-applications-data-upload/

# 为公共应用程序上传数据

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 为公共应用程序上传数据

通过公共应用程序上传数据的能力需要通过查询提供安全的上传端点。您可以通过创建一个公共应用程序并创建一个新查询来测试此功能。如果安全上传不可用，请联系您的Palantir代表以获得支持。

可以将公共应用程序配置为让用户上传数据到Foundry。上传数据的用户不需要访问Foundry。然而，只有拥有适当资源权限的Foundry用户才能访问上传的数据。

要在您的公共应用程序中设置数据上传，请按照以下说明进行操作：

## 1. 创建一个空数据集

在您选择的项目或文件夹中创建一个新的数据集资源。

## 2. 创建一个通道

在您的公共Slate应用程序中，基于安全上传源创建一个新查询。首先，通过勾选测试旁边下拉菜单中的复选框，将查询设置为仅手动运行。从可用服务中选择通道服务，然后从端点下拉菜单中选择放置通道。

如果安全上传不可用，请联系您的Palantir支持。

在channelId中，输入您的通道的唯一名称（例如，slate-app-name-data-upload）。channelId不能包含空格。请求体需要您之前创建的空数据集的RID。您可以从数据集的URL中获得数据集RID（例如：ri.foundry.main.dataset.1a2bcd34-5678-90e1-fa23-bc456d7e8f90）。

在请求体中输入以下JSON：

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
{
  "configuration": {
    "dataset": "<your_dataset_rid_here>",  // 你的数据集ID
    "maxBlobSize": <optional size limit for individual blob size (in bytes)>,  // 可选的单个Blob大小限制（以字节为单位）
    "options": {
      "type": "json",  // 数据类型为JSON
      "json": {}
    }
  }
}
```

选择测试。响应将返回一个与您在字段中输入的匹配的channelId。存储该channelId，因为在接下来的步骤中需要用到它。

除非您想创建更多的频道，否则用户上传数据时不再需要此查询。该查询可以安全地删除。

## 3. 创建词元

创建频道后，您需要创建一个词元。此词元是提交安全上传查询并将数据上传到数据集中所必需的。创建一个以secure-upload为源的新查询。像之前一样，将查询设置为仅手动运行。从可用服务中，选择词元服务，然后从端点下拉菜单中选择创建词元。

请求体的格式如下：

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
  "type": "blobUploadToDataset",
  "blobUploadToDataset": {
    "channel": "<channelId defined in step 2>", // 在步骤2中定义的channelId
    "expiry":"<expiration date in ISO-8601: e.g. 2021-06-30T00:00:00Z>", // 过期日期，采用ISO-8601格式，例如：2021-06-30T00:00:00Z
    "count": 1 // 上传的blob数量
  }
}
```

最大到期日期取决于您 Foundry 实例的安全上传配置。

选择Test以提交查询。响应包括一个需要保存的词元，因为它只会显示一次。如有必要，重新运行查询以获得另一个词元。除非您想创建更多词元，否则用户上传数据时不再需要此查询。该查询可以安全删除。

## 4. 为数据上传创建查询

为了允许用户提交查询，您需要再创建一个查询：

- 选择secure-upload-raw作为来源。这是一个 HTTP JSON 数据源，将提示您输入 JSON 数据以定义查询请求。
- 打开Test附近的下拉菜单并选择提交数据的时机（在按钮点击时或其他标准，就像常规查询一样）。请求的主体定义了将捕获并上传到先前创建的数据集中的字段。即使在初次提交后，您也可以编辑这些字段。在修改前输入的条目将在新增字段下显示为空值。
每个字段都需要映射到一个值。值需要是字符串。您可以使用 jsonStringify 句柄助手或使用函数将值转换为字符串。

以下是请求主体的示例：

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
{
    "path": "blobs",
    "method": "POST",
    "extractors": {
        "result": "$"
    },
    "headers": {
        "authorization": "Bearer <token_from_step_3>"
    },
    "bodyJson": {
        "content": {
            // 这里可以填入任何JSON格式的内容
            // 例如：
            "field1": "value1", // 字段1对应的值为"value1"
            "field2": {{jsonStringify w_input1.text}}, // 使用jsonStringify方法将w_input1.text转换为字符串格式
            "field3": [
                "item1", // 字符串项"item1"
                {{jsonStringify w_input2.text}}, // 将w_input2.text转换为字符串格式
                {{jsonStringify f_function1}} // 将f_function1的结果转换为字符串格式
            ]
        }
    }
}
```

这个JSON结构定义了一个POST请求，包含路径、提取器、请求头和请求体。请求体中的content字段可以包含任何JSON格式的数据，支持动态值的插入。
当此查询运行时，数据将落在一个附加了后缀_buffer_v2的数据集中，并与原始数据集一起存放。数据的形状将完全按照此步骤中定义的方式。例如，来自上述示例的查询主体将导致“content”列中的以下数据条目（数据集将在其他列中包含附加的元数据）：

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
{
  content: {
    "field1": "value1",  // 字段1的固定值
    "field2": "<<value of jsonStringify w_input1.text>>",  // 字段2的值来自 w_input1.text 的 JSON 序列化结果
    "field3": [
      "item1",  // 字段3数组的第一个固定项
      "<<value of jsonStringify w_input2.text>>",  // 数组的第二项来自 w_input2.text 的 JSON 序列化结果
      "<<value of jsonStringify f_function1>>"  // 数组的第三项来自 f_function1 的 JSON 序列化结果
    ]
  }
}
```

## 停止数据上传

要停止将新条目上传到数据集中，您需要同时取消发布应用程序并删除在最后一个查询中用作身份验证头的词元。

尽管取消发布会将应用程序隐藏于未经身份验证的用户，但未经身份验证的用户仍可以调用公共安全上传数据源。删除词元对维护应用程序安全性至关重要。

请记得将生成的词元存储在安全的位置，因为没有恢复选项。

要删除词元，请按照以下步骤操作：

- 在Slate中，创建一个以secure-upload为源的查询。
- 打开靠近Test的下拉菜单，勾选manually复选框以手动运行此查询。
- 从可用服务中选择词元服务。
- 从端点选择删除词元。
- 将您想要删除的词元输入为字符串（例如，1abcdefgha2bcdef3ghabcdefg）。
- 为验证词元是否被删除，通过提交数据进行检查。您应该收到以下InvalidToken响应：