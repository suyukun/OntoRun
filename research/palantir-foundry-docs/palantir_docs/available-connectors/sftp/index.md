来源: https://palantir.com/docs/zh/foundry/available-connectors/sftp/

# SFTP

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# SFTP

连接Foundry到SFTP服务器，以在文件夹和Foundry数据集中同步数据。

## 支持的功能

| 功能 | 状态 |
| --- | --- |
| 探索 | 🟢 一般可用 |
| 批量导入 | 🟢 一般可用 |
| 增量 | 🟢 一般可用 |
| 导出任务 | 🟡 终止（仅限旧版SFTP源） |
| 文件导出 | 🟢 一般可用 |

## 数据模型

连接器可以将任何类型的文件传输到Foundry数据集中。文件格式保持不变，并且在传输期间或之后不应用任何模式。对输出数据集应用任何必要的模式，或者编写下游变换以访问数据。

## 性能和限制

可传输文件的大小没有限制。然而，网络问题可能导致大规模传输失败。特别是，运行超过两天的直接云同步将被中断。为避免网络问题，我们建议使用较小的文件大小并限制每次同步执行时摄取的文件数量。同步可以安排频繁运行。

## 设置

- 打开数据连接应用程序，并在屏幕右上角选择**+ 新来源**。
- 从可用的连接器类型中选择SFTP。
- 选择通过互联网使用直接连接或通过中介代理连接。
- 根据以下部分中的信息，按照其他配置提示继续设置您的连接器。
要配置直接连接，Foundry必须能够通过互联网访问SFTP服务器。要访问本地SFTP服务器，请选择通过代理连接。

了解更多关于在Foundry中设置连接器的信息。

### 认证

可以使用密码或SSL私钥建立到SFTP服务器的连接。如果在连接服务器时遇到任何问题，请通过Foundry外部的SFTP客户端尝试连接来验证认证详情是否正确。此连接的用户必须具有对根目录的访问权限以及读取和列出根目录内所有文件和目录的权限。

| 选项 | 是否必需 | 描述 |
| --- | --- | --- |
| Username | 是 | SFTP登录用户名。 |
| Password | 否 | SFTP登录密码。 |
| Private key | 否 | RSA格式的SSL私钥。SFTP服务器必须正确配置公钥作为所提供用户名的授权密钥。 |

### 网络

如果直接连接正在运行SFTP连接器，您必须添加网络出口策略以允许列入白名单的连接。

出口策略应该为SFTP服务器主机名（如果通过域连接）以及SFTP服务器主机名解析到的IP创建。在正确配置出口策略后，由于主机名验证，非标准连接端口（22）可能仍无法工作。如果发生这种情况，请向Palantir支持报告问题，并提供应用于此连接的策略列表。

如果服务器的域解析为多个域和/或服务器，所有相关的域及其相关IP都需要列入白名单。要验证服务器是否解析为多个域和/或服务器，请在终端中运行命令dig <domain>以查看您尝试连接的服务器的答案部分。

在UNIX机器上，通过运行以下命令找到您的服务器域解析到的IP地址：

```
Copied!1
2
dig <domain> +short
# 该命令用于查询指定域名（<domain>）的DNS记录，+short选项使输出结果更简洁。
```

如果有代理正在运行您的连接器，请确保代理的服务器可以建立到SFTP服务器的网络连接，并且防火墙配置正确。我们建议在需要时使用netcat ↗或类似工具验证网络连接。

### 证书和私钥

#### 服务器SSH密钥

SFTP服务器通过公钥来标识自己。此密钥可以从服务器的管理员处获得（优选方法），或通过在任何可以访问目标SFTP服务器的Linux服务器上运行以下命令获取：

```
Copied!1
2
3
4
5
6
ssh-keyscan -t rsa -p {port} {hostname}  | awk '{print $3}'
# 使用 ssh-keyscan 命令扫描指定主机的 SSH 公钥
# -t rsa 指定使用 RSA 类型的密钥
# -p {port} 指定连接的端口
# {hostname} 是目标主机名
# awk '{print $3}' 从输出中提取第三列（即公钥的实际内容）
```

此密钥必须在连接详细信息页面的主机密钥部分中配置。如果无法获取此密钥，或密钥更改频繁，可以使用接受任何主机密钥开关来禁用密钥验证。请注意，禁用密钥验证是不安全的，不建议这样做。

