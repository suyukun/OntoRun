来源: https://palantir.com/docs/zh/foundry/data-connection/agent-worker-runtime/

# 代理工作器

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 代理工作器

要连接到您网络中无法接受来自Foundry的入站网络流量的系统，可以使用中介代理，作为代理工作器或代理代理。本页描述了代理工作器运行时可用的配置选项，并假设您已经熟悉数据连接代理。

仅当目标系统无法接受来自Foundry的入站网络流量，并且连接器不支持代理代理运行时时，才应使用代理工作器运行时。

## 设置代理

您必须设置代理以使用代理工作器运行时。在配置源时，您可以选择代理工作器选项并选择至少一个可用代理。功能将在该源连接上作为任务在代理工作器主机上执行。

## 功能执行

使用代理工作器运行时时，通过在代理主机上直接运行Java代码来执行功能。这些Java进程可以从您的系统中提取数据并推送到Foundry（如同批量同步），或者从Foundry提取数据并推送到您的系统（如同导出）。

此执行模型带来了一些缺点，包括：

- 代理上的潜在类路径冲突。这对于自定义JDBC工作流特别相关，因为自定义JAR可能与从Foundry发出的依赖项冲突，并在代理类路径上运行。
- 这对于自定义JDBC工作流特别相关，因为自定义JAR可能与从Foundry发出的依赖项冲突，并在代理类路径上运行。
- 在代理上运行的任务之间的争用。任务可能会随意使用分配给代理进程的整个内存和磁盘空间，并可能导致其他任务永远无法启动或崩溃。这对于使用代理工作器运行时运行的webhook尤其成问题。在这种情况下，我们强烈建议为webhook执行提供一个专用代理，以便长时间运行的同步不会阻止短时间运行的webhook执行。
- 任务可能会随意使用分配给代理进程的整个内存和磁盘空间，并可能导致其他任务永远无法启动或崩溃。
- 这对于使用代理工作器运行时运行的webhook尤其成问题。在这种情况下，我们强烈建议为webhook执行提供一个专用代理，以便长时间运行的同步不会阻止短时间运行的webhook执行。
- 某些功能的缺乏支持。功能如虚拟表和虚拟媒体与代理工作器运行时不兼容，因为这些需要直接从Foundry进行同步连接，无法作为任务在代理上运行。
- 功能如虚拟表和虚拟媒体与代理工作器运行时不兼容，因为这些需要直接从Foundry进行同步连接，无法作为任务在代理上运行。
## 内存分配和使用

代理内存是决定使用代理工作器运行时执行功能性能的关键因素之一。

代理内存的主要设置有：

- JVM堆:在代理设置页面上配置，指示代理在启动时应分配多少内存。这些内存将从操作系统的角度被代理占用，并且必须小于主机机器上的可用内存。默认的JVM堆值为1 GB。
- 主机内存:基于安装代理的机器的规格。我们建议至少有16 GB内存。
在主机上观察到的实际内存使用情况将根据代理工作器当前执行的工作负载，包括在同一主机上运行的其他进程而有所不同。

在观察和监控用作代理工作器的代理的内存使用时，有两个主要指标：

- 操作系统物理内存使用量:代理主机上的实际总内存使用量，包括代理进程和在同一主机上运行的任何其他进程。这可能会超过为代理进程分配的JVM堆大小，并达到可用的全部物理内存。
- 代理内存使用量:代理的内存使用量，将始终小于配置的JVM堆大小。
有关监控代理内存使用的信息，请查看代理指标和健康监控。

## 负载均衡

使用代理工作器运行时时，可以为单个源连接分配多个代理。代理被分配任务以执行配置在分配的源连接上的特定功能。任务将在任务启动时可用的代理之一上执行。

任务被分配给具有最大可用带宽的代理。带宽计算如下：

```
Copied!1
# (最大并发同步数) - (当前运行的批量同步数) = 带宽
```

这个公式表示可用于同步操作的剩余带宽。最大并发同步数是系统能够同时处理的同步任务的最大数量，而当前运行的批量同步数是当前正在进行的同步任务数量。通过计算两者的差值，可以得到当前可用的同步带宽。最大并发同步默认值为16，可以在代理设置中进行配置。最大并发同步配额适用于所有功能和所有指派的来源，这意味着在任何来源上运行任何功能都会占用一个可用的并发同步配额单位。这也包括传统的数据连接任务。如果所有可用代理的带宽为零，或者指派的代理有正带宽但当前运行的同步超过最大并发同步数，任务将会排队。

