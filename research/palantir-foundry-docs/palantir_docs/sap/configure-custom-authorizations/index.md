来源: https://palantir.com/docs/zh/foundry/sap/configure-custom-authorizations/

# 配置自定义授权和角色管理

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 配置自定义授权和角色管理

Palantir Foundry 2.0 版连接器以支持自 SP16 及更高版本的自定义授权管理。角色和对象访问定义可以在透明表上定义，而不是 SAP 标准授权管理 (PFCG)。

要启用此功能，请运行/PALANTIR/PARAM事务并维护以下参数值：

- Param ID:SYSTEM
- Param Name:AUTH_CHECK_SOURCE
- Param Value:TABLE
如果启用了此功能，将不会检查现有内容角色。要停用此功能，请删除参数或将参数值从TABLE更改为PFCG。

要创建自定义角色，请按照以下步骤操作：

- 运行/PALANTIR/AUTH_01事务以定义新角色。角色ID是角色的唯一标识符。它可以在所有上下文中使用。对象类型是 Foundry SAP 连接器支持的对象类型：TABLEREMOTETABLEINFOPROVIDERREMOTEINFOPROVIDERBEXFUNCTIONREMOTEFUNCTIONSLTEXTRACTOR对象是主要提取对象。例如，如果对象类型是TABLE，则对象应为表名（BSEG或B*；支持通配符）。配置Exc/Inc设置以允许或拒绝访问。使用Exclude拒绝访问对象。
运行/PALANTIR/AUTH_01事务以定义新角色。

- 角色ID是角色的唯一标识符。它可以在所有上下文中使用。
角色ID是角色的唯一标识符。它可以在所有上下文中使用。

- 对象类型是 Foundry SAP 连接器支持的对象类型：TABLEREMOTETABLEINFOPROVIDERREMOTEINFOPROVIDERBEXFUNCTIONREMOTEFUNCTIONSLTEXTRACTOR
对象类型是 Foundry SAP 连接器支持的对象类型：

- TABLE
- REMOTETABLE
- INFOPROVIDER
- REMOTEINFOPROVIDER
- BEX
- FUNCTION
- REMOTEFUNCTION
- SLT
- EXTRACTOR
- 对象是主要提取对象。例如，如果对象类型是TABLE，则对象应为表名（BSEG或B*；支持通配符）。
对象是主要提取对象。例如，如果对象类型是TABLE，则对象应为表名（BSEG或B*；支持通配符）。

- 配置Exc/Inc设置以允许或拒绝访问。使用Exclude拒绝访问对象。
配置Exc/Inc设置以允许或拒绝访问。使用Exclude拒绝访问对象。

- 运行/PALANTIR/AUTH_02事务并指派角色给用户和上下文。用户是 Foundry 用于连接到 SAP 的用户，在 Foundry 源配置中定义。如果没有远程代理、提取器或 SLT，则上下文应留空。同一个角色可以用于多个上下文和用户。
运行/PALANTIR/AUTH_02事务并指派角色给用户和上下文。

- 用户是 Foundry 用于连接到 SAP 的用户，在 Foundry 源配置中定义。
- 如果没有远程代理、提取器或 SLT，则上下文应留空。
- 同一个角色可以用于多个上下文和用户。