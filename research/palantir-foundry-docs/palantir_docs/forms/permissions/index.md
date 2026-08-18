来源: https://palantir.com/docs/zh/foundry/forms/permissions/

# 权限

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 权限

在大多数情况下，权限应保持默认设置。自定义权限往往会在追踪平台对不同用户的操作时造成挑战。

## 创建表单

默认情况下，所有用户都可以制作有电子表格支持的表单或无来源的表单。只有部分用户可以创建由对象类型支持的表单。

### 详情

要创建表单，您需要在表单所在的文件系统文件夹中创建资源的权限。

您还需要基于表单支持的数据的特定权限：

- 对于由对象支持的表单：fforms:form-definition:create-phonograph-form
- 对于由电子表格支持的表单：fforms:form-definition:create-fusion-form
- 对于没有支持来源创建的表单：fforms:form-definition:create-no-origin-form
以下用户组默认拥有这些权限，这些可以在Foundry Forms后端配置中被覆盖：

- fforms:form-definition:create-phonograph-form赋予组 "fforms-admins" 和 "Platform Administrators"。
- fforms:form-definition:create-fusion-form赋予所有用户。
- fforms:form-definition:create-no-origin-form赋予所有用户。
## 创建新条目

默认情况下，用户只需要对他们填写的表单具有只读权限即可创建新条目。在可视化编辑器的设置面板中关闭允许没有读取或写入权限的新对象创建，以限制只有在支持对象类型或电子表格上具有权限的用户才能填写表单。

### 详情

用户可能无法创建新条目的原因如下：

- 表单可能没有一个已发布的、可填写的版本。
- 如果表单中有任何附件字段，用户必须有权限将文件上传到附件文件夹。
默认情况下，fforms:form-definition:view赋予具有compass:view权限的表单用户。这可以在Foundry Forms后端配置中被覆盖。

## 编辑现有条目

与创建新条目一样，您需要查看表单的权限。此外，您需要编辑支持来源的权限，无论它是对象类型还是电子表格。

### 详情

允许没有读取或写入权限的新对象创建选项不影响编辑现有条目。目前没有相应的编辑条目选项。然而，Foundry Forms之前支持此功能，一些旧表单可能仍允许在没有来源权限的情况下编辑条目以便向后兼容。

与创建新条目一样，仍然必须存在一个已发布的版本，并且您需要上传文件到附件字段中引用的任何文件夹的权限。

## 保存表单定义的更改

要编辑表单，您需要该表单的编辑者权限。如果您想限制谁可以更改用户看到的表单版本，您可以通过限制谁有权限发布表单来实现。

### 详情

要编辑未发布版本的表单，您需要该表单的fforms:form-definition:edit权限。要编辑已发布版本的表单，您还需要所有发布该表单版本所需的权限。

默认情况下，fforms:form-definition:edit来自该表单的compass:edit。这可以在Foundry Forms后端配置中被覆盖。

## 发布表单版本

要发布表单，您需要该表单的编辑者权限。如果您想限制只有具有管理权限的用户才能发布表单，您可以将fforms:form-definition:manage从compass:edit移动到后端配置中的compass:manage扩展中。

### 详情

要发布表单版本，您需要该表单的fforms:form-definition:manage权限。您还需要：

- 管理表单来源的权限
- 对附件字段中使用的任何文件夹的compass:manage权限
默认情况下，fforms:form-definition:manage来自该表单的compass:edit。这些选项可以在Foundry Forms后端配置中更改，但对附件文件夹的要求不能更改。

## 创建表单新版本

要创建表单的新版本，您需要该表单的编辑者权限。您还需要属于能够制作对象支持或电子表格支持表单的组，具体取决于您的应用案例。

### 详情

要创建表单的新版本，您需要创建该来源类型表单的权限。您还需要fforms:form-definition:create-new-version和管理表单来源的权限。

默认情况下，fforms:form-definition:create-new-version来自compass:edit，但这可以在后端配置中更改。

## 更改表单的响应目标

要更改表单的响应目标，您需要：

- 创建该来源类型表单的权限
- 管理表单来源的权限
- 保存表单定义的更改的权限，尽管您不需要对附件字段中出现的任何文件夹的权限。
## 更改表单版本的名称

要更改表单版本的名称，您需要该表单的编辑者权限。如果表单是已发布版本，您将需要管理它的权限并且管理其来源。

### 详情

要管理已发布的表单，您需要该表单的fforms:form-definition:manage权限，默认来自compass:edit。这可以在后端配置中被覆盖。

## 删除表单

要删除表单，您需要该表单的编辑者权限。您将需要fforms:form-definition:manage权限，默认来自compass:edit。这可以在后端配置中更改。

## 取消发布表单

要取消发布表单的已发布版本，您需要该表单的编辑者权限。您还将需要fforms:form-definition:manage权限，默认来自compass:edit。这可以在后端配置中更改。

## 管理表单来源

此权限是多种操作所必需的。根据表单的支持类型，需要不同的权限：

- fforms:form-definition:create-phonograph-form：表单由对象类型支持
- fforms:form-origin:manage：表单由电子表格支持
fforms:form-definition:create-phonograph-form赋予 "Platform Administrators" 组的成员。fforms:form-origin:manage赋予在支持电子表格上具有fusion:edit-document权限的用户。这些可以在Foundry Forms后端配置中更改。
