来源: https://palantir.com/docs/zh/foundry/ontology-sdk/how-to-bootstrapping-server-side-typescript/

# 使用服务用户启动新的 Ontology SDK TypeScript 应用程序

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 使用服务用户启动新的 Ontology SDK TypeScript 应用程序

如权限类型部分所述，Ontology SDK 可以被用于在基于服务用户权限而非最终用户权限的基础上查询数据。以下演练展示了如何使用Next.js© ↗（外部链接）通过 Ontology SDK 和服务用户获取数据。

在开发使用机密客户端的服务或应用程序时，将会在您的 Developer Console 应用程序中创建一个服务用户。如果您计划使用属于与默认组织不同的组织的 Ontology 创建应用程序，您必须完成共享和启用应用程序的步骤。

## 1. 使用 Developer Console 创建 Ontology SDK 包

在您的 Foundry 实例中导航到 Developer Console，然后选择+ 新应用程序。

如果未出现+ 新应用程序按钮，则您可能没有正确的权限。查看权限文档以获取更多信息。

按照创建向导中的步骤操作，并添加以下详细信息：

- 在应用程序类型页面上，选择后端服务。
- 在权限页面上，选择应用程序的权限。
Developer Console 将根据应用程序名称为此应用程序创建一个服务用户。在上述示例中，生成的服务用户名称为Ontology SDK application using service user。除了任何操作类型的提交标准外，您必须授予此服务用户读取您将在下一步骤中选择的对象类型的数据所需的权限。

- 在Ontology 和资源范围页面上，选择是，生成一个 Ontology SDK。
- 选择要使用的 Ontology。然后，选择您希望 Ontology SDK 包包含的对象类型和操作类型。对于本次练习，选择任何可用的对象类型。
检查并确认您输入的信息，然后选择创建应用程序以查看新应用程序的客户端密钥。复制并安全地存储该密钥，因为这是唯一可见的时间。

如果您丢失了客户端密钥，您可以在权限和 OAuth页面上进行旋转并获得新密钥。请记住，这将破坏使用该服务用户和密钥的现有应用程序。

最后，选择生成第一个版本以使用您新创建的 Ontology SDK。

## 2. 安装生成的 SDK 包

一旦 Ontology SDK 的生成完成，您将看到一组安装步骤以指导您在代码项目中安装生成的 SDK。

## 3. 在您的代码项目中使用 Ontology SDK

在本次演练中，我们使用Next.js© ↗。Next.js 支持在服务器端渲染代码，这对于我们的服务用户示例是必需的。要启动一个新的 Next.js 项目，请遵循Next.js© 文档 ↗。

### 客户端和 OAuth 创建

服务用户身份验证是通过机密 OAuth 客户端完成的，该客户端允许您使用客户端密钥访问 Ontology，而无需用户身份验证。

创建一个名为client.ts的文件并输入以下代码：

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
import { createConfidentialOauthClient } from "@osdk/oauth";
import { createClient } from "@osdk/client";

// 创建一个机密的OAuth客户端
export const auth = createConfidentialOauthClient(
    process.env.CLIENT_ID!, // 从环境变量中获取客户端ID
    process.env.CLIENT_SECRET!, // 从环境变量中获取客户端密钥
    process.env.STACK_URL!, // 从环境变量中获取栈的URL
);

// 创建一个客户端实例
export const client = createClient(
    process.env.STACK_URL!, // 从环境变量中获取栈的URL
    <ONTOLOGY-RID>, // 这里需要提供一个本体资源标识符（RID）
    auth // 使用上面创建的OAuth认证客户端
)
```

创建一个.env文件，并使用相同的变量。不要将此文件提交到代码仓库中。

```
Copied!1
2
3
CLIENT_ID=<YOUR CLIENT ID> # 替换为您的客户端 ID
CLIENT_SECRET=<YOUR CLIENT SECRET> # 替换为您的客户端密钥
STACK_URL=<YOUR ONTOLOGY SERVER DOMAIN NAME> # 替换为您的本体服务器域名，例如，https://myfoundrystack.com
```

### 访问Ontology

以下代码使用了名为@serverside-osdk-example/sdk的包中的CountryObject类型。请将示例包名和Object类型替换为您创建的包和选择的Object类型。最后，将{country.countryName}替换为您的Object类型中的一个属性。

将page.tsx中的代码替换为以下代码：

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
import { Country } from "@serverside-osdk-example/sdk";
import { client, auth } from "./client";
import { Osdk } from "@osdk/client";

// 定义一个异步函数，用于获取国家列表
async function getCountries(): Promise<Osdk.Instance<Country>[]> {
    // 处理身份验证
    await auth.signIn();
    // 需要为服务用户提供对本体的读取权限
    try {
        const resp = await client(Country).fetchPage(); // 调用客户端获取国家数据
        return resp.data; // 返回数据
    } catch (err) {
        console.log(err); // 如果发生错误，打印错误信息
    }
    console.log("No countries found"); // 如果没有找到国家，打印信息
    return [];
};

// 默认导出异步函数Home
export default async function Home() {
  const countries: Osdk.Instance<Country>[]  = await getCountries(); // 获取国家列表
  return (
    <main>
        <div>
          {countries.map((country: Osdk.Instance<Country>) => (
            <span key={country.$primaryKey}>{country.countryName}</span> // 显示每个国家的名称
            )
          )}
        </div>
    </main>
  )
}
```

要运行您的设置演示，首先运行开发服务器：

```
Copied!1
2
npm run dev
# 运行开发环境服务器
```

然后，使用浏览器访问http://localhost:3000 ↗查看结果。
