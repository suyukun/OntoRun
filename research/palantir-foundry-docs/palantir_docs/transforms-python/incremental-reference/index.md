来源: https://palantir.com/docs/zh/foundry/transforms-python/incremental-reference/

# 增量变换参考

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 增量变换参考

## 增量装饰器

本指南的其余部分涉及增量与非增量搭建。假设在所有情况下，均使用了incremental()装饰器。因此，这个术语仅指变换是否实际以增量方式运行。

incremental()装饰器可以用于包装变换的计算函数，以启用增量计算的逻辑：incremental()装饰器可以被用于在任何现有的变换上，该变换使用了transform(),transform_df()或transform_pandas()装饰器。请注意，您的变换的计算函数必须支持以增量和非增量两种方式运行。incremental()装饰器有两个关键作用：

- 它允许变换查找有关其先前搭建的信息。使用此信息，incremental()装饰器然后根据下面描述的要求决定变换是否可以以增量方式运行。
- 它将输入、输出和上下文对象转换为提供附加功能的增量子类。具体来说，TransformInput变为IncrementalTransformInput，TransformOutput变为IncrementalTransformOutput，而TransformContext变为IncrementalTransformContext。这些增量对象随后被传递到由装饰器包装的变换中。
增量装饰器接受六个参数：

```
Copied!1
2
3
4
5
6
7
8
transforms.api.incremental(
    require_incremental=False,  # 不要求增量更新
    semantic_version=1,         # 语义版本设置为1
    snapshot_inputs=None,       # 快照输入设为None
    allow_retention=False,      # 不允许保留
    strict_append=False,        # 不严格要求追加
    v2_semantics=False          # 不使用V2语义
)
```

将require_incremental参数设置为True会导致变换无法以增量方式运行时失败。有两种情况下，即使require_incremental=True，变换也可以作为快照运行：

- 某个输出从未被搭建过。
- 语义版本发生了更改，意味着显式请求了快照。
要调试变换无法以增量方式运行的原因，请查看驱动程序日志中的警告transforms.api._incremental: Not running incrementally。

:func:~transforms.api.incremental装饰器中的semantic_version参数允许您强制下一次运行变换时为非增量模式。

- 如果当前运行的语义版本与前一次运行的语义版本不同，则变换将以非增量方式运行。
- 如果未指定，则语义版本设置为1。
- 如果之前的运行没有语义版本（例如，在将现有变换转换为增量变换时），则假定值为1。这允许变换在无需新快照的情况下开始增量运行。
- 要强制变换的后续运行为非增量，可以增加@incremental()装饰器中的semantic_version参数。请注意，增加语义版本时，只应使用整数。
- 请注意，增加语义版本时，只应使用整数。
snapshot_inputs参数允许您将某些输入定义为快照输入，与非快照输入不同，支持更新和删除修改。参见快照输入以了解更多信息。

将allow_retention参数设置为True允许Foundry保留删除输入和输出数据集中的文件，同时保持变换的增量性。

如果strict_append参数设置为True，则底层Foundry事务类型将被设置为APPEND，并且增量写入将使用APPEND事务。请注意，写入操作可能不会覆盖任何文件，即使是辅助文件，如Parquet摘要元数据或Hadoop SUCCESS文件。所有Foundry格式的增量写入都应支持此模式。

如果v2_semantics参数设置为True，将使用V2增量语义。V2和V1增量语义之间的行为应该没有区别，我们建议所有用户将此设置为True。如果使用v2语义，非目录输入和输出资源可能只能以增量方式读取/写入。

### 重要信息

如上所述，您的变换的计算函数在使用incremental()装饰器包裹时必须支持以增量和非增量方式运行。默认读取和写入模式（在本页其余部分中更详细地解释）可以帮助实现此双逻辑要求，但可能仍然需要根据计算上下文的is_incremental属性进行分支。

