来源: https://palantir.com/docs/zh/foundry/building-pipelines/remove-inherited-markings/

# 移除继承的权限标记和组织

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 移除继承的权限标记和组织

权限标记和组织基于用户的资格来限制对资源的访问。

当在派生资源中移除或模糊处理受限内容时，用户可能希望移除该派生资源上的权限标记和/或组织。可以通过使用stop_propagating和stop_requiring输入变换属性来完成移除继承的权限标记和组织的过程。

- stop_propagating用于移除继承的权限标记（例如PII）。
- stop_requiring用于移除继承的组织（例如Palantir）。
## 术语

- 组织是应用于项目的访问要求，确保用户组和资源之间的严格隔离。为了满足访问要求，用户必须是应用于项目的至少一个组织的成员或访客成员。
- 权限标记是应用于资源的访问要求，限制以全有或全无的方式访问。为了满足访问要求，用户必须是应用于资源的所有权限标记的成员。
- 角色是一组权限，定义用户可以在给定资源上执行的特定工作流程（例如访客、编辑者等）。
## 重要须知

- stop propagating和stop requiring关键词短语仅适用于组织和权限标记，而不适用于角色。
- 仓库需要至少有一个受保护的分支（例如，main）。该分支还必须强制执行至少一个所需的审批者。
- 您只能在受保护的分支上移除组织和权限标记。提及未受保护的分支（例如on_branches=[..., "not-protected-branch"]）将导致搭建失败。
- 在Python、Java和SQL中支持移除组织和权限标记。
- 需要特殊的用户权限才能批准移除继承的组织和权限标记。用户需要移除权限标记权限才能移除权限标记，并需要扩展访问权限才能移除组织。
## 基本工作流程

下图中项目C的灰色数据集框强调了必须为目标项目中的所有输入添加项目引用。

### 步骤

- 从受保护的分支创建一个新分支（例如，main）。
从受保护的分支创建一个新分支（例如，main）。

- 将stop_propagating和/或stop_requiring属性添加到输入变换中。例如：
将stop_propagating和/或stop_requiring属性添加到输入变换中。例如：

- 创建拉取请求以将此代码合并到受保护的分支。
创建拉取请求以将此代码合并到受保护的分支。

- 具有移除权限标记权限的用户或者具有扩展访问权限的用户可以批准或拒绝提议的更改。如果添加了多个审核者，任何审核者的拒绝都将导致整个拉取请求被拒绝。
具有移除权限标记权限的用户或者具有扩展访问权限的用户可以批准或拒绝提议的更改。如果添加了多个审核者，任何审核者的拒绝都将导致整个拉取请求被拒绝。

- 如果获得批准，代码编辑器将合并PR并搭建输出数据集。输出数据集搭建完成后，将不再具有传播的权限标记和/或组织。
如果获得批准，代码编辑器将合并PR并搭建输出数据集。输出数据集搭建完成后，将不再具有传播的权限标记和/或组织。

在内部，组织被表示为一种稍微不同的权限标记，因此在stop_requiring后面的变换关键词称为OrgMarkings。

## 输入变换属性

要移除继承的权限标记（例如PII），使用stop_propagating关键词短语。

要移除继承的组织（例如Palantir），使用stop_requiring关键词短语。

每个需要移除权限标记或组织的输入都必须指定这些关键词短语。对于每次移除，您还必须指定应适用于移除的受保护分支。权限标记ID、组织ID和分支应始终指定为带引号的字符串。

您需要提供至少一个上游组织，因为用户只需满足至少一个组织。每个列出的组织都需要批准。下面的详细工作流程提供了一个说明这一点的示例。

### Python

在Python中，权限标记的移除是在输入构造函数中指定的。

```
Copied!1
2
3
4
5
6
7
8
@transform(
  input_1=Input("<input_id>",
      # stop_propagating: 停止传播的标记列表，指定不应再向下游传播的标记ID和分支
      stop_propagating=Markings([markingId1, ...], [branch1, ...]),
      # stop_requiring: 停止要求的组织标记列表，指定不应再要求的组织标记ID和分支
      stop_requiring=OrgMarkings([orgMarking1, ...], [branch2, ...])),
  output=Output("<output_id>")
  )
```

