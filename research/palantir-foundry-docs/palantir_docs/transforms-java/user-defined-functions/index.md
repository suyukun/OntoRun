来源: https://palantir.com/docs/zh/foundry/transforms-java/user-defined-functions/

# 用户定义函数 (UDF)

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 用户定义函数 (UDF)

如果您无法使用 Pipeline Builder 中现有的变换选项来处理数据，想要整合外部 Java 库，或者有复杂的逻辑需要在多个管道中重用，您可以创建自己的用户定义函数 (UDF)。用户定义函数允许您在 Pipeline Builder 或可进行版本控制和升级的代码库中运行自己的任意 Java 代码。

用户定义函数仅应在必要时使用，我们建议在可能的情况下使用Pipeline Builder或Java 变换库中的现有变换。

必须在 Palantir 的云托管基础设施上注册才能使用 UDF。目前，Pipeline Builder 仅支持行映射和扁平映射 UDF，尽管将会添加对其他类型的支持。用户定义函数是高级功能。请务必仔细阅读以下文档以了解在管道中使用用户定义函数的影响。

## 创建用户定义函数 (UDF)

要创建用户定义函数库，首先导航到您希望保存该库的项目。

然后，选择New并选择Code Repository。在Foundry UDF Definitions选项下，选择Map UDF Definition/Implementation以使用 UDF 模板引导您的库。最后，选择Initialize repository。

您可以选择在自己的本地环境中本地工作（推荐）或直接在Code Repositories中工作。

### 设置本地开发环境（推荐）

我们建议本地工作来创建 UDF。请按照以下步骤设置本地环境。

- 要克隆您的库，请在屏幕右上角选择Work locally，然后复制 URL。
- 打开命令行接口 (CLI) 并运行git clone <repo url>。
打开命令行接口 (CLI) 并运行git clone <repo url>。

- 使用以下命令在您的开发环境中打开项目：
使用以下命令在您的开发环境中打开项目：

- IntelliJ IDEA:./gradlew idea open
- Eclipse IDE:./gradlew eclipse open
关键 CLI 命令：

- 在编辑 UDF 定义或 Java 实现文件后重新运行代码生成文件：IntelliJ IDEA:./gradlew ideaEclipse IDE:./gradlew eclipse。
- IntelliJ IDEA:./gradlew idea
- Eclipse IDE:./gradlew eclipse。
- 创建锁定文件以发布到 Pipeline Builder：./gradlew generateEddieLockfile
- ./gradlew generateEddieLockfile
- 运行测试：仅运行 testExamples:./gradlew test --tests examples.ExamplesTest.testExamples运行所有测试:./gradlew test
- 仅运行 testExamples:./gradlew test --tests examples.ExamplesTest.testExamples
- 运行所有测试:./gradlew test
### 设置代码库环境

如果您无法在本地 IDE 中工作，可以直接在代码库中编辑文件并在任务运行器中运行关键命令。

关键命令：

- 在编辑 UDF 定义或 Java 实现文件后重新运行代码生成文件：generateUdfResources
- generateUdfResources
- 创建锁定文件以发布到 Pipeline Builder：generateEddieLockfile
- generateEddieLockfile
- 运行测试：运行所有测试:test
- 运行所有测试:test
### 定义用户定义函数

UDF 在一个文件中定义，该文件指定其名称、输入模式、输出模式和参数类型。Java 类将基于此文件生成，文件名称将在您发布后在 Pipeline Builder 中可见。

要创建新的 UDF，请在src/main/resources/udfs/definitions/下添加一个名为<YourUdfName>.yml的文件，其中包含以下字段：

