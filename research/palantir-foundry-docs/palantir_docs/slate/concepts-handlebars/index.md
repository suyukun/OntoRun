来源: https://palantir.com/docs/zh/foundry/slate/concepts-handlebars/

# 使用 Handlebars 访问值

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 使用 Handlebars 访问值

Slate 在查询、函数和微件中使用Handlebars ↗进行模板化。Handlebars 模板被包裹在{{}}中，可以访问 Slate 对象，如微件、变量和查询/函数结果。例如，如果您有一个下拉微件w1，可以使用模板{{w1.selectedValue}}访问选定的值。Slate 会自动评估模板并将其替换为评估后的值。

Handlebars 模板还可以调用辅助函数。有关更多信息，请参见辅助函数。

## 可以引用哪些 Slate 对象？

### 变量

您可以使用{{variableName}}访问在变量编辑器中定义的变量。例如，如果您有一个变量var1={"a":[1,2,3]}，则模板{{var1.a.[0]}}评估为1。
您还可以访问 Slate环境变量，包括有关当前应用程序用户或用户专用存储的信息。例如，使用模板 {{$global.user.firstName}} 将显示用户的名字。

### 查询

您可以访问查询结果。例如，{{myQuery}}包含来自 SQL 或 HttpJson 查询的结果。还有一个隐藏的_response字段，包含一些元数据。

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
  "name": ["Ceres", "Pallas"],
  "earthmoid": [1.59376, 1.23071],
  "pha": [false, false],
  "datefirstobs": ["1830-04-18", "1825-03-23"],
  "_response": {
    "hasRun": true,
    "message": "Unable to parse query.", // 无法解析查询。
    "success": false
  }
}
```

注意：原始 JSON 数据中"_response"部分的逗号丢失，已在datefirstobs键之后添加了缺失的逗号。

### 函数

可以通过将函数名用双大括号括起来来访问函数的返回值。例如，{{myFunction}}。

### 微件属性

可以访问某些微件属性。具体来说，模板可以访问叶子属性（包括数组及其子属性）。例如，假设我们有一个图表微件。

这些是微件的原始JSON选项卡中列出的属性：

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
{
  "allowSelection": true, // 允许选择
  "animate": true, // 启用动画效果
  "datasets": [
    {
      "name": "dataset1",
      "renderer": "bar", // 使用条形图渲染
      "xValues": "{{yearToObsNum.name}}", // x轴值，使用yearToObsNum.name占位符
      "yValues": "{{yearToObsNum.numofobs}}" // y轴值，使用yearToObsNum.numofobs占位符
    }
  ],
  "labelsEnabled": false, // 不启用标签
  "panZoomEnabled": false, // 不启用平移和缩放功能
  "selection": {
    "indices": [], // 选择的索引
    "xMax": null, // x轴最大值
    "xMin": null, // x轴最小值
    "xValues": [], // x轴选择的值
    "yMax": null, // y轴最大值
    "yMin": null, // y轴最小值
    "yValues": [] // y轴选择的值
  },
  "tooltipsEnabled": false, // 不启用工具提示
  "xAxes": [
    {
      "gridlinesEnabled": false, // 不启用网格线
      "label": "first observed {{w9.selectedValue}}", // x轴标签，使用w9.selectedValue占位符
      "name": "x1", // x轴名称
      "position": "bottom", // x轴位置
      "scale": "category" // x轴刻度类型
    }
  ],
  "yAxes": [
    {
      "gridlinesEnabled": false, // 不启用网格线
      "label": "Number of Observations", // y轴标签
      "name": "y1", // y轴名称
      "position": "left", // y轴位置
      "scale": "linear" // y轴刻度类型
    }
  ]
}
```