#### 主机名验证

Foundry尝试对所有出口路由进行主机名验证。端口22以外的网络流量有时未经过验证，导致连接挂起和/或超时错误。如果尽管已正确配置出口策略仍然出现错误，请向Palantir客服支持报告问题，并提供希望禁用主机名验证的策略列表。

## 配置选项

| 选项 | 是否必需？ | 默认值 | 描述 |
| --- | --- | --- | --- |
| Hostname | 是 |  | 指向服务器的域名或服务器的IP地址。 |
| Port | 是 |  | SFTP服务器运行的端口。 |
| Root directory | 是 |  | 服务器上将用作此连接所有请求的起始目录的目录。 |
| Username | 是 |  | SFTP登录用户名。 |
| Password | 否 |  | SFTP登录密码。 |
| Private key | 否 |  | RSA格式的SSL私钥。SFTP服务器必须将公钥正确配置为所提供用户名的授权密钥。 |
| Host key | 是 |  | 有关详细信息，请参见上面的服务器SSH密钥。 |
| Accept any host key | 否 | false | 有关详细信息，请参见上面的服务器SSH密钥。 |
| Proxy | 否 | 直接 | 启用以允许与SFTP的代理连接。 |
| Timeout | 否 | 0 | 有关详细信息，请参见下面的超时。 |
| Maximum concurrent connections | 否 | 运行时（代理或直接连接）支持的最大并行上传 | 较高的值通常会导致更快的传输速度。将此值设置为高于运行时支持的最大并行上传数量不会产生任何影响。如果您的SFTP服务器可以限制到服务器的并发连接数量以管理负载，请使用此设置。 |
| 连接设置 | 否 |  | 有关详细信息，请参见下面的连接设置部分。 |
| Logs | 否 | Info | 要记录的日志级别。选择一个级别将记录该级别或更高级别的所有日志；例如，Error级别将记录Error和Fatal级别的日志。有关示例，请参见下面的日志部分。 |
| Extension Negotiation | 否 | N/A | 这些设置控制连接器发送给SFTP服务器的扩展协商消息。禁用这些功能有时可以解决建立连接的问题。有关更多指导，请参见下文。 |

### 超时

值为0表示连接将无限期等待服务器的每个响应。此超时控制连接器在与服务器建立连接时以及在服务器上运行每个命令时等待的时间。如果服务器继续响应，则不会触发超时。将此设置为较低的值不会阻止大文件传输，但可以帮助调试挂起的连接。

### 连接设置

在建立SFTP连接时，服务器和客户端（Foundry）必须协商必要的详细信息。这些详细信息包括帮助客户端和服务器决定使用哪些加密算法的信息。由于兼容性问题，您可能需要手动配置这些设置，而不是允许它们自动协商。下表列出了可以用来根据需要调整协商的可用配置选项。有关更多信息，请查看常见问题 ↗。

| 设置 | 描述 |
| --- | --- |
| Key exchange algorithms | 可用于密钥交换的算法的明确列表。必须至少选择一种算法。 |
| Ciphers | 可用于加密的密码列表。 |
| Message Authentication Code (MAC) | MAC类型列表。 |
| Host key types | 可用于此连接的主机密钥类型。 |
| Public key types | 将用于公钥认证的算法。 |

## 从SFTP同步数据

SFTP连接器使用file-based sync接口。

## 故障排除

### 借用连接进行ls失败

如果搭建失败并出现错误借用连接进行ls失败，且错误包含SocketException: Connection reset，请检查搭建日志以查看是否已建立与SFTP服务器的网络连接。如果日志中不包含连接已建立和远程版本字符串行，则防火墙正在阻止连接运行时的出口流量，或目标SFTP服务器不允许传入连接。检查出口策略和防火墙规则，并联系SFTP服务器管理员以解决网络连接问题。下面是成功连接日志的示例：

```
jschLogMessage: Connecting to <HOSTNAME> port 2232
jschLogMessage: Connection established
jschLogMessage: Remote version string: <value identifying the type of server>
```

```
// jschLogMessage: 正在连接到 <HOSTNAME> 端口 2232
// jschLogMessage: 连接已建立
// jschLogMessage: 远程版本字符串: <识别服务器类型的值>
```