- name: 用于代码生成创建描述其输入、输出和参数类的 UDF 名称。此名称还将在部署库的deployment.yml文件中用来引用此 UDF，并在 Pipeline Builder 中作为变换可见。
- customTypes(非必填): 定义可以在inputSchema和outputSchema定义中重用的自定义类型的块。详情请参见下文的自定义类型部分。
- inputSchema: 必须遵循此模式的输入行才能在 UDF 上运行。具有比此模式更多列的数据集将被接受，如果运行时可以选择此模式的话。代码生成将创建针对该模式的强类型输入对象。参数将在 Pipeline Builder 中可见。详情请参见下文的模式定义部分。
- outputSchema: 此 UDF 输出行的模式。代码生成将创建针对该模式的强类型输出对象。详情请参见下文的模式定义部分。
- arguments: UDF 的参数描述。用户将在 Pipeline Builder 或相应的部署库中构建时指定这些参数。代码生成将根据此定义创建一个强类型参数对象。
在库模板中的src/main/resources/udfs/definitions/Multiply.yml下提供了一个示例定义。在下文的UDF 定义部分中阅读有关参数的更多信息。

您可以通过在src/main/resources/udfs/definitions中添加另一个定义文件来在此库中定义多个 UDF。

## 实现用户定义函数

一旦您创建或编辑了 UDF 定义文件，请使用以下命令运行代码生成。代码生成将从您的定义文件中创建强类型对象，并将其放置在udf-definitions-map-udf-definition/build/generated/sources/udf/main/java中。生成的类包括与您的定义模式匹配的输入和输出对象以及用于实现变换创建和逻辑的接口。您还应在对YourUdfNameMapUdfFactoryImpl或YourUdfNameMapUdfImpl类进行更改后重新运行代码生成，以便它可以编译您的 Java 包并在检查未通过时提供出错信息。

本地环境：

- IntelliJ IDEA:./gradlew idea
- Eclipse IDE:./gradlew eclipse
代码库：

- 在 Java 任务运行器中运行generateUdfResources。生成的文件在代码库中不可见，但此命令提供代码补全。
### 实现行映射用户定义函数

行映射 UDF 接受一行作为输入，然后每个输入输出正好一行。行映射是默认的 UDF 类型。

要实现您的 UDF 创建和变换逻辑，请在src/main/resources/java/myproject下创建两个新的 Java 类文件，内容如下：

- YourUdfNameMapUdfFactoryImpl.java: 负责创建 UDF 实例并为其提供执行所需的参数。此类应实现生成的YourUdfNameMapUdfFactory接口。任何 UDF 参数都可以通过args.config()参数获得。create方法将在运行时调用一次以实例化 UDF。
- 此类应实现生成的YourUdfNameMapUdfFactory接口。
- 任何 UDF 参数都可以通过args.config()参数获得。
- create方法将在运行时调用一次以实例化 UDF。
- YourUdfNameMapUdfImpl.java: 实现从输入对象到输出对象的实际变换逻辑。此类应实现生成的YourUdfNameMapUdf接口。每个通过变换的行都会调用此逻辑一次。输入和输出类属性以及配置参数可以通过同名但采用驼峰命名法的方法访问。例如，argument_one将有一个匹配的方法argumentOne()。
- 此类应实现生成的YourUdfNameMapUdf接口。
- 每个通过变换的行都会调用此逻辑一次。
- 输入和输出类属性以及配置参数可以通过同名但采用驼峰命名法的方法访问。例如，argument_one将有一个匹配的方法argumentOne()。
库模板包括下面列出的 Java 类的示例实现。您可以使用这些示例来建模您自己的实现。在编辑后重新运行代码生成以确保没有问题。

- src/main/java/myproject/MultiplyMapUdfFactoryImpl.java
- src/main/java/myproject/MultiplyMapUdfImpl.java
### 实现扁平映射用户定义函数

扁平映射 UDF 接受一行作为输入，并可以为每个输入输出 0、1 或多行。

要实现您的扁平映射 UDF 创建和变换逻辑，请使用以下示例在src/main/resources/java/myproject下创建两个新的 Java 类文件。

YourUdfNameFlatMapUdfFactoryImpl.java: 负责创建 UDF 实例并为其提供执行所需的参数。

- 此类应实现生成的YourUdfNameFlatMapUdfFactory接口。
- 任何 UDF 参数都可以通过args.config()参数获得。
- create方法将在运行时调用一次以实例化 UDF。
示例：DuplicateRowsFlatMapUdfFactoryImpl.java

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
34
35
package myproject;

