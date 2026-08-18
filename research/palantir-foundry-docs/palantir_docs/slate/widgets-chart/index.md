来源: https://palantir.com/docs/zh/foundry/slate/widgets-chart/

# 图表

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 图表

图表微件类别包括以下微件：

- 条形图带图例的条形图堆叠条形图水平条形图多系列图
- 带图例的条形图
- 堆叠条形图
- 水平条形图
- 多系列图
- 甘特图
- 热网格
- 折线图
- 饼图
- 散点图
- 树状图
本页面包含有关图表微件可用属性的信息，以及微件的示例和常见CSS。

## 图表微件属性

下表提供了有关图表微件可用属性的使用详情。

| 属性 | 描述 | 类型 | 必需 | 更改者 |
| --- | --- | --- | --- | --- |
| dataSelectionEnabled | 指定用户是否可以选择条形和散点。图例选择在“Multiple”模式下也可用。选定的数据通过图表的selection.data属性公开。（如果启用平移/缩放，则禁用） | boolean | 是 | 直接编辑 |
| dataSelectionMode | 指定数据选择行为。“Single”模式仅允许单击交互。“Multiple”模式允许矩形框选择和cmd/ctrl+点击交互。（如果启用平移/缩放，则禁用） | 字符串 | 否 | 直接编辑 |
| animate | 指定图表数据在加载、更改和刷新时是否会动画化。 | boolean | 是 | 直接编辑 |
| areaSelectionEnabled | 指定用户是否可以在图表上绘制区域选择。（如果轴类型为‘Category’，数据选择为‘Multiple’，存在多个轴，或启用平移/缩放，则禁用） | boolean | 是 | 直接编辑 |
| autorangePanZoomEnabled | 当单轴启用平移和缩放时，可以应用自动范围动态缩放第二轴以适应数据。 | boolean | 是 | 直接编辑 |
| datasets | 参见IDatasetModel及其子类型如下。 | IDatasetModel[] | 是 | 直接编辑 |
| zeroBoundYAxisEnabled | 允许数据集不跨越Y值为0的定量图表具有以0为界的Y轴。警告：禁用此选项可能会导致视觉上误导的图表。 | boolean | 是 | 直接编辑 |
| hover | 当tooltipsEnabled = true时，此属性确定您悬停的值。要在其他地方链接到此变量，您必须首先通过模板声明它“hover”: { “xValue”: null, “yValue”: null }。有关更多信息，请参见IHover。请注意，hover适用于除stackedArea之外的所有图表。还请注意，hover默认为yValue。 | IHover | 否 | 用户交互 |
| labelsEnabled | 启用静态标签。仅适用于条形图。选项包括“start”、“middle”、“end”或“outside”。 | boolean | 是 | 直接编辑 |
| labelsPosition | 指定条形图标签的位置。选项包括“start”、“middle”、“end”或“outside”。 | 字符串 | 否 | 直接编辑 |
| legendEnabled | 启用显示图例。位置的可用选项包括“top”、“bottom”、“left”或“right”。 | boolean | 是 | 直接编辑 |
| legendPosition | 图例的位置。可用选项包括“top”、“bottom”、“left”或“right”。 | 字符串 | 否 | 直接编辑 |
| panZoomEnabled | 指定图表是否应允许平移和缩放。仅适用于数值轴。禁用此选项将重置比例。比例不会在保存时保持一致。（如果启用数据选择、区域选择，或所有轴类型为‘Category’，则禁用） | boolean | 是 | 直接编辑 |
| panZoomAxes | 启用平移和缩放的轴。可用选项是“X和Y”、“仅X”或“仅Y”。 | 字符串 | 否 | 直接编辑 |
| selection.area | 当前的区域选择。仅在启用区域选择时相关。参见IAreaSelection如下。 | IAreaSelection | 否 | 用户交互 |
| selection.data | 当前选定的图表数据。仅在启用数据选择时相关。参见IDataSelection如下。 | IDataSelection | 否 | 用户交互 |
| tooltipsEnabled | 指定是否启用工具提示。工具提示将显示由hover设置的数据值（默认值为y-value）。 | boolean | 是 | 直接编辑 |
| tooltipText | 工具提示中显示的文本（必须为true）。这通常用于显示悬停值。如果省略tooltipText或为空字符串，则工具提示将在所有图表中显示yValue，除水平条形图（显示xValue）外。 | 字符串 | 否 | 直接编辑 |
| xAxes | x轴数组。 | IAxis[] | 是 | 直接编辑 |
| yAxes | y轴数组。 | IAxis[] | 是 | 直接编辑 |
| title | 图表的标题。 | 字符串 | 否 | 直接编辑 |

### IAxis

