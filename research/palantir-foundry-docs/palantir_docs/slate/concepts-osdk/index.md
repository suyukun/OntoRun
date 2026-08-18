来源: https://palantir.com/docs/zh/foundry/slate/concepts-osdk/

# 在 Slate 中使用 Ontology SDK (OSDK)

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 在 Slate 中使用 Ontology SDK (OSDK)

Slate 中的 OSDK 处于 Beta 状态，在产品正式发布之前，某些功能可能会更改。Slate 中的 OSDK 可能并不适用于所有注册。

Ontology 软件开发工具包 (OSDK) 允许搭建者在 Slate 代码环境中充分利用 Ontology 的强大功能。OSDK 可以在函数编辑器选项卡中作为库访问。

## 起始步骤

- 导航到函数编辑器。您将在左下角面板找到库。
- 选择 Ontology SDK (OSDK) 以查看详细配置选项。
- 首先，选择您想访问的 Ontology。请注意，根据您的平台设置或权限，您可能只有一个 Ontology。
- 选择您希望引入到 Slate 应用中的 Object 类型、链接类型和操作。
- 点击+ 开始以打开一个新函数，其中将包含访问所选 Object 类型的代码片段。
### 在 Slate 函数中使用 OSDK

函数编辑器是您可以通过 OSDK 访问和变换数据的地方。使用以下代码片段导入您想要使用的 Object 类型：

```
Copied!1
import {client} from "@slate/osdk"; // 从 @slate/osdk 模块中导入客户端对象
```

示例JavaScript代码演示如何在Slate函数中使用OSDK为表格微件获取10个Objects：

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
import { client } from "@slate/osdk";

// 使用异步函数从 F1Driver 本体对象中获取一个页面的数据，页面大小为 10
const driverResponse = await client.ontology.objects.F1Driver.fetchPage({ pageSize: 10 });

// 如果返回类型是错误，返回一个空的 driverNames 和 driverIds 数组
if (driverResponse.type === "error") {
  return {
    driverNames: [],
    driverIds: [],
  };
}

// 从响应数据中提取每个车手的名字和姓氏，组合成一个完整的名字数组
const driverNames = driverResponse.data.map(driver => `${driver.forename} ${driver.surname}`);

// 从响应数据中提取每个车手的 ID
const driverIds = driverResponse.data.map(driver => driver.driverId);

// 返回包含车手名字和车手 ID 的对象
return {
  driverNames,
  driverIds,
};
```