这段代码使用了装饰器@transform，用于定义输入输出的转换逻辑。Input和Output是用来定义输入和输出的接口。stop_propagating和stop_requiring参数用于控制标记和组织标记的传播和要求行为。Markings类接受一个权限标记 ID 列表和一个需要应用权限标记移除的受保护分支列表。权限标记 ID 可以在Settings页面上的Markings列表中找到。

OrgMarking类接受一个组织 ID 列表和一个需要应用权限标记移除的受保护分支列表。组织 ID 可以在Settings页面上的Organizations列表中找到。

### Java

#### Java 自动注册

在 Java 中，权限标记移除通过对自动注册变换的输入进行注解来指定。

语法：

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
@Compute
public void myComputation(
  // @StopPropagating 注解用于停止某些标记的传播
  @StopPropagating(markings = {markingId1, ...}, onBranches = {branch1, ...})
  // @StopRequiring 注解用于停止对某些组织标记的需求
  @StopRequiring(orgMarkings = {orgId1, ...}, onBranches = {branch2, ...})
  // @Input 注解指定方法的输入
  @Input("<input_id>")
  FoundryInput input,
  // @Output 注解指定方法的输出
  @Output("<output_id>")
  FoundryOutput output)
```

此代码段定义了一个名为myComputation的方法，使用了多个注解来配置数据流的输入输出以及控制标记的传播和需求。在计算过程中特别关注数据的安全性和合规性。@StopPropagating和@StopRequiring注解需要一组权限标记ID和一组受保护的分支，以应用权限标记的移除。
当仅指定一个权限标记或分支时，无需将其用{}包裹（例如，@StopPropagating(markings = marking1, onBranches = "my-branch")）。

#### Java 手动注册

对于手动注册的 Java 变换，我们在MyPipelineDefiner.java文件中使用以下语法在注册期间指定取消权限标记。

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
  @Override
    public void define(Pipeline pipeline) {
        // 创建一个高层次的手动转换对象
        HighLevelTransform highLevelManualTransform = HighLevelTransform.builder()
                // 指定计算功能实例
                .computeFunctionInstance(new HighLevelManualFunction())
                // 设置输入参数的别名
                .putParameterToInputAlias("myInput", "/path/to/input/dataset")
                // 设置返回结果的别名
                .returnedAlias("/path/to/output/dataset")
                        // 定义期望的未标记集
                        .desiredUnmarkings(Set.of(
                                    Unmarking.builder()
                                        // 设置分支
                                        .branch("branch1")
                                        // 指定输入的别名
                                        .input(alias("/input1"))
                                        // 指定输出的别名
                                        .output(alias("/output"))
                                        // 设置标记ID
                                        .markingId(MarkingId.valueOf("markingId"))
                                        .build(),
                                    Unmarking.builder()
                                        .branch("branch1")
                                        .input(alias("/input1"))
                                        .output(alias("/output"))
                                        .markingId(MarkingId.valueOf("orgId1"))
                                        .build()
                                    ))
                .build();
        // 在管道中注册高层次手动转换
        pipeline.register(highLevelManualTransform);
    }
```

### SQL

在SQL中，权限标记的移除是通过使用SparkSQL提示语句来指定的：

```
Copied!1
2
3
CREATE TABLE <output_id> AS
  SELECT /*+ foundry_stop_propagating(markingId1, ...) foundry_stop_requiring(orgMarkingId1, ...) foundry_on_branches(branch1, ...) */ *
  FROM <input_id>
```