| 属性 | 描述 | 类型 | 必需 | 更改者 |
| --- | --- | --- | --- | --- |
| formatter | 格式化轴刻度。格式字符串取决于轴的类型：对于线性/对数，请参见Numeral.js 文档 ↗；对于时间序列，请参见moment.js 文档 ↗; 不适用于类别; 小数精度限制为20位。 | 字符串 | 否 | 直接编辑 |
| gridlinesEnabled | 指定是否应为轴显示网格线。目前仅适用于非类别轴 | boolean | 是 | 直接编辑 |
| betweenTicks | 指定轴网格线的对齐是否在刻度之间，默认为false并在刻度上绘制网格线 | boolean | 是 | 直接编辑 |
| name | 轴的名称，由ISeries中的xAxisName和yAxisName引用。 | 字符串 | 是 | 直接编辑 |
| position | 轴的位置。对于x轴，位置可以是顶部或底部。对于y轴，左或右。 | 字符串 | 是 | 直接编辑 |
| label | 与轴关联的标签。 | 字符串 | 否 | 直接编辑 |
| scale | 轴类型。对于y轴（位置左和右），比例可以是线性、修正对数或类别。对于x轴（位置顶部和底部），比例也可以是时间序列。注意：目前时间序列比例期望日期为表示纪元后毫秒的整数。SQL日期格式通常以字符串形式到达Slate，因此如果时间图表不起作用，请尝试按如下方式将其转换为整数：MySQL:SELECT UNIX_TIMESTAMP(date_column)*1000 AS date_number或 Postgres:SELECT EXTRACT(epoch FROM date_column)*1000 AS date_number。请记得在上述示例中将xValues更新为新创建的数字列，“{{query1.date_number}}}” | 字符串 | 否 | 直接编辑 |
| scaleMax | 轴的最大值（如果未指定，轴将自动范围）。 | number | 否 | 直接编辑 |
| scaleMin | 轴的最小值（如果未指定，轴将自动范围）。 | number | 否 | 直接编辑 |
| tickInterval | 刻度值之间的间隔。仅适用于线性比例的轴。 | number | 否 | 直接编辑 |
| tickLabelAngle | 旋转类别轴的刻度标签：90、0和90。仅适用于具有类别比例的轴。 | number | 否 | 直接编辑 |
| visible | 指定是否应显示轴。 | boolean | 是 | 直接编辑 |
| maxZoomSpan | 缩小时轴将显示的最大值跨度。无法超出此值进行缩小。 | number | 否 | 直接编辑 |
| minZoomSpan | 放大时轴将显示的最小值跨度。无法超出此值进行放大。 | number | 否 | 直接编辑 |

### IAreaSelection

| 属性 | 描述 | 类型 | 必需 | 更改者 |
| --- | --- | --- | --- | --- |
| selected | 区域是否被选中。 | boolean | 是 | 用户交互 |
| xMax | 区域选择的最大x值。 | number | 是 | 用户交互 |
| xMin | 区域选择的最小x值。 | number | 是 | 用户交互 |
| yMax | 区域选择的最大y值。 | number | 是 | 用户交互 |
| yMin | 区域选择的最小y值。 | number | 是 | 用户交互 |

### IDatasetModel

| 属性 | 描述 | 类型 | 必需 | 更改者 |
| --- | --- | --- | --- | --- |
| name | 数据集的名称。如果未指定系列值，则用作图例标签。图形视觉效果使用此名称进行CSS分类。 | 字符串 | 是 | 直接编辑 |
| renderer | 用于绘制数据集的渲染器。 | 字符串 | 是 | 直接编辑 |
| seriesColors | 颜色值数组，该数组映射到“系列名称”字段中指定的系列名称数组。颜色可以指定为十六进制（例如“#FF0000”）或CSS颜色名称（例如“red”）。如果“系列名称”数组中未指定系列名称，则颜色数组中指定的第一个颜色将为整个图表着色。如果未指定颜色值，图表将使用默认的蓝图颜色方案 | 字符串[] | 否 | 直接编辑 |
| seriesNames | 唯一系列名称数组，该数组映射到“颜色”字段中指定的颜色数组。 | any[] | 否 | 直接编辑 |
| seriesValues | 将数据分组为“系列”的标签数组（数字或字符串）。具有x = [1, 1]、y = [1, 2]和系列= [“series1”, “series2”]的堆叠条形数据集将在x=1处生成一个堆叠，其中“series2”条位于“series1”条的顶部。具有多个系列的线性数据集将生成多条线。 | any[] | 否 | 直接编辑 |

### ILabelsModel

| 属性 | 描述 | 类型 | 必需 | 更改者 |
| --- | --- | --- | --- | --- |
| labels | 与图表值对应的标签数组。 | any[] | 是 | 直接编辑 |

### IRangeDatasetModel

| 属性 | 描述 | 类型 | 必需 | 更改者 |
| --- | --- | --- | --- | --- |
| endValues | 用于结束值的数据。 | any[] | 是 | 直接编辑 |
| startValues | 用于起始值的数据。 | any[] | 是 | 直接编辑 |

### IXYDatasetModel

| 属性 | 描述 | 类型 | 必需 | 更改者 |
| --- | --- | --- | --- | --- |
| radiusValues | 对于散点渲染器，确定散点半径的数据。 | number[] | 否 | 直接编辑 |
| xAxisName | 与此系列关联的x轴的名称。如果未指定，默认为第一个x轴。 | 字符串 | 否 | 直接编辑 |
| xValues | 用于x值的数据。 | any[] | 是 | 直接编辑 |
| yAxisName | 与此系列关联的y轴的名称。如果未指定，默认为第一个y轴。 | 字符串 | 否 | 直接编辑 |
| yValues | 用于y值的数据。 | any[] | 是 | 直接编辑 |
| symbolValues | 对于散点渲染器，每个散点的形状。有效值为“circle”、“square”、“diamond”、“cross”、“triangle”、“wye”和“star”。如果使用图例，系列的最后一个符号将用作图例的符号。如果最后一个符号无效或未定义，则图例默认为一个圆圈。 | 字符串[] | 否 | 直接编辑 |

### IHover

| 属性 | 描述 | 类型 | 必需 | 更改者 |
| --- | --- | --- | --- | --- |
| index | 图表中当前悬停的关联数据集的索引。 | number | 是 | 用户交互 |
| xValue | 图表中当前悬停的x值。 | any | 是 | 用户交互 |
| yValue | 图表中当前悬停的y值。 | any | 是 | 用户交互 |

### IDataSelection