import com.google.auto.service.AutoService;
import com.palantir.foundry.duplicaterows.config.DuplicateRowsConfiguration;
import com.palantir.foundry.duplicaterows.DuplicateRowsFlatMapUdf;
import com.palantir.foundry.duplicaterows.DuplicateRowsFlatMapUdfAdapter;
import com.palantir.foundry.duplicaterows.DuplicateRowsFlatMapUdfFactory;
import com.palantir.foundry.udf.api.flatmap.FoundryRowFlatMapUdf;
import com.palantir.foundry.udf.api.flatmap.FoundryRowFlatMapUdfFactory;

/**
 * Factory for creating the "ChangeMe" UDF.
 * 用于创建“ChangeMe” UDF（用户定义函数）的工厂类。
 */
@AutoService(FoundryRowFlatMapUdfFactory.class)
public final class DuplicateRowsFlatMapUdfFactoryImpl implements DuplicateRowsFlatMapUdfFactory {

    /**
     * Service-loading at runtime requires a public, no-arg constructor.
     * 运行时服务加载需要一个公共的无参数构造函数。
     */
    public DuplicateRowsFlatMapUdfFactoryImpl() {}

    /**
     * Creates the UDF implementation to use at runtime. Authors should return the adapter wrapping their UDF implementation.
     * 创建在运行时使用的UDF实现。作者应该返回包装他们UDF实现的适配器。
     */
    @Override
    public final FoundryRowFlatMapUdf create(FoundryRowFlatMapUdfFactory.Arguments<DuplicateRowsConfiguration> args) {
        // 创建 DuplicateRowsFlatMapUdf 的实现，并传入配置参数
        DuplicateRowsFlatMapUdf impl = new DuplicateRowsFlatMapUdfImpl(args.config());
        // 返回一个适配器，封装了UDF实现
        return new DuplicateRowsFlatMapUdfAdapter(impl);
    }
}
```

YourUdfNameFlatMapUdfImpl.java：实现从输入对象到输出对象的实际变换逻辑。

- 该类应实现生成的YourUdfNameFlatMapUdf接口。
- 每行通过变换时将调用此逻辑一次。
- 输入和输出类属性及配置参数可以通过相同名称但驼峰命名法的方法访问。例如，argument_one将有一个匹配的方法argumentOne()。
示例：DuplicateRowsFlatMapUdfImpl.java

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
package myproject;

import com.palantir.foundry.duplicaterows.config.DuplicateRowsConfiguration;
import com.palantir.foundry.duplicaterows.DuplicateRowsFlatMapUdf;
import com.palantir.foundry.duplicaterows.input.InputRow;
import com.palantir.foundry.duplicaterows.output.OutputRow;
import com.palantir.foundry.udf.api.flatmap.Collector;

/**
 * "DuplicateRows" UDF 逻辑的实现。
 */
public final class DuplicateRowsFlatMapUdfImpl implements DuplicateRowsFlatMapUdf {

    private final DuplicateRowsConfiguration config;

    public DuplicateRowsFlatMapUdfImpl(DuplicateRowsConfiguration config) {
        this.config = config;
    }

    @Override
    public void flatMap(Context ctx, InputRow input, Collector<OutputRow> out) throws Exception {
        OutputRow outputRow = OutputRow.create(ctx.getRowBuilderFactory())
                .key(input.key())
                .value(input.value());
        // 将所有输入行复制两次
        out.collect(outputRow);
        out.collect(outputRow);
    }
}
```

### 为行映射用户自定义函数编写示例

示例提供有关给定用户自定义函数的信息，并可被用于在单元测试框架中。这些示例在将 UDF 导入管道时也会出现在 Pipeline Builder 中，从而更易于理解 UDF 的功能。示例框架仅支持行映射用户自定义函数，对于平面映射用户自定义函数，我们建议编写您自己的 JUnit 测试，这些测试将不会在 Builder 变换文档中可见。

