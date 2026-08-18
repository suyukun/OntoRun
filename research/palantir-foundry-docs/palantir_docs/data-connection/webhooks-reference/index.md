来源: https://palantir.com/docs/zh/foundry/data-connection/webhooks-reference/

# 配置参考

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 配置参考

本页面记录了在数据连接中与Webhooks相关的详细配置选项和权限。

## 配置输入和输出

每个Webhook都可以灵活配置，将输入参数映射到将发送到外部系统的请求中。然后，可以将系统的响应捕获为输出参数，这些参数可以在Palantir Foundry的其他地方使用。

### 输入参数

输入参数表示在用户执行Webhook时可以传递的输入。通常，Webhook配置用于操作类型，在这里可以指定操作参数和Webhook输入参数之间的映射。

Webhook输入参数有多种数据类型和约束条件：

- Boolean参数可以是true或false。
- Integer、Long和Double参数表示数值。
- String参数表示文本值，可以限制仅允许特定值。
- Date和Timestamp参数表示基于时间的数据。
除了这些基本类型，还有几种集合类型可用：

- List参数表示特定类型的有序输入集合。
- Record参数允许传递键/值对，并且可以限制要求特定键和特定类型的值。
- Optional参数表示输入可能存在也可能不存在。
如果您希望使用Object上的函数从操作参数映射到Webhook输入，您还可以在映射输入的函数返回undefined时有条件地不触发Webhook。例如，WebhookInput | undefined。

最后，还有一种Attachment类型，可以用于传递在操作表单中上传的文件。请注意，此功能仅支持直接连接或代理代理源。

### 输出参数

输出参数允许您捕获从外部系统返回的数据，以便在Foundry的其他地方使用。例如，当您在外部系统中创建新记录时，系统可能会返回新记录的ID。通过在输出参数中捕获此新ID，您可以将其传播到操作中，并立即将其写入Foundry对象。

Webhook设置向导中显示了一个名为unique_id的单个输出参数的示例配置：

或者，也可以在Webhook配置步骤中直接访问输出参数。下面显示了一个示例，其中一个Webhook调用使用了上一个调用响应中的值。第一个Webhook调用返回的响应如下所示：

```
Copied!1
2
3
4
5
{
  "results": {
    "unique_id": "ID4567" // 唯一标识符
  }
}
```

配置第二个 webhook 调用。在Headers选项卡中，您可以通过键入@来创建行内引用，这将打开一个菜单，您可以在其中引用上一次调用的响应值。

选择From a call并选择具有要解析的响应的上一次调用。有三种选项可用于从响应中提取必要的值：

- Whole response:将整个响应提取为字符串。
- Extract by key:使用响应中的键提取所需的值。
- Extract by index:使用索引位置（从零开始）从数组响应中提取所需的值。
如下例所示，选择Extract by key并配置键：results后跟unique_id使用Add nested key选项。

选择Add，您将能够在标头值字段中看到显示的引用。

捕获的输出参数取决于您使用的任务类型。

了解更多关于如何从 REST Webhook 捕获输出参数并在操作中使用这些参数的信息。

为了方便起见，在某些情况下，Webhook 任务的结果会自动转换为适当的输出参数类型：

- 如果配置了字符串输出参数，而 Webhook 任务结果不是字符串，则结果将转换为 JSON 字符串。
- 如果配置了Record输出参数，而 Webhook 任务结果是字符串，则 Webhooks 服务将尝试将字符串解析为 JSON。
- 如果配置了Double输出参数，则 Webhook 任务结果为整数或长整数时将自动转换。
输出参数可以使用通过“测试连接”侧面板发出的请求接收到的响应进行配置。一旦成功发出测试请求，在添加新的输出参数时，将自动显示从响应中解析的建议输出。

### 任务主体

某些 webhooks 作为任务实现。对于这些 webhooks，任务主体代表在 webhook 执行时将发送到任务的数据。

每个任务期望的结构取决于将列出的具体任务类型（如果相关），在该webhook 类型的条目下。任务主体应使用Handlebars ↗语法定义。在任务主体中，您可以引用上文为 webhook 定义的任何输入参数。

## Webhook 类型

每种类型的 webhook 支持不同的配置选项。本节记录了各种 webhook 类型可用的选项，并提供了基本示例以帮助您入门。