| 属性 | 描述 | 类型 | 必需 | 更改者 |
| --- | --- | --- | --- | --- |
| indices | 所提供数据中选定值的索引。 | number[] | 是 | 用户交互 |
| xValues | 通过点击选定的离散x值。 | any[] | 是 | 用户交互 |
| yValues | 通过点击选定的离散y值。 | any[] | 是 | 用户交互 |

### 操作

| 操作名称 | 描述 |
| --- | --- |
| redraw | 触发此操作会导致图表重绘 |

## 图表微件示例

### 默认设置

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
{
  "animate": true,  // 动画效果启用
  "areaSelectionEnabled": false,  // 区域选择功能禁用
  "dataSelectionEnabled": false,  // 数据选择功能禁用
  "datasets": [
    {
      "name": "dataset1",  // 数据集名称
      "renderer": "line",  // 渲染器类型为折线图
      "xValues": [],  // x轴数值列表，当前为空
      "yValues": []   // y轴数值列表，当前为空
    }
  ],
  "labelsEnabled": false,  // 标签显示禁用
  "panZoomEnabled": false,  // 平移缩放功能禁用
  "tooltipsEnabled": false,  // 工具提示禁用
  "xAxes": [
    {
      "gridlinesEnabled": false,  // x轴网格线禁用
      "name": "x1",  // x轴名称
      "position": "bottom",  // x轴位置在底部
      "scale": "linear"  // x轴比例为线性
    }
  ],
  "yAxes": [
    {
      "gridlinesEnabled": false,  // y轴网格线禁用
      "name": "y1",  // y轴名称
      "scale": "linear",  // y轴比例为线性
      "position": "left"  // y轴位置在左侧
    }
  ]
}
```

### 带图例的条形图

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
{
  "animate": true,  // 动画效果启用
  "areaSelectionEnabled": false,  // 区域选择功能禁用
  "dataSelectionEnabled": false,  // 数据选择功能禁用
  "datasets": [
    {
      "name": "dataset1",  // 数据集名称
      "renderer": "bar",  // 使用柱状图渲染
      "xValues": "{{query1.state}}",  // X轴值，绑定到查询结果中的州信息
      "yValues": "{{query1.avgIncome}}"  // Y轴值，绑定到查询结果中的平均收入
    }
  ],
  "labelsEnabled": false,  // 标签显示禁用
  "legendPosition": "top",  // 图例位置在顶部
  "panZoomEnabled": false,  // 平移缩放功能禁用
  "tooltipsEnabled": false,  // 工具提示功能禁用
  "xAxes": [
    {
      "gridlinesEnabled": false,  // X轴网格线禁用
      "name": "x1",  // X轴名称
      "position": "bottom",  // X轴位置在底部
      "label": "State",  // X轴标签
      "scale": "category"  // X轴为分类刻度
    }
  ],
  "yAxes": [
    {
      "gridlinesEnabled": false,  // Y轴网格线禁用
      "name": "y1",  // Y轴名称
      "formatter": "$0,0.00",  // Y轴数据格式，显示为货币格式
      "position": "left",  // Y轴位置在左侧
      "label": "Average Income ($)",  // Y轴标签
      "scale": "linear",  // Y轴为线性刻度
      "scaleMax": 1000000,  // Y轴最大刻度值
      "scaleMin": 10000  // Y轴最小刻度值
    }
  ]
}
```

### 堆积条形图

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
{
  "animate": true,  // 启用动画效果
  "areaSelectionEnabled": false,  // 禁用区域选择
  "dataSelectionEnabled": false,  // 禁用数据选择
  "datasets": [
    {
      "name": "dataset1",  // 数据集名称
      "renderer": "stackedBar",  // 使用堆叠条形图进行渲染
      "seriesValues": "{{query1.gender}}",  // 系列值为性别
      "xValues": "{{query1.state}}",  // x轴值为州
      "yValues": "{{query1.avgIncome}}"  // y轴值为平均收入
    }
  ],
  "labelsEnabled": false,  // 禁用标签显示
  "panZoomEnabled": false,  // 禁用平移和缩放
  "tooltipsEnabled": false,  // 禁用工具提示
  "xAxes": [
    {
      "gridlinesEnabled": false,  // 禁用x轴网格线
      "name": "x1",  // x轴名称
      "position": "bottom",  // x轴位置在底部
      "label": "State",  // x轴标签
      "scale": "category"  // x轴使用类别比例尺
    }
  ],
  "yAxes": [
    {
      "gridlinesEnabled": false,  // 禁用y轴网格线
      "name": "y1",  // y轴名称
      "formatter": "$0,0.00",  // y轴格式化为货币格式
      "position": "left",  // y轴位置在左侧
      "label": "Average Income ($)",  // y轴标签
      "scale": "linear",  // y轴使用线性比例尺
      "scaleMax": 1000000,  // y轴最大值
      "scaleMin": 10000  // y轴最小值
    }
  ]
}
```

### 水平条形图

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
{
  "animate": true,  // 启用动画效果
  "areaSelectionEnabled": false,  // 禁用区域选择
  "dataSelectionEnabled": false,  // 禁用数据选择
  "datasets": [
    {
      "name": "dataset1",  // 数据集名称
      "renderer": "horizontalBar",  // 使用水平条形图渲染
      "xValues": "{{query1.avgIncome}}",  // x轴的值来源于query1的平均收入
      "yValues": "{{query1.state}}"  // y轴的值来源于query1的州名称
    }
  ],
  "labelsEnabled": false,  // 禁用标签显示
  "panZoomEnabled": false,  // 禁用平移和缩放功能
  "tooltipsEnabled": false,  // 禁用工具提示
  "xAxes": [
    {
      "gridlinesEnabled": false,  // 禁用x轴的网格线
      "name": "x1",  // x轴名称
      "position": "bottom",  // x轴位置在底部
      "label": "Average Income ($)",  // x轴标签为“平均收入（$）”
      "scale": "linear",  // x轴为线性刻度
    }
  ],
  "yAxes": [
    {
      "gridlinesEnabled": false,  // 禁用y轴的网格线
      "name": "y1",  // y轴名称
      "position": "left",  // y轴位置在左侧
      "label": "State",  // y轴标签为“州”
      "scale": "category"  // y轴为类别刻度
    }
  ]
}
```

