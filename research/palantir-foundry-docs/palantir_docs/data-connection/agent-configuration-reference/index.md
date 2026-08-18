来源: https://palantir.com/docs/zh/foundry/data-connection/agent-configuration-reference/

# 代理配置参考

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 代理配置参考

以下部分描述了在创建、监控和管理网络中的代理时可用的各种配置。将解释以下工作流：

- 代理配置参考代理权限代理配置代理管理器配置引导程序代理配置源代理配置代理指标和健康监控指标“距离下次过期时间”指标健康监控自动升级窗口升级窗口错开升级安排数据集同步将代理移动到新目录将代理移动到新主机在Windows主机上安装
- 代理权限
- 代理配置代理管理器配置引导程序代理配置源代理配置
- 代理管理器配置
- 引导程序代理配置
- 源代理配置
- 代理指标和健康监控指标“距离下次过期时间”指标健康监控
- 指标“距离下次过期时间”指标
- “距离下次过期时间”指标
- 健康监控
- 自动升级窗口升级窗口错开升级安排数据集同步
- 升级窗口
- 错开升级
- 安排数据集同步
- 将代理移动到新目录
- 将代理移动到新主机
- 在Windows主机上安装
了解更多关于代理的信息，以及如何在数据连接应用程序中设置它们。

## 代理权限

权限在2023年5月27日之前配置的注册中可能会有所不同。有关这些注册的代理管理问题，请联系Palantir客服支持。

要开始在控制面板中管理代理创建，具有组织管理员权限的用户必须被授予一个额外的工作流，称为更改代理创建认证方法。此工作流权限允许管理员选择严格执行基于角色的代理创建管理。此执行会自动应用于上述日期之后配置的注册。

代理创建权限在控制面板中管理。要创建代理，您必须被指派组织管理员或数据流管理员角色。也可以创建一个自定义角色，并将创建代理工作流指派给该角色。组织角色在控制面板的组织权限页面上管理。

了解更多关于在控制面板中管理角色的信息。

除了组织级别的角色外，您还必须是要保存新创建代理的项目的编辑者或所有者。

创建后，基于项目的角色用于控制谁可以查看、修改和删除代理或将代理指派为特定源的运行时。这意味着代理创建者应确保存储代理的项目配置了正确的角色。

## 证书

代理与Foundry及您的内部网络通信。这意味着代理需要在其信任库中拥有正确的证书，以建立这些连接。

有两种情况可能需要在代理上配置额外的证书：

- 允许代理与Foundry通信的证书
- 允许代理与您的系统通信的证书
在这两种情况下，都可以从数据连接应用程序中的代理管理页面添加证书。

### 向代理添加证书

要向代理添加证书，请导航至数据连接中您的代理的代理详情页面，然后选择管理代理证书。

在这里，选择要添加的证书，并根据需要添加别名。然后，添加证书的内容。证书应作为类似于以下示例的字符串添加，包括换行符，但不包括末尾的换行字符。下方显示的证书是https://palantir.com的公共证书。

