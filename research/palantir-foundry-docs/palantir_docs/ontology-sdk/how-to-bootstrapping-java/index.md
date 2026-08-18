来源: https://palantir.com/docs/zh/foundry/ontology-sdk/how-to-bootstrapping-java/

# 引导启动一个新的 Ontology SDK (OSDK) Java 应用程序

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 引导启动一个新的 Ontology SDK (OSDK) Java 应用程序

本页面介绍了使用 Ontology SDK (OSDK) 创建 Java 应用程序的过程。

## 创建一个 Developer Console 应用程序

在使用 Ontology SDK (OSDK) 创建新的 Java 应用程序之前，您必须首先创建一个新的 Developer Console 应用程序页面。这将设置您的应用程序权限，并选择您希望 Java 应用程序使用的 Objects。

### 设置个人访问词元

接下来，在本地环境中导出您的个人访问词元。此词元与您的 Palantir 用户或应用程序关联，允许您通过第三方应用程序和 APIs 访问 Foundry 资源。下面是使用示例个人访问词元的示例，但您可以在 Developer Console 中生成一个更长时间有效的词元。

请勿将此词元检入源代码管理，因为这可能会造成安全漏洞。例如，您不应该在 Git 仓库中包含您的个人访问词元。

## 确认Java版本

Java OSDK需要Java版本在17到21之间。要检查您使用的Java版本，请运行以下命令，并在必要时升级Java。

```
Copied!1
2
java --version
# 这个命令用于检查当前安装的Java版本。
```

## 安装最新版本的OSDK

在您的build.gradle文件（或等效文件，如果您使用不同的构建工具）中添加以下存储库和依赖项，以便安装最新版本的SDK。将任何< >替换为您在开发者控制台的应用程序概览页面上找到的应用程序特定值。

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
repositories {
    maven {
        credentials {
            // 从环境变量获取密码
            username ''
            password System.getenv('FOUNDRY_TOKEN')
        }
        // Maven 仓库的应用程序 URL
        url 'https://<APPLICATION-URL>'
    }

    maven {
        credentials {
            // 从环境变量获取密码
            username ''
            password System.getenv('FOUNDRY_TOKEN')
        }
        // Maven 仓库的生成器 URL
        url 'https://<GENERATOR-URL>'
    }
}

dependencies {
    // 添加依赖包
    implementation '<YOUR-PACKAGE-NAME>'
}
```

## 开发您的Java应用

在您的应用中，初始化Foundry客户端并开始开发。如果您需要创建一个服务用户来托管后端应用，这是将Java SDK集成到现有Java服务中的一个典型应用案例，请参考获取所需OAuth信息的指南。

### 使用用户词元初始化Foundry客户端

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
import <PACKAGE-NAME>.FoundryClient;
import <PACKAGE-NAME>.objects.Aircraft;
import com.palantir.osdk.api.Auth;
import com.palantir.osdk.api.UserTokenAuth;
import com.palantir.osdk.internal.api.FoundryConnectionConfig;

// 使用用户令牌认证构建认证对象
Auth auth = UserTokenAuth.builder().token(System.getenv("FOUNDRY_TOKEN")).build();

// 创建Foundry客户端
FoundryClient client = FoundryClient.builder()
        .auth(auth)  // 设置认证信息
        .connectionConfig(FoundryConnectionConfig.builder()
                .foundryUri("<YOUR-FOUNDRY-URL>")  // 设置Foundry服务器的URL
                .build())
        .build();

// 打印从Foundry本体中获取的对象信息，替换<ANY-OBJECT>为具体的对象类型
System.out.println(client.ontology().objects().<ANY-OBJECT>.fetch(1));
```

### 使用OAuth初始化Foundry客户端

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
import <PACKAGE-NAME>.FoundryClient; // 引入FoundryClient类
import <PACKAGE-NAME>.objects.Aircraft; // 引入Aircraft对象类
import com.palantir.osdk.api.Auth; // 引入Auth接口
import com.palantir.osdk.api.UserTokenAuth; // 引入UserTokenAuth类
import com.palantir.osdk.internal.api.FoundryConnectionConfig; // 引入FoundryConnectionConfig类

// 创建认证对象，使用ConfidentialClientAuth构建器
Auth auth = ConfidentialClientAuth.builder()
                .clientId("<YOUR-CLIENT-ID>") // 设置客户端ID
                .clientSecret("<YOUR-SECURELY-STORED-CLIENT-SECRET>") // 设置安全存储的客户端密钥
                .build();

// 创建Foundry客户端实例，设置认证信息和连接配置
FoundryClient client = FoundryClient.builder()
        .auth(auth) // 传递认证对象
        .connectionConfig(FoundryConnectionConfig.builder()
                .foundryUri("<YOUR-FOUNDRY-URL>") // 设置Foundry URI
                .build())
        .build();

// 输出从Foundry中获取的对象信息
System.out.println(client.ontology().objects().<ANY-OBJECT>.fetch(1)); // 替换<ANY-OBJECT>为具体对象类型
```

此代码片段展示了如何通过Palantir Foundry的API进行认证并建立连接，然后从Foundry中获取对象信息。请确保替换占位符<PACKAGE-NAME>,<YOUR-CLIENT-ID>,<YOUR-SECURELY-STORED-CLIENT-SECRET>,<YOUR-FOUNDRY-URL>, 和<ANY-OBJECT>为实际的值。
