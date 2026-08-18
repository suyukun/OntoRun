来源: https://palantir.com/docs/zh/foundry/ontology-sdk/typescript-osdk-migration/

# TypeScript OSDK 迁移指南（1.x 到 2.0）

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# TypeScript OSDK 迁移指南（1.x 到 2.0）

本指南旨在帮助您将使用 TypeScript OSDK 1.x 的应用迁移到 TypeScript OSDK 2.0。以下部分解释了两个版本之间的区别，并突出显示了语法和结构的相关更改。

TypeScript 文档也可以在平台内的 Developer Console 中找到，路径为/workspace/developer-console/。使用版本选择器选择2.0以获取有关 TypeScript OSDK 2.0 的文档。

## 为什么从 TypeScript OSDK 1.x 升级到 2.0？

### 性能和可扩展性

TypeScript OSDK 1.x 使用户能够在 Palantir 平台之外与 Ontology 进行交互。然而，该初始版本的可扩展性有限：

- TypeScript OSDK 1.x 为任何对象、操作或其他 Ontology 项目生成完整的代码实现。这意味着 OSDK 1.x 的扩展与您整个 Ontology 的大小相关，可能非常大。
- TypeScript OSDK 1.x 紧密耦合客户端与生成的 Ontology。
TypeScript OSDK 2.0 通过全面改进 SDK 的生成方式和 Ontology 的访问方式，提供了许多性能和可用性改进。

- TypeScript OSDK 2.0 按照 Ontology 的形状和元数据线性扩展，而不是实际 Ontology。这显著提高了 OSDK 的性能，因为 OSDK 不再与 Ontology 中的所有项目相关联。TypeScript OSDK 2.0 还支持延迟加载，这意味着应用只需要在使用时加载所需内容。
- TypeScript OSDK 2.0 将客户端与生成的代码分离，这使得通过更快的库依赖更新来部署快速热修复变得更容易，而无需重新生成 SDK。TypeScript OSDK 2.0 还通过 OSDK 代码库显著提高了代码重用的功能。
- TypeScript OSDK 2.0 提供了精简的代码生成，这可以显著提高构建大型 Ontology 时的迭代速度。
有关两个版本之间主要设计差异及其背后原理的更多详细信息，请查看开源 TypeScript OSDK 存储库中的开发者文档。

### 支持和功能

新的 TypeScript 版本的 OSDK 增强了与 Ontology 的交互功能。由于此原因，新功能的发布，如接口和媒体集将需要 TypeScript OSDK 2.0。

Palantir 将在 TypeScript OSDK 2.0 发布后至少一年内维护对 TypeScript 1.x 版本 OSDK 的支持。

## 如何从 TypeScript OSDK 1.x 升级到 2.0？

您可以在应用的SDK 版本选项卡中使用 TypeScript OSDK 2.0 生成器为现有的 Developer Console 应用生成新的 SDK 版本。现有应用还必须具备所需的依赖项以使用新生成的 SDK。在 Developer Console 中创建的新应用将默认使用 TypeScript OSDK 2.0 生成器生成 SDK，开发人员可以通过开始开发选项卡中的说明快速入门。

## 从 TypeScript OSDK 1.x 迁移到 2.0

- 确保您已在项目中安装所有新要求的依赖项。
- 实例化一个新的 TypeScript OSDK 2.0 客户端。
- 修改项目的查询调用，重点是更新调用的语法和根据需要调整返回类型的处理。
- 修改项目的操作调用。除了语法外，这里的主要变化是更新可能查看验证或操作编辑响应的代码。
- 迁移对象类型。彻底审查 OSDK 对象类型在代码中的使用方式。确定您依赖于 OSDK 1.x 版本生成的对象类型的位置，并了解它们与 2.0 版本使用的类型的差异。为您的代码库决定一个最佳解决方案路径。接下来，审查您的 OSDK 使用情况并修改对象加载以使用新客户端。按照对象语法翻译部分中的步骤操作，并注意属性类型的任何变化。
- 彻底审查 OSDK 对象类型在代码中的使用方式。确定您依赖于 OSDK 1.x 版本生成的对象类型的位置，并了解它们与 2.0 版本使用的类型的差异。为您的代码库决定一个最佳解决方案路径。
- 确定您依赖于 OSDK 1.x 版本生成的对象类型的位置，并了解它们与 2.0 版本使用的类型的差异。
- 为您的代码库决定一个最佳解决方案路径。
- 接下来，审查您的 OSDK 使用情况并修改对象加载以使用新客户端。按照对象语法翻译部分中的步骤操作，并注意属性类型的任何变化。
- 查看 OSDK 两个版本之间的其他差异。
## 初始设置