请注意，您不能输入证书链；必须分别输入每个证书。

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
-----BEGIN CERTIFICATE-----
MIIGXjCCBUagAwIBAgIQASByQ6gv8Z6X7wEqsyBb1DANBgkqhkiG9w0BAQsFADBY
MQswCQYDVQQGEwJCRTEZMBcGA1UEChMQR2xvYmFsU2lnbiBudi1zYTEuMCwGA1UE
AxMlR2xvYmFsU2lnbiBBdGxhcyBSMyBEViBUTFMgQ0EgMjAyNCBRMjAeFw0yNDA2
MTcxNjUwMTVaFw0yNTA3MTkxNjUwMTRaMBkxFzAVBgNVBAMMDioucGFsYW50aXIu
Y29tMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvBalUG3JFYaSiRO2
enRnEwdeGUgtal9isJfB1++LxcPwo/DP2dncK+ur7URID0TVWOqu+4vXE2mmC9jz
Kx0o/URrMoz70i6qF6/Oyq6CuOHjZINiAN0ovNBBEPNGbSVD3Xq/eWgI7PNQ8hfI
9BJ/3WVA17oSG3zEXiWP3+CiL3Wm1Gn38oOt4URBMA0hgLqyOoU3ooqYIK8Fz2K/
OxAJvq45z2lonMZFFzj5thO5dBBch26mNAacO4MvI9mhUrMZtYvGBRZoXrph4EmF
TJDo2UTYiST0Tq6ibNW+NTuv66DrqFvzOpZybNuZsS6VrisYQ4huPN9jVz7RNFhJ
aeJvbQIDAQABo4IDYTCCA10wGQYDVR0RBBIwEIIOKi5wYWxhbnRpci5jb20wDgYD
VR0PAQH/BAQDAgWgMB0GA1UdJQQWMBQGCCsGAQUFBwMBBggrBgEFBQcDAjAdBgNV
HQ4EFgQUuAbgKrz0fIAXR1I/89IpUMN57AgwVwYDVR0gBFAwTjAIBgZngQwBAgEw
QgYKKwYBBAGgMgoBAzA0MDIGCCsGAQUFBwIBFiZodHRwczovL3d3dy5nbG9iYWxz
aWduLmNvbS9yZXBvc2l0b3J5LzAMBgNVHRMBAf8EAjAAMIGeBggrBgEFBQcBAQSB
kTCBjjBABggrBgEFBQcwAYY0aHR0cDovL29jc3AuZ2xvYmFsc2lnbi5jb20vY2Ev
Z3NhdGxhc3IzZHZ0bHNjYTIwMjRxMjBKBggrBgEFBQcwAoY+aHR0cDovL3NlY3Vy
ZS5nbG9iYWxzaWduLmNvbS9jYWNlcnQvZ3NhdGxhc3IzZHZ0bHNjYTIwMjRxMi5j
cnQwHwYDVR0jBBgwFoAUrw0C0MMbnlj47zdiLecDXZ5BSoowSAYDVR0fBEEwPzA9
oDugOYY3aHR0cDovL2NybC5nbG9iYWxzaWduLmNvbS9jYS9nc2F0bGFzcjNkdnRs
c2NhMjAyNHEyLmNybDCCAX0GCisGAQQB1nkCBAIEggFtBIIBaQFnAHUA5tIxY0B3
jMEQQQbXcbnOwdJA9paEhvu6hzId/R43jlAAAAGQJxs/FAAABAMARjBEAiATvomb
hMrUty8Vj703fTBSzY5qDxEMI473IigiGIiXugIgbj4/j24jloGdVoedM3jb6DFw
yAXkuZD3SMHBLsEvP9gAdgDd3Mo0ldfhFgXnlTL6x5/4PRxQ39sAOhQSdgosrLvI
KgAAAZAnGz7qAAAEAwBHMEUCIAHXbm9F2rwyxD36aHoGZRrnDtgg9UDRy5UtHK6D
OrmKAiEAjfomH4CGUrkBbwD8pzt9BbC6u6gPPveYiURxFIq//RUAdgB9WR4S4Xgq
exxhZ3xe/fjQh1wUoE6VnrkDL9kOjC55uAAAAZAnG0C6AAAEAwBHMEUCIQDDOg9s
KZqzbCu0mNBQMRAv6/2HkuLjZSGMxjq/F0R1/wIgKMHBSsNgeVED+LpTcIBYgp1q
SXgbwSizE6OD+1Ewol0wDQYJKoZIhvcNAQELBQADggEBAAr/tnc9dtTfwrczP7Ok
1+tLKmFRss4/1KQgLY8Tyy45Pag53ikn2n3tSPG1OpRTSmfPhPs9/UQRtMf7f2Gk
ObSXDVpPArtFBFDfZug+j22gVSYQr6zgFJu4Y9QD1GGtICqkmTScubfnjwdffTv6
5oNY4LbVGp5yctAd80OFUXspy+oVGsvv61a1pFO+s/NXleSrqDGL1oWcFW5Uj8GH
jnTM+Lt/HupqZ/ThVSkjMOug+hB875Yf8mWvadKYBX0Ga2s51cp8CI49FRswziY6
3oXPKfHHQybpIKhGosuSyzY8pL8UofHNp8gicAV80Vj6Mw+L8gWaAkCR6YnzQIyJ
9lc=
-----END CERTIFICATE-----
```

这段代码表示一个数字证书（Digital Certificate），通常用于在网络通信中验证身份和加密数据。证书以-----BEGIN CERTIFICATE-----和-----END CERTIFICATE-----标记为边界，内容为经过 Base64 编码的证书数据。证书包含多个信息字段，比如发行者、有效期、主体信息等。

在修改证书后，必须重启代理以使更改生效。如果在初始设置之前添加证书，添加后的证书将包含在下载链接中。

### 允许代理与Foundry通信的证书

用于连接到Foundry实例的证书包含在默认的代理安装包中。通常，这意味着您的代理主机与Foundry通信不需要额外的证书。

如果代理与Foundry之间的流量通过显式或透明代理中介，则可能需要在初始设置时将代理的证书添加到代理中。由于在这种情况下缺少证书将阻止代理被Foundry管理，因此必须在下载初始安装包之前将这些证书添加到代理中。

如果代理启动时出现与证书相关的错误，阻止代理与Foundry通信，这些错误将出现在名为<bootvisor_directory>/var/service.log的日志文件中。

如果您在首次设置代理时遇到错误或事先知道需要额外的证书，您应该：

- 跳过代理设置页面，不尝试在代理主机上下载和安装。
- 从代理管理页面添加必要的证书，如上文所述，然后下载并按照标准安装说明进行操作。
如果您的额外证书用于显式代理，可能需要额外配置。

一旦代理成功连接到Foundry，除非代理主机和Foundry之间的网络配置发生更改，否则这些证书不需要更改。

### 允许代理与您的系统通信的证书

当使用代理作为代理工作者运行时时，您可能需要添加证书以允许与特定目标系统的连接。这在代理工作者配置参考文档中有更详细的描述。

### 在TLS检查环境中的代理

如果您在安装代理的主机上对流量进行TLS检查，则需要在代理管理器首次连接到Foundry之前手动将您的根CA导入到代理管理器的信任库中。

请按照以下说明进行操作：

- 获取用于重新签署检查流量的根CA的公共证书。您的网络团队应该能够提供这一点。或者，您可以在代理的主机上使用OpenSSL检查证书链并找到根证书：openssl s_client -showcerts -connect FOUNDRY_URL:443。
- 使用SSH访问代理的主机，并将证书放置在代理管理器运行用户可访问的某个位置。一个可能的位置是<agent-manager-install-directory>/var/security。
- 导航到代理管理器的Java安装目录：cd <agent-manager-install-directory>/jdk/amazon-corretto*。
- 将证书导入代理管理器的信任库：./bin/keytool -import -alias <CERT_NAME> -file /path/to/certificate.pem -keystore ../../var/security/truststore.jks（当提示输入时，密码是truststore）。
- 启动代理管理器。您应该在Data Connection的代理详细信息页面上看到Connected to Agent Manager, but no connection from agent，确认代理管理器已成功连接到Foundry。
- 为了允许代理连接到Foundry，请按照上述说明将相同的证书添加到代理中。
## 代理配置

首次配置代理或连接到远程源时，可能需要根据组织的网络配置来配置代理。代理可能用于管理代理与Foundry之间的通信，或者可能需要用于访问网络内的数据源。

为了让代理使用代理，您需要在Data Connection的代理配置页面中的管理配置窗口的高级选项卡中，在代理和引导程序配置中配置代理。确保提供的主机名不以http://开头。

### 代理管理器代理配置

代理管理器代理配置必须添加到安装代理的主机上的<agent-manager-install-directory>/var/conf/runtime.yml文件中。下面是包含proxy-configuration块的代理管理器配置示例片段：

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
service-discovery:
    services:
    magritte-coordinator:
        ...
        proxy-configuration:
            hostAndPort: proxy-host.com:3128  # 代理服务器的主机和端口
            credentials: # these are optional  # 这些是可选的凭证
                username: USERNAME  # 用户名
                password: PASSWORD  # 密码
```