定义示例测试用例是非必填的，但强烈建议这样做，因为它将在 Pipeline Builder 的变换文档下可见，使用户更容易理解 UDF 的作用。如果您不想包含示例，请删除文件夹src/test并继续下一部分。

您可以在Map UDF Definition/Implementation存储库的默认模板中找到一个Examples类示例。

- src/test/java/examples/registry/MultiplyExamples.java
要为 UDF 定义新示例，请在examples.registry下创建一个实现Examples接口的类。请参考MultiplyExamples.java了解接口期望。

示例实现的name()方法必须返回与被测试的 UDF 相同的名称。否则，示例将无法正确注册或发布到 Pipeline Builder 界面。

实际示例应在examples()方法中定义。以下是默认MultiplyExamples类中定义的examples()方法实现：

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
34
@Override
public List<UdfExample<SettableMultiplicand, Product, MultiplyConfiguration>> examples() {
    return List.of(UdfExample.<SettableMultiplicand, Product, MultiplyConfiguration>builder()
            // A unique ID for this example
            // 此示例的唯一ID
            .id(ExampleId.of("baseCase"))
            // Optional: A description of what this example represents
            // 可选：此示例的描述
            .description("Multiply values by 2.")
            // Whether this example should have PROMINENT or DEFAULT visibility in Pipeline Builder
            // 此示例在Pipeline Builder中应该是PROMINENT还是DEFAULT可见性
            .visibility(ExampleVisibility.DEFAULT)
            // The case that this example illustrates (base case, null case, edge case)
            // 此示例说明的情况（基本情况，空情况，边界情况）
            .category(ExampleCategory.BASE)
            // The arguments to pass to the UDF that this example illustrates
            // 传递给此示例说明的UDF的参数
            .configuration(MultiplyConfiguration.builder().multiplier(2.0d).build())
            // The example input rows to the UDF
            // UDF的示例输入行
            .input(
                    SettableMultiplicand.create(ctx().getRowBuilderFactory())
                            .key("key")
                            .value(1.5d),
                    SettableMultiplicand.create(ctx().getRowBuilderFactory())
                            .key("key")
                            .value(3.0d))
            // The example output rows (what the input rows should look like after the UDF has been called on them)
            // 示例输出行（调用UDF后的输入行应呈现的样子）
            .output(
                    Product.create(ctx().getRowBuilderFactory()).key("key").value(3.0d),
                    Product.create(ctx().getRowBuilderFactory()).key("key").value(6.0d))
            .build());
}
```

一旦定义了您的示例，就可以运行所有测试。

- 本地环境：仅运行 testExamples:./gradlew test --tests examples.ExamplesTest.testExamples运行所有测试:./gradlew test
- 仅运行 testExamples:./gradlew test --tests examples.ExamplesTest.testExamples
- 运行所有测试:./gradlew test
- 代码库：运行所有测试: 在 Java Task Runner 中运行test。
- 运行所有测试: 在 Java Task Runner 中运行test。
运行ExamplesTest.testExamples()将加载examples.registry包下Examples的实现并检查其有效性。在上面显示的MultiplyExamples.examples()方法的情况下，它将使用configuration中提供的参数（multiplier = 2.0d）在两个input行（["key", 1.5d]和["key", 3.0d]）上执行 UDF，并验证其结果是否为指定的输出行（["key", 3.0d]和["key", 6.0d]）。

### 保存更改

一旦完成开发工作，请务必提交您的更改。

本地环境：通过按顺序运行以下命令，将更改推送回 Foundry 代码库。

- git add .
- git commit -m "<commit message>"
- git push
- 代码库中将出现一个蓝色弹出窗口，指出“已对此分支进行了新的提交”。选择更新到最新版本以查看您的更改。
代码库：选择提交。

## 部署用户定义函数

可以通过 Pipeline Builder（推荐）或标准的 UDF 部署库来部署 UDF。

### 发布到 Pipeline Builder（推荐）

发布到 Pipeline Builder 目前仅适用于 Rubix 注册的行映射和扁平映射 UDF。其他 UDF 类型的支持将被添加。

按照以下步骤将您的 UDF 发布到 Pipeline Builder：

- 从底部面板打开任务运行器。然后，选择Java选项卡并输入generateEddieLockfile以生成一个包含唯一标识符的文件，以便 Pipeline Builder 注册您库中的每个 UDF。
generateEddieLockfile命令根据 UDF 名称返回一个随机唯一标识符。如果在发布后重命名 UDF，代码将作为新 UDF 发布，而不是覆盖先前的 UDF。同样，如果删除并重新生成锁文件，UDF 将获得新的唯一标识符并注册为新 UDF。在导入 Pipeline Builder 中的 UDF 时，弹出窗口中将显示 UDF 的所有版本，包括旧名称、新名称和新锁文件。

- 提交锁文件和更改。
- 为您的发布标记版本（例如，0.0.1）。
- 验证检查是否通过。如果检查失败，UDF 将无法发布到 Pipeline Builder。
如果没有锁文件，UDF 将无法注册到 Pipeline Builder 以导入到管道中。要生成锁文件，请运行generateEddieLockfile。如果您在代码库中工作，则不需要锁文件。

- 检查通过后，导航到当前或新的 Pipeline Builder 管道。
- 转到Reusables > User-defined functions > Import UDF。
- 从列表中选择您的 UDF，然后选择Add。您的 UDF 应出现在 Pipeline Builder 变换选择器中，并可以像管道中的其他变换一样使用。
要在 UDF 的第一个版本之后部署新的更改或修复，包括对定义 YML 的编辑，请重复上述实现和发布步骤。然后，在您的 Pipeline Builder 管道中：

- 转到Reusables > User-defined functions。
- 为您的 UDF 选择Edit version，并选择更新的版本。
### 发布到部署库

按照以下步骤将您的 UDF 发布到代码库：

- 选择提交您的更改和标记版本以设置发布版本。
- 在标签检查通过后，使用Foundry UDF Definitions > Foundry Streaming UDF Deployment模板为流式或Foundry UDF Definitions > Foundry Batch UDF Deployment模板为批处理创建另一个库
- 按照模板中的说明部署 UDF。
要在 UDF 的第一个版本之后部署新的更改或修复，包括对定义 YAML 的编辑，请重复上述实现和发布步骤。然后，更新部署库的 build.gradle 依赖项中引用的标签版本。

## 用户定义函数定义 YAML

UDF 定义 YAML 文件的结构如下：

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
name: # (string) 这个用户自定义函数（UDF）的名称。
customTypes: # (optional<CustomTypes>) 可以在当前UDF定义中引用的自定义类型。详见下面的[Custom Types](#custom-types)部分。
inputSchema: # (Schema) 输入行必须遵循的模式，以便运行此UDF。详见下面的[Schema YAML definition](#schema-yaml-definition-documentation)部分。
outputSchema: # (Schema) 此UDF输出行的模式。详见下面的[Schema YAML definition](#schema-yaml-definition-documentation)部分。
arguments: # (map<ArgumentId, Argument>) 在构建时指定的参数，并在部署时提供给UDF作者。
  # (ArgumentId: string) 参数的本地唯一名称。
  [ArgumentId]:
    required: # (Boolean) 此参数是否为必需。
    description: # (optional<string>) 在Pipeline Builder中显示的描述，帮助用户理解此参数的用法。
    type: # (FieldType) 参数的数据类型。
# 针对键值处理UDF
keyColumns: # (list<string>) 用于分区的键列。这些列必须存在于输入模式中。
eventTimeColumn: # (string) 包含事件时间的列。此列必须存在于输入模式中。
# 针对所有其他UDF类型
description: # (optional<string>) 在Pipeline Builder中显示的此UDF的描述，帮助用户理解这个UDF的功能。
type: # (optional<Type>) UDF的类型，决定UDF的逻辑如何定义和执行。
  # Type枚举的允许值：
  # - DEFAULT
  # - ASYNC_DEPLOYED_APP_UDF
  # - ASYNC_CUSTOM_UDF
  # - FLAT_MAP_UDF
```