从 npm 安装最新版本的@osdk/client包，或相应地更新项目的package-lock.json。

```
Copied!1
2
npm install @osdk/client
npm install @osdk/oauth
```

以上命令用于安装两个 npm 包：

- @osdk/client：这是一个客户端库，可能用于与某个服务进行通信。
- @osdk/oauth：这是一个 OAuth 相关的库，可能用于处理身份验证和授权。
通过运行这些命令，您将把这些包安装到您的 Node.js 项目中。

## 客户端/认证

### 创建

在 TypeScript OSDK 2.0 中，客户端是通过createClient函数创建的。此函数需要一个名为ontologyRid的附加参数。ontologyRid参数可以作为字符串传递，可以从环境变量中读取，或者可以动态地从在您的SDK包中生成的新变量$ontologyRid中读取。

#### TypeScript OSDK 1.x（旧版）

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
import { FoundryClient, PublicClientAuth } from "@your-generated-sdk";

// 使用公共 OAuth 进行身份验证
const auth = new PublicClientAuth({
        clientId: FOUNDRY_CLIENT_ID, // 客户端 ID
        url: FOUNDRY_API_URL, // Foundry API 的 URL
        redirectUrl: APPLICATION_REDIRECT_URL, // 应用程序的重定向 URL
    });

// 创建一个 FoundryClient 实例
const legacyClient = new FoundryClient({
    url: API_PROXY_TARGET_URL, // API 代理目标的 URL
    auth: auth, // 使用前面定义的身份验证对象
});
```

#### TypeScript OSDK 2.0

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
import { createClient } from "@osdk/client";
import {
    PublicOauthClient,
    createConfidentialOauthClient,
    createPublicOauthClient
} from "@osdk/oauth";
import { $ontologyRid } from "@your-generated-sdk";

// 机密的 OAuth 客户端
const auth = createConfidentialOauthClient(
    FOUNDRY_CLIENT_ID, // Foundry 客户端 ID
    FOUNDRY_CLIENT_SECRET, // Foundry 客户端密钥
    FOUNDRY_URL, // Foundry URL
);

// 或者使用公共 OAuth 客户端

// 公共 OAuth 客户端
const auth = createPublicOauthClient(
    FOUNDRY_CLIENT_ID, // Foundry 客户端 ID
    FOUNDRY_API_URL, // Foundry API 的 URL
    APPLICATION_REDIRECT_URL // 应用程序重定向 URL
);

const client = createClient(
    FoundryApiUrl, // Foundry API 的 URL
    $ontologyRid, // 请参阅备注
    auth // OAuth 客户端
);
```

备注:$ontologyRid是通过 SDK 生成的标识符，用于与特定的本体论相关联。

如果您通过CLI安装Ontology的OSDK，您的$ontologyRid将从SDK包的根目录导出，您可以像上面那样访问。否则，您需要在构建客户端时传入已知的ontologyRid。您可以从Foundry中的Ontology管理器获取此信息。选择您想要的Ontology，导航到Ontology配置标签，然后从Ontology元数据部分复制您的Ontology RID。

### 使用和一般语法

#### TypeScript OSDK 1.x（遗留版）

在TypeScript OSDK 1.x中，您可以通过嵌套对象结构访问客户端上的方法。例如：

```
Copied!1
2
// 调用 legacyClient 对象中的 legacyObject 的 fetchPage 方法
legacyClient.objects.legacyObject.fetchPage();
```

#### TypeScript OSDK 2.0

在 TypeScript OSDK 2.0 中，客户端现在可以直接调用。这意味着您可以与客户端进行接口交互，传递您想要使用的对象或操作。新的使用模式通常遵循以下语法：