这些是您可以访问和无法访问的属性：

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
{{w1.allowSelection}}             (leaf property) // 叶子属性，允许选择
{{w1.animate}}                    (leaf property) // 叶子属性，动画效果
{{w1.datasets}}                   (array) // 数组，数据集
{{w1.datasets.[0]}}               (subproperty inside array) // 数组内的子属性，第一个数据集
{{w1.datasets.[0].xValues}}       (array subproperty inside array) // 数组内的子属性，X值
{{w1.datasets.[0].xValues.[0]}}   (subproperty inside array) // 数组内的子属性，第一个X值
{{w1.labelsEnabled}}              (leaf property) // 叶子属性，标签启用
{{w1.panZoomEnabled}}             (leaf property) // 叶子属性，平移缩放启用
{{w1.selection.indices}}          (array) // 数组，选中索引
{{w1.selection.xMax}}             (leaf property) // 叶子属性，X最大值
{{w1.selection.xMin}}             (leaf property) // 叶子属性，X最小值
{{w1.selection.xValues}}          (array) // 数组，选中X值
{{w1.selection.yMax}}             (leaf property) // 叶子属性，Y最大值
{{w1.selection.yMin}}             (leaf property) // 叶子属性，Y最小值
{{w1.selection.yValues}}          (array) // 数组，选中Y值
{{w1.tooltipsEnabled}}            (leaf property) // 叶子属性，工具提示启用
{{w1.xAxes}}                      (array) // 数组，X轴
{{w1.yAxes}}                      (array) // 数组，Y轴
{{w1.yAxes.[0]}}                  (subproperty inside array) // 数组内的子属性，第一个Y轴

{{w1}}                            (not accessible, not leaf) // 不可访问，非叶子
{{w1.selection}}                  (not accessible, not leaf) // 不可访问，非叶子
```

## Handlebars可以在哪里使用？

### 查询编辑器

查询编辑器中的Handlebars模板始终替换为字符串值。如果模板未评估为字符串，则首先将该值转换为字符串。这是因为查询本身始终是一个字符串。例如：

```
Copied!1
SELECT {{column w8.selectedValues}} FROM allNamed WHERE name = {{param w12.selection.xValues}};
```

```
Copied!1
2
3
-- 该SQL查询从表`allNamed`中选择指定列，其中列名由`w8.selectedValues`参数提供。
-- 查询条件为`name`字段等于`w12.selection.xValues`参数提供的值。
-- 这是一个动态SQL查询，通常用于处理可变列和条件。
```

非字符串值通过toString方法进行转换。对于整数和布尔值，这通常效果很好，但在更复杂的对象上可能会产生意外的输出。例如，在一个对象上运行toString会得到[object Object]，这可能不是您想要的结果。您可以使用类似{{jsonStringify myObject}}这样的助手来解决此问题。

### 函数编辑器

与查询不同，函数编辑器中的Handlebars模板总是被其评估值替换。例如：

```
Copied!1
2
var a = {{query1}};  // query1 是一个对象
var b = a.results[0];  // 你可以访问其属性，这里访问的是 results 数组的第一个元素。
```

辅助函数不能在函数编辑器中使用，必须直接引用Slate对象。此外，您不能设置变量或属性值，因为您不能更改函数之外的任何状态。例如：

```
Copied!1
2
var c = {{jsonStringify query1}}; // 无效 - 不能使用助手函数
{{var1}} = [1,2,3];  // 无效 - 不能设置全局变量
```

### 微件属性编辑器

当应用程序处于编辑模式时，您可以在微件的属性编辑器中使用Handlebars。在微件中，Handlebars模板必须始终用双引号""括起来，因为花括号不是有效的JSON语法。

```
Copied!1
2
3
4
5
6
{
  "property1": "{{variable1}}",
  "property2": "Hello, my name is {{var1}}",
  "property3": [1, 2, "{{var3}}"],
  "property4": {{variable1}}  // 无效：JSON 解析错误
}
```

在 JSON 中，所有的值都必须是有效的 JSON 数据类型，例如字符串、数字、数组、对象、true、false 或 null。property4中直接使用{{variable1}}是无效的，因为这不是一个有效的 JSON 数据类型。如果{{variable1}}是一个模板占位符，应将其置于字符串中，即"{{variable1}}"。
一般情况下，微件中的模板会被替换为字符串。如果评估的值不是字符串，那么Slate会对该值运行toString。此规则有几个例外。当满足以下条件时，Slate会直接用评估的值替换模板：

- 只有一组括号{{}}并且
- 括号外没有其他字符（包括空格）。
让我们来看几个例子：

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
  // 值替换示例
  "property1": "{{var1}}",  // 直接替换变量var1的值
  "property2": "{{ var1 }}",  // 花括号内部有空格，仍然替换变量var1的值
  "property3": "{{ add 2 (add 1 var1) }}",  // 使用助手函数，支持嵌套运算
  "property4": ["{{var1}}", "{{w1.property.[0]}"],  // 数组中的元素进行值替换

  // 字符串替换示例
  "property5": "Hello {{var1}}!",  // 字符串中嵌入变量值
  "property6": " {{var1}} ",  // 花括号外部的空格不影响替换
  "property7": "{{#if 0}}3{{else}}4{{/if}}"  // 条件语句，0为假，返回else分支的值
}
```

