来源: https://palantir.com/docs/zh/foundry/forms/code-editor/

# 代码编辑器

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 代码编辑器

在Foundry上，Foundry Forms不再是数据输入或数据输出工作流的推荐方法。相反，使用Foundry Ontology搭建用户输入工作流，将相关数据结构表示为对象类型，并通过操作配置数据输出交互。更多信息请查阅Forms概述文档。

代码编辑器允许用户查看和编辑表单的YAML表示。虽然大多数配置可以通过可视化编辑器完成，但代码编辑器提供完整的功能，包括添加四个仅限代码字段的能力。

要查看代码编辑器的实际操作，请通过选择表单左下角的黑色</>按钮打开它。然后，使用可视化编辑器添加一个字段。注意，当配置字段时，代码会自动填充和更新。

选择代码编辑器右上角的书本图标，可以直接在代码编辑器窗口中打开示例和文档。

## 代码结构

表单的一般结构如下：

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
name: New form
fields:
  - uri: name
    name: Full name
    type: Text
    # 和其他通用选项
    options:
      placeholder: 'Last, First'
      # 和其他特定选项
sheets:
  - name: New sheet
    fields:
      - uri: date_of_birth
        name: Date of birth
        type: DatePicker
        options:
          precision: day
      - uri: weight_kg
        name: Weight
        type: Numeric
        options:
          unit: kg
```

这个代码片段定义了一个表单结构，其中包含多个字段和一个工作表（sheet）。表单的名称是 "New form"。在字段定义部分：

- uri指定字段的唯一标识符。
- name指定字段的显示名称。
- type指定字段的数据类型，例如文本（Text）或日期选择器（DatePicker）。
- options提供额外的字段选项，例如占位符文本（placeholder）和日期精度（precision）。
工作表定义类似于表单字段，并允许对数据进行更详细的分类和组织。
在顶层，有name（表单的标题）、fields（字段列表）和sheets（表单页的列表）。然后，每个sheet本身也有这些相同的选项。字段具有通用选项，如uri、name和type，以及特定选项（在options下），如placeholder、precision和unit。

### 通用选项

以下选项可以为每个字段配置：

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
    uri: string  # 资源标识符
    type: string  # 类型
    name: string  # 名称
    urlParam: string  # URL参数
    tag: string  # 标签
    helperText: string  # 辅助文本
    infoText: string  # 信息文本
    columnSpan: integer  # 列跨度
    disabled: Boolean  # 是否禁用
    hidden: Boolean  # 是否隐藏
    isBlock: Boolean  # 是否为块元素
    noLabel: Boolean  # 是否无标签
    validators: list<Validators>  # 验证器列表
    transforms: list<Transforms>  # 转换器列表
```

- uri: 该字段的唯一标识符。如果字段被写回到Fusion或Ontology中，则需要分别匹配列名或属性ID。如果字段不被写回，则需要以前缀display.开头。
- type: 字段的类型（例如，Text、Numeric、DatePicker）。
- name: 字段的标签。
- urlParam: 与字段相关联的URL参数。这允许用户在表单嵌入到iframe时预填充值。
- tag: 字段的另一个唯一标识符，但没有限制。当一个字段引用另一个字段时使用此标识符（例如，Calculation、Template），attachments除外。
- helperText: 字段下方的说明文字。
- infoText: 显示在字段标签旁边的信息提示内容。
- columnSpan: 字段占用的列数。
- disabled: 允许用户将字段设置为只读。
- hidden: 允许用户隐藏字段但记录值。
- isBlock: 允许用户将标签显示在字段上方而不是左侧。
- noLabel: 允许用户隐藏字段的标签。这仅通过代码编辑器可用。
- validators: 字段上的验证器。
- transforms: 字段上的变换。
## 仅限代码的字段

四个字段仅通过代码编辑器可用：

- Hidden
- List
- Composite
- List aggregate
### Hidden

hidden字段允许用户记录一个值而不显示字段。配置如下：

```
Copied!1
2
3
4
5
- uri: Hidden
  name: Hidden
  type: Hidden
  options:
    val: string # 这里的`val`是一个字符串类型的选项
```

