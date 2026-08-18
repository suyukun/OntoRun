来源: https://palantir.com/docs/zh/foundry/slate/widgets-control/

# 控件

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 控件

控件微件类别包含以下微件：

- 按钮
- 复选框
- 下拉框
- 输入框
- 多选框
- 单选按钮
- 分段控件
- 滑块
- 文本区域
- 切换按钮
## 按钮微件

以下表格提供了按钮微件可用属性的使用详情。表格后附有几个示例。

### 属性

| 属性 | 描述 | 类型 | 必填 | 更改方式 |
| --- | --- | --- | --- | --- |
| cssClasses | 按钮的CSS类。 | 字符串[] | 否 | 直接编辑 |
| disabled | 指定用户是否可以与微件交互。默认为false。值通常是生成布尔值的模板表达式（例如“{{w1.on}}”）。 | boolean | 是 | 直接编辑 |
| text | 按钮的显示文本。 | 字符串 | 是 | 直接编辑 |

### 示例

#### 按钮

```
Copied!1
2
3
4
5
{
  "cssClasses": ["pt-button", "pt-intent-primary"], // CSS类，用于定义按钮的样式
  "disabled": false, // 按钮是否禁用，false表示未禁用
  "text": "Run" // 按钮上显示的文本
}
```

```
Copied!1
2
3
4
5
6
{
  "cssClasses": ["pt-button", "pt-intent-primary"], // CSS类名数组，指定按钮的样式和意图
  "disabled": false, // 按钮是否禁用，false表示按钮可以使用
  "queryNames": [], // 查询名称数组，目前为空，可能用于存储与按钮相关的查询
  "text": "Run" // 按钮上显示的文本
}
```

## 复选框微件

下表提供了复选框微件可用属性的使用详情。

### 属性

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| disabled | 指定用户是否可以与微件交互。默认值为false。值通常是生成布尔值的模板化表达式（例如“{{w1.on}}”）。 | boolean | 是 | 直接编辑 |
| displayValues | 一个非必填的列表，用于定义复选框组中项目的显示值。每个项目的“values”应有一个显示值。如果未指定“displayValues”，则会显示每个项目的原始值。 | 字符串[] | 否 | 直接编辑 |
| hover | 当tooltipsEnabled = true时，此属性决定你悬停的值。 | ICheckboxHover | 否 | 用户交互 |
| selectedDisplayValues | 当前已选中项目的显示值列表。 | 字符串[] | 是 | 用户交互 |
| selectedValues | 当前已选中的项目列表。 | any[] | 是 | 用户交互 |
| tooltipsEnabled | 指定是否启用工具提示。 | boolean | 是 | 直接编辑 |
| tooltipText | 工具提示中显示的文本。如果此值为null或空字符串，则不会显示工具提示。支持HTML。 | 字符串 | 否 | 直接编辑 |
| values | 复选框组中项目的值。 | any[] | 是 | 直接编辑 |

#### ICheckboxHover

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| displayValue | 当前悬停复选框的显示值。 | 字符串 | 是 | 用户交互 |
| index | 当前悬停复选框标签的索引。 | number | 是 | 用户交互 |
| value | 当前悬停复选框的原始值。 | any | 是 | 用户交互 |

## 下拉微件

下表提供了下拉微件可用属性的使用详情。若干示例跟随在表格之后。

### 属性

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| disabled | 指定用户是否可以与微件交互。默认值为false。值通常是生成布尔值的模板化表达式（例如“{{w1.on}}”）。 | boolean | 是 | 直接编辑 |
| fuzzySearchEnabled | 切换搜索的模糊匹配。 | boolean | 是 | 直接编辑 |
| displayValues | 下拉列表中显示的值。如果未指定，将使用“values”。 | any[] | 否 | 直接编辑 |
| groups | 对应“values”条目将显示的组。 | any[] | 否 | 直接编辑 |
| maintainValidSelection | 指示当微件无效时，当前选定值是否应保持选定状态，只要该值仍然有效。 | boolean | 是 | 直接编辑 |
| searchText | 用于筛选“values”数组的搜索文本。参见serverSearchEnabled获取详细信息。 | 字符串 | 是 | 用户交互 |
| selectedDisplayValue | 下拉列表的显示值。 | 字符串 | 是 | 用户交互 |
| selectedValue | 当前用户选定的下拉值。 | any | 是 | 用户交互 |
| serverSearchEnabled | 指示用户输入的搜索文本应触发新查询。否则，本地搜索“values”数组中的匹配项。 | boolean | 是 | 直接编辑 |
| values | 设置“selectedValue”的值。如果使用displayValues，应与displayValues一一对应。 | any[] | 是 | 直接编辑 |