## Handlebars不能使用的地方？

- Handlebars不能用于变量编辑器。
- Handlebars不能用于样式编辑器。
- Handlebars不能用于应用程序的查看模式中。如果您在微件或文本字段中输入handlebars，表达式既不会被评估也不会被替换。
## 教程：链接微件

以下教程将教您如何创建一个按钮，以便用户可以选择了解更多关于特定航班的飞机信息。为此，我们需要在两个微件之间创建一个链接。

要链接微件，您必须知道微件的名称和要链接的属性。在我们的例子中，我们希望获取原始表中选定行的tail_num值，但我们在表中配置选择使用flight_id作为主键。

这是使用另一个帮助函数的理想时机。由于获取选定表格行的列值是一个常见模式，我们可以使用一个函数来实现：

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
function getRowData(s){
    var returnObj = {};
    var index = data[selectionColumn].indexOf(s);

    // 遍历对象data中的每个数组
    // value是实际的数组，key是该数组的键
    _.forOwn(data, function(value, key){
        returnObj[key] = value[index];
    });

    return returnObj;
}

// 与表格中使用的数据相同
var data = {{f_data}};

// 表格中当前的选择
var selection = {{w_mainTable.selectedRowKeys}};

// 被配置为表格主键的列
var selectionColumn = {{w_mainTable.selectionIdentityColumnId}}

// 使用selection数组中的每个元素调用getRowData函数
// 并返回每一行的数据
var rowData = _.map(selection, getRowData);

return rowData;
```

将一个新的函数命名为f_selectedRowValues添加到上述代码中。更改var data的 Handlebar 模板以指向{{q_allFlights}}，并将selectionColumn和selection变量指向我们的w_flightTable。

要理解selectedRowKeys是什么，请回顾表格微件的代码。我们将"selectionIdentityColumnId"设置为"flight_id"。这意味着列flight_id被用作给定行的唯一键。一旦用户在表格中选择了一行，该唯一键（航班 ID 号）就会被添加到selectedRowKeys。

selectedRowKeys是表格微件的一个属性，只能通过用户交互进行修改。当编辑微件时，您可以在 JSON 编辑器下方看到用户交互属性的只读值。

现在，我们可以通过选择测试在表格中做出选择，以验证函数行为。

在配置了我们的选择函数后，我们可以添加一个文本微件，将其命名为w_linkingButton并将其移动到表格上方。在微件的属性编辑器中，切换到内容下的HTML选项卡并输入以下内容：

```
Copied!1
2
3
4
5
6
7
8
<a
     class = 'pt-button pt-intent-primary pt-icon-document-open'
     target = '_blank'
     href = 'https://registry.faa.gov/AircraftInquiry/Search/NNumberResult?nNumberTxt={{f_selectedRowValues.[0].tail_num}}'
     role='button'>
        Learn More About Aircraft {{f_selectedRowValues.[0].tail_num}}
        <!-- 了解更多关于飞机的信息 {{f_selectedRowValues.[0].tail_num}} -->
</a>
```

该代码段是一个HTML超链接按钮，通过点击它可以打开一个新标签，访问FAA（美国联邦航空管理局）的飞机查询页面。{{f_selectedRowValues.[0].tail_num}}是一个动态值，表示所选飞机的尾号。

上面的代码具有两个功能。添加pt-button使微件看起来像一个按钮，而添加pt-intent-primary则将背景变为蓝色。添加"pt-icon-document-open"会在按钮上添加一个Blueprint图标。您可以从Blueprint文档 ↗中查看完整的图标列表。

接下来，我们通过将用户输入添加到基础URL来搭建一个链接。然后，我们设置显示文本。

此外，我们可以添加一段样式代码以右对齐微件，方便调整：

sl-text {text-align: right}

文本和链接都依赖于上面配置的选择函数：{{f_selectedRowValues.[0].tail_num}}。f_selectedRowValues指的是从我们在教程中早期创建的表格选择中读取的函数。

当没有选择时，文本微件将显示了解更多关于飞机。此时选择它会导致一个损坏的链接。

一旦表格中的一行被选中，按钮文本将更新为反映选择的名称；选择按钮会带您进入正确的网页。

确保保存您的应用程序，并从右上角选择X退出到查看模式。