### 多系列图表

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
{
  "areaSelectionEnabled": false, // 禁用区域选择
  "dataSelectionEnabled": false, // 禁用数据选择
  "datasets": [
    {
      "name": "dataset1", // 数据集名称
      "renderer": "line", // 渲染器类型为折线图
      "seriesValues": "{{query1.series}}", // 系列值
      "xValues": "{{query1.key}}", // x轴值
      "yValues": "{{query1.doc_count}}" // y轴值
    }
  ],
  "labelsEnabled": false, // 禁用标签
  "panZoomEnabled": false, // 禁用平移和缩放
  "tooltipsEnabled": false, // 禁用工具提示
  "xAxes": [
    {
      "gridlinesEnabled": false, // 禁用x轴网格线
      "name": "x1", // x轴名称
      "position": "bottom", // x轴位置在底部
      "scale": "linear" // x轴比例类型为线性
    }
  ],
  "yAxes": [
    {
      "gridlinesEnabled": false, // 禁用y轴网格线
      "name": "y1", // y轴名称
      "scale": "linear", // y轴比例类型为线性
      "position": "left" // y轴位置在左侧
    }
  ]
}
```

### 散点图

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
{
  "animate": true,  // 启用动画效果
  "areaSelectionEnabled": false,  // 禁用区域选择功能
  "dataSelectionEnabled": false,  // 禁用数据选择功能
  "datasets": [
    {
      "name": "dataset1",  // 数据集名称
      "radiusValues": "{{query1.pop}}",  // 气泡图的半径值，使用查询结果中的人口数据
      "renderer": "scatter",  // 数据渲染类型为散点图
      "xValues": "{{query1.gdp}}",  // X轴的值，使用查询结果中的GDP数据
      "yValues": "{{query1.cpi}}"  // Y轴的值，使用查询结果中的CPI数据
    }
  ],
  "labelsEnabled": false,  // 禁用标签
  "panZoomEnabled": false,  // 禁用平移和缩放功能
  "tooltipsEnabled": false,  // 禁用工具提示
  "xAxes": [
    {
      "gridlinesEnabled": false,  // 禁用X轴网格线
      "name": "x1",  // X轴名称
      "position": "bottom",  // X轴位置在底部
      "scale": "linear"  // X轴采用线性刻度
    }
  ],
  "yAxes": [
    {
      "gridlinesEnabled": false,  // 禁用Y轴网格线
      "name": "y1",  // Y轴名称
      "scale": "linear",  // Y轴采用线性刻度
      "position": "left"  // Y轴位置在左侧
    }
  ]
}
```

#### 教程: 添加一个散点图微件

假设您想创建一个散点图微件来显示展示距离和时间值的路线指标。选择左上角的微件按钮，然后选择图表 > 散点图将一个散点图微件添加到您的应用程序中。它将预先填充一些示例数据，您可以在继续之前从右侧编辑面板中清除这些数据。

首先，将图表微件重命名为容易识别的名称，例如w_routeMetrics。

我们想在 x 轴上绘制路线的平均距离。这意味着您必须将X 值设置为"{{q_routeMetrics.avg_distance}}"。

接下来，在 y 轴上绘制路线的持续时间。在数据选项卡中将Y 值设置为"{{q_routeMetrics.avg_time}}"。

为了使散点图更易于阅读，为您的坐标轴添加标签。选择坐标轴选项卡，并将第一个X 轴对象的名称从x1更改为Distance，并添加一个标签，例如Distance (miles)来描述绘制的信息。您也可以打开网格线以帮助识别每个点在图表上的位置。

将您的Y 轴命名为Duration，并按如下方式配置：

最后，为您的点赋予不同的大小。我们希望点的大小根据路线的繁忙程度而变化。为此，切换回数据选项卡，并将半径设置为"{{q_routeMetrics.num_flights}}"。

再次检查图表。似乎有些问题，因为图表现在被填满。这是因为半径值在提供的值和像素数之间是 1:1 映射，而我们的一些路线有超过 150 次航班。您必须缩放半径值。您可以在查询中计算一个“显示”值来实现这一点。您可以硬编码这个值，但使用变量可以让您在不编辑查询的情况下轻松进行后续更改。

选择顶部栏中的变量选项卡以打开变量窗口。在右下角创建一个新变量。将新变量命名为v_routeCountDisplayScale，并设置值为100。

返回到q_routeMetrics微件并添加一个新列：

COUNT(flight_id)/{{v_routeCountDisplayScale}} as num_flights_disp

同时，为每一行生成一个显示标签：

CONCAT(origin, ' -> ', dest) as route_name

您现在的整个查询如下所示：

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
SELECT
    origin,  -- 出发地
    dest,  -- 目的地
    AVG(distance) as avg_distance,  -- 平均距离
    AVG(actual_elapsed_time) as avg_time,  -- 平均实际飞行时间
    COUNT(flight_id) as num_flights,  -- 航班数量
    COUNT(flight_id)/{{v_routeCountDisplayScale}} as num_flights_disp,  -- 按比例显示的航班数量
    CONCAT(origin, ' -> ', dest) as route_name  -- 航线名称
