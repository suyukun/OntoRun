来源: https://palantir.com/docs/zh/foundry/sap/sap-source-setup/

# 创建一个新的来源

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 创建一个新的来源

为了使Foundry连接到Palantir Foundry Connector 2.0 for SAP Applications（“连接器”），需要在数据连接应用中配置一个来源。该配置需要一个代理、用于连接的用户凭据和SAP源系统的URL。

要创建一个SAP来源，请按照以下步骤操作：

- 在侧边栏中导航到数据连接应用。
在侧边栏中导航到数据连接应用。

- 选择添加自定义来源选项。
选择添加自定义来源选项。

- 选择通过代理连接选项。
选择通过代理连接选项。

- 为来源命名并指定位置。
为来源命名并指定位置。

- 完成来源设置要求：选择SAP网络中的代理。在自定义YAML部分，按如下方式填写定义。Copied!123type: magritte-sap-source
  url: https://<host>:<port>/sap/palantir
  usernamePassword: <username>:{{password}}用户名和密码是为Foundry连接SAP而创建的技术用户的凭据。主机是相关SAP应用服务器的所在位置。端口是ICM（Internet Communication Manager，互联网通信管理器）的默认HTTPS（或HTTP）端口。表达式{{password}}应按原样书写。然后可以在对话框右侧的加密值下输入密码，它将被加密。
完成来源设置要求：

- 选择SAP网络中的代理。
选择SAP网络中的代理。

- 在自定义YAML部分，按如下方式填写定义。Copied!123type: magritte-sap-source
  url: https://<host>:<port>/sap/palantir
  usernamePassword: <username>:{{password}}用户名和密码是为Foundry连接SAP而创建的技术用户的凭据。主机是相关SAP应用服务器的所在位置。端口是ICM（Internet Communication Manager，互联网通信管理器）的默认HTTPS（或HTTP）端口。表达式{{password}}应按原样书写。然后可以在对话框右侧的加密值下输入密码，它将被加密。
在自定义YAML部分，按如下方式填写定义。

```
Copied!1
2
3
  type: magritte-sap-source
  url: https://<host>:<port>/sap/palantir
  usernamePassword: <username>:{{password}}
```

- 用户名和密码是为Foundry连接SAP而创建的技术用户的凭据。
- 主机是相关SAP应用服务器的所在位置。
- 端口是ICM（Internet Communication Manager，互联网通信管理器）的默认HTTPS（或HTTP）端口。
表达式{{password}}应按原样书写。然后可以在对话框右侧的加密值下输入密码，它将被加密。

- 保存来源定义。
保存来源定义。

## 配置

以下是可以在来源上配置的额外参数。

| 参数 | 必需？ | 默认 | 描述 |
| --- | --- | --- | --- |
| url | Y |  | SAP附加服务端点的基本URL。 |
| usernamePassword | Y |  | 用户名和密码是为Foundry连接SAP而创建的技术用户的凭据。 |
| useKernelJsonSerialization | N | false | 开启内核JSON序列化以处理从SAP返回的分页数据。仅适用于JSON格式的数据：如果设置为true且useTsvFormat:true，则检查将失败。 |
| useTsvFormat | N | false | 开启使用TSV格式处理从SAP返回的分页数据（相对于JSON）。 |
| output | N | 50,000行 | 定义从SAP返回的最大文件大小（行或字节）。 |
| convertDatesToStrings | N | false | 将所有日期作为字符串导入此来源。 |
| proxy | N | 无 | 连接SAP的代理配置。 |
| cacheConfigurations | N | 无 | 用于配置不同SAP对象类型缓存超时的缓存配置。 |

### 配置每个Parquet文件的最大大小

可以在特定同步（针对该特定同步）或在来源上（针对所有同步）定义Foundry数据集中每个Parquet文件的最大文件大小。

如果您希望更改某个来源下所有同步的每个Parquet文件的最大大小，可以在来源配置中进行配置。

示例：

```
Copied!1
2
3
4
5
output:
  maxFileSize:
    type: rows
    rows:
      max: 10000  # 设置最大行数为10000行
```

```
Copied!1
2
3
4
5
output:
  maxFileSize:
    type: bytes
    bytes:
      approximateMax: 400MB  # 近似最大值为400MB
```

指定的最大字节大小只是近似值。生成的文件大小可能略小或略大。

如果指定最大字节大小，则字节数需要至少是Parquet写入器内存缓冲区大小的两倍（默认值为128MB）。
