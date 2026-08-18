来源: https://palantir.com/docs/zh/foundry/analytics-connectivity/tableau-oauth-setup/

# Tableau OAuth 设置

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Tableau OAuth 设置

Tableau 支持通过 OAuth 认证到 Foundry。这意味着用户无需手动输入词元，而是可以通过网络浏览器登录 Foundry。有关 Tableau 中 OAuth 的概述，请参阅 Tableau 的OAuth 连接 ↗文章。

需要 Foundry 管理员权限才能启用此 OAuth 集成。此外，如果您要为 Tableau Server 启用 OAuth 集成，则需要 Tableau 管理员权限，并且必须重新启动 Tableau Server。

## 第 1 部分：为 Tableau Desktop 启用 OAuth 客户端

- 按照说明访问控制面板中的第三方应用程序配置页面。
- 在应用程序列表中找到Tableau Desktop；从操作菜单中选择启用设置。
- 使用切换开关启用应用程序。
当 Tableau 用户使用 OAuth 认证到 Foundry 时，会强制执行个人用户权限。如果您使用了项目访问或权限标记限制面板来配置第三方应用程序的限制，这些限制将叠加在用户的个人权限之上。

此时，Tableau Desktop 用户可以按照说明使用 OAuth 认证到 Foundry。

## 第 2 部分：为 Tableau Server 配置 OAuth 客户端

按照以下说明启用发布到 Tableau Server 的报告的 OAuth 认证。

### 步骤 1：为 Tableau Server 注册第三方应用程序

在与上述相同的第三方应用程序页面上，选择新建应用程序以创建新的第三方应用程序：

- 在详细信息步骤中，将应用程序命名为<ORGANIZATION> Tableau Server，替换为您自己的组织名称。
- 在客户端类型步骤中，选择机密客户端。
- 在授权授予类型步骤中，选择授权代码授予并将重定向 URL设置为https://<YOUR_SERVER>/auth/add_oauth_token，其中<YOUR_SERVER>是您的 Tableau Server 主机名。
创建应用程序并安全地存储客户端 ID 和密钥。

### 步骤 2：配置 Tableau Server

在服务器上运行以下命令，替换您在上一步中获得的客户端 ID、密钥和重定向 URL：

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
tsm configuration set -k oauth.config.clients -v "[{\"oauth.config.id\":\"FoundryJdbc\", \"oauth.config.client_id\":\"<YOUR_CLIENT_ID>\", \"oauth.config.client_secret\":\"<YOUR_CLIENT_SECRET>\", \"oauth.config.redirect_uri\":\"https://<YOUR_TABLEAU_SERVER>/auth/add_oauth_token\"}]" --force-keys

# 这是一个用来设置Tableau服务器OAuth配置的命令。
# 1. `tsm configuration set` 是用来配置Tableau Server Manager (TSM) 的命令。
# 2. `-k oauth.config.clients` 指定了要配置的键是OAuth客户端配置。
# 3. `-v "[{...}]"` 指定了配置的值，这里是一个JSON格式的字符串。
#    - `oauth.config.id` 是OAuth配置的ID，这里设定为 "FoundryJdbc"。
#    - `oauth.config.client_id` 是OAuth客户端ID，需要替换为你的客户端ID `<YOUR_CLIENT_ID>`。
#    - `oauth.config.client_secret` 是OAuth客户端密钥，需要替换为你的客户端密钥 `<YOUR_CLIENT_SECRET>`。
#    - `oauth.config.redirect_uri` 是OAuth重定向URI，需要替换为你的Tableau服务器地址 `<YOUR_TABLEAU_SERVER>`。
# 4. `--force-keys` 表示强制更新指定的键，即使这些键已经存在。
```

### 步骤3：重启Tableau服务器

通过运行以下命令重启Tableau服务器：

```
tsm pending-changes apply
```

## tsm pending-changes apply是一个命令行工具，用于在 Tableau Server Management (TSM) 中应用挂起的更改。这个命令通常用于在对 Tableau Server 的配置进行了更改之后，将这些更改应用到服务器上。

## 使用说明

### Tableau Desktop

在Tableau Desktop中，用户现在可以按照说明通过Foundry OAuth认证选项进行身份验证。

### Tableau Server

在发布到Tableau Server时，可以配置报告以提示访客在打开报告时通过OAuth进行身份验证。这样，实时查询将使用访客的权限运行。

要进行配置，请在Tableau Desktop中使用Foundry OAuth认证选项开发报告。当您准备发布时，选择认证的提示选项。当用户在Tableau Server上查看报告时，实时连接将使用访客的凭据刷新。