另一个关键点是，使用incremental()装饰器与transform_df()或transform_pandas()时，您只能访问默认的读取和写入模式。如果您的变换中添加的输出行仅是添加的输入行的函数（请参阅追加示例），这就足够了。但是，如果您的变换执行更复杂的逻辑（如合并、聚合或去重）且需要设置输入读取模式或输出写入模式，那么您应该使用incremental()装饰器与transform()。使用与transform()的增量装饰器允许您设置读取和写入模式。

请注意，代码库预览功能将始终以非增量模式运行变换。这即使在将require_incremental=True传递给incremental()装饰器时也是如此。

## 输入和输出的增量模式

### IncrementalTransformInput

transforms.api.IncrementalTransformInput对象扩展了dataframe()方法以接受一个可选的读取模式。

可选的输入读取模式参数仅在您使用transform()装饰器时可用。transform_df()和transform_pandas()装饰器在输入上调用dataframe()和pandas()，没有任何参数，以提取PySpark和Pandas DataFrame对象。这意味着所使用的读取模式将始终是默认的added模式。

如果您使用增量装饰器定义变换，读取模式的行为会根据您的变换是增量运行还是非增量运行而有所不同：

| 读取模式 | 增量行为 | 非增量行为 |
| --- | --- | --- |
| added* | 返回一个包含自上次变换运行以来追加到输入的任何新行的DataFrame↗。 | 返回一个包含整个数据集的DataFrame↗，因为所有行都被视为未见过。 |
| previous | 返回上次变换运行时给定的整个输入的DataFrame↗。 | 返回一个空的DataFrame↗。 |
| current | 返回当前运行的整个输入数据集的DataFrame↗。 | 返回当前运行的整个输入数据集的DataFrame↗。这将与added相同。 |

默认读取模式是added。

在某些情况下，尽管变换被标记为incremental()，但不希望将输入以增量方式处理。有关更多信息以及这些类型输入的读取模式行为有何不同，请参阅快照输入。

请注意，默认的输出读取模式是current，可用的输出读取模式有added、current和previous。有关输出读取模式的更多信息，请参阅下面的部分。

增量变换的性质意味着我们从最后一个SNAPSHOT事务开始加载输入数据集上的所有过去的事务以搭建输入视图。如果您开始在增量变换中看到逐渐变慢的情况，我们建议在增量输入数据集上运行一次SNAPSHOT搭建。

### IncrementalTransformOutput

transforms.api.IncrementalTransformOutput对象提供了对输出数据集的读取和写入模式的访问。编写兼容增量和非增量搭建的逻辑的关键是默认的modify写入模式。有两种写入模式：

- modify：此模式会修改搭建期间写入的数据的现有输出。例如，当输出处于modify模式时调用write_dataframe()将会将写入的DataFrame↗追加到现有输出。
- replace：此模式完全替换搭建期间写入的数据的输出。
当我们说一个变换以增量方式运行时，这意味着输出的默认写入模式设置为modify。同样，当我们说一个变换以非增量方式运行时，这意味着输出的默认写入模式设置为replace。

请记住，输入DataFrames的默认读取模式是added。由于默认输入读取模式为added和默认输出写入模式为modify，编写兼容增量和非增量搭建的逻辑变得更加容易：

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
@incremental()
@transform(
    students=Input('/examples/students_hair_eye_color'),
    processed=Output('/examples/hair_eye_color_processed')
)
def incremental_filter(students, processed):
    # type: (IncrementalTransformInput, IncrementalTransformOutput) -> None
    # 仅读取我们之前没有见过的行。
    new_students_df = students.dataframe()  # 这相当于 students.dataframe('added')

    # 非增量时，读取所有行并替换输出。
    # 增量时，仅读取新行，并将其追加到输出。
    processed.write_dataframe(
        new_students_df.filter(new_students_df.hair == 'Brown')  # 过滤出头发颜色为棕色的行
    )