该代理将被用于在Agent Manager连接回Foundry的magritte-coordinator。它不会被用于从代理到源的连接。

### 引导程序代理配置

一旦您配置了Agent Manager代理，您就可以配置引导程序代理。为此，请导航到Data Connection中的代理配置页面，在管理配置部分切换高级选项，最后选择引导程序选项卡。以下是一个包含proxyConfiguration块的引导程序配置代码片段示例：

```
Copied!1
2
3
4
5
6
7
coordinator:
    proxyConfiguration:
        host: HOST
        port: PORT
        credentials: # 凭证是可选的
            username: USERNAME
            password: PASSWORD
```

一旦您更新了配置，您必须保存更改并重启代理以使其生效。

此代理将被用于在Bootstrapper中连接回Foundry的magritte-coordinator。它不会被用于从代理到源的连接。

### 源代理配置

要通过代理从代理连接到数据源，请在管理配置页面的高级部分的Bootstrapper选项卡上配置代理的JVM级别代理。

使用这些JVM标志：

```
Copied!1
2
3
4
5
6
7
agent:
  jvmArguments: >-
    -Dhttp.proxyHost=<PROXY URL> -Dhttp.proxyPort=<PROXY PORT>
    -Dhttps.proxyHost=<PROXY URL> -Dhttps.proxyPort=<PROXY PORT>
    # 通过JVM参数设置HTTP和HTTPS代理
    # <PROXY URL> 替换为代理服务器的URL地址
    # <PROXY PORT> 替换为代理服务器的端口号
```

