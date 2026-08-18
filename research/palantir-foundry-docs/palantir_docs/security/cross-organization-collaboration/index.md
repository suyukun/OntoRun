来源: https://palantir.com/docs/zh/foundry/security/cross-organization-collaboration/

# 跨组织协作

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 跨组织协作

## 概述

我们的航班警报收件箱应用非常成功，现在已成为我们支持团队工作的重要组成部分。Sky Industries 的领导层已向多家合作航空公司展示了该应用，并获得了极高的评价。某家航空公司，Sunrise Airline，现在希望将运营工作流程提升到一个新水平。他们提议将所有导致乘客延误的内部维护问题与 Sky Industries 共享。通过将维护问题数据与我们的航班延误数据结合，Sky Industries 和 Sunrise Airlines 可以合作解决重复出现的维护问题，并减少未来 Sunrise Airline 飞机的延误。

Foundry 平台是为支持跨组织协作而搭建的。退一步看，组织是应用于项目的访问要求，用于在用户组和资源之间强制严格的隔离。每个用户仅属于一个组织，但可以成为多个组织的客座成员。

一个注册代表了 Foundry 平台的一个实例，由一个或多个组织组成。在大多数情况下，公司会有一个组织，所有用户都在其注册中。有些注册有多个组织，以强制在用户组之间进行严格的隔离，例如，当多家公司在同一个 Foundry 平台上协作时。

在我们的例子中，我们一直在名为 Sky Industries 的单个 Foundry 注册中操作，该注册只有一个同名的组织。为了让 Sunrise Airlines 入驻，我们需要在 Sky Industries 的注册中创建一个新的组织、空间和 Ontology。通过这种设置，Sky Industries 和 Sunrise Airlines 将能够协作，同时也拥有自己的私人工作空间。

## 创建一个组织

我们需要创建一个 Sunrise Airline 组织，以便 Sunrise Airline 用户可以保护他们的私人数据，并仅共享他们希望与 Sky Industries 共享的数据。作为注册管理员，您可以在控制面板中创建这个新组织。作为组织创建工作流程的一部分，您可以选择性地配置与其他组织的协作，并创建一个私人空间和 Ontology。

查看组织文档以确定创建新组织是否适合您的应用案例。

### 配置协作

协作使来自不同组织的用户能够共享他们的数据并在 Foundry 中一起工作。添加协作组织将允许两个组织的成员发现对方的名称。然后可以为每个组织分别配置用户和组的发现。

在我们的例子中，我们将使 Sky Industries 和 Sunrise Airlines 彼此相互可发现，并允许两个组织的用户和组相互查看。

### 创建一个私人空间和 Ontology

私人空间和 Ontology 提供了一个不应与其他协作组织共享的隔离工作空间。在我们的案例中，空间和 Ontology 仅对 Sunrise Airline 组织中的人员可访问。

## 配置身份提供者

在创建 Sunrise Airline 组织后，您可能需要在控制面板中进行一些额外设置。以下是您可能需要执行的一些步骤。在控制面板文档中阅读更详细的说明。

- 将 Sunrise Airline 身份提供者添加到控制面板，以便 Sunrise Airline 用户可以登录 Foundry。
- 将 Sunrise Airline 用户分配到上述创建的 Sunrise Airline 组织。
- 设置入口规则，以便 Sunrise Airline 用户可以从他们的网络访问 Foundry。
完成上述步骤后，Sunrise Airline 员工应能够使用他们的身份提供者进行身份验证并登录 Foundry。

### 授予管理权限

一旦 Sunrise Airline 管理员登录到 Foundry，您将能够在控制面板中授予他们必要的组织角色。应将管理组织角色授予与 Sunrise Airline 身份提供者同步的组。使用提供者组允许任何成员用户在登录 Foundry 时自动获得适当的角色。了解更多关于同步身份提供者组与 Foundry 的信息。

## 创建一个共享空间和 Ontology

接下来，我们需要创建一个共享空间和 Ontology。它们将被标记为 Sky Industries 和 Sunrise Airline 组织，以便两个组织可以访问在这个空间和 Ontology 中共享的内容。

我们需要授予 Sunrise Airlines 和 Sky Industries 管理员在共享空间上的角色，以便他们可以创建项目和更改空间设置。要创建一个共享空间和 Ontology，请联系 Palantir 支持。

## 创建一个共享项目

Sunrise Airline 开发人员将在他们的私人 Sunrise Airline 空间中创建自己的数据基础设施，类似于我们为 Sky Industries 的航班警报收件箱应用和数据基础设施所做的。在 Sunrise Airline 开发人员搭建他们可共享的维护数据集之后，Sky Industries 和/或 Sunrise Airline 管理员将在共享空间中创建一个共享项目。在项目创建期间或之后，管理员将把 Sky Industries 和 Sunrise Airline 组织应用到项目中。为此，您必须拥有 Sky Industries 和 Sunrise Airline 组织的应用组织权限。这在Foundry 设置选项卡中进行管理。

按照其他项目的相同模板，我们将创建三个新组来管理这个共享项目的权限。每个组应对 Sunrise Airline 和 Sky Industries 都可见。

## 移除继承的组织

在设置好空的共享项目后，两个组织的开发人员可以开始从他们的私人项目中引用数据。

当一个组织从他们的私人项目中引用数据集到共享空间时，该数据集会继续继承源组织的要求，直到明确移除。在这种情况下，虽然 Sky Industries 数据集被引用到共享空间中，但 Sunrise Airline 组织的用户仍然无法查看数据。为了解决这个问题，引用私人 Sky Industries 数据集的 Sky Industries 开发人员需要停止继承上游 Sky Industries 组织。对 Sunrise Airline 开发人员在共享项目中引用的私人数据集也是如此。

在共享项目中，Sky Industries 开发人员将创建一个代码库文件。在代码库中，Sky Industries 开发人员需要执行以下操作：

- 创建一个分支
- 移除任何 Sky Industries 敏感列（如果有的话）
- 从输入数据集中移除继承的 Sky Industries 组织（使用stop_requiring语法）
- 创建拉取请求
- 获得必要的批准并合并拉取请求
我们建议查看有关如何移除继承的权限标记和组织的文档。

在下面的例子中，Sky Industries 开发人员将输入的aircraft数据集筛选到仅包含 Sunrise Airline 的飞机，然后停止继承 Sky Industries 组织。

在变换搭建完成后，输出的aircraft数据集将对 Sunrise Airline 和 Sky Industries 组织可见。类似地，Sunrise Airline 开发人员可以对他们想要引入共享项目的数据进行相同操作。一旦两个开发人员完成共享他们组织的数据，他们就可以开始使用这些共享的数据集进行联合应用的开发。

一旦继承的组织被移除，所有基于输入数据集的工作将对两个组织可见。这意味着从这一点开始的工作将是可共享的。