### REST API

webhooks 最常见的用途是向 REST API 发出 HTTP 请求。在配置 REST API 源后，您可以使用请求构建器界面构建您希望发出的请求。

REST API 源的可用选项包括：

| 选项 | 是否必需 | 描述 |
| --- | --- | --- |
| Method | 是 | 请求的 HTTP 方法。 |
| Relative path | 否 | 指定请求端点的相对路径。这应该相对于在 REST API 源中配置的一个域。 |
| Query Params | 否 | 为要包含在请求中的任何查询参数提供键值对。某些查询参数可能会根据源配置在运行时包含。那些将在此处显示为只读。 |
| Authorization | 否 | 授权详细信息基于源配置。任何编辑都应通过导航回源来完成。 |
| Headers | 否 | 为要包含在请求中的任何标头提供键值对。某些查询参数可能会根据源配置在运行时包含。那些将在此处显示为只读。 |
| Body | 否 | 对于接受正文的请求，您可以从可用类型中包含正文。这些类型包括Raw JSON、Form Data、Form URL Encoded、二进制File、XML、Plain Text和HTML。 |

#### 多个请求

单个 webhook 可能包含多个请求。请求可以串联在一起，后续调用中引用来自上一次调用的响应值。

### REST API（遗留）

此处记录的遗留 REST API 选项和使用magritte-rest-v2插件仅供历史参考。新工作流应使用 REST API 源实现。

在设置magritte-rest-v2源后，您可以使用generic-rest-webhook-task创建 REST Webhooks。

对于 REST Webhook，任务主体的结构必须是calls数组，每个call代表一个将对外部系统发出的 REST 请求。

对于 webhooks，唯一支持的call类型是magritte-rest-call。

以下是 REST Webhook 的基本任务主体模板示例，代表单个 HTTP 调用：

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
    "calls": [
        {
            "type": "magritte-rest-call",  // REST API调用类型
            "method": "POST",  // 使用POST方法
            "requestMimeType": "application/json",  // 请求的MIME类型为application/json
            "path": "your/request/path",  // 请求的路径，需要替换为实际路径
            "body": { "text": {{json message}} }  // 请求体，包含一个键为"text"的JSON对象，{{json message}}需要替换为实际消息内容
        }
    ]
}
```

此任务主体模板将向your/request/path端点发送一个 POST 请求，请求主体为{ text: <message> }，其中<message>是 Webhook 中的字符串输入参数。

#### 提取输出参数

有两种主要方法从 REST Webhook 中提取输出参数：1）通过名称捕获 JSON 响应中的顶级字段，2）定义 JSON 提取器以实现更自定义的提取逻辑，并明确列出您希望输出的字段。

您还可以选择将完整的响应 JSON 提取为字符串输出。这为在使用函数进行后续编辑或通知渲染时遍历响应提供了额外的灵活性。

REST 插件支持多种提取器类型，包括 JSON、XML、HTML、HTTP 状态等。Webhook 需要返回 JSON 的外部端点，因此在 webhook 任务配置中只能使用json提取器。

对于捕获顶级字段，假设您已经配置了一个 REST 调用，它返回以下响应：

```
Copied!1
2
3
{
    "id": "c52fd6e4-6eb5-4da1-8908-4845e51c801b" // 唯一标识符（UUID），用于唯一标识一个对象或实体
}
```

您可以在JSON响应中以相同的ID定义输出参数来捕获它们。在此示例中，您可以添加一个参数ID为id的字符串输出参数，此字段将从响应中捕获。

如果需要从响应中捕获嵌套字段，可以通过指定extractors来提取值。提取的值还可以在后续调用中用于链接调用。如果需要捕获完整响应，可以通过指定根路径为目标的extractors提取整个响应："result": "/"。

下面是一个任务体模板的示例，该模板进行两个请求：一个请求GET端点以检索一些数据，然后一个请求POST端点使用上一次调用的数据。

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
{
    "calls": [
        {
            "type": "magritte-rest-call",  // 表示这是一个REST API调用
            "method": "GET",  // 使用GET方法请求数据
            "path": "path/to/fetchData",  // 请求的路径
            "extractor": [
              {
                "type": "json",  // 指定返回数据的格式为JSON
                "assign": {
                  "request_output": "/json/path/to/output"  // 提取数据的JSON路径，并分配给变量request_output
                }
              }
            ]
        },
        {
            "type": "magritte-rest-call",  // 表示这是一个REST API调用
            "method": "POST",  // 使用POST方法发送数据
            "path": "your/request/path",  // 请求的路径
            "body": { "text": {%request_output%} },  // 请求体中包含上一步提取的request_output数据
            "extractor": [
              {
                "type": "json",  // 指定返回数据的格式为JSON
                "assign": {
                  "result": "/json/path/to/result"  // 提取数据的JSON路径，并分配给变量result
                }
              }
            ]
        }
    ],
    "output": ["result"]  // 最终输出的结果变量
}
```