### 示例

#### 动态下拉列表

```
Copied!1
2
3
4
5
6
7
8
{
  "disabled": false,  // 指示此元素是否被禁用，false 表示未禁用
  "displayValues": "{{query1.memberName}}",  // 显示的值，使用模板引擎从 query1 中获取 memberName
  "searchText": "John",  // 搜索框中的文本，默认搜索文本为 "John"
  "selectedValue": "65849",  // 已选择的值，当前选中的 ID 为 "65849"
  "serverSearchEnabled": true,  // 是否启用服务器端搜索，true 表示启用
  "values": "{{query1.memberId}}"  // 值的来源，通过模板引擎从 query1 中获取 memberId
}
```

#### 静态下拉菜单

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
{
  "disabled": false,  // 控件是否禁用，false表示未禁用
  "searchText": "",   // 搜索框中的文本，默认为空字符串
  "selectedValue": "giraffe",  // 当前选中的值，默认为"giraffe"
  "serverSearchEnabled": false,  // 是否启用服务器端搜索，false表示不启用
  "values": [
    "giraffe",    // 可供选择的值之一：长颈鹿
    "rhinoceros", // 可供选择的值之一：犀牛
    "elephant"    // 可供选择的值之一：大象
  ]
}
```

```
Copied!1
2
3
4
5
6
7
{
  "disabled": false,  // 是否禁用
  "searchText": "",  // 搜索文本
  "selectedValue": null,  // 选中的值
  "serverSearchEnabled": false,  // 是否启用服务器搜索
  "values": []  // 值列表
}
```

## 输入框微件

以下表格提供了输入框微件可用属性的使用详情。表格后面是几个例子。

### 属性

| 属性 | 描述 | 类型 | 必填 | 更改了 |
| --- | --- | --- | --- | --- |
| disabled | 指定用户是否可以与微件交互。默认为false。值通常是模板表达式，产生布尔值（例如“{{w1.on}}”）。 | boolean | 是 | 直接编辑 |
| placeholder | 用于输入框占位符的文本（不支持IE9）。 | 字符串 | 否 | 直接编辑 |
| queryNames | 按下Enter键时该输入框应执行的查询名称。 | 字符串[] | 否 | 直接编辑 |
| text | 用户在框中输入的文本。 | 字符串 | 是 | 用户交互 |

### 示例

#### 输入框

```
Copied!1
2
3
4
5
6
{
  "disabled": false,  // 控制组件是否禁用，false表示启用
  "placeholder": "Choose an animal...",  // 输入框的占位符文本
  "queryName": "query1",  // 查询的名称或标识符
  "text": ""  // 输入的文本内容，初始为空
}
```

### 默认设置

```
Copied!1
2
3
4
5
{
  "disabled": false,  // 控制是否禁用的标志，false表示未禁用
  "placeholder": "placeholder goes here",  // 输入框的占位符文本
  "text": ""  // 输入框中的实际文本内容，默认为空字符串
}
```

## 多选框微件

下表提供了多选框微件可用属性的使用详情。表格后面是几个示例。

### 属性

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| disabled | 指定用户是否可以与微件交互。默认为false。值通常是生成布尔值的模板表达式（例如“{{w1.on}}”）。 | boolean | 是 | 直接编辑 |
| displayValues | 显示在多选框中的值。如果未指定，将使用‘values’。 | 字符串[] | 否 | 直接编辑 |
| fuzzySearchEnabled | 为搜索切换模糊匹配。 | boolean | 是 | 直接编辑 |
| placeholder | 多选框占位符使用的文本 | 字符串 | 否 | 直接编辑 |
| hasValues | 指示用户是否输入了值。 | boolean | 是 | 用户交互 |
| selectedDisplayValues | 当前用户输入显示的已选值。 | 字符串[] | 是 | 用户交互 |
| selectedValues | 当前用户输入的已选值。 | any[] | 是 | 用户交互 |
| searchText | 筛选‘values’数组的搜索文本。有关详细信息，请参见serverSearchEnabled。 | 字符串 | 是 | 用户交互 |
| serverSearchEnabled | 指示用户输入的搜索文本是否应触发新查询。否则，将在本地搜索‘values’数组以匹配。 | boolean | 是 | 直接编辑 |
| tokenSeparator | 分隔输入中词元的字符串。如果未指定，输入将不会被词元化。换行符在输入中被视为空格。 | 字符串 | 否 | 直接编辑 |
| values | 用于设置‘selectedValues’的值。如果使用‘displayValues’，则应与‘displayValues’一一映射。 | any[] | 是 | 直接编辑 |

### 示例

#### 动态多选

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
{
  "disabled": false,  // 控件是否被禁用，false表示未禁用
  "displayValues": "{{query1.memberName}}",  // 显示的值，动态绑定到query1的memberName字段
  "hasValues": false,  // 是否包含值，false表示当前没有可用值
  "searchText": "John",  // 搜索框中的默认文本
  "selectedDisplayValues": [],  // 用户选择后显示的值，目前为空
  "selectedValues": [],  // 用户选择的值，目前为空
  "serverSearchEnabled": true,  // 是否启用服务器端搜索，true表示启用
  "values": "{{query1.memberId}}"  // 可用的值，动态绑定到query1的memberId字段
}
```

