来源: https://palantir.com/docs/zh/foundry/available-connectors/hubspot/

# Hubspot

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Hubspot

连接Foundry到HubSpot，以导入数据并创建、修改和删除HubSpot中的记录。

## 源配置

在配置HubSpot连接之前，生成一个HubSpot API密钥。您可以按照以下步骤获取现有的API密钥或生成新的HubSpot API密钥。

- 在您的Hubspot账户中，选择主导航栏中的设置图标。
- 在左侧边栏菜单中，导航到Integrations > API Key。
- 如果您的账户从未生成过密钥，选择Generate API Key。如果API密钥已经存在，选择Show以查看它。
您现在可以在api-key连接属性中设置检索到的密钥。

以下是Hubspot连接的最基本结构：

```
Copied!1
2
3
type: hubspot
config:
  apiKey: '{{api-key}}'  # HubSpot的API密钥
```

在这个YAML配置文件中，type指定了目标服务为HubSpot，而config中定义了具体的配置参数。apiKey是一个占位符，用于插入实际的HubSpot API密钥。