第一次调用对path/to/fetchData的端点发起一个GET请求，然后从/json/path/to/output的 JSON 路径中提取数据到一个名为request_output的状态变量中。接着，request_output状态在第二次调用的主体中使用。从第二次调用中，我们从 JSON 响应中提取另一个字段到一个名为result的状态变量中。最后，配置中的"output"字段定义了哪些提取的字段应该作为输出参数返回。

#### 其他选项

除了指定calls和output，REST Webhook 任务还有一些额外的配置选项可用：

- 如果您在一个 REST Webhook 中进行多次调用，只允许一个调用使用不安全的 HTTP 方法。不安全的调用是指可能在外部系统中修改状态的调用。默认情况下，只有GET、OPTIONS和HEAD请求被视为安全。您可以通过在调用中指定"isHttpMethodSafe": true来覆盖不同类型调用的安全性（例如POST或PUT）。如果您在多次请求中，其中一个较早的请求是POST，并且您正在其后续请求中使用其响应，这可能很有用。
- 您可以指定一个retryable-status-codes数组，表示可以重试的 HTTP 状态码。例如，您可以配置 Webhook 在从服务器接收到 503 响应时重试外部请求。此选项默认为一个空列表。
- 例如，您可以配置 Webhook 在从服务器接收到 503 响应时重试外部请求。此选项默认为一个空列表。
- 您可以指定一个external-system-not-changed-status-codes数组，表示尽管请求失败，您连接的服务器并没有更改任何数据。此选项默认为从 400 到 431 的所有状态码。当 Webhook 执行并失败时，是否可能更改外部系统的指示被捕获，以支持调试写入失败。
- 此选项默认为从 400 到 431 的所有状态码。
- 当 Webhook 执行并失败时，是否可能更改外部系统的指示被捕获，以支持调试写入失败。
### Salesforce

我们建议使用 REST API 源来配置与 Salesforce 交互的 webhooks。下面描述的传统任务型 webhook 选项仅供历史参考。传统的 Salesforce 源应迁移以使用新的配置选项。

以下是 Salesforce webhooks 可用的任务类型：

- create-record-salesforce-webhook-task：创建给定类型的 Salesforce 记录。
- update-record-salesforce-webhook-task：更新给定类型的 Salesforce 记录。
- delete-record-salesforce-webhook-task：删除 Salesforce 记录。
- composite-salesforce-webhook-task：通过使用 Salesforce综合请求 ↗修改 Salesforce 记录。
以下是每种任务类型的任务主体示例。

#### create-record-salesforce-webhook-task

此任务类型对应于此 Salesforce API ↗。

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
  "record-type-name": "Account",
  "data": {
    "Name": {{json name}}, // 账户名称
    "Industry": {{json industry}}, // 行业
    "BillingCountry": {{json country}} // 账单国家
  }
}
```

#### update-record-salesforce-webhook-task

此任务类型对应于此 Salesforce API ↗。

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
  "record-type-name": "Account", // 记录类型名称为“Account”
  "record-id": {{json record-id}}, // 记录的唯一标识符
  "data": {
    "Name": {{json name}}, // 账户的名称
    "Industry": {{json industry}}, // 账户所属行业
    "BillingCountry": {{json country}} // 账户的账单国家
  }
}
```

#### delete-record-salesforce-webhook-task

此任务类型对应于此 Salesforce API ↗。

```
Copied!1
2
3
4
{
  "record-type-name": "Account", // 记录的类型名称为“Account”
  "record-id": {{json record-id}} // 记录的ID，使用模板中的“record-id”变量
}
```

#### composite-salesforce-webhook-task