```

对于增量计算，有更复杂的应用案例，在这种情况下，可能需要计算正确的写入模式并手动设置。这可以通过在增量输出上使用set_mode()方法来完成。

只有当您使用transform()装饰器时，才能手动设置输出写入模式。使用此装饰器，您可以在显式调用write_dataframe()方法保存输出之前使用set_mode()。另一方面，transform_df()和transform_pandas()装饰器会调用write_dataframe()和write_pandas()来保存DataFrame输出。这意味着使用的写入模式将由incremental()装饰器决定。

当使用set_mode()时，值得确保在变换增量运行或非增量运行时，这都是有效行为。如果不是这种情况，您应该利用is_incremental属性。

除了写入模式之外，transforms.api.IncrementalTransformOutput还可以从输出数据集中读取DataFrames。这可以通过dataframe()方法来完成，该方法同样接受一个非必填的读取模式。默认读取模式设置为current，其他可用的输出读取模式为added和previous。读取模式的行为取决于数据集的写入模式。

虽然默认读取模式是current，但在大多数情况下，您实际上希望使用previous。其他读取模式应在写入数据集后使用。

#### 从上一次运行中读取数据，有效组合：

要从上一次输出中读取数据，变换必须以增量模式运行（ctx.is_incremental is True），否则dataframe将为空。

| 输出读取模式 | 输出写入模式 | 是否已写入新数据？ | 行为 |
| --- | --- | --- | --- |
| current | modify | 否 | dataframe()将返回变换的上一次输出。 |
| current | modify | 是 | dataframe()将返回变换的上一次输出加上当前运行搭建中写入的输出数据。 |
| current | replace | 否 | 这些设置无效，可能导致意外行为。如果您希望合并和替换具有潜在不同架构的新输入的上一次输出，请参见合并和替换架构更改示例。 |
| current | replace | 是 | dataframe()将返回当前运行搭建中写入的输出数据。 |
| added | modify/replace | 否 | 这些设置没有应用案例。请使用previous模式。 |
| added | modify/replace | 是 | dataframe()将返回当前运行搭建中写入的输出数据。 |
| previous | modify | 是/否 | dataframe()将返回变换的上一次输出。读取previous模式时架构是必填字段。 |
| previous | replace | 是/否 | dataframe()将返回变换的上一次输出。读取previous模式时架构是必填字段。 |

请注意，使用.dataframe()调用时读取模式的计算是惰性的（按需调用），意味着计算会延迟到需要该值时。读取dataframe的输出根据数据集在write_dataframe调用期间的写入模式进行计算，因此忽略之前的写入模式。调用.localCheckpoint(eager=True)会强制读取数据，并在那时评估输出写入模式，并且不会重新计算。

当使用current获取上一个dataframe时，您不必提供schema。这是因为current使用的架构是已经搭建好的输出架构。然而，current模式比previous更脆弱。如果出现以下情况，current模式将失败：

- 变换以非增量方式运行，并且在调用输出上的dataframe之前未将write_mode覆盖为modify
- 变换以前从未计算过，因此无法构建空的DataFrame↗，因为架构未知。
在读取上一个dataframe时提供的架构 ↗将与最后一个输出的实际架构进行比较。如果列类型、列的可空性或列的顺序不匹配，将引发异常。为了确保列的顺序保持不变，请使用以下构造：

```
Copied!1
2
3
4
previous = out.dataframe('previous', schema)  # schema 是一个 pyspark.sql.types.StructType 对象