### 连接挂起

如果连接挂起而没有任何进展或明显的失败，将超时时间设置为一个较小的值（例如，1000），以帮助识别哪个调用挂起。例如，可能是在列出某个特定目录时耗时较长，或文件的某些部分读取时间过长。

由于主机名验证，可能会发生连接挂起，设置一个较小的超时时间将允许生成出错日志，这可以帮助支持团队识别连接问题的根本原因。

### Agent连接

如果您在设置Agent连接时遇到问题，请使用SFTP客户端并尝试使用与源相同的配置连接到服务器。如果此连接失败，则问题不是连接器的错误。在提交问题之前，调查网络连接、身份验证和SFTP服务器配置。

如果您使用出口代理负载均衡器，请注意FTP是一个有状态协议。如果连续请求不是来自同一IP，使用负载均衡器可能会导致同步失败（非确定性）。

## 以SFTP格式导出数据

连接器可以将文件从Foundry数据集复制到SFTP服务器上的任何位置。

要以SFTP格式导出，首先启用导出以用于您的SFTP连接器。然后，创建一个新的导出。

## 旧版SFTP连接器

以下部分涵盖了旧版SFTP连接器，仅在维护此连接器的现有使用时参考。任何新的SFTP源创建应遵循上面部分中描述的步骤。

### 设置旧版SFTP连接器

要设置旧版SFTP连接器，请导航到数据连接应用程序，然后选择**+ 新建源**。在源选择屏幕上，向下滚动到高级，然后选择自定义源。按照配置屏幕中的提示继续设置您的SFTP连接器。

SFTP YAML配置的完整示例如下所示：

:::{callout theme=warning}
请注意，旧版SFTP源的type必须是magritte-sftp。
:::

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
type: magritte-sftp
hostname: my.host.name  # 服务器主机名
port: 22  # 连接端口，默认SFTP使用端口22
username: username  # 用户名
password: '{{password}}'  # 用户密码
rootDirectory: /home/palantir/sftp  # SFTP根目录
base64Hostkey: >-
  FULL CONTENTS OF THE HOST KEY  # 主机密钥的Base64编码内容
unsafeAcceptAllHostKeys: false  # 是否接受所有主机密钥，不建议设为true，可能不安全
privateKeyFile: location/of/private/key/file  # 私钥文件的位置
privateKeyPassphrase: '{{passphrase}}'  # 私钥文件的密码
proxyConfiguration:  # 代理配置
    host: hostname.of.proxy  # 代理主机名
    port: port.of.proxy  # 代理端口
    type: HTTP (can be HTTP/HTTPS/SOCKS)  # 代理类型，可以是HTTP/HTTPS/SOCKS
    credentials:  # 代理凭证
        username: proxyUsername  # 代理用户名
        password: `{{proxyPassword}}`  # 代理密码
timeout: 0  # 超时时间，0表示不限制
maxConcurrentConnections: 10  # 最大并发连接数
sessionParams:  # 会话参数
    customKex:  # 自定义密钥交换算法
        - "ecdh-sha2-nistp256"
        - "ecdh-sha2-nistp384"