此配置影响代理的所有出站网络请求。我们建议在可用时使用源特定的代理配置。

## 代理指标和健康监控

一旦您在Data Connection中设置了一个代理，您可以查看指标并监控健康状况以保持性能。

### 指标

在Data Connection中导航到代理页面，然后选择指标选项卡。您的代理可用的指标包括但不限于以下内容：

- 操作系统物理内存
- 磁盘空间
- 可用磁盘空间
- 操作系统负载相对于核心的标准化
- CPU利用率
- 代理密钥库中下一个到期时间
- 代理信任库中下一个到期时间
- 代理堆内存
- 已使用堆内存百分比
- 代理正常运行时间
- 代理线程
- 自上次代理重启以来的同步/任务上传
- 正在运行的同步/任务
- 代理同步/任务排队
- 同步/任务持续时间
- 代理最后心跳时间
- 代理管理器版本陈旧时间
- 代理版本陈旧时间
将鼠标悬停在指标卡片上以获取时间戳详细信息，并选择卡片右上角以展开详细视图。

#### “下一个到期时间”指标

代理密钥库中下一个到期时间和代理信任库中下一个到期时间指标指的是代理密钥库和信任库中最早的证书到期时间。例如，如果代理的密钥库中有两个证书，一个在一周后到期，一个在一个月后到期，那么数值将为1w，因为这是最近的到期日期。

代理密钥库和信任库包括用户添加的证书以及由代理管理器自动添加的证书。代理管理器证书会自动升级。

如果证书已经过期，指标将显示000ms。如果代理没有存储任何证书，图表将为空。

#### “版本陈旧时间”指标

代理管理器版本陈旧时间和代理版本陈旧时间指标指的是代理和代理管理器相对于您环境中可用的版本有多过时。

