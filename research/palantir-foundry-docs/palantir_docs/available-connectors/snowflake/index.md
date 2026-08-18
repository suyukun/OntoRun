来源: https://palantir.com/docs/zh/foundry/available-connectors/snowflake/

# Snowflake

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Snowflake

将Foundry连接到Snowflake以读取和同步Snowflake与Foundry之间的数据。

## 支持的功能

| 功能 | 状态 |
| --- | --- |
| 探索 | 🟢 一般可用 |
| 批量导入 | 🟢 一般可用 |
| 增量 | 🟢 一般可用 |
| 虚拟表 | 🟢 一般可用 |
| 导出任务 | 🟡 即将停用 |

## 设置

- 打开数据连接应用程序，并在屏幕右上角选择+ 新建来源。
- 从可用的连接器类型中选择Snowflake。
- 选择通过互联网使用直接连接或通过中介代理连接。
- 根据以下部分中的信息，按照额外的配置提示继续设置您的连接器。
了解更多有关在Foundry中设置连接器的信息。

## 连接详情

| 选项 | 必须的? | 描述 |
| --- | --- | --- |
| Account identifier | 是 | 这是在“.snowflakecomputing.com”之前的标识符。有关更多详情，请参阅Snowflake的官方文档 ↗。 |
| Roles | 否 | 这是连接所用的默认角色，以防提供的凭据具有访问多个角色的权限。 |
| Database | 是 | 指定连接后要使用的默认数据库。 |
| Schema | 否 | 选项以指定连接后要使用的默认模式。如果未指定，将提供凭据范围内的所有模式。 |
| Warehouse | 否* | 连接后要使用的虚拟仓库。在注册的虚拟表情况下，这将用于任何源端计算。 |
| Credentials | 是 | 选项1：用户名和密码提供用户名和密码。我们建议使用服务凭据而不是单个用户凭据。选项2：密钥对认证提供用户名和私钥。有关配置密钥对认证的详情，请参阅Snowflake的官方文档 ↗。选项3：外部OAuth (OIDC)按照显示的源系统配置说明设置外部OAuth。有关外部OAuth的详情，请参阅Snowflake的官方文档 ↗和我们的文档，了解OIDC如何与Foundry协作。对于所有凭据选项，请确保提供的用户和角色对目标数据库和模式具有使用权限，并对目标表具有选择权限。在注册虚拟表时，用户及其角色还应具有对仓库的使用权限。 |
| Network Connectivity | 是** | 在Snowflake中运行SELECT SYSTEM$ALLOWLIST()并确保至少将SNOWFLAKE_DEPLOYMENT和STAGE的条目添加为Foundry中的出口策略。有关更多详情，请参阅下面的网络部分。 |

* 仓库详细信息对于同步Foundry数据集是非必填的，但对于注册虚拟表是必须的。** 网络出口策略对于直接连接是必须的，但对于基于代理的连接不是。

## 网络

要在Snowflake和Foundry之间启用直接连接，必须在数据连接应用程序中设置来源时添加适当的出口策略。

要识别要列入允许名单的Snowflake帐户的主机名和端口号，可以在Snowflake控制台中运行以下命令。确保至少将SNOWFLAKE_DEPLOYMENT和STAGE的条目添加为Foundry中的出口策略。

```
Copied!1
2
3
4
5
SELECT t.VALUE:type::VARCHAR as type,  -- 将JSON解析后的type字段转换为VARCHAR类型，并命名为type
       t.VALUE:host::VARCHAR as host,  -- 将JSON解析后的host字段转换为VARCHAR类型，并命名为host
       t.VALUE:port as port            -- 直接选择JSON解析后的port字段
FROM TABLE(FLATTEN(input => PARSE_JSON(SYSTEM$ALLOWLIST()))) AS t;
-- PARSE_JSON(SYSTEM$ALLOWLIST())解析系统白名单并将其展开为一个表格，t为临时表别名
```

请参阅Snowflake的官方文档 ↗以获取有关识别主机名和端口号以进行允许列表的更多信息。

在某些情况下（取决于您的Foundry和Snowflake环境），可能需要通过PrivateLink建立连接。通常情况下，Foundry和Snowflake由相同的CSP托管（例如，AWS-AWS或Azure-Azure）。如果您认为这适用于您的设置，请联系您的Palantir代表以获取更多指导。

对于依赖于与您的Foundry实例位于同一区域的S3桶的出口策略，请确保您已完成我们Amazon S3桶策略文档中详细描述的受影响桶的额外配置步骤。

## 虚拟表

本节提供了有关使用Snowflake源的虚拟表的更多详细信息。当同步到Foundry数据集时，本节不适用。

| 虚拟表功能 | 状态 |
| --- | --- |
| 源格式 | 🟢 一般可用：表、视图和物化视图 |
| 手动注册 | 🟢 一般可用 |
| 自动注册 | 🟢 一般可用 |
| 下推计算 | 🟢 一般可用；通过Snowflake Spark连接器 ↗可用 |
| 增量 | 🟢 一般可用：仅APPEND[1] |

使用虚拟表时，请记住以下源配置要求：

- 必须将源设置为直接连接。虚拟表不支持使用中介代理。
- 确保如本文档网络部分中所述建立双向连接和允许列表。
- 如果在代码库中使用虚拟表，请参阅虚拟表文档以获取所需的额外源配置的详细信息。
- 必须在连接详情中指定仓库。
- 提供的凭证必须具有仓库的使用权限。
有关更多详细信息，请参阅上面的连接详情部分。

[1]为了启用由Snowflake虚拟表支持的管道的增量支持，确保为适当的保留期限启用了变更跟踪 ↗和时间旅行 ↗。此功能依赖于CHANGES ↗。在Python变换中支持current和added读取模式。这些将根据METADATA$ACTION列揭示变更提要的相关行。在Python变换中，将提供METADATA$ACTION、METADATA$ISUPDATE、METADATA$ROW_ID列。

## 数据模型

请注意，类型为array↗、object↗和variant↗的列将被Foundry解析为类型字符串。这是由于源的可变类型。

例如，Snowflake数组[ 1, 2, 3 ]将被Foundry解释为字符串"[1,2,3]"。

请参阅Snowflake的官方文档 ↗以获取更多详细信息。