knownHostsFile: /path/to/known_hosts_file  # 已知主机文件路径
```

### 使用旧版 SFTP 连接器导出

我们通常不建议使用导出任务将数据写回外部来源，以下文档仅用于支持现有的旧版导出任务。所有新的导出必须使用更新的、一流的SFTP 连接器创建。

如果您想从基于代理的来源导出数据，您必须首先将导出任务插件magritte-export-task-source安装到代理中。如有需要，请联系 Palantir 客服支持以获取插件副本。

要导出数据，您必须配置一个导出任务。导航到包含您要导出到的连接器的项目文件夹。右键选择连接器名称，然后选择创建数据连接任务。

在数据连接视图的左侧面板中：

- 验证Source名称是否与您要使用的连接器匹配。
- 添加名为inputDataset的Input。输入数据集是正在导出的 Foundry 数据集。
- 添加名为outputDataset的Output。输出数据集用于运行、调度和监控任务。
- 最后，在文本字段中添加一个 YAML 块以定义任务配置。
连接器和输入数据集在左侧面板中显示的标签不反映在 YAML 中定义的名称。

在创建导出任务 YAML 时使用以下选项：

| 选项 | 是否必需 | 描述 |
| --- | --- | --- |
| directoryPath | 是 | 文件将被写入的目录。路径必须以结尾的/结束。 |
| excludePaths | 否 | 正则表达式列表；名称匹配这些表达式的文件将不会被导出。 |
| rewritePaths | 否 | 参见下面的部分获取更多信息。 |
| uploadConfirmation | 否 | 当值为exportedFiles时，输出数据集将包含已导出的文件列表。 |
| createTransactionFolders | 否 | 启用时，数据将被写入指定directoryPath内的子文件夹。每个子文件夹将为 Foundry 中每个导出的事务具有唯一的名称，并基于事务在 Foundry 中提交的时间。 |
| incrementalType | 否 | 对于增量构建的数据集，设置为incremental以仅导出自上次导出以来发生的事务。 |
| flagFile | 否 | 参见标记文件部分获取更多信息。 |
| spanMultipleViews | 否 | 如果true，则 Foundry 中的多个事务将同时导出。如果false，则单次构建将一次仅导出一个事务。如果启用了增量，文件将按最旧的事务优先导出。 |

### rewritePaths

如果第一个键匹配文件名，键中的捕获组将被替换为值。值本身可以有额外的部分以向文件名添加元数据。

如果值包含：

- ${dt:javaDateExpression}: 该值的这一部分将被替换为文件导出时的时间戳。javaDateExpression遵循DateTimeFormatter ↗模式。
- ${transaction}: 该值的这一部分将被替换为包含该文件的 Foundry 交易 ID。
- ${dataset}: 该值的这一部分将被替换为包含该文件的 Foundry 数据集 ID。
示例：

考虑在 Foundry 数据集中名为 "spark/file_name" 的文件，事务 ID 为transaction_id，数据集 ID 为dataset_id。如果您使用表达式fi.*ame作为键，并使用file_${dt:DD-MM-YYYY}-${transaction}-${dataset}_end作为值，当文件被写入 SFTP 时，它将存储为spark/file_79-03-2023-transaction_id-dataset_id_end。

### 标记文件

连接器可以在所有数据被复制以用于给定构建后，向 SFTP 服务器写入一个空的标记文件。空文件表示内容已准备好供消费，并且不再会被修改。标记文件将写入directoryPath。然而，如果启用了createTransactionFolders，将为每个内容被写入的文件夹创建一个标记文件。如果启用了标记文件，并且标记文件被称为confirmation.txt，则在构建中导出的文件被写入后，所有标记文件将同时被写入。

标记文件在构建结束时写入，而不是在子文件夹导出时写入。

如果 SFTP 服务器中的文件比标记文件更新，这通常表示之前的导出未成功，或者该文件夹的导出正在进行中。

一个简单的导出配置示例如下：

```
Copied!1
2
type: export-sftp-task # 导出任务类型：SFTP任务
directoryPath: export-directory/subdirectory # 指定导出文件的目录路径：export-directory/subdirectory
```

配置导出任务后，选择右上角的保存。

在directoryPath中指定的目录必须已存在于SFTP服务器上。

在directoryPath中指定的目录是相对于根目录的。例如，如果连接配置为rootDirectory: /home/palantir/sftp且directoryPath为export-directory，那么文件将被导出到/home/palantir/sftp/export-directory/。

## 迁移到新的SFTP连接器

无法自动从旧的连接器迁移到新的连接器。新的连接器支持几乎相同的配置选项，应该创建一个新的源以替换旧的源。

请注意：

- 无法从旧的源中检索密码，如果您不再能够访问它们，必须向服务器管理员请求。
- 不再支持privateKeyFile和privateKeyPassphrase，如果使用私钥认证，私钥的内容应直接在源设置中输入。
- 不再支持knownHostsFile，必须在源设置中正确配置base64HostKey。
## 日志

选择数据连接中的日志选项卡以查看来自探索和搭建的日志。这些日志对于调试连接问题很有用。搜索jschLogMessage以查看详细信息。

下面的日志详情显示了一次成功的登录尝试：

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
45
46
47
48
49
50
51
52
jschLogMessage: Connecting to <HOSTNAME> port 2232
jschLogMessage: Connection established
jschLogMessage: Remote version string: SSH-2.0-OpenSSH_8.4p1 Debian-5+deb11u1
jschLogMessage: Local version string: SSH-2.0-JSCH_0.2.12
jschLogMessage: CheckCiphers: chacha20-poly1305@openssh.com
jschLogMessage: CheckKexes: curve25519-sha256,curve25519-sha256@libssh.org,curve448-sha512
jschLogMessage: CheckSignatures: ssh-ed25519,ssh-ed448
jschLogMessage: server_host_key proposal before known_host reordering is: ssh-ed25519,ecdsa-sha2-nistp256,ecdsa-sha2-nistp384,ecdsa-sha2-nistp521,rsa-sha2-512,rsa-sha2-256,ssh-dss,ssh-rsa
jschLogMessage: server_host_key proposal after known_host reordering is: ssh-ed25519,rsa-sha2-512,rsa-sha2-256,ssh-rsa,ecdsa-sha2-nistp256,ecdsa-sha2-nistp384,ecdsa-sha2-nistp521,ssh-dss
jschLogMessage: SSH_MSG_KEXINIT sent
jschLogMessage: SSH_MSG_KEXINIT received
jschLogMessage: server proposal: KEX algorithms: curve25519-sha256,curve25519-sha256@libssh.org,ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-hellman-group-exchange-sha256,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512,diffie-hellman-group14-sha256
jschLogMessage: server proposal: host key algorithms: ssh-ed25519,rsa-sha2-512,rsa-sha2-256,ssh-rsa
jschLogMessage: server proposal: ciphers c2s: chacha20-poly1305@openssh.com,aes128-ctr,aes192-ctr,aes256-ctr,aes128-gcm@openssh.com,aes256-gcm@openssh.com
jschLogMessage: server proposal: ciphers s2c: chacha20-poly1305@openssh.com,aes128-ctr,aes192-ctr,aes256-ctr,aes128-gcm@openssh.com,aes256-gcm@openssh.com
jschLogMessage: server proposal: MACs c2s: umac-64-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha1-etm@openssh.com,umac-64@openssh.com,umac-128@openssh.com,hmac-sha2-256,hmac-sha2-512,hmac-sha1
jschLogMessage: server proposal: MACs s2c: umac-64-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha1-etm@openssh.com,umac-64@openssh.com,umac-128@openssh.com,hmac-sha2-256,hmac-sha2-512,hmac-sha1
jschLogMessage: server proposal: compression c2s: none,zlib@openssh.com
jschLogMessage: server proposal: compression s2c: none,zlib@openssh.com
jschLogMessage: server proposal: languages c2s:
jschLogMessage: server proposal: languages s2c:
jschLogMessage: client proposal: KEX algorithms: curve25519-sha256,curve25519-sha256@libssh.org,ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-hellman-group-exchange-sha256,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512,diffie-hellman-group14-sha256,diffie-hellman-group14-sha1,diffie-hellman-group-exchange-sha1,diffie-hellman-group1-sha1,ext-info-c
jschLogMessage: client proposal: host key algorithms: ssh-ed25519,rsa-sha2-512,rsa-sha2-256,ssh-rsa,ecdsa-sha2-nistp256,ecdsa-sha2-nistp384,ecdsa-sha2-nistp521,ssh-dss
jschLogMessage: client proposal: ciphers c2s: aes128-ctr,aes192-ctr,aes256-ctr,aes128-gcm@openssh.com,aes256-gcm@openssh.com,aes128-cbc,3des-ctr,3des-cbc,blowfish-cbc,aes192-cbc,aes256-cbc
jschLogMessage: client proposal: ciphers s2c: aes128-ctr,aes192-ctr,aes256-ctr,aes128-gcm@openssh.com,aes256-gcm@openssh.com,aes128-cbc,3des-ctr,3des-cbc,blowfish-cbc,aes192-cbc,aes256-cbc
jschLogMessage: client proposal: MACs c2s: hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha1-etm@openssh.com,hmac-sha2-256,hmac-sha2-512,hmac-sha1,hmac-md5,hmac-sha1-96,hmac-md5-96
jschLogMessage: client proposal: MACs s2c: hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha1-etm@openssh.com,hmac-sha2-256,hmac-sha2-512,hmac-sha1,hmac-md5,hmac-sha1-96,hmac-md5-96
jschLogMessage: client proposal: compression c2s: none
jschLogMessage: client proposal: compression s2c: none
jschLogMessage: client proposal: languages c2s:
jschLogMessage: client proposal: languages s2c:
jschLogMessage: kex: algorithm: curve25519-sha256
jschLogMessage: kex: host key algorithm: ssh-ed25519
jschLogMessage: kex: server->client cipher: aes128-ctr MAC: hmac-sha2-256-etm@openssh.com compression: none
jschLogMessage: kex: client->server cipher: aes128-ctr MAC: hmac-sha2-256-etm@openssh.com compression: none
jschLogMessage: SSH_MSG_KEX_ECDH_INIT sent
jschLogMessage: expecting SSH_MSG_KEX_ECDH_REPLY
jschLogMessage: ssh_eddsa_verify: ssh-ed25519 signature true
jschLogMessage: Host '[<HOSTNAME>]:2232' is known and matches the EDDSA host key
jschLogMessage: SSH_MSG_NEWKEYS sent
jschLogMessage: SSH_MSG_NEWKEYS received
jschLogMessage: SSH_MSG_SERVICE_REQUEST sent
jschLogMessage: SSH_MSG_EXT_INFO received
jschLogMessage: server-sig-algs=<ssh-ed25519,sk-ssh-ed25519@openssh.com,ssh-rsa,rsa-sha2-256,rsa-sha2-512,ssh-dss,ecdsa-sha2-nistp256,ecdsa-sha2-nistp384,ecdsa-sha2-nistp521,sk-ecdsa-sha2-nistp256@openssh.com,webauthn-sk-ecdsa-sha2-nistp256@openssh.com>
jschLogMessage: SSH_MSG_SERVICE_ACCEPT received
jschLogMessage: Authentications that can continue: publickey,keyboard-interactive,password
jschLogMessage: Next authentication method: publickey
jschLogMessage: PubkeyAcceptedAlgorithms = ssh-ed25519,ecdsa-sha2-nistp256,ecdsa-sha2-nistp384,ecdsa-sha2-nistp521,rsa-sha2-512,rsa-sha2-256,ssh-rsa
jschLogMessage: PubkeyAcceptedAlgorithms in server-sig-algs = [ssh-ed25519, ecdsa-sha2-nistp256, ecdsa-sha2-nistp384, ecdsa-sha2-nistp521, rsa-sha2-512, rsa-sha2-256, ssh-rsa]
jschLogMessage: rsa-sha2-512 preauth success
jschLogMessage: rsa-sha2-512 auth success
jschLogMessage: Authentication succeeded (publickey).
```