# 选择 dataframe 中的列，并按照 schema 中定义的字段名进行选择
out.write_dataframe(df.select(schema.fieldNames()))
```

Foundry会将所有列保存为可为空，无论在你的变换中使用的是什么schema。因此，如果你提供的schema中某些字段设置为不可为空，那么在以previous模式读取输出时，你的搭建将会因SchemaMismatchError而失败。

请参阅合并和替换示例以获取更多信息。

#### 读取当前运行中写入的数据，有效组合:

| 输出读取模式 | 输出写入模式 | 是否已写入新数据? |
| --- | --- | --- |
| current或added | modify/replace | 是 |

优先使用added，因为它能更清晰地表达你的意图。
一个受益于读取当前变换写入的数据的场景是，对数据进行检查，如果检查未通过则搭建失败。这样我们就不必重新计算数据或在Spark中缓存数据以进行检查。

### IncrementalTransformContext

与TransformContext对象相比，IncrementalTransformContext对象提供了一个额外的属性：is_incremental。如果变换是增量运行的，该属性将被设置为True，这意味着：

- 默认输出写入模式设置为modify，以及
- 输入默认读取模式设置为added。
### 增量模式摘要

增量装饰器让你通过指定读取模式为“previous”来访问变换的先前输入和输出。这样你可以基于历史上下文来进行当前搭建。如果变换在快照模式下运行，“previous”数据帧将是空的，因为这是第一次运行，或者逻辑或数据显著更改需要重新计算。

然而，最常见的情况是对输入使用“added”模式，对输出使用“modify”模式。这些模式是默认使用的。它们允许你从输入数据集中检索新添加的行，处理它们，并将它们附加到输出数据集中。

如果不想将行附加到输出中，你可能希望修改输出数据集中已存在的一些行。为此，请使用“replace”模式，如常见场景的示例中所示。

## 增量计算的要求

让我们分析一个增量变换，该变换筛选学生以仅包含棕色头发的学生：

```
Copied!1
2
3
4
5
6
7
8
@incremental()
@transform(
    students=Input('/examples/students_hair_eye_color'),
    processed=Output('/examples/hair_eye_color_processed')
)
def filter_hair_color(students, processed):
    students_df = students.dataframe()  # 将输入的数据转换为数据框
    processed.write_dataframe(students_df.filter(students_df.hair == 'Brown'))  # 过滤头发颜色为棕色的学生，并写入输出
```

假设/examples/students_hair_eye_color输入数据集已完全替换为一组新学生。如我们所见，将新学生集追加到先前输出会导致输出数据集不正确。这是一个incremental()装饰器会决定不增量运行变换的情况。

要使变换增量运行，必须满足以下要求：

- 自上次运行以来更新的所有变换的non_snapshot输入数据集仅向其添加了文件或由于保留而删除。
- 如果通过更新或删除文件修改了输入，则输入被标记为快照输入。
- 可在不影响搭建增量性的情况下修改变换的输入列表。
- 对于多输出变换，所有输出最后都是通过相同变换搭建的。
如果变换具有incremental()装饰器，但不满足上述任何要求，则变换将自动以非增量方式运行。这意味着默认输出写入模式将设置为replace而不是modify，并且输入将以非增量方式呈现。这也意味着在变换中从输出读取将返回空数据框，因为无法访问之前的历史。同样，输入也将以非增量方式呈现。如果我们设置require_incremental=True，变换将失败而不是以非增量方式运行。

通常希望允许某些输入被完全重写而不影响变换的增量运行能力。有关更多信息，请参见快照输入。

可以通过将require_incremental=True参数传递给incremental装饰器，强制变换仅增量运行（除非它从未运行过或语义版本已提升）。如果变换无法增量运行，它将故意失败而不是尝试以非增量方式运行。

### 仅追加输入更改

如果自上次运行以来，其所有增量输入仅向其添加了文件（通过APPEND或UPDATE事务），则变换可以增量运行。

相反，如果任何增量输入

- 已被完全重写，例如有SNAPSHOT事务，
- 已通过UPDATE或DELETE事务更新或删除文件。
例如，如果students_hair_eye_color中的学生列表完全更改，先前筛选学生的输出无效，必须被替换。

### 从Foundry Retention来的删除输入

如果上游数据集无限增长，并且您希望能够删除旧行（使用Foundry Retention）而不影响下游计算的增量性，则依赖于该数据集的增量变换必须明确设置为允许保留输入。这可以通过使用transforms.api.incremental装饰器的allow_retention参数来实现。

- 如果此字段设置为True，则在评估输入是否保留增量性时，将忽略来自Foundry Retention的所有删除。这意味着来自Retention的removed输入不会影响增量性，并且如果唯一的非added输入是具有保留行的输入，变换仍将增量运行。
- 如果字段为False（默认），则输入数据集中的任何removed类型更改将导致变换运行快照。
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
@incremental(allow_retention=True)
# 使用incremental装饰器，允许保留先前处理的结果
@transform(
    students=Input('/examples/students_hair_eye_color'),
    processed=Output('/examples/hair_eye_color_processed')
)
def filter_hair_color(students, processed):
    students_df = students.dataframe()  # 将输入的数据转换为DataFrame
    # 筛选头发颜色为“Brown”的记录，并写入输出
    processed.write_dataframe(students_df.filter(students_df.hair == 'Brown'))
```