```
Copied!1
2
3
4
5
6
此SQL代码用于创建一个新表 `<output_id>`，其内容基于从表 `<input_id>` 中选择的所有列和行。
- `/*+ foundry_stop_propagating(markingId1, ...) */`: 这是一个提示（hint），用于停止标记在数据流中的传播，`markingId1` 是标记ID。
- `/*+ foundry_stop_requiring(orgMarkingId1, ...) */`: 这是另一个提示，指示不再需要某些标记，`orgMarkingId1` 是原始标记ID。
- `/*+ foundry_on_branches(branch1, ...) */`: 这是用于在指定分支上运行查询的提示，`branch1` 是分支名称。

这些提示通常在数据工程平台如Palantir Foundry中用于控制数据的标记和分支行为。
```

权限标记和组织删除可以添加到任何SELECT语句中。例如：

```
Copied!1
2
CREATE TABLE <output_id> AS SELECT * FROM <input_1_id>
  CROSS JOIN (SELECT /*+ foundry_stop_propagating(markingId1) foundry_on_branches("my-branch") */ * FROM <input_2_id>)
```

```
Copied!1
2
3
4
5
6
-- 该SQL语句用于创建一个新的表<output_id>，其内容是通过CROSS JOIN连接<input_1_id>和<input_2_id>两个表的所有数据。
-- CROSS JOIN会生成笛卡尔积，即每一行<input_1_id>都会与<input_2_id>的每一行进行组合。

-- 在第二个子查询中，使用了Foundry平台的提示：
-- `foundry_stop_propagating(markingId1)`：用于停止某个标记ID的传播。
-- `foundry_on_branches("my-branch")`：指定在名为"my-branch"的分支上执行操作。
```

## 删除权限

为了能够查看代码并批准拉取请求，批准者必须通过项目和代码库本身上的任何组织和权限标记，并拥有一个包含基本StemmaView Repository工作流程的角色（默认情况下，包含在只读角色中）。用户还必须对每个组织和权限标记具有设置批准模式或批准删除这些组织和权限标记的拉取请求的权限。用户不一定需要是组织或权限标记的成员。

对于权限标记的批准，批准的用户需要在权限标记上具有Remove marking角色。

对于组织的批准，批准的用户需要在权限标记上具有Expand access角色。

## 批准模式

对于每个代码库以及每个组织和权限标记，数据治理用户可以定义应该使用哪种模式来触发新的批准：

- 需要重新批准：这是每个组织和权限标记的默认模式。代码库总是需要安全批准任何提交到删除了该组织和权限标记的分支的拉取请求。此模式防止对逻辑的更改，从而确保安全地删除组织和权限标记。
- 不需要重新批准：当首次在特定输入的变换中删除此组织和/或权限标记时，需要批准。后续对逻辑的更改不会因安全批准而被阻止。
### 示例 1

上面是在一个代码库中进行的一个变换，其中一个权限标记PHI需要重新批准。

在上述设置下，将发生以下情况：

- 当用户创建他们的第一个PR以停止传播PHI权限标记时，他们需要获得在PHI权限标记上具有Remove角色的用户的批准。
- 如果用户在下一个PR中修改了上述变换，他们将再次被要求获得批准。
- 如果用户在代码库中修改了任何内容——在此文件或任何其他文件中，他们将再次被要求获得PHI权限标记的批准。
### 示例 2

上面是在一个代码库中进行的一个变换，其中一个组织PALANTIR不需要重新批准。

在上述设置下，将发生以下情况：

- 当用户创建他们的第一个拉取请求以停止要求PALANTIR组织时，他们需要获得在PALANTIR组织上具有Expand access角色的用户的批准。
- 如果用户在下一个拉取请求中修改了上述变换，他们将不会被要求获得批准。
- 如果用户随后修改了此代码库中的任何内容，他们将不会被要求获得批准。
### 示例 3

变换1：上面是一个包含一个权限标记PII和一个组织PALANTIR的变换。PII权限标记需要重新批准，而PALANTIR组织不需要重新批准。

变换2：上面是一个包含一个权限标记USA的变换，该标记不需要重新批准。

在上述设置下，将发生以下情况：