过时版本指标的计算方法是代理或代理管理器最后更新与最新版本发布日期之间的天数。以下示例说明了这些指标和相关监控预计的行为：

| 天数 | 最新发布版本 | 代理/代理管理器当前版本 | 版本陈旧时间指标值 | 备注 |
| --- | --- | --- | --- | --- |
| 0 | v1.0 | v1.0 | 0 | 代理更新到当前最新版本。 |
| 1 | v1.0 | v1.0 | 0 |  |
| 2 | v0.1 -> v2.0 | v1.0 | 0->2 | 当Palantir发布新版本时，指标跳至2。 |
| 3 | v2.0 | v1.0 | 3 |  |
| 4 | v2.0 | v1.0 -> v2.0 | 4->0 | 在维护窗口期间成功更新后，指标回到0。 |

在此示例中，前两天的代理版本陈旧时间指标为0。当新版本可用时，指标跳至2，然后在下一个代理维护窗口之前继续增加，最后在维护窗口期间成功完成更新后回到0。

如果监控设置为在软件版本过旧时发送警报，并且Palantir的新版本发布间隔超过允许的天数，此监控将在新版本可用时立即发送警报，即使某个代理没有机会更新。在上述示例中，如果监控设置为陈旧时间天数>2发出警报，那么即使代理没有机会升级到最新版本，也会在第3天发出警报。警报将在维护窗口期间成功更新后自动解决。

### 健康监控

健康监控允许您在满足某些条件或阈值时为任何指标配置不同严重程度（高、中或低）的警报。

您可以在Data Health应用程序中创建监控视图来监控代理的健康状况。监控视图是一组特别感兴趣的用户组订阅的监控规则的集合。

您可以通过选择监控视图选项卡来查看现有的监控视图。

选择特定监控视图后，您可以通过选择管理监控配置代理的健康监控。在此页面中，您可以创建新的监控规则。

在创建监控规则页面中，您可以配置不同严重程度的特定规则和警报。

了解更多关于使用监控追踪数据健康和将监控与PagerDuty集成。

## 自动升级窗口

Data Connection代理服务定期更新以提供安全性、稳定性和性能改进。确保代理及时接收这些重要改进的最佳方法是为每个使用中的代理配置升级窗口。以下部分描述了在升级窗口期间发生的事情并提供最佳实践指南。

### 升级窗口

代理升级窗口是一组时间间隔，在这些时间间隔内，代理暂时离线被认为是安全的。这些时间间隔每周重复，并可以在Data Connection应用程序中给定代理的代理设置选项卡中的维护窗口页面上定义。

Data Connection协调器监控代理及其各自的升级窗口；当有新版本可用时，它们将在这些升级窗口期间自动升级代理。

作为升级的一部分，代理将重新启动。这将终止任何正在运行的任务，并短暂地阻止新任务在代理上运行。

代理升级窗口应至少为60分钟。然而，实际升级时间应相对较短；它应大致与代理重启所需的时间相同。

### 分散升级

为了确保对数据管道的影响最小，我们建议为所有Data Connection源指派至少两个代理，并分散这些代理上运行的源的升级窗口。例如，一个代理可以在周日定义升级窗口，而另一个在周三安排升级窗口。这确保在任何给定代理的升级窗口期间，被中断的任务可以在备用代理上重试，并且新任务可以继续排队并运行，直到正在升级的代理完全重新上线。

### 安排数据集同步

当无法使用分散的升级窗口时，重要的是在低（理想情况下为零）活动期间安排升级窗口。在这种情况下，应安排数据集同步，使其在升级窗口开始前完成，或在窗口结束后几分钟开始（以考虑窗口结束时的重启）。

## 将代理移至新目录

按照以下步骤将代理移至同一台机器的新安装目录。