在上述示例中，如果在数据集/examples/students_hair_eye_color中进行了一系列变更后运行变换，这些变更仅包括使用Foundry Retention进行的添加变更和移除变更，则变换将增量运行。如果存在通过其他方式进行的任何移除变更或任何修改变更，将触发快照。

指定allow_retention=True仅能防止来自Foundry Retention的移除变更对增量性的影响。输入数据集中的任何其他删除仍然会导致变换运行快照而不是增量计算。

### 快照输入

在某些情况下，允许对输入进行完整重写而不使变换的增量性失效。例如，假设您有一个简单的参考数据集，将电话号码国家代码映射到国家，并且这个数据集会定期重写。对此数据集的更改并不一定会使之前任何计算的结果失效，因此不应阻止变换增量运行。

默认情况下，如上所述，如果自变换上次运行以来任何输入被完全重写，则变换不能增量运行。快照输入不受此检查的影响，它们的起始事务允许在运行之间有所不同。

可以通过在incremental()装饰器上使用snapshot_inputs参数来配置快照输入。

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
@incremental(snapshot_inputs=['country_codes'])
@transform(
    phone_numbers=Input('/examples/phone_numbers'),
    country_codes=Input('/examples/country_codes'),
    output=Output('/examples/phone_numbers_to_country')
)
def map_phone_number_to_country(phone_numbers, country_codes, output):
    # type: (TransformInput, TransformInput, TransformOutput) -> None

    # 这将是自上次运行以来所有未见过的电话号码
    phone_numbers = phone_numbers.dataframe()
    # 这将是所有国家代码，不论以前是否见过
    country_codes = country_codes.dataframe()

    # 根据电话号码的国家代码与国家代码表进行连接匹配
    cond = [phone_numbers.country_code == country_codes.code]
    # 使用左外连接方式将匹配结果写入输出数据框
    output.write_dataframe(phone_numbers.join(country_codes, on=cond, how='left_outer'))
```

在这段代码中，我们使用增量处理的方式，将新的电话号码与国家代码进行匹配，以便将电话号码映射到对应的国家。使用左外连接的方式确保所有电话号码都能与国家代码对接，即使没有匹配到国家代码，电话号码仍然会出现在输出数据中。
当变换以增量或非增量方式运行时，快照输入的行为是相同的。因此，added和current读取模式将始终返回整个数据集。所有其他读取模式将返回空数据集。

鉴于快照输入的先前版本没有约束，可以在保留增量运行变换的能力的同时添加或删除快照输入。请记住，如果输入的修改从根本上改变了变换的语义，那么值得审查是否应该更新incremental()装饰器上的semantic_version参数。

### 输入的更改

现有输入的列表可以被修改。在以下情况下，增量性将被保留：

- 添加新的输入或新的快照输入，或
- 删除现有输入或现有快照输入。
请注意，增量变换必须至少有一个输入。
我们还要求每个非快照输入数据集的起始事务与上次运行所使用的一致。

### 最后由同一变换搭建的输出

对于多输出增量变换，每个输出上的最后一次提交事务必须由同一变换生成。

### 增量计算的要求总结

变换仅当且仅当其所有增量输入仅有文件附加到它们时，或者在文件被删除的情况下，这些文件是使用Foundry Retention删除且allow_retention=True时，可以以增量方式运行。快照输入不包括在此检查中。