关于collateSubrequests选项的信息，请参阅Salesforce 文档 ↗。

在下面的示例中，我们使用"@{createAccount.id}"来引用在第一个子请求中创建的记录的ID。了解更多关于依赖请求的信息，请参阅Salesforce 文档 ↗。

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
{
  "request": {
    "collateSubrequests": true, // 设置为true表示合并子请求，以便在一个请求中处理多个操作
    "compositeRequest": {
      "createAccount": {
        "type": "createRecord", // 指定操作类型为创建记录
        "createRecord": {
          "recordTypeName": "Account", // 要创建的记录类型是“Account”
          "data": {
            "Name": {{json name}} // 使用模板插值方式插入账户名称
          }
        }
      },
      "updateId": {
        "type": "updateRecord", // 指定操作类型为更新记录
        "updateRecord": {
          "recordTypeName": "Account", // 要更新的记录类型是“Account”
          "data": {
            "Industry": {{json industry}} // 使用模板插值方式插入行业信息
          },
          "recordId": "@{createAccount.id}" // 指定要更新的记录ID，从之前创建的账户获取ID
        }
      }
    }
  }
}
```

此JSON结构体定义了一个复合请求，包含两个子请求：一个用于创建“Account”记录，另一个用于更新刚创建的“Account”记录的“Industry”字段。使用模板插值方式填充名称和行业字段，确保动态插入数据。

### SAP

SAP插件允许您连接到企业SAP环境并调用业务API ↗(BAPIs)以修改SAP业务对象。设置SAP源后，您可以创建调用特定BAPI的SAP Webhook。

目前，SAP插件中唯一可用的任务类型是sap-run-function-webhook-task-v0。以下是该任务类型的任务主体示例。

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
{
    "function-name": "BAPI_SALESORDER_CHANGE",  // 函数名：用于更改销售订单的BAPI函数
    "inputs": {
        "SALESDOCUMENT": {{json sales-doc-id}},  // 销售订单ID
        "ORDER_HEADER_IN": {
            "PURCH_DATE":  {{json purchase-date}}  // 采购日期
        },
        "ORDER_HEADER_INX": {
            "UPDATEFLAG": "U",  // 更新标志：U表示更新
            "PURCH_DATE": "X"   // 指定采购日期字段需要更新
        }
    },
    "output": "RETURN",  // 返回值
    "remote": {
      "context": SAP_CONTEXT_NAME (Optional)  // 远程调用的上下文名称（可选）
    }
}
```

上面的任务调用了一个名为BAPI_SALESORDER_CHANGE的BAPI，它用于修改给定销售文件的购买日期。您还可以选择为Webhook指定一个SAP上下文。

## 限制

对于每个Webhook，您可以设置三种类型的限制来约束Webhook的执行方式：时间限制、并发限制和速率限制。

时间限制允许您设置Webhook应执行的最长时间。这使您能够确保最终用户应用程序保持响应状态，并在连接的外部系统响应过慢时显示超时错误。如果未提供值，默认超时时间为20秒。允许的最大超时时间为180秒。

并发限制指定同时运行的Webhook执行的最大数量。这可以避免向外部系统发送过多的并发请求。

速率限制限制在您指定的时间窗口内Webhook可以执行的次数。如果您希望确保Webhook在每秒、每分钟、每小时或每天仅执行特定次数，可以启用这种类型的限制。

## 权限

创建、配置和删除webhooks的权限来自于关联的源的权限。

了解更多关于数据连接权限的信息，并查看更多关于Webhook权限的详细信息。

## Webhook历史记录

Webhook历史记录显示了webhooks被触发的时间线。历史记录元数据将始终包括触发Webhook的用户ID、时间戳以及执行的成功或失败状态，如下所示：

默认情况下，传递给Webhook的输入和完整响应仅对调用Webhook的用户可见。这保护了Webhook调用中传入或返回的任何敏感数据。webhooks:read-privileged-data权限将允许访问完整历史记录，默认情况下不授予任何用户此权限。需要一个具有此权限的自定义角色才能访问Webhook的完整历史记录。

## 其他选项

### 存储响应

默认情况下，Webhook响应将被存储并在历史视图中显示六个月。完整响应仅对执行Webhook的用户和任何具有webhooks:read-privileged-data权限的管理员可见。