- 在Data Connection中，导航到同步页面并确保当前没有同步正在运行。使用页面左侧的筛选查看当前具有运行中状态的同步，检查是否有同步正在运行。如果有同步正在运行，要么等待它们完成，要么通过选择它们的状态链接（例如，14分钟前运行），然后在构建页面中选择取消构建来取消它们。确保在需要取消同步时适当通知同步所有者。
- 使用页面左侧的筛选查看当前具有运行中状态的同步，检查是否有同步正在运行。
- 如果有同步正在运行，要么等待它们完成，要么通过选择它们的状态链接（例如，14分钟前运行），然后在构建页面中选择取消构建来取消它们。确保在需要取消同步时适当通知同步所有者。
- 导航到代理页面。选择您要移动的代理的名称。
- 在配置面板中，选择高级。对于高级设置的每个选项卡，更改所有使用绝对路径的引用。查找以/开头的任何内容，并将其修改为新路径。注意：Kerberos设置需要绝对路径。
- 注意：Kerberos设置需要绝对路径。
- 在Foundry中停止代理。为此，选择屏幕右上角重启代理下拉箭头，然后选择停止（不安全）。注意：不安全标签旨在警告停止代理将中断任何正在运行的同步，这就是为什么我们在第1步中采取了预防措施。
- 注意：不安全标签旨在警告停止代理将中断任何正在运行的同步，这就是为什么我们在第1步中采取了预防措施。
- 在您的机器终端上，通过SSH进入代理。
- 切换到代理的管理用户。根据您的配置，这可能需要输入-- sudo -su palantir或-- sudo -su admin。
- 在终端中，使用cd导航到代理安装目录。
- 通过运行./service/bin/init.sh stop停止代理。
- 如果代理之前配置为自动启动：对于Linux，运行./service/bin/auto_restart.sh clear。对于Windows，删除按照在Windows主机上安装说明设置的任何计划任务。
- 对于Linux，运行./service/bin/auto_restart.sh clear。
- 对于Windows，删除按照在Windows主机上安装说明设置的任何计划任务。
- 等待几分钟，检查管理用户是否正在运行任何Java进程。如果有，手动停止它们。
- 可选：删除./var/data/binaries、./var/data/cache和./var/data/processes文件夹的内容，以减少传输的数据量。
- 通过输入mv <source directory> <new installation directory>将代理移动到新目录文件夹。
- 导航到新的代理安装目录。通过运行./service/bin/init.sh start重新启动代理。
- 如果代理之前配置为自动重启，请按照自动重启设置说明重新启用它。
- 等待五分钟，然后刷新Foundry中的代理页面以确保代理已连接并且同步成功。
## 将代理移至新主机

在将代理移至新主机时，请确保新主机满足操作系统要求并具有与以前代理相同的操作系统和架构。新主机还必须具有与旧主机相同的防火墙网络配置。例如，如果代理以前在运行x86_64架构的Linux发行版上运行，则新主机可以具有任何Linux发行版，但必须在相同架构上运行。以下说明将无法将代理从Linux移动到Windows或ARM架构。对于这些情况，请从UI获取新的下载链接并继续新的安装。请注意，如果代理使用新的下载链接重新安装，则需要重新输入在代理上运行的源的凭据。

按照以下步骤将代理移至新主机：

- 按照将代理移至新目录说明中的步骤1到11（不包括第3步）。这将停止代理并准备将其传输到新主机。
- 使用rsync或任何其他文件传输工具将代理文件夹从旧主机复制到新主机上的位置。
- 按照将代理移至新目录说明中之前跳过的第3步进行操作。对于每个由绝对路径引用的文件或文件夹，将该资源复制到新主机上的位置并更新配置以指向新路径。
- 按照将代理移至新目录指南中的步骤13到16进行操作。
## 在Windows主机上安装

Linux主机是设置代理的首选选项。除非无法获得Linux主机或在Windows主机上运行Linux虚拟机，否则不应使用Windows主机。