我们强烈建议为UDF及其参数包含非必填的description字段，特别是在UDF将被部署于Pipeline Builder时。这些描述可以提高用户对UDF功能的理解，以及更改参数如何影响输出。

## Schema定义YAML

UDF模式具有以下结构：

```
Copied!1
2
3
4
5
6
7
8
name: # (string) 此架构的项目唯一名称，代码生成将使用此名称作为生成对象的前缀。
description: # (optional<string>) 此架构的描述信息，当在 Pipeline Builder 中使用此 UDF 时会显示以提供上下文。
fields: # (list<Field>) 此架构中的所有字段
  - name: # (string) 此字段的本地唯一名称
    nullable: # (boolean) 此值是否可能为 null
    type: # (FieldType) 此字段的数据类型及任何相关的元数据。例如：
      type: double
      double: {}
```

这里的注释解释了 YAML 文件中各个字段的用途和数据类型。
如上所述，我们强烈建议您为每个模式提供描述，以帮助用户在Pipeline Builder中了解输入和输出期望。

所有Foundry数据集类型都被UDFFieldType支持，并采用以下形式：

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
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
# 数组类型
type: array
array:
  elementType:
    type: <FieldType>
    nullable: # (布尔值) 数组中的值是否可能为null

# 二进制类型
type: binary
binary: {}