#### 静态多选

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
{
  "disabled": false, // 表示该功能未禁用
  "hasValues": true, // 表示存在可用的值
  "selectedDisplayValues": [
    "giraffe", // 长颈鹿
    "rhinoceros" // 犀牛
  ],
  "selectedValues": [
    "giraffe", // 长颈鹿
    "rhinoceros" // 犀牛
  ],
  "serverSearchEnabled": false, // 表示服务器搜索功能未启用
  "values": [
    "giraffe", // 长颈鹿
    "rhinoceros", // 犀牛
    "elephant" // 大象
  ]
}
```

```
Copied!1
2
3
4
5
6
7
8
{
  "disabled": false,  // 指示该功能或选项是否被禁用，false表示启用
  "hasValues": false,  // 指示是否有可用的值，false表示没有可用值
  "selectedDisplayValues": [],  // 用户选择的显示值列表，当前为空
  "selectedValues": [],  // 用户选择的值列表，当前为空
  "serverSearchEnabled": false,  // 是否启用服务器端搜索，false表示未启用
  "values": []  // 可用值的列表，当前为空
}
```

## 单选按钮微件

下表提供了有关单选按钮微件可用属性的使用详细信息。

### 属性

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| disabled | 指定用户是否可以与微件交互。默认为false。值通常是生成布尔值的模板表达式（例如“{{w1.on}}”）。 | boolean | 是 | 直接编辑 |
| displayValues | 一个非必填的列表，用于定义单选按钮组中项目的显示值。‘values’中的每个项目都应该有一个显示值。如果未指定‘displayValues’，将显示每个项目的原始值。 | 字符串[] | 否 | 直接编辑 |
| preselectFirstElement | 指定是否默认选择第一个值。 | boolean | 是 | 直接编辑 |
| hover | 当tooltipsEnabled = true时，此属性确定您正在悬停的值。 | IRadioHover | 否 | 用户交互 |
| selectedDisplayValue | 当前选定的显示值。 | 字符串 | 是 | 用户交互 |
| selectedValue | 当前选定的值。 | any | 是 | 用户交互 |
| tooltipsEnabled | 指定是否启用工具提示。 | boolean | 是 | 直接编辑 |
| tooltipText | 工具提示中显示的文本。如果此值为null或空字符串，则不会显示工具提示。支持HTML。 | 字符串 | 否 | 直接编辑 |
| values | 单选按钮组中项目的值。 | any[] | 是 | 直接编辑 |

#### ICheckboxHover

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| displayValue | 当前悬停的单选按钮的显示值。 | 字符串 | 是 | 用户交互 |
| index | 当前悬停的单选标签的索引。 | number | 是 | 用户交互 |
| value | 当前悬停的单选按钮的原始值。 | any | 是 | 用户交互 |

## 分段控制微件

下表提供了有关分段控制微件可用属性的使用详细信息。

### 属性

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| disabled | 指定用户是否可以与微件交互。默认为false。值通常是生成布尔值的模板表达式（例如“{{w1.on}}”）。 | boolean | 是 | 直接编辑 |
| displayValues | 分段控制中显示的值。如果未指定，将使用‘values’。 | any[] | 否 | 直接编辑 |
| hover | 当tooltipsEnabled = true时，此属性确定您正在悬停的值。 | ISegmentedControlHover | 否 | 用户交互 |
| multiselectEnabled | 指定用户是否只能选择一个值或多个值。 | boolean | 是 | 直接编辑 |
| preselectFirstElement | 指定是否默认选择第一个值。 | boolean | 是 | 直接编辑 |
| selectionRequired | 指定是否可以取消选择所有值。启用时，此标志会阻止用户取消选择微件中最终选定的值。如果微件开始时没有选择任何值，则在用户进行初始选择后才阻止取消选择。 | boolean | 是 | 直接编辑 |
| selectedValues | 当前用户选定的值或多个值。 | any[] | 是 | 用户交互 |
| tooltipsEnabled | 指定是否应显示工具提示 | boolean | 是 | 用户交互 |
| tooltipText | 工具提示中显示的文本。支持HTML。 | 字符串 | 否 | 直接编辑 |
| values | ‘selectedValues’设置的值。如果使用displayValues，应该与displayValues一一对应。 | any[] | 是 | 直接编辑 |

#### ISegmentedControlHover

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| displayValue | 当前悬停的段的显示值。 | 字符串 | 是 | 用户交互 |
| index | 当前悬停的段的索引。段从左到右编号 | number | 是 | 用户交互 |
| value | 当前悬停的段的原始值。 | any | 是 | 用户交互 |

## 滑块微件

下表提供了有关滑块微件可用属性的使用详细信息。表格后面跟随几个示例。

### 属性

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| disabled | 指定用户是否可以与微件交互。默认为false。值通常是生成布尔值的模板表达式（例如“{{w1.on}}”）。 | boolean | 是 | 直接编辑 |
| formatMode | 指定如何格式化滑块标签。“Grouped”将使用指定的分隔符将数字分组。例如：如果分隔符是逗号，1000000将变成1,000,000。“Numeric”将使用提供的Numeral.js ↗格式格式化值。“Time”将使用提供的moment.js ↗格式格式化值。 | 字符串 | 是 | 直接编辑 |
| formatter | 当选择“Numeric”或“Time”时，此属性保存格式字符串。 | 字符串 | 否 | 直接编辑 |
| from | 当启用范围模式时，此属性保存范围的下限值。否则，它保存与单个滑块手柄当前位置关联的值。 | number | 是 | 用户交互 |
| groupingDelimiter | 当选择“Grouped”格式时，此属性保存用于分组的分隔符字符串。 | 字符串 | 否 | 直接编辑 |
| max | 可选择的最大值。 | number | 是 | 直接编辑 |
| min | 可选择的最小值。 | number | 是 | 直接编辑 |
| numLabels | 显示的轴标签数量。如果没有提供值，默认为6。 | number | 是 | 直接编辑 |
| postfix | 附加到所有值的文本。例如：“ €”将“100”转换为“100 €” | 字符串 | 否 | 直接编辑 |
| prefix | 前置到所有值的文本。例如：“$”将“100”转换为“$100” | 字符串 | 否 | 直接编辑 |
| rangeEnabled | 指定是否启用范围值选择或仅启用单点选择。 | boolean | 是 | 直接编辑 |
| step | 可选择值的步长。 | number | 否 | 直接编辑 |
| to | 当启用范围模式时，此属性保存范围的上限值。 | number | 否 | 用户交互 |
| updateOnSlide | 指定滑块的值何时更新。“Release”表示在释放手柄后更新值。“Slide”表示在拖动滑块时更新值。由于性能影响，应避免使用“Slide”进行重操作（如UI更新）。“Slide”更新被限制为100ms。 | boolean | 是 | 直接编辑 |

### 示例

#### 滑块

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
{
  "disabled": false,  // 启用状态，false表示启用
  "from": 25,  // 范围的起始值
  "groupingDelimiter": " ",  // 分组分隔符
  "groupingEnabled": true,  // 启用分组，true表示启用
  "max": "{{query1.maxValue}}",  // 最大值，动态获取自query1的maxValue
  "min": 1,  // 最小值
  "prefix": "$",  // 前缀符号，这里是美元符号
  "rangeEnabled": true,  // 启用范围，true表示启用
  "to": 50  // 范围的结束值
}
```