FROM "foundry_sync"."{{v_flightTable}}"
GROUP BY
    origin,  -- 按出发地分组
    dest  -- 按目的地分组
ORDER BY
    COUNT(flight_id) DESC  -- 按航班数量降序排列
LIMIT 50  -- 限制结果为前50条记录
```

返回到w_routeMetrics微件，并调整Radius配置以引用num_flights_disp列而不是num_flights。

要完成图表，请在w_routeMetrics配置面板顶部的Title输入中添加标题Route Metrics。

您最终应该得到如下所示的应用程序：

### 带有 X 和 Y 范围的折线图

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
{
  "animate": true,  // 动画效果启用
  "areaSelectionEnabled": false,  // 区域选择功能禁用
  "dataSelectionEnabled": false,  // 数据选择功能禁用
  "datasets": [
    {
      "name": "dataset1",  // 数据集名称
      "renderer": "line",  // 渲染方式为折线图
      "xValues": [1,2,3,4,5,6,7,8,9],  // x轴数据值
      "yValues": [3,4,1,4,5,4,2,4,1],  // y轴数据值
      "seriesValues": null,  // 系列值为空
      "xAxisName": "x1",  // x轴名称
      "yAxisName": "y1"  // y轴名称
    },
    {
      "endValues": [3],  // 终止值
      "name": "dataset2",  // 数据集名称
      "renderer": "yRange",  // 渲染方式为y轴范围
      "startValues": [2]  // 起始值
    },
    {
      "endValues": [3.5,8],  // 终止值
      "name": "dataset3",  // 数据集名称
      "renderer": "xRange",  // 渲染方式为x轴范围
      "startValues": [2.5,6],  // 起始值
      "seriesValues": ["Range A","Range B"]  // 系列值
    }
  ],
  "labelsEnabled": false,  // 标签功能禁用
  "panZoomEnabled": false,  // 平移缩放功能禁用
  "tooltipsEnabled": false,  // 工具提示功能禁用
  "xAxes": [
    {
      "gridlinesEnabled": true,  // 网格线启用
      "name": "x1",  // x轴名称
      "position": "bottom",  // x轴位置
      "scale": "linear",  // 线性刻度
      "label": "",  // 标签为空
      "formatter": "\"0\""  // 格式化器
    }
  ],
  "yAxes": [
    {
      "gridlinesEnabled": false,  // 网格线禁用
      "name": "y1",  // y轴名称
      "position": "left",  // y轴位置
      "scale": "linear",  // 线性刻度
      "formatter": "\"0\""  // 格式化器
    }
  ]
}
```

## 热力网格

以下表格提供了关于热力网格图表微件的属性使用详情。表格后面有几个示例。

### 属性

#### IAxis

| 属性 | 描述 | 类型 | 是否必填 | 更改者 |
| --- | --- | --- | --- | --- |
| label | 与轴关联的标签。 | 字符串 | 否 | 直接编辑 |
| position | 轴的位置。对于x轴，位置可以是顶部或底部。对于y轴，左侧或右侧。 | 字符串 | 是 | 直接编辑 |
| visible | 指定是否显示该轴。 | boolean | 是 | 直接编辑 |

#### IHeatGridModel

| 属性 | 描述 | 类型 | 是否必填 | 更改者 |
| --- | --- | --- | --- | --- |
| cellValues | 用于确定每个单元格值的数据 | number[] | 是 | 直接编辑 |
| colorScale | 用于创建线性渐变以着色热力网格单元的两种或更多颜色的数组。例如：对于cellValues = [0, 5, 10]和颜色数组[“red”, “blue”]，结果颜色将是：红色、紫色、蓝色。颜色可以指定为十六进制（例如“#FF0000”）或CSS颜色名称（例如“red”）。如果未指定或少于两种颜色，默认颜色范围使用Blueprint的@blue5（#B9D7EA）到@blue1（#1f6b9a）的50%不透明度 | 字符串[] | 是 | 直接编辑 |
| labelFormat | 热力网格单元上的标签格式。使用Numeral.js ↗格式字符串。例如$0.00将1000.23格式化为$1000.23。小数精度限制为20位。 | 字符串 | 否 | 直接编辑 |
| labelsEnabled | 启用静态标签，使用每个单元格的值作为默认文本。 | boolean | 是 | 直接编辑 |
| legendLabel | 图例标签中使用的文本 | 字符串 | 否 | 直接编辑 |
| legendPosition | 图例的位置。可用选项包括“顶部”、“底部”、“左侧”或“右侧”。如果未指定，图例将不显示。 | 字符串 | 否 | 直接编辑 |
| selection | 所选热力网格单元格的值。仅在启用选择且用户已进行选择时相关。请参见下面的IHeatGridSelection。 | IHeatGridSelection | 否 | 用户交互 |
| selectionEnabled | 指定用户是否可以在热力网格上选择单元格。 | boolean | 是 | 直接编辑 |
| selectionMode | 指定选择行为。“单一”模式仅允许单击交互。“多重”模式允许cmd/ctrl+点击交互。 | 字符串 | 否 | 直接编辑 |
| xAxis | 类别比例x轴（见IAxis） | IAxis | 是 | 直接编辑 |
| xValues | 与每个单元格的x坐标关联的数据。 | any[] | 是 | 直接编辑 |
| yAxis | 类别比例y轴（见IAxis）。 | IAxis | 是 | 直接编辑 |
| yValues | 与每个单元格的y坐标关联的数据。 | any[] | 是 | 直接编辑 |
| title | 图表的标题。 | 字符串 | 否 | 直接编辑 |

#### IHeatGridSelection