# 布尔类型
type: boolean
boolean: {}

# 字节类型
type: byte
byte: {}

# 自定义类型
type: custom
custom: # (字符串) 在 `customTypes` 块中定义的自定义类型名称

# 日期类型
type: date
date: {}

# 十进制类型
type: decimal
decimal:
  precision: # (整数) 范围在1到38（包括）之间的整数。
  scale: # (整数) 范围在0到precision（包括）之间的整数。

# 双精度浮点类型
type: double
double: {}

# 浮点类型
type: float
float: {}

# 整数类型
type: integer
integer: {}

# 长整型
type: long
long: {}

# 映射类型
type: map
map:
  keyType:
    type: <FieldType>
    nullable: # (布尔值) 映射中的键是否可能为null
  valueType:
    type: <FieldType>
    nullable: # (布尔值) 映射中的值是否可能为null

# 短整型
type: short
short: {}

# 字符串类型
type: string
string: {}

# 时间戳类型
type: timestamp
timestamp: {}

# 结构体类型
type: struct
struct:
  fields: [] # (列表<字段>)
```

## 自定义类型

UDF中的自定义类型允许定义可在整个模式定义中重复引用的类型。

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
customTypes: # 这个块是可选的，如果没有使用自定义类型，可以不包含它。
  types: # 不要忘记这个 `types` 块！这个块是为了以后在 `customTypes` 中支持附加字段（如 `imports`）而预留的。
    customType: # 这个键应该是这个自定义类型的唯一名称
      # (FieldType) 这个自定义字段的数据类型，以及任何相关的元数据。例如：
      type: double
      double: {}
    anotherCustomType:
      # 定义另一个自定义类型
      # ...
```

自定义类型可以定义为任何字段类型的别名，包括原始类型、数组、映射和结构。然而，通常情况下，自定义类型在定义输入和输出模式中反复出现的结构类型时最为有用。

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
customTypes:
  types:
    customStruct: # 自定义结构体类型
      type: struct # 类型为结构体
      struct:
        fields: # 字段列表
          - name: "doubleField" # 字段名称
            nullable: false # 字段不可为空
            type:
              type: double # 字段类型为双精度浮点数
              double: {} # 双精度浮点数类型的额外配置（此处为空）
```

可以在模式中按如下方式引用自定义类型：

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
inputSchema:
  name: "Input" # 输入模式名称
  fields:
    - name: "inputStruct" # 输入结构名称
      nullable: false # 是否允许为空
      type:
        type: custom # 自定义类型
        custom: customStruct # 自定义类型名称，定义在上面
outputSchema:
  name: "Output" # 输出模式名称
  fields:
    - name: "outputStruct" # 输出结构名称
      nullable: false # 是否允许为空
      type:
        type: custom # 自定义类型
        custom: customStruct # 自定义类型名称，定义在上面
```