对于已知返回不应存储在Webhook历史记录中的敏感信息的Webhook，可以完全禁用此选项。

## 使用OAuth 2.0的Webhooks

### 授权码授权

Palantir Webhooks支持使用OAuth 2.0授权码授权流程调用端点。这需要使用一个出站应用程序来定义与OAuth 2.0服务器的交互。一旦配置完成，出站应用程序可以用作REST API Webhook的认证，并会在尝试执行Webhook时提示用户与OAuth服务器进行身份验证。

### 客户端凭证授权

Webhooks可以用于执行使用客户端凭证的OAuth流程。客户端凭证授权流程通常使用一个长期有效的密钥来检索一个短期有效的访问令牌，该令牌可以用于对目标系统执行操作。REST API Webhooks支持连续执行多个API调用，可以用于执行客户端凭证握手，然后作为单个执行发送所需请求。

以下演练解释了如何针对假想的示例系统配置客户端凭证授权流程。

要继续，您需要以下信息：

- OAuth 2.0服务器域和词元端点的路径。词元端点用于检索用于向资源域发出请求的有效词元。在许多情况下，OAuth 2.0服务器域和资源域是相同的。例如，当使用第三方应用程序进行身份验证时，这是Foundry API的情况。
- 在许多情况下，OAuth 2.0服务器域和资源域是相同的。例如，当使用第三方应用程序进行身份验证时，这是Foundry API的情况。
- 您希望使用Authorization标头中包含从OAuth 2.0服务器检索到的持票词元调用的资源域和所需端点的路径。
- OAuth 2.0服务器的客户ID。
- OAuth 2.0服务器的客户密钥。
并非所有OAuth 2.0服务器都严格遵循OAuth 2.0标准。Webhooks请求生成器接口旨在足够灵活以适应您可能需要进行的任何非标准配置以成功进行身份验证。我们建议在尝试遵循本教程之前，查看您要连接的系统的文档。

#### 创建REST API源

首先，选择在数据连接应用程序中创建一个**+ 新建源**，并选择REST API作为源类型。了解更多关于REST API源类型的信息。

配置源时，添加如下面所示的OAuth 2.0服务器域和资源域。不要选择任何身份验证选项，因为我们将在Webhook调用的序列中手动执行OAuth 2.0握手。

在附加密钥部分，添加一个新密钥，并输入在向词元端点发出请求时将包含的ClientSecret。我们将在构建Webhook调用时引用此值；当在此处输入时，ClientSecret将被加密，即使对于Foundry中的其他编辑者或源的所有者也不会暴露。

#### 构建执行客户端凭证握手的Webhook

源创建完成后，选择创建新Webhook的选项。

Webhook将由两个链式调用组成：

- 初始调用词元端点以检索有效的持票词元
- 后续调用，包括在对资源域上的所需端点的请求中解析的持票词元。
下面显示了如何配置第一次调用的示例：

在对词元端点的调用中显示的参数是许多使用OAuth 2.0的系统的标准参数。然而，字段名称可能会有所不同，可能还需要其他字段。请查阅您要连接的系统的文档，并构建与该系统提供的词元端点兼容的请求。

通常，请求类型需要为POST，默认为"写API"调用。事实上，通常可以安全地对词元端点进行重复调用，您可以使用配置块右侧的下拉选择器将此调用标记为“读API”调用。一般来说，不允许Webhooks执行多次写API调用，因为不能保证多个请求之间的事务性。

在第二次调用中，使用可用的配置选项构建所需请求。要将持票词元注入授权标头，请转到调用配置的标头部分，并如下面的示例中所示添加一个标头。您可以使用@引用来自前一次调用的值。大多数OAuth 2.0服务器将返回一个名为access_token或类似的JSON参数。选择添加值来自调用的选项，然后选择按键提取并输入您希望从第一次调用的响应中提取的键的值。

下面的截图显示了如何从第一次调用中选择持票词元的示例：

配置完成后，包含两个链式调用的完整Webhook应类似于此示例：

最后，我们强烈建议禁用存储Webhook第一次调用的完整响应。如果存储了响应，则包含在其中的持票词元可能对具有查看完整Webhook历史记录权限的其他用户可见。通常会在Webhook配置的存储和保留页面上自动弹出提示，以禁用对词元端点请求存储历史记录，如下所示：
