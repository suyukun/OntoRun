来源: https://palantir.com/docs/zh/foundry/platform-security-management/manage-users/

# 管理用户

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 管理用户

通过导航侧边栏进入账户 > 设置来访问用户管理页面。然后，在侧边栏的平台设置部分选择用户。

在这里，您可以查看 Foundry 中用户的不同信息：

- 用户 ID：用户的永久唯一 ID。
- 组织：用户所属的组织。
- 组：用户所属组的列表。
- 属性：以键值格式表示的用户信息，通常被其他 Foundry 服务使用。例如，用户可能有一个用于地理区域的属性，可以用来限制用户在 Ontology 中可以看到的对象。
了解更多关于限制视图的信息。

## 预注册用户

具有预注册权限的平台管理员可以在用户首次登录 Foundry 之前对其执行操作。管理员可以创建用户名，给予用户适当的组成员资格，指派组织和权限标记访问等，以确保新用户在首次登录时能够正确访问资源。

创建的用户名需要与用户的登录用户名完全匹配，以便预注册操作能够正常工作。

## 用户不活跃

如果 Foundry 用户账户在 30 天内没有成功登录，则会自动被视为不活跃账户。不活跃账户在 Foundry 中的行为与活跃账户相同，唯一不同的是不活跃用户账户的所有词元在账户不活跃时均无效。

在成功登录后，不活跃用户账户将自动设置为活跃状态，重新启用所有被禁用的词元。不需要管理员采取任何行动来重新激活。

可以将某些 Foundry 组和身份验证域中的用户排除在此不活跃行为之外。有关这些排除的更多信息，请联系您的 Palantir 代表。

如果用户在登录时遇到以下信息：“您的账户已锁定。请联系您的支持人员解锁，然后重试。”，请联系您的 Palantir 代表以解锁账户。

## 故障排除

### “您的账户已被禁用”出错

如果登录失败，并显示出错信息您的账户已被禁用，这意味着用户账户已被删除。您可以联系管理员，通过getDeletedUsers和undeleteExternalUser端点分别查找和“取消删除”账户。具有管理成员资格权限的组织管理员可以调用这些端点。下面列出了示例 curl 请求。

#### 通过 getDeletedUsers 查找已删除的用户

此步骤是非必填的，仅在未知已删除用户的用户 ID 时需要。

```
Copied!1
curl -XGET -H "Authorization: Bearer $TOKEN" '<FOUNDRY_URL>/multipass/api/administration/users/deleted?pageSize=<NUMBER_OF_RESULTS_TO_RETURN>&pageToken=<PAGE_START_TOKEN>'
```

此命令使用curl发送一个 HTTP GET 请求，获取已删除用户的信息。以下是各部分的含义：

- -XGET：指定请求方法为 GET。
- -H "Authorization: Bearer $TOKEN"：在请求头中添加授权信息，使用 Bearer Token 进行身份验证。
- '<FOUNDRY_URL>/multipass/api/administration/users/deleted'：请求的 URL，替换<FOUNDRY_URL>为实际的服务器地址。
- pageSize=<NUMBER_OF_RESULTS_TO_RETURN>：查询参数，指定返回结果的数量。
- pageToken=<PAGE_START_TOKEN>：查询参数，用于分页，指定从哪个位置开始返回结果。
```
该命令通常用于从系统中分页获取已删除用户的列表，确保替换 URL 和参数为实际值。
**注意：** 最大页面大小为1000。

#### 通过 undeleteExternalUser 恢复已删除用户
```bash
# 使用 cURL 命令恢复被删除的用户账户
# -XPOST 指定使用 POST 方法
# -H 用于设置 HTTP 请求头，这里是设置授权头，其中 $TOKEN 是访问令牌
# <FOUNDRY_URL> 是 API 的基础 URL
# <USER_ID> 是要恢复的用户的唯一标识符

curl -XPOST -H "Authorization: Bearer $TOKEN" '<FOUNDRY_URL>/multipass/api/administration/users/<USER_ID>/undelete/external'
```