| 属性 | 描述 | 类型 | 是否必填 | 更改者 |
| --- | --- | --- | --- | --- |
| cellValues | 通过点击选择的离散cellValues。 | number[] | 是 | 用户交互 |
| indices | 所选数据中值的索引。 | number[] | 是 | 用户交互 |
| xValues | 通过点击选择的离散x值。 | any[] | 是 | 用户交互 |
| yValues | 通过点击选择的离散y值。 | any[] | 是 | 用户交互 |

#### 操作

| 操作名称 | 描述 |
| --- | --- |
| redraw | 触发此操作会导致图表重新绘制 |

### 默认值

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
{
    "cellValues": [], // 单元格的值，当前为空数组
    "colorScale": ["#B9D7EA", "#1F6B9A"], // 颜色比例，定义了用于可视化的颜色范围
    "labelsEnabled": false, // 是否启用标签，当前设置为不启用
    "xAxis": {
        "gridlinesEnabled": false, // x轴是否启用网格线，当前设置为不启用
        "name": "x1", // x轴的名称
        "position": "bottom", // x轴的位置，当前设置在底部
        "scale": "category", // x轴的刻度类型，当前为分类刻度
        "visible": true // x轴是否可见，当前设置为可见
    },
    "xValues": [], // x轴的值，当前为空数组
    "yAxis": {
        "gridlinesEnabled": false, // y轴是否启用网格线，当前设置为不启用
        "name": "y1", // y轴的名称
        "position": "bottom", // y轴的位置，当前设置在底部
        "scale": "category", // y轴的刻度类型，当前为分类刻度
        "visible": true // y轴是否可见，当前设置为可见
    },
    "yValues": [] // y轴的值，当前为空数组
}
```

## 饼图

下表提供了关于饼图微件可用属性的使用详情。表格后面有几个示例。

### 属性

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| colors | 一个颜色值数组，与“Keys”字段中指定的键值数组相映射。颜色可以指定为十六进制（例如“#FF0000”）或CSS颜色名称（例如“red”）。如果未指定颜色值，图表将使用默认的Blueprint配色方案 | string[] | 否 | 直接编辑 |
| hover | 当tooltipsEnabled = true时，此属性包含与悬停的饼图切片相关的数据。有关更多信息，请参见IPieHover。 | IPieHover | 否 | 用户互动 |
| innerPadding | 用于创建甜甜圈孔的半径的分数。 | number | 否 | 直接编辑 |
| keys | 图例中显示的键。 | any[] | 是 | 直接编辑 |
| labelFormat | 饼图切片上的标签格式。使用Numeral.js ↗格式字符串。例如，$0.00会将1000.23格式化为$1000.23。小数精度限制为20位。 | string | 否 | 直接编辑 |
| labelsEnabled | 启用饼图切片上的静态标签 | boolean | 是 | 直接编辑 |
| legendPosition | 图例的位置。 | string | 是 | 直接编辑 |
| selection | 选定饼图切片的值。仅当启用选择并且用户进行了选择时才相关。请参见下文的IPieSelection。 | IPieSelection | 否 | 用户互动 |
| selectionEnabled | 指定用户是否可以选择饼图切片和图例条目。 | boolean | 是 | 直接编辑 |
| selectionMode | 指定选择行为。“Single”模式仅允许单击交互。“Multiple”模式允许cmd/ctrl+点击交互。 | string | 否 | 直接编辑 |
| tooltipsEnabled | 指定是否启用工具提示。默认情况下，工具提示的文本将是悬停的饼图切片的值 | boolean | 是 | 直接编辑 |
| tooltipText | 工具提示中显示的文本（tooltipsEnabled必须为true）。这通常用于显示悬停值。如果省略tooltipText或为空字符串，则工具提示将显示与饼图切片关联的值 | string | 否 | 直接编辑 |
| values | 决定每个切片大小的值。 | number[] | 是 | 直接编辑 |
| title | 图表的标题。 | string | 否 | 直接编辑 |

#### IPieHover

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| index | 悬停的饼图切片的索引。 | number | 是 | 用户互动 |
| key | 悬停的饼图切片的键。 | any | 是 | 用户互动 |
| value | 悬停的饼图切片的值。 | number | 是 | 用户互动 |

#### IPieSelection

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| indices | 所提供数据中选定值的索引。 | number[] | 是 | 用户互动 |
| keys | 通过点击选择的相关键。 | any[] | 是 | 用户互动 |
| values | 通过点击选择的离散值。 | number[] | 是 | 用户互动 |

#### 操作

| 操作名称 | 描述 |
| --- | --- |
| redraw | 触发此操作会导致图表重绘 |

### 示例

#### 饼图绘制

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
  "keys": "{{query1.teamName}}",  // 使用 query1 的 teamName 作为键
  "labelsEnabled": false,         // 不启用标签
  "legendPosition": "right",      // 图例位置设为右侧
  "selectionEnabled": false,      // 不启用选择功能
  "tooltipsEnabled": false,       // 不启用工具提示
  "values": "{{query1.headCount}}" // 使用 query1 的 headCount 作为值
}
```

#### 环形图表

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
{
  "innerPadding": 0.6, // 内间距设置为0.6
  "keys": "{{query1.teamName}}", // 键值获取自query1的teamName字段
  "labelsEnabled": false, // 标签显示设置为关闭
  "legendPosition": "right", // 图例位置设置在右侧
  "selectionEnabled": false, // 选择功能设置为关闭
  "tooltipsEnabled": false, // 提示工具设置为关闭
  "values": "{{query1.headCount}}" // 值获取自query1的headCount字段
}
```

### 默认值

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
  "keys": [],  // 键数组，当前为空
  "labelsEnabled": false,  // 标签是否启用，false表示不启用
  "legendPosition": "right",  // 图例位置，当前设置为右侧
  "selectionEnabled": false,  // 是否启用选择功能，false表示不启用
  "tooltipsEnabled": false,  // 是否启用工具提示，false表示不启用
  "values": []  // 值数组，当前为空
}
```