### 代码说明

这段代码是一个SSH连接日志的输出，描述了客户端和服务器之间建立SSH连接的过程。以下是关键步骤的解释：

- 连接建立：客户端尝试连接到服务器<HOSTNAME>的端口2232。
- 版本信息：显示了客户端和服务器所使用的SSH协议版本。
- 加密算法检查：列出了可用的加密算法、密钥交换算法和签名算法。
- 主机密钥提议：展示了在已知主机重新排序前后的主机密钥提议。
- 密钥交换：进行密钥交换协议，选择了curve25519-sha256算法。
- 加密和消息认证：配置了用于加密和认证的算法。
- 认证：使用公钥认证方法，公钥认证成功。
这段日志提供了SSH连接建立和认证的详细过程，适用于调试和分析SSH连接问题。
请注意，在上述示例中，服务器支持的主机密钥算法包括ssh-ed25519、rsa-sha2-512、rsa-sha2-256和ssh-rsa。如果使用ssh-ed25519时出现任何连接问题，您可以将主机密钥算法设置更改为rsa-sha2-512。

## 扩展协商

如果客户端和服务器都支持，SFTP 协议允许客户端使用协议的高级功能。对于大多数行业标准的 SFTP 实现，我们建议保持扩展启用。然而，如果存在兼容性问题，扩展可能会导致连接失败。Foundry SFTP 连接器允许根据需要禁用扩展。一般来说，最佳实践是尽量少禁用扩展，而不是禁用所有扩展。