```
Copied!1
2
3
4
5
6
7
8
{
  "disabled": false,          // 是否禁用，false表示未禁用
  "from": 25,                 // 起始值为25
  "groupingEnabled": false,   // 是否启用分组，false表示未启用
  "max": 100,                 // 最大值为100
  "min": 0,                   // 最小值为0
  "rangeEnabled": false       // 是否启用范围，false表示未启用
}
```

## 文本区域微件

下表提供了文本区域微件可用属性的使用详情。表格后附有几个示例。

### 属性

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| delimiter | 一个或多个字符的序列，用于表示两个值的分隔。例如，如果‘text’是“hello- -world”且‘delimiter’是“- -”，‘values’将变为["hello", "world"] | 字符串 | 否 | 直接编辑 |
| disabled | 指定用户是否可以与微件互动。默认为false。值通常是模板化表达式，生成布尔值（例如：“{{w1.on}}”）。 | 布尔值 | 是 | 直接编辑 |
| hasValues | 指示用户是否输入了值。 | 布尔值 | 是 | 用户互动 |
| maxLengthEnabled | 如果启用，限制用户输入文本的长度。 | 布尔值 | 是 | 直接编辑 |
| maxLength | 允许输入到框中的文本的最大长度。 | 数字 | 否 | 直接编辑 |
| placeholder | 用于文本区域占位符的文本（不支持IE9） | 字符串 | 否 | 直接编辑 |
| text | 用户输入到框中的文本。 | 字符串 | 是 | 用户互动 |
| values | 从inputText派生的用户输入值。 | 数组 | 是 | 用户互动 |