```
// 调用 `client` 对象的方法 `fetchPage()`，传入参数 `myObject`
client(myObject).fetchPage()

// 调用 `client` 对象的方法 `fetchPage()`，传入参数 `Objects.myObject`
// 注意：这里的 `$Objects` 可能是一个全局对象或框架特定的对象集合
client($Objects.myObject).fetchPage()
```

## 对象

TypeScript 版本 1.x 和版本 2.0 中对象类型的主要区别在于用于访问对象数据的不同类型。在 1.x 版本中，您可以通过接口myObject类型来访问对象的属性。然而，在 2.0 版本中，与传统对象类型类似的功能存在于包装类型：Osdk.Instance<myObject>中。

这反映在整个 SDK 的方法返回类型中。例如，TypeScript OSDK 1.x 的页面结果类型是Page<myObject>，而 TypeScript OSDK 2.0 的页面结果类型是PageResult<Osdk.Instance<myObject>>。

这可能会在转换代码时造成几个不同的兼容性问题。

#### 问题：Osdk.Instance<myObject>不等于legacyMyObject

两个对象的属性发生了重大变化。

- TypeScript OSDK 1.x 使用GeoShape, GeoPoint，而 TypeScript OSDK 2.0 使用GeoJSON
- TypeScript OSDK 1.x 使用Timestamp, LocalDate，而 TypeScript OSDK 2.0 将这些类型视为字符串
假设您希望用新的客户端替换您的对象加载调用，但不想更改任何期望来自传统 TypeScript OSDK 1.x 的对象类型的辅助函数。假设您仍在从传统 TypeScript OSDK 1.x 导入对象类型，在这种情况下，您将遇到由于两种类型不兼容而导致的出错。

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
const objectResult: Result<legacyMyObject, GetObjectError> =
    await legacyClient.ontology.
    objects.legacyMyObject.fetchOne("<primaryKey");

// 使用新的客户端 API 获取对象实例
const object = client(myObject).fetchOne("<primaryKey>");
   -> Returns Osdk.Instance<myObjectV2>

// 获取对象的位置信息
const locationName = getObjectLocation(object)

// 该函数用于获取旧版对象的位置信息，保持不变
function getLocation(obj: legacyMyObject){...} : Unmodified
```

这是因为Osdk.Instance<myObjectV2>与legacyMyObject不兼容。

#### 问题: ObjectType ≠ Osdk.Instance

在TypeScript OSDK 2.0中，将对象类型包装在Osdk.Instance<>中对于访问各种属性至关重要。Osdk包装器将这些属性提升到类型的顶层，使其更类似于TypeScript OSDK 1.x中的旧类型。

然而，如果您将对象类型导入更改为来自TypeScript OSDK 2.0，将会出现问题。没有Osdk包装器，您将无法在顶层访问对象属性，并且导入将缺少上述其他字段。

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
const object = client(myObjectV2).fetchOne("<primaryKey>");
// 通过主键从客户端获取一个myObjectV2对象实例
// 返回类型为Osdk.Instance<myObjectV2>

const locationName = getObjectLocation(object);
// 获取对象的位置名称

function getLocation(obj: myObjectV2){ ... }
// 定义一个函数getLocation，该函数用于处理myObjectV2类型的对象
```

这是因为Osdk.Instance<myObjectV2>与myObjectV2不兼容。

#### 解决方案路径

考虑以下方法来编辑您的代码，以在TypeScript OSDK 2.0中使用新的OSDK对象类型：

- 直接替换：在修改对象检索时，将代码库中所有旧对象类型的实例替换为相应的TypeScript OSDK 2.0对象类型。对于简单的应用案例来说，这是最优的，但对于大量使用TypeScript OSDK 1.x对象类型的代码库来说，这具有挑战性。
- 自定义前端类型：在将对象迁移到TypeScript OSDK 2.0之前，重构您的代码以使用自定义前端类型，而不是内置的旧TypeScript OSDK 1.x类型。然后，开发一个转换函数，将旧的TypeScript OSDK 1.x类型映射到您的自定义类型。当您开始迁移到TypeScript OSDK 2.0时，您只需更新转换函数，其余代码库保持不变。
### 语法转换