在计算带宽时，仅考虑批量同步。这意味着为分配额外任务而运行在代理上的其他功能将被忽略。如果您的主要代理工作负载是流同步、变更数据捕获同步、导出或其他功能，您可能会在多代理设置中分配任务时看到意外行为。无法保证任务会均匀分布在具有相同带宽值的多个可用代理上。

一般来说，我们不建议使用多个代理作为负载均衡的一种方式，以处理单个代理无法成功运行的更大工作负载。多个代理的主要用途是允许代理因维护而下线。为了获得最佳性能和可靠性，我们建议在多代理设置中，每个代理都应能够处理指派的源连接上配置的所有功能。

## 直接上传与数据代理上传策略

代理工作者运行时支持两种选项来指定批量同步的数据应如何上传到Palantir平台：

### 数据代理模式

在数据代理模式下，数据通过公共Foundry API使用数据代理服务上传。这使用了与调用Foundry API读取和写入数据集时相同的API网关。

配置为使用数据代理模式的代理将在代理配置YAML中包含以下内容：

```
Copied!1
2
3
4
destinations:
  foundry:
    uploadStrategy:
      type: data-proxy  # 数据上传策略类型为 data-proxy
```

### 直接模式 [终止]

直接模式在2024年6月之后设置的新代理或注册中不可用。数据代理模式是新代理支持的默认且唯一选项。之前配置为使用直接模式的代理将继续得到支持，只要安装代理的主机的公共IP不变。

在直接模式中，数据直接上传到Foundry数据目录中的底层存储桶。虽然提供了性能改进，但这只能通过Palantir支持的自定义网络配置实现，并且在我们最新的云基础设施上不可用。

配置为使用直接模式的代理将在代理配置YAML中包含以下内容：

```
Copied!1
2
3
4
destinations:
  foundry:
    uploadStrategy:
      type: direct  # 上传策略类型：直接上传
```

在这个代码片段中，我们定义了一个名为destinations的配置，其中foundry是目标，uploadStrategy是上传策略。type: direct表示上传策略类型为直接上传。

## 自定义 JDBC 驱动程序

有关如何向代理添加自定义 JDBC 驱动程序的信息，请参阅JDBC（自定义）连接器的文档。驱动程序必须由 Palantir 签名，并直接添加到代理中，以便与代理工作器运行时一起使用。

对于代理代理和直接连接运行时，自定义驱动程序会直接在 JDBC（自定义）连接器用户界面中添加，如我们的文档所述。这些驱动程序不需要由 Palantir 签名。

## 凭证

代理工作器运行时的一个独特方面是凭证永远不会存储在 Foundry 中。相反，在 Data Connection 用户界面输入凭证时，它们会使用指派到源的每个代理的公钥进行加密。加密后的凭证存储在各自的代理上。

这意味着在使用代理工作器运行时配置凭证时，以下注意事项和限制适用：

- 如果指派到源的代理集更改，必须在 Data Connection 中重新输入凭证。
- 如果使用新的下载链接重新配置代理，凭证不会自动传输，必须在 Data Connection 中重新输入凭证。
有关在目录和主机之间移动代理的更多信息，请参阅代理配置参考文档，其中包括在移动现有代理目录时保留加密凭证的说明。

## 证书

代理与 Foundry 和您的内部网络通信。这意味着代理需要在其信任存储中具有正确的证书，以便建立这些连接。

有两种情况可能需要在代理上配置额外的证书：

- 允许代理与 Foundry 通信的证书
- 允许代理与您的系统通信的证书
### 允许代理与 Foundry 通信的证书

代理与 Foundry 通信所需的证书要求在代理配置文档中进行了说明，无论代理将用作代理代理还是代理工作器，这些证书都是必需的。

### 允许代理与您的系统通信的证书

当代理用作代理工作器时，可能需要额外的证书，以便在代理上运行的 Java 进程能够成功与您的系统通信。每个新的源连接可能需要添加新的证书，如果这些证书过期或轮换，也应进行更新。

当缺少所需的证书时，您在尝试使用诸如探索之类的源功能时会看到如下错误：

```
包装异常: javax.net.ssl.SSLHandshakeException: sun.security.validator.ValidatorException:
PKIX 路径构建失败: sun.security.provider.certpath.SunCertPathBuilderException:
无法找到到请求目标的有效认证路径
```