### 示例

#### 文本区域

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
{
  "delimiter": ";",  // 分隔符，用于分隔多个值
  "disabled": false, // 是否禁用此项，false表示未禁用
  "hasValues": true, // 指示是否存在值，true表示存在
  "placeholder": "Choose an animal...", // 占位符文本，提示用户选择动物
  "text": "giraffe; rhinoceros; elephant", // 显示的文本，列出所有动物
  "values": [
    "giraffe",    // 长颈鹿
    "rhinoceros", // 犀牛
    "elephant"    // 大象
  ]
}
```

```
Copied!1
2
3
4
5
6
7
{
  "delimiter": ";", // 定义数据分隔符为分号
  "disabled": false, // 表示未禁用
  "hasValues": false, // 指示当前没有值
  "text": "", // 文本字段为空
  "values": [] // 值列表为空
}
```

## 切换微件

下表提供了关于切换微件可用属性的使用详情。表格后面有几个示例。

### 属性

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| disabled | 指定用户是否可以与微件交互。默认值为false。值通常是生成布尔值的模板表达式（例如“{{w1.on}}”）。 | boolean | 是 | 直接编辑 |
| offLabel | 切换开关“关闭”状态的标签 | 字符串 | 是 | 直接编辑 |
| onLabel | 切换开关“开启”状态的标签 | 字符串 | 是 | 直接编辑 |
| useCustomIcons | 选中时，切换将使用Blueprint中的自定义图标 | 复选框 | 是 | 直接编辑 |
| onIcon | 切换开关“开启”状态的图标 | 字符串 | 否 | 直接编辑 |
| offIcon | 切换开关“关闭”状态的图标 | 字符串 | 否 | 直接编辑 |
| on | 切换开关的当前状态，“开启”状态对应“true” | boolean | 是 | 用户交互 |