当在UDF模式中引用自定义结构体如上所述时，代码生成不会为InputStruct和OutputStruct创建单独的类。相反，输入和输出对象都引用相同的代码生成类，用于引用的自定义类型（在下面的例子中为CustomStruct）：

```
Copied!1
2
3
4
5
6
7
public final Output map(FoundryRowMapUdf.Context ctx, Input input) {
    // 一个不进行操作的UDF，将输入结构体字段传递到输出结构体字段
    Output output = Output.create(ctx.getRowBuilderFactory());
    CustomStruct inputStruct = input.inputStruct(); // 返回一个 `CustomStruct`
    output.outputStruct(inputStruct); // 需要一个 `CustomStruct` 参数
    return output;
}
```

自定义结构体是使用自定义类型的一个主要好处；当输入代码生成类型与输出代码生成类型结构相同时，无需进行额外的转换工作。

## 故障排除

本节描述了一些用户定义函数实现和部署中的常见问题，以及调试步骤。

### 代码生成未运行

通常，这是由不可解析的UDF定义YAML引起的。

请按照以下步骤解决：

- 检查代码助手中的任何可识别错误，查看红色的Code Assist task failed弹出框。
- 验证所有字段是否已提供，并且没有拼写错误。您可以与初始示例定义进行交叉检查。
- 如果故障仍然存在，通过将鼠标悬停在代码编辑器底部的Code Assist running消息上并选择刷新来刷新代码助手。
- 在本地下载库，并执行./gradlew idea或./gradlew eclipse命令以查看控制台产生的错误。
### 我可以注销UDF吗？

一旦发布，UDF无法从Pipeline Builder中取消发布。如果您删除锁文件条目并在您的库上重新运行generateEddieLockfile命令，将为您的UDF授予一个新的ID，这将导致它在Pipeline Builder变换列表的UDFs部分中出现两次。

### 本地环境：不支持的类文件主要版本

如果./gradlew idea open或./gradlew eclipse open失败，并显示错误Could not open proj generic class cache for build file <build.gradle> ... Unsupported class file major version，您可能正在运行一个与Gradle不兼容的Java版本。

请按照以下步骤解决：

- 通过运行./gradlew --version检查您的Java和Gradle版本。
- 交叉检查您的JVM版本是否与Gradle文档 ↗中列出的Gradle版本兼容。
- 如果您的JVM版本不兼容，并且您本地没有其他兼容版本，请下载一个兼容的Java版本 ↗。
- 将您的JAVA_HOME设置为export JAVA_HOME=<jdk install directory>/Contents/Home/。
您现在应该可以成功运行open命令。

### 我无法在任务运行器中运行generateEddieLockfile任务

如果您收到Failed to start Java server错误，或者无法在任务运行器中运行该命令，请验证以下内容：

- 您的库模板版本为0.517.0或更高。要检查这一点，请导航到文件编辑器，然后选择显示设置 > 显示隐藏的文件和文件夹。templateConfig.json文件将出现在文件列表中。如果库不是兼容版本，请从右上角或库视图中选择**... > 升级**，以生成带有最新模板的拉取请求。批准拉取请求，然后在请求合并并检查通过后重建您的工作区。
- 要检查这一点，请导航到文件编辑器，然后选择显示设置 > 显示隐藏的文件和文件夹。templateConfig.json文件将出现在文件列表中。
- 如果库不是兼容版本，请从右上角或库视图中选择**... > 升级**，以生成带有最新模板的拉取请求。批准拉取请求，然后在请求合并并检查通过后重建您的工作区。
- 您的工作区已连接。如果您的工作区未连接，请重建您的工作区。
- 如果您的工作区未连接，请重建您的工作区。
- 您在任务运行器中选择了Java选项卡，而不是Eclipse Java。