## 树状图

树状图微件提供了一种灵活的方法，以一组嵌套的矩形可视化层级数据。这对于发现其他可视化中难以揭示的模式非常有用。

树状图用于可视化给定实体（label）的绝对数量（size），该实体可能属于某个（非必填）category，并具有某个（非必填）相对数量（density）。每个单元的矩形具有：与size成比例的面积；由density和category定义的颜色；以及由label给出的名称。

可以用此图表可视化的一些数据集示例：

- 属于某个行业（category）的股票（label），它们在市场上占有一定份额（size），并且价格有一定的百分比变化（density）
属于某个行业（category）的股票（label），它们在市场上占有一定份额（size），并且价格有一定的百分比变化（density）

- 按地区（category）划分的工厂位置（label），这些工厂生产一定数量的商品（size）并且具有错误阳性率（density）
按地区（category）划分的工厂位置（label），这些工厂生产一定数量的商品（size）并且具有错误阳性率（density）

- 具有存储空间（size）的集群节点（label）和一定百分比的存储空间利用率（density）
具有存储空间（size）的集群节点（label）和一定百分比的存储空间利用率（density）

- 属于某个世界地区（category）的国家（label）的人口规模（size）
属于某个世界地区（category）的国家（label）的人口规模（size）

### 数据配置

- label（非必填）：显示在每个单元上的名称
- size：决定单元矩形的大小
- density（非必填）：决定单元颜色的阴影
- category（非必填）：决定单元的分组，从而决定单元的颜色
在默认示例中，单元矩形对应于单元的size。有两个类别，I和II。注意H具有最大的大小（45），因此是最大的矩形。H也具有最小的密度（3），因此是最深的颜色（可以通过颜色面板下的复选框翻转渐变）。

### 颜色配置

根据是否启用了categories和/或densities，提供了不同的颜色配置。

#### 启用类别和密度

当同时启用categories和densities时，单元的颜色根据色相-饱和度-明度（HSV）↗颜色空间中的渐变来定义。为每个类别定义一个色相。可以提供色相列表（0到360之间的数字）或将类别名称映射到色相的字典。然后，所有类别的渐变都使用相同的定义起始饱和度和明度。渐变使用渐变类型（变亮、变暗、饱和、去饱和）和渐变强度定义。

#### 仅启用类别

仅启用categories时，可以为类别指定颜色列表或将类别名称映射到颜色的字典。

颜色可以是十六进制（#FF0000, #00FF00）或规范名称（如红色、绿色）。

#### 仅启用密度

仅启用densities时，可以定义一个颜色列表作为带渐变的范围应用。必须至少提供两种颜色来定义颜色渐变，尽管可以提供更多颜色以更精细地定义此颜色渐变。

颜色可以是十六进制（#FF0000, #00FF00）或规范名称（如红色、绿色）。

#### 禁用类别和密度

同时禁用categories和densities时，可以定义一个颜色列表作为调色板。它必须是与数据点数量相同长度的颜色列表。

颜色可以是十六进制（#FF0000, #00FF00）或规范名称（如红色、绿色）。

### 杂项配置

可以进行非必填的杂项配置：

- 单元样式每个单元的边框宽度边框颜色单元标签单元工具提示
单元样式

- 每个单元的边框宽度
- 边框颜色
- 单元标签
- 单元工具提示
- 图例图例位置（顶部、底部、左侧、右侧）图例标签（图例标题）
图例

- 图例位置（顶部、底部、左侧、右侧）
- 图例标签（图例标题）
- 平铺策略以生成单元。平铺策略由d3 ↗定义：二进制、骰子、重新方形化、切片、切片骰子、方形化。
平铺策略以生成单元。平铺策略由d3 ↗定义：二进制、骰子、重新方形化、切片、切片骰子、方形化。

- 选择（多选或单选）
选择（多选或单选）

### 示例

在这一系列示例中，一位投资者希望可视化其投资组合的持股情况。数据有多个维度：股票名称（label）、每只股票的投资金额（size）、股票价格的百分比变化（density）以及股票所属的行业（category）。

我们将此数据加载到树状图图表微件中：

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
labels: ["MSFT", "AAPL", "NFLX", "AMZN", "GS", "MS", "BLK", "JPM", "XOM", "BP"]
// 股票代码列表，分别代表微软、苹果、奈飞、亚马逊、高盛、摩根士丹利、贝莱德、摩根大通、埃克森美孚和英国石油

sizes: [10, 20, 5, 25, 8, 15, 18, 30, 10, 40]
// 每个股票的大小数据，可以表示为市场份额、投资金额等

densities: [8, 15, -10, 10, 3, -5, -3, 4, 20, 8]
// 每个股票的密度数据，这里可能表示增长率、波动性等，负值可能表示负增长或高波动性