本节包含简单示例，说明如何在TypeScript OSDK 1.x和2.0客户端之间进行映射。有关更复杂的TypeScript OSDK 2.0语法示例，请参阅Palantir公开GitHub库上的OSDK示例 ↗。

### 加载单个对象

#### TypeScript OSDK 1.x（旧版）

```
Copied!1
2
3
4
5
const objectResult: Result<legacyObject, GetObjectError> =
    await legacyClient.ontology.objects.legacyObject.fetchOneWithErrors("<primaryKey>");
// objectResult 是一个类型为 Result<legacyObject, GetObjectError> 的常量
// 通过调用 legacyClient.ontology.objects.legacyObject.fetchOneWithErrors("<primaryKey>")
// 方法来获取指定主键的对象，同时可能会返回错误
```

#### TypeScript OSDK 2.0

```
Copied!1
2
3
4
5
6
const objectResult: Result<Osdk.Instance<myObject>> =
    await client(myObject).fetchOneWithErrors("<primaryKey>");

// 上述代码定义了一个常量 objectResult，其类型为 Result<Osdk.Instance<myObject>>。
// 使用了 await 来异步调用 client(myObject).fetchOneWithErrors("<primaryKey>") 方法。
// 该方法的作用是根据 "<primaryKey>" 从 myObject 中获取一个实例，并且在获取过程中可能会产生错误。
```

您也可以使用fetchOne方法以不使用结果包装器的方式返回对象。

### 加载具有分页功能的对象

#### TypeScript OSDK 1.x（旧版）

```
Copied!1
2
3
const objectResult =
    await legacyClient.ontology.objects.legacyObject.fetchPage({ pageSize: 30 });
// 通过异步调用获取页面数据，pageSize参数设置每页包含30个对象
```

```
Copied!1
2
3
4
5
const objectResult = await client(myObject).fetchPage({ $pageSize: 30 });
// 使用 fetchPage 方法从 client 中获取分页数据，分页大小设置为 30

const object = objectResult.data[0];
// 从获取的数据中提取第一个对象
```

### 加载所有对象

#### TypeScript OSDK 1.x（旧版）

```
// 定义一个空数组 `objects`，类型为 `legacyObject`，用于存储异步迭代获取的对象
const objects: legacyObject[]= [];

// 使用 `for await` 循环异步迭代从 `client.ontology.objects.legacyObject.asyncIter()` 获取的对象
for await (const obj of client.ontology.objects.legacyObject.asyncIter()) {
    // 将每个获取的对象 `obj` 推入数组 `objects` 中
    objects.push(obj);
}

// 尝试访问 `objects` 数组的 `value` 属性的第一个元素
const object = objects.value[0];
```

注意：最后一行代码可能存在问题，因为objects是一个数组，数组没有value属性，应该直接访问数组的第一个元素objects[0]。

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
const objects: myObject[]= [];

// 异步迭代client(myObject).asyncIter()返回的对象
for await(const obj of client(myObject).asyncIter()) {
    objects.push(obj); // 将每个对象推入objects数组中
}

// 试图访问objects数组的value属性的第一个元素，但这可能会导致错误，
// 因为objects没有value属性，可能需要确认意图或修正代码。
const object = objects.value[0];
```

### 链接

#### TypeScript OSDK 1.x（旧版）

```
Copied!1
2
3
4
5
const object = ...load ontology object with legacy client
// 使用旧版客户端加载本体对象

const link = object.legacyObjectProperty.fetchPage({ pageSize: 100 });
// 从旧版对象属性中获取分页数据，每页大小为100
```

```
Copied!1
2
3
4
5
const object = ...load ontology object with new client
// 使用新客户端加载本体对象

const link = object.$link.myObjectProperty.fetchPage({ $pageSize: 100 });
// 从对象的链接中获取分页数据，每页大小为100
```

### 筛选

#### WHERE子句

##### TypeScript OSDK 1.x（旧版）**

```
Copied!1
2
3
legacyClient.ontology.objects.legacyObject
    .where(query => query.legacyProperty.startsWith("foo"))...
    // 过滤条件：选择所有legacyProperty以"foo"开头的对象