在这个YAML文件片段中，uri、name和type都是被隐藏的属性，而options下的val属性类型为字符串。

### 列表

列表字段允许用户在字段本身不支持的情况下存储多个值。配置如下：

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
- uri: names
  name: Full names
  type: List
  options:
    # allowZeroItems: true  # 允许列表为空
    item:
      type: Text
      # and other supported generic options (helperText, infoText, validators)
      # 以及其他支持的通用选项（helperText、infoText、validators）
      options:
        placeholder: 'Last, First'  # 输入框的占位符提示为“姓，名”
        # and other specific options
        # 以及其他特定选项
```

allowZeroItems是非必填的，默认值为 false。

### 复合

复合字段允许用户将多个字段的值存储为一个字符串化的JSON。其配置如下：

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
- uri: info
  name: Composite
  type: Composite
  options:
    fields:
      - uri: date_of_birth
        name: Date of birth
        type: DatePicker
        # 其他支持的通用选项（helperText、infoText、disabled、isBlock、noLabel、validators）
        options:
          precision: day
          # 其他特定选项
      - uri: weight_kg
        name: Weight
        type: Numeric
        options:
          unit: kg
```

这个代码片段定义了一个名为Composite的复合组件，其中包含两个字段：date_of_birth和weight_kg。date_of_birth使用DatePicker类型，并设置了日期精度为天（day）。weight_kg使用Numeric类型，并指定单位为千克（kg）。

隐藏字段和允许多个值的字段不允许在组合字段中使用。

### 列表聚合

列表聚合字段类似于计算和模板字段，但作用于存储多个值的字段。其配置如下：

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
- uri: single_value
  tag: single_value
  name: Single Value
  type: RadioButtons
  options:
    options:
      - value: '10'
      - value: '20'
      - value: '30'
- uri: multi_values
  name: Multiple Values
  tag: multi_values
  type: Checkboxes
  options:
    options:
      - value: '40'
      - value: '50'
      - value: '60'
- uri: avg_value
  name: Average Value
  type: ListAggregate
  options:
    listOperation:
      operation: mean
      listTag: [single_value, multi_values]
    # errorValue: No values selected
    # 计算平均值的操作，listTag 指定要计算的标签
    # 如果没有选择任何值，将返回错误信息
```

这个 YAML 配置文件定义了三个组件：

- Single Value: 单选按钮，用户可以从 '10', '20', '30' 中选择一个值。
- Multiple Values: 复选框，用户可以从 '40', '50', '60' 中选择多个值。
- Average Value: 计算平均值的组件，它从single_value和multi_values中选择的值来计算平均值。如果没有选择任何值，将返回错误信息（注释掉的部分）。
或者，当与复合字段一起使用时：
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
- uri: grades
  tag: grades
  name: Grades
  type: List
  options:
    item:
      type: Composite
      options:
        fields:
          - uri: name
            name: Name
            type: Text
            options:
              placeholder: 'Last, First'  # 提示文本格式为"姓, 名"
          - uri: grade
            name: Grade
            type: Numeric
            options:
              unit: '%'  # 成绩单位为百分比
- uri: all_grades
  name: All grades
  type: ListAggregate
  options:
    listOperation:
      operation: concatenate  # 操作类型为连接
      joinWith: ', '  # 使用逗号和空格进行分隔
      listTag: grades  # 连接的列表标签为grades
      displayItem: grade  # 显示的项目为grade
    # errorValue: No grades added  # 错误信息：未添加成绩
```

配置options字段时：

- errorText为非必填，默认是空字符串。
- 在listOperation中：operation可以是concatenate、sum、min、max、mean或count。listTag是被聚合字段的标签（或标签数组）。当操作为concatenate时，joinWith是必需的。当聚合字段是composite字段时，displayItem是必需的，并且是嵌套字段的URI。
- operation可以是concatenate、sum、min、max、mean或count。
- listTag是被聚合字段的标签（或标签数组）。
- 当操作为concatenate时，joinWith是必需的。
- 当聚合字段是composite字段时，displayItem是必需的，并且是嵌套字段的URI。