categories: ["Tech", "Tech", "Tech", "Tech", "Finance", "Finance", "Finance", "Finance", "Energy", "Energy"]
// 每个股票所属的类别，包括科技、金融和能源
```

#### 示例1：启用类别和密度

#### 示例2：仅启用密度

在此配置中，投资组合分析师可以查看哪些股票的价格变化最大。

#### 示例3：仅启用类别

在此配置中，投资组合分析师可以查看投资组合中哪个行业代表性最强，以及这些行业中哪些股票代表最大持股。

值得注意的是，您可以使用配置来提供更细粒度的数据表示。例如，可以将投资组合中的股票规模可视化，并根据红、黄、绿风险评级对其进行着色。

#### 示例4：禁用类别和密度

在此配置中，投资组合分析师仅能看到每个股票在投资组合中所占的份额。这实际上与默认的饼图相同。

值得注意的是，如果需要自定义颜色策略（超出默认可配置的范围），可以通过为每个方块单独提供颜色来使用此配置。

## 常用CSS

### 折线图

系列颜色：

```
Copied!1
2
3
4
5
.line-plot .render-area g:nth-of-type(1) path {stroke: #6a2d9f;}
/* 第一个路径（线）应用颜色 #6a2d9f，通常是一个深紫色。 */

.line-plot .render-area g:nth-of-type(2) path {stroke:#c993f1;}
/* 第二个路径（线）应用颜色 #c993f1，通常是一个浅紫色。 */
```

图例颜色：

```
Copied!1
.legend .legend-row .legend-entry:nth-of-type(1) path {fill: #6a2d9f;} /* 设置第一个图例条目的路径填充色为紫色 */
```

或者，

```
Copied!1
2
3
4
5
/* 设置第二个.legend-row中的.legend-entry和.content中的.legend-row的路径颜色为#c993f1 */
.legend .legend-row .legend-entry:nth-of-type(2) path,
.legend .content .legend-row:nth-of-type(2) path {
    fill: #c993f1;
}
```

### 条形图

以下适用于堆叠、聚类和常规条形图。

条形颜色：

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
.bar-plot .render-area g:nth-of-type(1) rect,
.bar-plot:nth-of-type(1) .render-area rect {
  fill: #6a2d9f; /* 为第一个柱状图的矩形填充颜色 */
}

.bar-plot .render-area g:nth-of-type(2) rect,
.bar-plot:nth-of-type(2) .render-area rect {
  fill: #c993f1; /* 为第二个柱状图的矩形填充颜色 */
}
```

这个CSS代码片段为第一个和第二个柱状图的矩形设置了不同的填充颜色。
图例颜色：

```
Copied!1
2
3
4
5
6
7
8
.legend .legend-row .legend-entry:nth-of-type(1) path {
  fill: #6a2d9f; /* 设置第一个图例项的填充颜色为紫色 */
}

.legend .legend-row .legend-entry:nth-of-type(2) path,
.legend .content .legend-row:nth-of-type(2) path {
  fill: #c993f1; /* 设置第二个图例项和第二行图例内容的填充颜色为浅紫色 */
}
```

### 区域图

以下适用于堆叠和常规区域图。

区域颜色：

```
Copied!1
2
3
4
5
6
7
.area-plot .render-area g:nth-of-type(1) path, .area-plot:nth-of-type(1) path {
    fill: #009900; /* 设置第一个g元素的路径以及第一个.area-plot元素的路径填充颜色为绿色 (#009900) */
}

.area-plot .render-area g:nth-of-type(2) path, .area-plot:nth-of-type(2) path {
    fill: #99CC00; /* 设置第二个g元素的路径以及第二个.area-plot元素的路径填充颜色为浅绿色 (#99CC00) */
}
```

线条颜色：

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
/* 选择第一个.area-plot类型元素的.area类和.line-plot的第一个g元素中的path，设置描边颜色为#009900 */
.area-plot:nth-of-type(1) .area,
.line-plot .render-area g:nth-of-type(1) path {
    stroke: #009900;
}

/* 选择第一个.area-plot类型元素的.area类和.line-plot的第二个g元素中的path，设置描边颜色为#99CC00 */
.area-plot:nth-of-type(1) .area,
.line-plot .render-area g:nth-of-type(2) path {
    stroke: #99CC00;
}
```

```
Copied!1
2
.legend .legend-row .legend-entry:nth-of-type(1) path {fill: #009900;}
/* 选择.legend类下的.legend-row类中的第一个.legend-entry元素的路径，并将其填充颜色设置为绿色 (#009900)。 */
```

或者：

```
Copied!1
2
3
4
5
/* 为第二个类型的图例条目和图例行设置填充颜色 */
.legend .legend-row .legend-entry:nth-of-type(2) path,
.legend .content .legend-row:nth-of-type(2) path {
    fill: #99CC00; /* 设置路径的填充颜色为绿色 #99CC00 */
}
```

### 饼图

可以通过索引或CSS类名选择一个切片（经过清理的标签名称用作CSS类名）

按索引样式：

饼图切片颜色：

```
Copied!1
.pie-plot .render-area .arc:nth-of-type(1) {fill: #009900;} /* 为第一个扇形区域填充颜色 #009900 */
```

```
Copied!1
2
.arc:nth-of-type(2) { fill: #99CC00; }
/* 选择第二个 .arc 元素，并将其填充颜色设置为 #99CC00 */
```

```
Copied!1
2
sl-pie .legend .legend-row:nth-of-type(1) path { fill: #009900; } /* 第一行图例的路径填充颜色为深绿色 */
sl-pie .legend .legend-row:nth-of-type(2) path { fill: #99CC00; } /* 第二行图例的路径填充颜色为浅绿色 */
```

按名称样式化：

饼图切片颜色：

```
Copied!1
.pie-plot .render-area .arc._A {fill: #009900;} /* 设置类名为.arc._A的元素的填充颜色为绿色 */
```

或者：

```
Copied!1
.arc._B { fill: #99CC00; } /* 设置类.arc和类_B组合选择器的填充颜色为#99CC00 */
```

```
Copied!1
2
sl-pie .legend .legend-row ._A path { fill: #009900; } /* 设置类名为_A的图例行的路径填充颜色为绿色 */
sl-pie .legend .legend-row ._B path { fill: #99CC00; } /* 设置类名为_B的图例行的路径填充颜色为浅绿色 */
```