- 当用户在变换1中创建他们的第一个拉取请求时，他们需要获得在PII权限标记上具有Remove marking角色的用户和在PALANTIR组织上具有Expand access角色的用户的批准。
- 如果用户在下一个拉取请求中修改了变换1，他们将被要求仅从PII权限标记上具有Remove marking角色的用户获得批准。
- 当用户为变换2创建他们的第一个拉取请求时，他们需要获得在USA权限标记上具有Remove marking角色的用户和在PII权限标记上具有Remove marking角色的用户的批准。
- 如果用户在下一个拉取请求中修改了变换2，他们将被要求仅从PII权限标记上具有Remove marking角色的用户获得批准。
- 如果用户随后修改了此代码库中的任何内容，他们将被要求仅从PII权限标记上具有Remove marking角色的用户获得批准。
## 详细工作流程

在此示例场景中，一名代码编辑希望使用来自敏感上游项目的两个数据集，删除某些信息，并允许更广泛的受众访问生成的数据集。这两个数据集，每个都有两个权限标记，已作为参考添加到下游项目中。代码编辑希望停止传播四个权限标记中的三个，以便它们不会出现在输出数据集上。此外，上游项目仅限于OrgA或OrgB的用户，意图是将下游数据分发给OrgC的用户。

之前：代码编辑分支上的输出数据集继承了所有四个权限标记，并且仍然仅限于OrgA或OrgB的用户。

之后：一旦合并到受保护的分支（例如，主），输出数据集现在仅有一个继承的权限标记，并且不再要求用户是OrgA或OrgB的成员。

### 步骤

- 代码编辑在下游项目的代码库的feature/clean-data分支上编写新的变换。
- 由于所有的权限标记更改都被请求用于主分支，因此在feature/clean-data上工作不需要任何批准。换句话说，当在feature/clean-data分支上构建输出数据集时，所有上游权限标记仍将被继承。
由于所有的权限标记更改都被请求用于主分支，因此在feature/clean-data上工作不需要任何批准。换句话说，当在feature/clean-data分支上构建输出数据集时，所有上游权限标记仍将被继承。

- 代码编辑创建一个到主分支的拉取请求，并向管理受lemon、apple和cherry权限标记限制的数据的数据治理用户请求批准。代码编辑还请求来自OrgA的Expand access组织管理员的批准，当OrgA的数据需要与其他组织共享时，他们可以批准。
代码编辑创建一个到主分支的拉取请求，并向管理受lemon、apple和cherry权限标记限制的数据的数据治理用户请求批准。代码编辑还请求来自OrgA的Expand access组织管理员的批准，当OrgA的数据需要与其他组织共享时，他们可以批准。

通过删除继承的组织来扩展访问权限会删除所有继承的组织，但仅需要获得在变换中列出的组织上具有适当权限的用户的批准。如果您想要获得所有组织的批准，那么您需要在`stop_requiring`组件中列出所有的ID。在此示例中，OrgA主要负责上游项目中的数据，因此编辑选择OrgA进行跨组织批准流程。因此，编辑只需要获得OrgA管理员的批准即可删除继承的组织。根据编辑想要请求的组织批准，编辑可以选择`stop_requiring`以下任一项：
(1) OrgA（由OrgA管理员批准），
(2) OrgB（由OrgB管理员批准），或
(3) OrgA和OrgB（由两个组织的管理员批准）。

最终结果是输出数据集将不会继承任何来自输入的组织，并且只会遵循其所在项目的组织。

- 数据治理用户和组织管理员收到Foundry通知，告知他们的批准请求。
数据治理用户和组织管理员收到Foundry通知，告知他们的批准请求。

- 假设PR获得批准，代码编辑将其合并并构建输出数据集，如上图所示的之后图像。
假设PR获得批准，代码编辑将其合并并构建输出数据集，如上图所示的之后图像。

- 下一周，另一名代码编辑对不同的代码文件进行了更改，并打开了一个合并到主的PR。
下一周，另一名代码编辑对不同的代码文件进行了更改，并打开了一个合并到主的PR。

如果所有的权限标记都不需要重新批准，则PR可以在不进行安全审查的情况下获得批准。如果任何权限标记确实需要批准，则此新PR将需要由管理该权限标记的数据治理或组织管理员进行安全审查。