该错误信息一般出现在使用 SSL/TLS 协议进行安全通信时，无法验证证书路径。这通常是因为缺少必要的证书或未正确配置信任库。
按照这些说明以添加额外的证书用于连接到特定的源系统。

## 将源从代理切换到直接连接

如果基于代理的源连接到可通过互联网访问的系统，则应迁移到直接连接运行时。按照以下步骤执行此迁移。

- 导航到连接设置 > 连接详情，然后选择切换到直接云连接。
- 按照引导对话框中的说明开始迁移。
- 选择一个代表性的代理。这应该是一个健康的代理，如果需要，可以提供源机密和驱动程序。
- （非必填）配置一个驱动程序。
- 添加出口策略。
要创建新的出口策略，您必须具有在控制面板中名为管理网络出口配置的工作流的访问权限，该权限授予信息安全官角色。

- 选择迁移以完成此过程。
### 故障排除

本节描述迁移过程中可能出现的情况以及建议的解决步骤。迁移是可逆的。

#### 无法将类型ID解析为'com.palantir.magritte.api.Source'的子类型

建议解决方案：

当找不到源所需的依赖项时会发生这种情况。确保您已配置特定源所需的所有证书、代理和驱动程序，然后重试迁移。

#### UnknownHostException

建议解决方案：

- 确保为源指派了正确的出口策略。
- 确认Foundry能够访问引发异常的终端。
#### 未找到驱动程序类

建议解决方案：确认正确的驱动程序已上传到JDBC源。

#### PKIX路径构建失败

建议解决方案：确保为源添加了正确的证书。

## 添加私钥

如果您连接的系统需要双向TLS（mTLS），则必须手动向代理添加私钥。

每当代理重新启动时，默认引导程序密钥库和信任库都会重新生成，并且对默认密钥库所做的任何更改都将在重新启动时被覆盖。以下说明解释了如何覆盖默认密钥库，以指向代理主机上不同位置的自定义密钥库，以及如何修改此自定义密钥库以添加您的私钥。

- 复制默认引导程序密钥库并将其存储在代理主机上的单独位置。使用与代理在主机上运行的相同用户名运行以下命令。您可以选择将该文件夹命名为security或根据您的喜好命名。Copied!12$ mkdir /home/<username>/security
$ cp <bootvisor_root>/var/data/processes/<bootstrapper_dir>/var/conf/keyStore.jks  /home/<username>/security/
复制默认引导程序密钥库并将其存储在代理主机上的单独位置。使用与代理在主机上运行的相同用户名运行以下命令。您可以选择将该文件夹命名为security或根据您的喜好命名。

```
Copied!1
2
$ mkdir /home/<username>/security
$ cp <bootvisor_root>/var/data/processes/<bootstrapper_dir>/var/conf/keyStore.jks  /home/<username>/security/
```

- 使用Javakeytool命令行工具将客户提供的密钥库中的密钥导入到复制的代理密钥库中。如果尚未安装此工具，请在与代理捆绑的JDK的bin目录中找到它。Copied!1234$ keytool -importkeystore -srckeystore <CUSTOM_KEYSTORE.jks> -destkeystore /home/<username>/security/keyStore.jks
Importing keystore CUSTOM_KEYSTORE.jks to keyStore.jks...
Enter destination keystore password: keystore
Enter source keystore password:您可以使用keytool -list命令验证密钥/密钥是否已添加到复制的密钥库中：Copied!1234567891011$ keytool -list -keystore /home/<username>/security/keyStore.jks
Enter keystore password:
Keystore type: jks
Keystore provider: SUN

Your keystore contains 2 entries

<CUSTOM_KEY>>, 15-Dec-2022, PrivateKeyEntry,
Certificate fingerprint (SHA-256): A5:B5:2F:1B:39:D3:DA:47:8B:6E:6A:DA:72:4B:0B:43:C7:2C:89:CD:0D:9D:03:B2:3F:35:7A:D4:7C:D3:3D:51
server, 15-Dec-2022, PrivateKeyEntry,
Certificate fingerprint (SHA-256): DB:82:66:E8:09:43:30:9D:EF:0A:41:63:72:0C:2A:8D:F0:8A:C1:25:F7:89:B1:A3:6E:6F:C6:C5:2C:17:CB:B2
使用Javakeytool命令行工具将客户提供的密钥库中的密钥导入到复制的代理密钥库中。如果尚未安装此工具，请在与代理捆绑的JDK的bin目录中找到它。