在使用Windows代理作为代理工作程序运行时时，某些功能可能无法在Windows代理上运行。特别是，Windows代理不支持表导出，并且将无法运行。

按照设置代理指南中的步骤进行操作，但在下载并配置代理步骤中选择Windows作为操作系统。安装代理后，您需要设置一个Windows计划任务，在崩溃或机器重启时重新启动代理管理器，具体步骤如下：

- 以管理员身份打开Windows任务计划程序。
- 创建一个新的计划任务。
- 在常规选项卡下，执行以下操作：将运行任务时使用以下用户帐户设置为SYSTEM。确保选择无论用户是否登录都运行。确保不存储密码...未选中。将配置为更新为Windows虚拟机的正确操作系统。选择以最高权限运行。
- 将运行任务时使用以下用户帐户设置为SYSTEM。
- 确保选择无论用户是否登录都运行。
- 确保不存储密码...未选中。
- 将配置为更新为Windows虚拟机的正确操作系统。
- 选择以最高权限运行。
- 在触发器选项卡下，创建两个触发器：设置一个触发器在事件上并选择启动时。确保任务是启用的。设置另一个触发器在计划上：设置任务每天运行。勾选每复选框，并选择5分钟持续时间为1天。
- 设置一个触发器在事件上并选择启动时。确保任务是启用的。
- 确保任务是启用的。
- 设置另一个触发器在计划上：设置任务每天运行。勾选每复选框，并选择5分钟持续时间为1天。
- 设置任务每天运行。
- 勾选每复选框，并选择5分钟持续时间为1天。
- 在操作选项卡下：添加一个新的启动程序操作。将magritte-bootvisor-win批处理文件的完整路径复制到程序/脚本框中。完整路径将类似于C:\example\path\to\folder\containing\magritte\agent\magritte-bootvisor-win-{version}\service\bin\magritte-bootvisor-win.bat。将批处理脚本所在文件夹的完整路径复制到起始位置（可选）框中。完整路径将类似于C:\example\path\to\folder\containing\magritte\agent\magritte-bootvisor-win-{version}。没有参数，因此保持添加参数（可选）为空。
- 添加一个新的启动程序操作。
- 将magritte-bootvisor-win批处理文件的完整路径复制到程序/脚本框中。完整路径将类似于C:\example\path\to\folder\containing\magritte\agent\magritte-bootvisor-win-{version}\service\bin\magritte-bootvisor-win.bat。
- 完整路径将类似于C:\example\path\to\folder\containing\magritte\agent\magritte-bootvisor-win-{version}\service\bin\magritte-bootvisor-win.bat。
- 将批处理脚本所在文件夹的完整路径复制到起始位置（可选）框中。完整路径将类似于C:\example\path\to\folder\containing\magritte\agent\magritte-bootvisor-win-{version}。
- 完整路径将类似于C:\example\path\to\folder\containing\magritte\agent\magritte-bootvisor-win-{version}。
- 没有参数，因此保持添加参数（可选）为空。
- 选择确定保存任务。
- 右键点击任务并选择运行，尝试手动运行任务。
- 您应该看到代理成功启动。界面中反映这一点可能需要一到两分钟。如果代理未成功启动，请检查计划任务的历史记录选项卡中的错误。您还可以通过使用Windows命令提示符更改目录到特定文件夹并执行相关的.bat文件来验证操作的成功。
## 备份和缓存

代理可能会在安装、版本升级、版本降级和持续使用过程中备份或缓存文件。通常，备份和缓存可以安全地忽略，并将在30天后自动删除。如果备份和缓存文件在代理主机上占用了比预期更高的磁盘空间，可以在维护窗口之外安全删除它们。

备份和缓存文件将在代理安装目录内的以下子目录中找到：

| 子目录 | 用途 |
| --- | --- |
| /backups | 用于在执行升级时存储代理配置的备份。 |
| /var/data/cache | 用于在代理正常运行期间缓存数据。 |