```

##### TypeScript OSDK 2.0

```
Copied!1
2
3
4
client(myObject).where({
        // 筛选myObject的属性myObjectProperty以"foo"开头的对象
        myObjectProperty: { $startsWith: "foo" }
    })...
```

#### orderBy子句

排序子句现在是在传递给fetchPage的对象中指定的，而不是单独的筛选子句。

##### TypeScript OSDK 1.x (旧版)

```
Copied!1
2
3
client.ontology.objects.legacyObject
    .orderBy(sortBy => sortBy.OntologyProperty.asc())  // 按照OntologyProperty属性进行升序排序
    .fetchPageWithErrors({ pageSize: 30 });            // 获取每页30个对象并处理可能的错误
```

```
Copied!1
2
3
4
client(myObject).fetchPage({
    $orderBy: { "OntologyProperty": "asc" } // 按照 "OntologyProperty" 属性升序排序
    $pageSize: 30 // 每页返回30个结果
});
```

### 聚合

TypeScript OSDK 2.0语法允许您传入一个参数以确定聚合的排序方式。这使您能够在指定groupBy聚合时控制结果返回的顺序。可用的选项有unordered（无序）、asc（升序）和desc（降序）。

#### 返回对象的计数

##### TypeScript OSDK 1.x（遗留）

```
Copied!1
2
3
4
5
6
7
8
const aggResults = legacyClient.ontology.objects.legacyObject.where(...).count().compute();
// 使用 legacyClient 从本体对象中进行计数计算

if (isOk(aggResults)) {
    // 检查 aggResults 是否成功
    const count: number = aggResults.value;
    // 如果成功，提取计数结果
}
```

```
Copied!1
2
3
4
const aggResults = client(myObject).where(...).aggregate({
    select: { $count: "unordered" } // 使用聚合函数计数，结果存储在"unordered"字段中
    })
const count: number = aggResults.$count; // 从聚合结果中提取计数值
```

#### 分组 (groupBy)

##### TypeScript OSDK 1.x（旧版）

```
// 对 legacyObject 进行分组和计数操作

legacyClient.ontology.objects.legacyObject.where(...)
    .groupBy(legacyObject => legacyObject.imageId.exact) // 首先根据 imageId 进行分组
    .groupBy(legacyObject => legacyObject.objectLabel.exact) // 然后根据 objectLabel 进行分组
    .count() // 统计每个分组中的对象数量
    .compute(); // 计算结果
```

```
// 该代码段是一个数据库查询操作，使用了类似于MongoDB的聚合框架。
// 目标是对数据进行统计和分组。

client(myObject).where(...)
    .aggregate({
        $select: { $count: "unordered" }, // 选择查询的结果以计数的方式展示，"unordered"表示不关心顺序。
        $groupBy: {
            imageId: "exact",   // 按照imageId进行精确分组。
            objectLabel: "exact" // 按照objectLabel进行精确分组。
        }
    });
```

### 常见聚合

#### TypeScript OSDK 1.x（旧版）

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
const aggResults = legacyClient.ontology.objects.legacyObject
    .aggregate(obj => ({
        legacyObject: obj.createdBy.approximateDistinct(),  // 对象的创建者进行近似去重
    }))
    .compute();

//OR

const aggResults = legacyClient.ontology.objects.legacyObject
 .approximateDistinct((obj) => obj.legacyProperty) // 对象的某个属性进行近似去重
 .count() // 计算去重后的数量
 .compute();

if (isOk(aggResults)) { // 检查聚合结果是否成功
    const result = aggregationResults.value; // 提取聚合结果的值
}
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
const aggregationResults = client(myObject)
    .aggregate({
        // 使用 $select 操作符来指定需要的聚合操作
        $select: { "ObjectProperty:approximateDistinct": "unordered" },
    });

// 获取聚合结果中的 ObjectProperty 属性
const result = aggregationResults.ObjectProperty;
```

## 操作

### 简单操作

TypeScript OSDK 2.0 应用简单操作的语法与旧版 TypeScript OSDK 1.x 的语法非常相似：在这两者中，您都调用applyAction函数。

