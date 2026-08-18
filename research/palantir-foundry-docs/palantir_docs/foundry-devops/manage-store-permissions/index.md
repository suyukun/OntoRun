来源: https://palantir.com/docs/zh/foundry/foundry-devops/manage-store-permissions/

# 管理商店权限

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 管理商店权限

Marketplace 商店可以是您 Foundry Enrollment 中的本地商店或远程商店。本地 Marketplace 商店可以在项目或文件夹中找到，并将继承其所在项目或文件夹的权限。远程商店是在一个 Foundry enrollment 上创建的，然后在其他 enrollments 上可用。远程商店的权限在控制面板中配置。了解更多关于配置远程商店访问的信息。

## 查看权限

要在 DevOps 或 Marketplace 中查看本地 Marketplace 商店，您需要具有marketplace:read-local-marketplace操作，这通常通过只读角色授予。远程商店的查看权限在控制面板中配置。

## 安装产品权限

要从本地或远程商店安装产品，您必须能够查看商店并具有marketplace:install-from-local-marketplace操作，这通常通过只读角色授予。

对于作为此安装输入选择的每个资源，您必须具有marketplace:use-resource-as-input操作，这也通常通过只读角色授予。

此外，您可以安装的位置，通常是 Space 和 Ontology，需要marketplace:install-in操作，这通常通过编辑者角色授予。

在每次安装时，Marketplace 将在所选 Space 中创建一个新项目或安装到现有项目中。为此，您需要在 Space、所选项目或文件夹上具有marketplace:install-in操作。此权限通常通过编辑者角色授予。

您还必须能够访问商店中存在的至少一个组织权限标记。然而，这些权限标记通常从项目继承。

### 应用于产品安装的组织权限标记

Marketplace 商店必须包括您想要安装的 Spaces 的所有相关组织权限标记。例如，如果您想将商店安装到包含组织 A 和 B 的 Space 中，但 Marketplace 商店仅有组织 A 的权限标记，您将需要组织 A 的Expand access权限，因为您正在将内容从组织 A 扩展到 B。在安装过程中，您可以选择仅将组织 A 的权限标记应用于您的产品安装，这将消除扩展访问权限的需要。或者，您可以将组织 B 的权限标记添加到商店，但此选项将允许更多用户从商店安装产品。

## 创建商店权限

要创建本地商店，您必须在项目或文件夹中具有marketplace:create-local-marketplace操作，这通常通过编辑者角色授予。

目前，远程商店只能由 Palantir 创建。

## 编辑产品权限

要在本地商店中创建或编辑产品，用户必须具有marketplace:create-block、marketplace:edit-block-set和marketplace:upload-attachment操作，这通常会授予编辑者角色。

远程商店在 DevOps 中不可编辑。

## 导出产品权限

要从本地商店导出产品，用户必须具有marketplace:export-block-set操作，这通常会授予拥有者角色。目前，用户无法从远程商店导出产品。

## 导入产品权限

要将产品导入本地商店，用户必须具有marketplace:import-blockset-with-provenance操作，这通常会授予拥有者角色。目前，用户无法将产品导入远程商店。

## 编辑商店标签权限

要编辑本地商店的标签，用户必须具有marketplace:edit-local-marketplace操作，这通常会授予编辑者角色。目前，用户无法编辑远程商店的标签。