```
Copied!1
2
3
4
$ keytool -importkeystore -srckeystore <CUSTOM_KEYSTORE.jks> -destkeystore /home/<username>/security/keyStore.jks
Importing keystore CUSTOM_KEYSTORE.jks to keyStore.jks...
Enter destination keystore password: keystore
Enter source keystore password:
```

- 您可以使用keytool -list命令验证密钥/密钥是否已添加到复制的密钥库中：Copied!1234567891011$ keytool -list -keystore /home/<username>/security/keyStore.jks
Enter keystore password:
Keystore type: jks
Keystore provider: SUN

Your keystore contains 2 entries

<CUSTOM_KEY>>, 15-Dec-2022, PrivateKeyEntry,
Certificate fingerprint (SHA-256): A5:B5:2F:1B:39:D3:DA:47:8B:6E:6A:DA:72:4B:0B:43:C7:2C:89:CD:0D:9D:03:B2:3F:35:7A:D4:7C:D3:3D:51
server, 15-Dec-2022, PrivateKeyEntry,
Certificate fingerprint (SHA-256): DB:82:66:E8:09:43:30:9D:EF:0A:41:63:72:0C:2A:8D:F0:8A:C1:25:F7:89:B1:A3:6E:6F:C6:C5:2C:17:CB:B2
您可以使用keytool -list命令验证密钥/密钥是否已添加到复制的密钥库中：

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
$ keytool -list -keystore /home/<username>/security/keyStore.jks
Enter keystore password:
Keystore type: jks
Keystore provider: SUN

Your keystore contains 2 entries

<CUSTOM_KEY>>, 15-Dec-2022, PrivateKeyEntry,
Certificate fingerprint (SHA-256): A5:B5:2F:1B:39:D3:DA:47:8B:6E:6A:DA:72:4B:0B:43:C7:2C:89:CD:0D:9D:03:B2:3F:35:7A:D4:7C:D3:3D:51
server, 15-Dec-2022, PrivateKeyEntry,
Certificate fingerprint (SHA-256): DB:82:66:E8:09:43:30:9D:EF:0A:41:63:72:0C:2A:8D:F0:8A:C1:25:F7:89:B1:A3:6E:6F:C6:C5:2C:17:CB:B2
```

- 使用keytool -keypasswd命令更新导入的密钥密码。代理密钥库要求密钥和密钥库密码相匹配。Copied!12$ keytool -keypasswd -alias <CUSTOM_KEY> -new keystore -keystore /home/<username>/security/keyStore.jks
Enter keystore password:
使用keytool -keypasswd命令更新导入的密钥密码。代理密钥库要求密钥和密钥库密码相匹配。

```
Copied!1
2
$ keytool -keypasswd -alias <CUSTOM_KEY> -new keystore -keystore /home/<username>/security/keyStore.jks
Enter keystore password:
```

- 在数据连接中，导航到代理，然后打开代理设置选项卡。在管理配置部分，选择高级，选择代理选项卡，并更新keyStore以指向新复制的密钥库。然后，添加keyStorePassword并设置为适当的值（默认情况下为keystore）。Copied!12345security:
    keyStore: /home/<username>/security/keyStore.jks
    keyStorePassword: keystore
    trustStore: var/conf/trustStore.jks
...
在数据连接中，导航到代理，然后打开代理设置选项卡。在管理配置部分，选择高级，选择代理选项卡，并更新keyStore以指向新复制的密钥库。然后，添加keyStorePassword并设置为适当的值（默认情况下为keystore）。

```
Copied!1
2
3
4
5
security:
    keyStore: /home/<username>/security/keyStore.jks
    keyStorePassword: keystore
    trustStore: var/conf/trustStore.jks
...
```

- 最后，选择资源管理器选项卡并更新keyStorePath和keyStorePassword。保存新配置。Copied!12345security:
    keyStorePath: /home/<username>/security/keyStore.jks
    keyStorePassword: keystore
    trustStorePath: var/conf/trustStore.jks
...
最后，选择资源管理器选项卡并更新keyStorePath和keyStorePassword。保存新配置。

```
Copied!1
2
3
4
5
security:
    keyStorePath: /home/<username>/security/keyStore.jks
    keyStorePassword: keystore
    trustStorePath: var/conf/trustStore.jks
...
```

- 重启代理。
重启代理。

注意在代理选项卡中配置时字段命名为keyStore，而在资源管理器选项卡中为keyStorePath。不需要对引导程序配置进行更改。