#### TypeScript OSDK 1.x（旧版）

```
// 使用 legacyClient 创建一个新的对象
await legacyClient.ontology.actions.createObject({ ...params });
```

```
Copied!1
2
3
await client(createObject).applyAction({ ...params });
// 使用 `await` 等待 `client(createObject)` 的异步操作完成，并调用 `applyAction` 方法。
// `applyAction` 方法接收一个对象作为参数，该对象通过扩展运算符 `...` 展开 `params` 对象中的所有属性。
```

### 批量操作

批量操作将需要与简单操作类似的语法更改。

#### TypeScript OSDK 1.x（旧版）

```
Copied!1
2
3
await legacyClient.ontology.batchActions.createObject({ ...params });
// 使用解构语法将参数传递给createObject方法，以创建一个新的对象。
// 这里的legacyClient可能是一个旧版本的客户端实例，ontology是其属性，batchActions是一个批量操作的对象。
```

```
Copied!1
2
// 使用客户端异步调用createObject，并对参数进行批量操作
await client(createObject).batchApplyAction({ ...params });
```

### 操作验证与编辑

如果您在OSDK 1.x中验证输入或接收ActionEdits，现在可以通过在Options对象中指定$returnEdits和$validateOnly属性来定义这些操作。无法同时返回编辑和仅验证。

#### TypeScript OSDK 1.x（遗留）

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
await legacyClient.ontology.actions.`createObject`({ ...params },
    { mode: ActionExcecutionMode.VALIDATE_AND_EXECUTE,
    returnEdits: ReturnEditsMode.ALL });

// 执行创建对象操作，并同时进行验证。
// 使用 ActionExcecutionMode.VALIDATE_AND_EXECUTE 模式进行验证和执行。
// returnEdits: ReturnEditsMode.ALL 表示返回所有编辑。

// If you only want to validate
await legacyClient.ontology.actions.createObject({ ...params },
    { mode: ActionExcecutionMode.VALIDATE_ONLY });

// 如果只想进行验证
// 使用 ActionExcecutionMode.VALIDATE_ONLY 模式只进行验证，不执行创建对象操作。
```

```
// 这个调用会在验证错误时抛出异常
await client(createObject).applyAction({ ...params }, { $returnEdits: true });

// 这个调用只进行验证，不执行实际操作
await client(createObject).applyAction({ ...params }, { $validateOnly: true });
```

## 查询

TypeScript OSDK 1.x 到 2.0 查询语法的更改与操作的更改非常相似。在 TypeScript OSDK 2.0 中，您可以在传入要执行的查询后，在客户端上调用executeFunction对象。

#### TypeScript OSDK 1.x (遗留)

```
await legacyClient.queries.legacyQuery({ ...params });
// 使用await关键字调用legacyClient对象的queries方法中的legacyQuery方法，并传入展开的参数对象
```

```
// 使用客户端异步执行函数
await client(exampleQuery).executeFunction({ ...params });
```

## 其他差异

### DateTime处理

1.x版本的TypeScript OSDK提供了自定义类型以处理日期和时间，例如LocalDate和Timestamp。TypeScript OSDK 2.0并未为DateTime提供具体类型。相反，在OSDK中返回和接受DateTime值的操作中，我们使用国际标准ISO 8601 ↗的原始字符串。

OSDK在使用DateTime属性时需要正确格式化的ISO 8601字符串。例如，当使用where子句筛选对象集时，您必须提供正确格式的字符串：

```
Copied!1
2
3
4
5
6
client(myObject).where({
    "dateTimeProperty": {
        // 查询 dateTimeProperty 大于 2010年10月1日的对象
        "$gt": "2010-10-01T00:00:00Z",
    }
});
```

来自各种OSDK方法的DateTime值也将以这种格式返回。例如，当加载对象时，对象上的DateTime属性将以日期时间字符串返回。

### 常用工具

#### OntologyObject

在TypeScript OSDK V2中不存在OntologyObject类型。一个在上下文中等效的类型是在@osdk/api包中找到的OsdkBase类型。

#### IsOntologyObject

在TypeScript OSDK V2中不存在IsOntologyObject。
