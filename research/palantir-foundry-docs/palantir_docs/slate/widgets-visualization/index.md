来源: https://palantir.com/docs/zh/foundry/slate/widgets-visualization/

# 可视化

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 可视化

可视化微件类别由以下微件组成：

- 图表
- 图像库
- 地图
- 表格
- 通知
- 树形结构
## 图表

以下表格提供了关于图表微件可用属性的使用细节。表格后面有几个示例。

### 属性

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| defaultEdgeIcon | 边的默认图像URL或Blueprint图标。 | 字符串 | 否 | 直接编辑 |
| defaultNodeIcon | 节点的默认图像URL或Blueprint图标。 | 字符串 | 否 | 直接编辑 |
| directedEdgesEnabled | 确定边是否在末端有指向目标节点的箭头。 | boolean | 否 | 直接编辑 |
| edgeArrowSize | 有向边中箭头的大小，以像素为单位。 | boolean | 否 | 直接编辑 |
| edgeIconOffset | 边的图标从边中心的偏移量。偏移方向取决于边标签是否水平 | number | 否 | 直接编辑 |
| edgeIconSize | 边图标的宽度和高度，以像素为单位。 | number | 否 | 直接编辑 |
| edgeLabelHorizontal | 确定边标签是否保持水平而不是与边平行。 | boolean | 否 | 直接编辑 |
| edgeLabelOffset | 边标签从边中心的偏移量。偏移方向取决于边标签是否水平 | number | 否 | 直接编辑 |
| edgeLength | 提供给流和力导向设计的边长度值。 | number | 否 | 直接编辑 |
| edges | 在图表中显示的边的值。 | IEdges | 否 | 直接编辑 |
| hideLabelsScale | 标签隐藏的缩放级别。用于隐藏太小而无法阅读的标签。 | number | 否 | 直接编辑 |
| nodeColorScaleRange | 用于创建线性渐变以着色节点的两种或多种颜色的数组。示例：若 node.colorScaleValues = [0, 5, 10] 且颜色范围数组为 [“red”, “blue”]，则生成的颜色将为：红色、紫色、蓝色。颜色可以指定为十六进制（例如“#FF0000”）或CSS颜色名称（例如“red”）。如果未指定或少于2种颜色，则使用的默认颜色范围由Blueprint颜色 @green4, @gold4 和 @red4 组成（[“#15B371”, “#F2B824”, “#F55656”]） | 字符串[] | 否 | 直接编辑 |
| nodeLabelPosition | 标签相对于节点圆的位置信息。 | 字符串 | 否 | 直接编辑 |
| 设计 | 图表将用于排列节点的设计类型。“力导向”：图表使用一种方法展开节点。“流向上/下/左/右”：节点被排列成边大致指向给定方向。“手动”允许用户拖动节点到新位置并在保存时保留位置。在其他设计中拖动的节点位置不会被保存。 | 字符串 | 否 | 直接编辑 |
| nodeDiameter | 节点圆的直径，以像素为单位。 | number | 否 | 直接编辑 |
| nodeLabelOffset | 标签从节点中心的偏移量。偏移方向由标签位置决定 | number | 否 | 直接编辑 |
| nodeMargin | 节点之间的最小距离，由流和力导向设计使用。 | number | 否 | 直接编辑 |
| nodeIconSize | 节点图标的宽度和高度。 | number | 否 | 直接编辑 |
| nodes | 在图表中显示的节点的值。 | INodes | 是 | 直接编辑 |
| nodeSelectorDiameter | 指示节点被选中的圆的直径。 | number | 否 | 直接编辑 |
| selectedNodeIds | 当前用户选择的节点的唯一标识符。 | 字符串[] | 否 | 用户交互 |
| zoomScaleRange | 设置图表的允许缩放范围。 | number | 否 | 直接编辑 |

#### IEdges

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| cssClasses | 用于应用CSS样式的边的CSS类名。 | 字符串[] | 否 | 直接编辑 |
| icons | 边的图像URL或Blueprint图标。 | 字符串[] | 否 | 直接编辑 |
| labels | 与边相关的标签。 | 字符串[] | 否 | 直接编辑 |
| sourceNodeIds | 创建边所需的源节点的ID。 | number[] | 是 | 直接编辑 |
| targetNodeIds | 创建边所需的目标节点的ID。 | number[] | 是 | 直接编辑 |

#### INodes

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| colorScaleValues | 用于着色节点的数值，使用颜色比例范围中的颜色进行插值 | number[] | 否 | 直接编辑 |
| cssClasses | 用于应用CSS样式的节点的CSS类名。 | 字符串[] | 否 | 直接编辑 |
| icons | 节点的图像URL或Blueprint图标。 | 字符串[] | 否 | 直接编辑 |
| ids | 节点的唯一标识符。 | 字符串[] | 是 | 直接编辑 |
| labels | 与节点相关的标签。 | 字符串[] | 否 | 直接编辑 |
| xPositions | 在手动设计中，指定节点的X位置。缺少值的节点将按网格排列。 | number[] | 是 | 用户交互 |
| yPositions | 在手动设计中，指定节点的Y位置。缺少值的节点将按网格排列。 | number[] | 是 | 用户交互 |

### 示例

#### 动态图表

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
  "camera": {
    "ratio": null, // 摄像机的比例，目前未设置，保留为null
    "x": null, // 摄像机的x坐标，目前未设置，保留为null
    "y": null  // 摄像机的y坐标，目前未设置，保留为null
  },
  "edges": {
    "sourceNodeIds": "{{graph.sourceNodeIds}}", // 边的源节点ID，通过模板变量获取
    "targetNodeIds": "{{graph.targetNodeIds}}"  // 边的目标节点ID，通过模板变量获取
  },
  "nodes": {
    "iconUrls": "{{graph.iconUrls}}", // 节点的图标URL，通过模板变量获取
    "ids": "{{graph.ids}}", // 节点的ID，通过模板变量获取
    "labels": "{{graph.ids}}", // 节点的标签，与ID相同，通过模板变量获取
    "xPositions": "{{graph.xPositions}}", // 节点的x坐标，通过模板变量获取
    "yPositions": "{{graph.yPositions}}"  // 节点的y坐标，通过模板变量获取
  },
  "selectedNodeIds": [
    "n18" // 当前选中的节点ID
  ]
}
```

#### 静态图表

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
{
  "camera": {
    "ratio": null,  // 相机比例，当前未设置
    "x": null,      // 相机X轴位置，当前未设置
    "y": null       // 相机Y轴位置，当前未设置
  },
  "defaultIconUrl": "resources/map-people.svg",  // 默认图标的URL路径
  "edges": {
    "ids": [
      "e1",
      "e2",
      "e3",
      "e4",
      "e5"
    ],
    "labels": [
      "e1",
      "e2",
      "e3",
      "e4",
      "e5"
    ],
    "sourceNodeIds": [
      "n1",
      "n2",
      "n3",
      "n4",
      "n5"
    ],
    "targetNodeIds": [
      "n2",
      "n3",
      "n4",
      "n5",
      "n1"
    ]
  },
  "layout": {
    "type": "layered"  // 布局类型为分层布局
  },
  "nodes": {
    "ids": [
      "n1",
      "n2",
      "n3",
      "n4",
      "n5"
    ],
    "labels": [
      "n1",
      "n2",
      "n3",
      "n4",
      "n5"
    ],
    "xPositions": [
      100,
      30.9,
      -80.9,
      -80.9,
      30.9
    ],
    "yPositions": [
      0,
      95.1,
      58.78,
      -58.78,
      -95.1
    ]
  },
  "selectedNodeIds": [
    "n1"  // 当前选中的节点ID
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
9
10
11
12
13
14
15
16
17
{
  "camera": {
    "ratio": null,  // 摄像机的比例，初始化为 null
    "x": null,      // 摄像机的 x 轴位置，初始化为 null
    "y": null       // 摄像机的 y 轴位置，初始化为 null
  },
  "edges": {
    "sourceNodeIds": [],  // 边的起始节点 ID 列表，初始化为空
    "targetNodeIds": []   // 边的目标节点 ID 列表，初始化为空
  },
  "nodes": {
    "ids": [],            // 节点 ID 列表，初始化为空
    "xPositions": [],     // 节点在 x 轴上的位置列表，初始化为空
    "yPositions": []      // 节点在 y 轴上的位置列表，初始化为空
  },
  "selectedNodeIds": []   // 被选中的节点 ID 列表，初始化为空
}
```

## 图像库

下表提供了有关图像库微件可用属性的使用详情。

### 属性

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| imageUrls | 此图库的图像。 | string[] | 是 | 直接编辑 |
| captions | 每张图像的标题。 | string[] | 否 | 直接编辑 |

## 地图

Slate的地图微件由Leaflet ↗支持。

地图由图层组成：基础图层（也称为瓦片图层；这是背景地图图像）和一些叠加图层（也称为特征图层；这是您感兴趣的数据）。地图微件支持特征图层的光栅和矢量瓦片。

有关网络地图技术的有用介绍，请参阅Mapbox 文档 ↗。Slate使用Mapbox作为其基础地图图像的来源。

## 术语

- 地图瓦片：地图微件的基础图层，这些瓦片只是图像。它们不包含数据。您可以将地图瓦片视为地图的“背景”。地图瓦片在Misc选项卡中配置，并适用于整个地图微件，而不仅仅是单个图层。一次只能显示一种地图瓦片。
- 特征：在地图上绘制的点或形状，与某种数据相关联。
- 矢量：表示图像的另一种方法。光栅图像逐像素描述图像；基本上是一个彩色像素的网格。矢量图像则相反，描述点之间的线。这意味着矢量图像可以在不同的大小上清晰显示。
- 矢量瓦片：以矢量形式包含形状数据。
- 瓦片服务器：动态地将形状数据作为瓦片提供。
- 地图瓦片来源：提供地图的基础瓦片。技术上也是一个瓦片服务器。
## 图层类型

Slate具有以下叠加图层类型：

- 位置
- 热力图和热网格
- 形状
- 矢量
- 分级统计图
- Raven
### 位置

位置图层仅包含点（Leaflet标记 ↗），由纬度/经度对标识。您可以配置地图微件以将这些点显示为圆形或图标。

### 热力图和热网格

热力图和热网格图层也处理点数据，但不是简单地在地图上显示这些点，而是显示一个关于这些点分布的计算叠加层。热力图显示点的密度为彩色渐变，而热网格将点分组到桶中，并将桶显示为离散的彩色单元。

### 形状

除了单独的点外，形状和矢量图层还可以包含多边形形式的数据—信息存储为一系列点和它们之间的线。形状图层以GeoJSON ↗格式提供这些多边形。GeoJSON文件可以直接从您的Slate服务器提供。

GeoJSON特征存储为JSON，并翻译为SVG（图像）文件。这些图像在地图微件首次加载时一起加载。

### 矢量

矢量图层在矢量瓦片中提供形状数据。您必须运行一个外部瓦片服务器来提供矢量瓦片。
矢量瓦片是动态加载的（仅在它们进入地图视野时）。矢量瓦片也直接在画布上绘制特征，而不是将它们渲染为图像，因此矢量图层可以比形状图层拥有更多特征。

### 分级统计图

分级统计图图层也处理多边形数据，但它们为每个特征添加了一个附加值，并将这些值投影到一个色彩尺度上。然后，每个特征在地图上显示为与该值相对应的颜色。这作为某些特定统计数据的可视化。

例如，您可能有一个按人口密度着色的州地图，或按社会脆弱性指数着色的邮政编码地图。

### Raven

如果您需要在Slate应用程序中使用Raven地图，请联系您的Palantir代表。

## 基础瓦片

地图微件附带多种基础瓦片图层选项。选项包括深色主题、浅色主题、卫星主题、街道地图主题和我们的默认主题。还有一个All选项，允许您使用图层选择器直接在地图上切换主题。

在属性编辑器的Misc选项卡中，从Tile Layer下拉菜单中选择：

## 地图上的数据规模

形状图层（GeoJSON）支持最低的数据规模。在大约1000个特征时，地图性能明显下降。对于大于此的数据，您应该改用矢量图层。您也可以尝试简化GeoJSON中的几何形状以提高性能。

位置图层在大约5000-10000个点时性能下降。

## 禁用交互功能

如果您想在应用程序中显示静态地图，可以禁用平移和缩放功能。您还可以移除基础图层，如果您只想显示特征数据（而不是基础地图瓦片）。

## 示例

### 位置地图图层

包含自定义样式：

您还可以使用图层名称或.layer${layerIndex}为图层中的所有标记/群集进行样式设置。只有作为有效CSS类的图层名称才会被添加：

### 分级统计图地图图层

### 矢量地图图层

### 热力图图层

### 属性

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| autoZoom | 指定地图是否会根据地图中的数据自动缩放。 | boolean | 是 | 直接编辑 |
| bounds | 用户缩放和平移时的可见区域。参见下方IBounds。 | IBounds | 是 | 用户交互或直接编辑 |
| crs | 使用的坐标参考系统：EPSG3395（椭圆墨卡托投影）、EPSG3857（球形墨卡托投影）或EPSG4326（等角投影）。 | string | 否 | 直接编辑 |
| fixedBoundsEnabled | 指定地图的边界是否可以通过缩放和拖动更改。 | boolean | 否 | 直接编辑 |
| zoomControlEnabled | 指定地图是否在左上角显示一个可点击的缩放控件。 | boolean | 否 | 直接编辑 |
| layerSelectorEnabled | 指定地图是否在右上角显示图层控制菜单。 | boolean | 否 | 直接编辑 |
| layers | 参见ILayerModel。 | ILayerModel[] | 否 | 直接编辑 |
| maxBounds | 用户缩放/平移时可用的最大可见区域。 | IBounds | 否 | 直接编辑 |
| minMaxZoomLevel | 设置地图的允许缩放范围。缩放级别从0开始，代表整个地球，到18，约为个别房屋的规模。 | number | 否 | 直接编辑 |
| zoomLevel | 地图的当前缩放级别。 | number | 是 | 用户交互 |
| selection | 选择对象，其中包含选择的形状和选定的ID。 | IMapSelection | 是 | 用户交互 |
| tileLayerEnabled | 指定瓦片图层（例如街道地图）是否启用。 | boolean | 是 | 直接编辑 |
| tileUrlsEnabled | 启用自定义瓦片URL用于瓦片图层。您必须在下方输入瓦片图层的URL，及其（可选的）标签。您必须启用瓦片图层（如上所述）以显示任何自定义瓦片图层。如果您启用了瓦片图层选择器，瓦片URL将被添加到选择器中。 | boolean | 是 | 直接编辑 |
| tileLayer | 基础瓦片图层。 | string | 是 | 直接编辑 |
| tileUrlLabels | 自定义瓦片图层URL的名称数组。如果不提供标签，将使用默认名称，如“Custom”，“Custom (1)”等。 | string | 否 | 直接编辑 |
| tileUrls | 自定义瓦片图层URL的JSON数组。瓦片图层URL应为“http:/{s}.example.com/blah/{z}/{x}/{y}.png”标准形式。其中{s}是可选的子域，{z}是缩放级别，{x}和{y}是瓦片坐标。此模板URL将用于地图查找每个瓦片图像。 | string | 否 | 直接编辑 |
| shapeSelectionEnabled | 在地图上启用拖动选择控件。按住CMD或CTRL键以使用附加选择。拖动选择支持两种模式：区域选择将创建一个持久形状，并将在模板上以数组形式命名为selection.areas。数据选择进一步允许用户直接选择位置标记，更新selection.ids的值。 | boolean | 是 | 直接编辑 |
| selectionType | 选择的模式。区域选择将创建一个持久形状，并将在模板上以数组形式命名为selection.areas。数据选择进一步允许用户直接选择位置标记，更新selection.ids的值。 | string | 否 | 直接编辑 |

#### IBaseLayerOptions

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| name | 将在图层选择器中显示的图层名称。位置和形状图层将默认为CSS选择器，如果没有提供名称。Raven图层提供它们自己的名称，因此使用此字段将覆盖所有Raven图层提供的名称。 | string | 否 | 直接编辑 |

#### IBounds

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| northEast | 矩形地图区域的东北点。 | ILatLng | 是 | 用户交互或直接编辑 |
| southWest | 矩形地图区域的西南点。 | ILatLng | 是 | 用户交互或直接编辑 |

#### IChoroplethLayerOptions

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| colorScaleOptions | 如果存在，将使用指定的自定义色彩尺度为分级统计图中的元素着色。 | IColorScaleOptions | 否 | 直接编辑 |
| ids | 映射回geoJson文件中“ids”的数据值。同样，在用户选择的基础上，选择.ids返回的IDs。 | string[] | 是 | 直接编辑 |
| layerSource | 用于渲染特征的数据类型。来源可以是GeoJSON文件或提供矢量瓦片的服务器。 | string | 是 | 直接编辑 |
| shapeGeoJson | 图层的原始GeoJSON。推荐值是返回有效GeoJSON ↗对象的模板化函数或查询。此值仅在“形状来源”设置为“原始”时设置。 | any | 否 | 直接编辑 |
| shapeSource | 指示如何检索形状GeoJSON。使用“服务器资源”指向Slate服务器上的静态GeoJSON形状文件。使用“原始”直接指定GeoJSON。由于Slate应用程序大小限制，大型GeoJSON应作为“服务器资源”或从查询中检索。 | any | 否 | 直接编辑 |
| shapeUrl | 形状文件的URL。例如：“resources/map/us-states.geojson”。此值仅在“形状来源”设置为“服务器资源”时设置。 | string | 否 | 直接编辑 |
| values | 数据点的值。 | number[] | 是 | 直接编辑 |
| vectorTileOptions | 配置矢量瓦片图层的选项。仅在layerSource设置为“矢量瓦片”时可用 | IVectorTileOptions | 是 | 直接编辑 |

#### IColorScaleOptions

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| colorScaleTypes | 色彩尺度使用插值颜色表示数据值。 | string | 是 | 直接编辑 |
| colors | 用于创建线性渐变以为元素着色的两种或更多颜色的数组。例如，给定值为[0, 25, 100]的元素和颜色数组为[“red”, “yellow”, “green”]，结果颜色将是：红色，橙色，绿色。颜色可以指定为十六进制（例如“#FF0000”）或CSS颜色名称（例如“red”） | string | 是 | 直接编辑 |
| defaultColor | 用于值为null的元素的默认颜色。可以是十六进制颜色（例如“#FF0000”）或CSS颜色名称（例如“red”） | string | 是 | 直接编辑 |
| opacity | 色彩尺度的不透明度范围。值为0时完全透明，值为1时完全不透明。 | string | 是 | 直接编辑 |
| linearity | 调整色彩尺度的线性度。低“线性度”值将在尺度的低端显示更多颜色差异。值为1是完美的线性尺度。 | string | 是 | 直接编辑 |

#### IHeatgridLayerOptions

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| latitudes | 数据点的纬度值。 | number[] | 是 | 直接编辑 |
| longitudes | 数据点的经度值。 | number[] | 是 | 直接编辑 |
| values | 数据点的值。 | number[] | 是 | 直接编辑 |
| feature | 指定如何绘制每个网格单元。 | string | 否 | 直接编辑 |
| colorScale | 用于绘制热网格单元的色彩尺度。 | number | 否 | 直接编辑 |
| granularity | 热网格单元的大小。 | number | 否 | 直接编辑 |
| opacityRange | 色彩尺度的最小和最大不透明度 | number[] | 否 | 直接编辑 |
| colorScaleLinearity | 确定色彩尺度的线性度。1.0是完全线性的，0.5是平方根。 | number[] | 否 | 直接编辑 |
| radiusScale | 确定圆形特征的半径范围。将范围的最小/最大值设置为相同的值意味着所有圆形将具有相同的大小。 | number[] | 否 | 直接编辑 |

#### IHeatmapLayerOptions

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| latitudes | 数据点的纬度值。 | number[] | 是 | 直接编辑 |
| longitudes | 数据点的经度值。 | number[] | 是 | 直接编辑 |
| radius | 每个数据点的半径。当半径随着地图缩放而缩放时，半径以地图的尺度测量（默认值：2）；否则半径以像素测量（默认值：20）。 | number | 否 | 直接编辑 |
| scaleRadiusEnabled | 指定数据点的半径是否应根据地图的缩放级别进行缩放（默认值：true）。 | boolean | 否 | 直接编辑 |
| values | 数据点的值。 | number[] | 是 | 直接编辑 |

#### ILatLng

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| latitude | 地图上某点的纬度值。 | number | 是 | 用户交互或直接编辑 |
| longitude | 地图上某点的经度值。 | number | 是 | 用户交互或直接编辑 |

#### ILayerModel

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| options | 图层的选项。详细信息请参见IChoroplethLayerOptions、IHeatmapLayerOptions、ILocationLayerOptions、IShapeLayerOptions和IRavenLayerOptions | IChoroplethLayerOptions | IHeatmapLayerOptions | ILocationLayerOptions |
| type | 地图图层的类型：分级统计图、位置、热力图、形状或Raven。 | string | 是 | 直接编辑 |

#### ILocationLayerOptions

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| clustering | 启用时，将在地图上对点进行聚类。 | boolean | 是 | 直接编辑 |
| cssClasses | 用于通过CSS编辑器覆盖默认标记设置的标记的CSS类名。 | string[] | 否 | 直接编辑 |
| ids | 选择.ids返回的基于用户选择的ID。 | string[] | 是 | 直接编辑 |
| latitudes | 数据点的纬度值。 | number[] | 是 | 直接编辑 |
| longitudes | 数据点的经度值。 | number[] | 是 | 直接编辑 |
| weights | 聚类标签的聚合数据点权重（默认值：1）。 | number[] | 否 | 直接编辑 |
| markerType | 标记的类型，“circle”或“icon”。 | string | 否 | 直接编辑 |
| markerRadius | 圆形标记的半径 | number | 否 | 直接编辑 |

#### IMapSelection

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| areas | 此数组包含用户在启用拖动选择时创建的选择形状。支持的形状有‘rectangle’，它具有纬度/经度边界，以及‘circle’，它具有纬度/经度中心和半径（以米为单位） | Array<IRectangleShape | ICircleShape> | 否 |
| ids | 此数组包含地图上被选择的位置标记的ID。 | string[] | 是 | 用户交互 |

#### IRectangleShape

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| bounds | 形状的纬度/经度边界。 | IBounds | 是 | 用户交互 |
| type | 字符串‘rectangle’ | string | 是 | 用户交互 |

#### ICircleShape

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| bounds | 形状的纬度/经度边界。边界被定义为完全包含圆的最小矩形。 | IBounds | 是 | 用户交互 |
| center | 圆的纬度/经度中心。 | ILatLng | 是 | 用户交互 |
| radius | 圆的半径（以米为单位）。 | number | 是 | 用户交互 |
| type | 字符串‘circle’ | string | 是 | 用户交互 |

#### IRavenLayerFilterOptions

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| propertyName | 用于筛选的属性名称。例如：“City” | string | 是 | 直接编辑 |
| propertyValue | 用于筛选的属性值。例如：“Medford” | string | 是 | 直接编辑 |

#### IRavenLayerOptions

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| filter | 如果存在，将根据Raven中的元数据筛选Raven特征 | IRavenLayerFilterOptions | 否 | 直接编辑 |
| serverUri | Raven服务器的URI。此域必须在slate.yml中明确允许用于脚本和图像的内容安全策略中。 | string | 是 | 直接编辑 |

#### IShapeLayerOptions

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| cssClasses | 用于通过CSS编辑器覆盖默认设置的geojson形状和标记的CSS类名。 | string[] | 否 | 直接编辑 |
| ids | 映射回geoJson文件中“ids”的数据值。这些主要用于指派CSS类到个别geoJson ID。 | string[] | 是 | 直接编辑 |
| markerType | 标记的类型，“circle”或“icon”。 | string | 否 | 直接编辑 |
| markerRadius | 圆形标记的半径 | number | 否 | 直接编辑 |
| shapeGeoJson | 图层的原始GeoJSON。推荐值是返回有效GeoJSON ↗对象的模板化函数或查询。此值仅在“形状来源”设置为“原始”时设置。 | any | 否 | 直接编辑 |
| shapeSource | 指示如何检索形状GeoJSON。使用“服务器资源”指向Slate服务器上的静态GeoJSON形状文件。使用“原始”直接指定GeoJSON。由于Slate应用程序大小限制，大型GeoJSON应作为“服务器资源”或从查询中检索。 | any | 否 | 直接编辑 |
| shapeUrl | 形状文件的URL。例如：“resources/map/us-states.geojson”。此值仅在“形状来源”设置为“服务器资源”时设置。 | string | 否 | 直接编辑 |

#### IVectorTileLayerOptions

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| baseStyle | 矢量瓦片特征的样式选项。 | IVectorTileStyleOptions | 否 | 直接编辑 |
| clickStyle | 选择时矢量瓦片特征的样式选项。 | IVectorTileStyleOptions | 否 | 直接编辑 |
| hoverStyle | 悬停时矢量瓦片特征的样式选项。 | IVectorTileStyleOptions | 否 | 直接编辑 |
| vectorTileOptions | 配置矢量瓦片服务器的选项 | IVectorTileOptions | 是 | 直接编辑 |

#### IVectorTileOptions

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| featureIdKey | 用于作为id的特征属性名称。必须是唯一的。默认为字符串“id”。 | string | 否 | 直接编辑 |
| layerName | 服务器返回的图层的字符串名称。矢量瓦片服务器可以为每个瓦片提供多个图层，因此这用于选择要渲染的那些图层。 | string | 是 | 直接编辑 |
| vectorTileUrl | 提供要显示的瓦片的矢量瓦片服务器的URL。瓦片应按其x，y和缩放（z）坐标检索，因此URL应包含{x}，{y}和{z}作为其结构的一部分。 | string | 是 | 直接编辑 |
| featureIdWhitelist | 用于筛选瓦片特征的字符串或正则表达式列表。如果这是一个非空数组，则特征的featureIdKey不符合任何字符串或正则表达式的特征将不会显示。 | string[] | 否 | 直接编辑 |

#### IVectorTileStyleOptions

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| color | 代表特征样式的CSS字符串。适用于所有特征类型。在“outline”对象中也用于轮廓颜色。 | string | 否 | 直接编辑 |
| outline | 表示多边形特征轮廓样式的JSON对象。接受“color”和“size”属性 | object | 否 | 直接编辑 |
| radius | 点特征的半径大小。 | number | 否 | 直接编辑 |
| size | 线特征的线条厚度。在“outline”对象中也用于轮廓厚度。 | number | 否 | 直接编辑 |

## 表格

下表提供了有关表格微件可用属性的使用详情。表格后面跟随多个示例。

### 属性

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| bodyTooltip | 表格正文工具提示中显示的文本。如果bodyTooltip被省略或为null，则不会显示工具提示。支持HTML。 | string | 否 | 直接编辑 |
| columnData | 在表格中显示的数据。这通常只是与表格关联的查询。参见下方示例。 | {columnId: any[]}（注意：columnId是字符串） | 是 | 直接编辑 |
| columnOptions | 将应用于特定列的选项。参见下方IColumnOption。 | {columnId: IColumnOption}（注意：columnId是字符串） | 是 | 直接编辑 |
| columnOrder | 指示要显示的列的顺序和子集。这应该是来自columnData的“columnId”数组。如果留为空数组，则顺序可能是非确定性的。 | string[] | 是 | 直接编辑 |
| gridOptions | 参见下方IGridOptions。 | IGridOptions | 是 | 直接编辑 |
| selectedRowKeys | 所有用户选中的行的selectedIdentityColumnId值。 | any[] | 是 | 用户交互 |
| selectionIdentityColumnId | 用于确定行的唯一身份或键的columnData中的columnId。对于给定的行，“selectionIdentityColumnId”列中的值提供唯一键。当一行被选中时，唯一键被放入“selectedRowKeys”。 | string | 否 | 直接编辑 |
| serverEnabled | 启用服务器端分页和排序。默认情况下设置为false。如果保留为false，表格排序和分页将在客户端执行，从而减少对服务器的调用并提高性能。然而，因为这需要预先加载所有数据，所以具有客户端排序的表格需要更多内存。如果设置为true，查询必须使用分页和/或排序选项来修改返回的查询结果。例如，如果pageSize为10，则最多可以返回10行。 | boolean | 是 | 直接编辑 |
| tooltipPosition | 指定工具提示将渲染的位置。 | Blueprint.Position | 否 | 直接编辑 |
| tooltipsEnabled | 指定是否启用工具提示。 | boolean | 是 | 直接编辑 |
| headerTooltip | 列标题工具提示中显示的文本。如果headerTooltip被省略或为null，则不会显示工具提示。支持HTML。 | string | 否 | 直接编辑 |
| transpose | 指示表格的行和列是否应转置。 | boolean | 否 | 直接编辑 |
| clickEvents | 此表格微件公开的点击事件名称列表。 | boolean | 是 | 直接编辑 |

#### IColumnOption

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| horizontalAlignment | 行的水平对齐：左、居中或右。 | string | 否 | 直接编辑 |
| name | 列的显示名称。 | string | 否 | 直接编辑 |
| width | 覆盖列宽。 | number | 否 | 直接编辑 |

#### IGridOptions

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| enableSelection | 指示用户是否可以选择表格上的行。 | boolean | 否 | 直接编辑 |
| enableSorting | 指示用户是否可以对表格中的数据进行排序。（也应设置sortOptions的值。） | boolean | 否 | 直接编辑 |
| pagingOptions | 参见下方ITablePagingOptions。 | ITablePagingOptions | 否 | 直接编辑 |
| selectionOptions | 参见下方ISelectionOptions（enableSelection也必须设置为true）。 | ISelectionOptions | 否 | 直接编辑 |
| sortOptions | 参见下方ISortOptions（enableSorting也必须设置为true）。 | ISortOptions | 否 | 用户交互 |

#### ISelectionOptions

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| checkbox | 指示是否应显示一个复选框列作为行选择的视觉提示。 | boolean | 否 | 直接编辑 |
| multiSelect | 指示是否可以选择多行。 | boolean | 否 | 直接编辑 |
| selectionRequired | 指定是否可以取消选择所有值。启用时，此标志阻止用户取消选择最后选定的值。如果微件开始时没有选定的值，则仅在用户进行初始选择后阻止取消选择。 | boolean | 否 | 直接编辑 |

#### ISortOptions

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| columnId | 当前表格排序的数据字段。 | string | 是 | 用户交互 |
| isAscending | 当前排序的方向。 | boolean | 是 | 用户交互 |

#### ITableHover

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| columnIndex | 悬停单元格的列号。枚举从0开始。 | number | 是 | 用户交互 |
| displayValue | 悬停单元格的显示值。 | string | 是 | 用户交互 |
| isHeader | 指定当前单元格是否为表头。 | string | 是 | 用户交互 |

#### ITablePagingOptions

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| currentOffset | 当前可见页（从0开始索引）。 | number | 是 | 用户交互 |
| pageSize | 每页显示的结果数。 | number | 是 | 直接编辑 |
| totalServerItems | 可用结果的总数（用于计算所需的页数）。 | number | 否 | 直接编辑 |

### 示例

#### 动态表格

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
{
  "columnData": "{{query1}}",  // 查询数据源
  "columnOptions": {
    "id": {
      "name": "ID",  // 列名为ID
      "width": 50    // 列宽度为50
    },
    "name": {
      "name": "Full Name"  // 列名为全名
    },
    "address": {
      "name": "Home Address"  // 列名为家庭住址
    },
    "phone_number": {
      "name": "Phone Number"  // 列名为电话号码
    },
    "score": {
      "name": "Score",  // 列名为分数
      "horizontalAlignment": "right"  // 水平对齐方式为右对齐
    }
  },
  "columnOrder": [
    "id",
    "name",
    "address",
    "phone_number",
    "score"
  ],
  "gridOptions": {
    "enableSelection": true,  // 启用选择功能
    "enableSorting": true,    // 启用排序功能
    "pagingOptions": {
      "currentOffset": 0,      // 当前偏移量
      "pageSize": 10,          // 每页显示的条目数
      "totalServerItems": 100  // 服务器中的总条目数
    },
    "selectionOptions": {
      "checkbox": false,    // 不启用复选框选择
      "multiSelect": true   // 启用多选
    },
    "sortOptions": {
      "columnId": "score",  // 排序的列为分数
      "isAscending": false  // 以降序排序
    }
  },
  "selectedRowKeys": [],  // 当前选中的行键
  "selectionIdentityColumnId": "id",  // 用于选择的标识列ID
  "serverEnabled": true,  // 启用服务器功能
  "tooltipsEnabled": false  // 不启用工具提示
}
```

#### 静态表格

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
{
  "columnData": {
    "staticOptions": [
      "option1",
      "option2",
      "option3"
    ]
  },
  "columnOptions": {},
  "columnOrder": [],
  "gridOptions": {
    "enableSelection": true, // 启用选择功能
    "selectionOptions": {
      "checkbox": true, // 启用复选框选择
      "multiSelect": false // 禁用多选功能
    }
  },
  "selectedRowKeys": [], // 当前选中行的键
  "selectionIdentityColumnId": "staticOptions", // 选择标识列的ID
  "serverEnabled": false, // 不启用服务器功能
  "tooltipsEnabled": false // 不启用工具提示
}
```

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
{
  "columnOptions": {},  // 列选项
  "columnOrder": [],  // 列顺序
  "gridOptions": {},  // 网格选项
  "selectedRowKeys": [],  // 选中行的键
  "selectionIdentityColumnId": "Metric",  // 选择标识列ID
  "serverEnabled": false,  // 服务器启用状态
  "tooltipsEnabled": false  // 工具提示启用状态
}
```

### 教程：添加一个表格微件

假设你想要添加一个表格微件来显示航班数据。在左上角选择微件按钮，然后选择可视化 > 表格，以向你的 Slate 应用程序中添加一个表格微件。

将表格微件重命名为一个更容易识别的名称。在属性编辑器中选择微件的名称，并将其更改为w_flightTable。

通过在数据字段中输入"{{q_allFlights}}"来配置表格以使用q_allFlights查询。你应该会看到表格填充了数据。

注意，"{{q_allFlights}}"不是纯 JSON 语法。大括号是 Handlebars 语法，其中每个表达式表示为 {{expression}}。参见Handlebars以了解其在 Slate 中的使用。

你的表格现在具有正确的数据，但格式可以改进。选择添加所有列以查看底层数据中每列的格式选项。

由于flight_id列不是人类可读的列，现在将其隐藏。然而，我们将在稍后配置选择一行或多行的功能时保留在表中以作参考。

对于其余的列，选择一个显示名称作为标题，并添加格式字符串以使用MomentJS ↗的格式化字符串来清理时间戳。

我们现在有一个整洁显示所有数据的表格：

接下来，设置用户如何通过选择和排序与表格交互。

在属性编辑器中切换到杂项选项卡，并勾选允许选择和启用排序。用户现在可以直接选择列以查看表格以不同方式排序，并可以点击特定行以选择它。

最后，决定使用什么作为表格中给定行的唯一标识符。在这种情况下，使用航班的名称。在标记为键列 ID的下拉菜单中，选择flight_id。

如果未勾选服务器分页/排序选项，表格将只对已经加载的数据进行排序和分页，这在我们目前的例子中仅是表格的前10行。在 Slate 中，你可以可靠地将5-10k行加载到浏览器内存中，但这将受到用户浏览器标签页可用资源的限制。

在大多数情况下，最佳实践是配置服务器端的分页和排序。由于在last-mile-flights表中有大约75k个航班，在 Foundry 参考项目中的flights表中有大约400万个航班，因此不可能一次性将所有结果带入前端。

#### 配置分页和排序

勾选启用分页和服务器分页/排序选项。选择一个页面大小数字来设置一次显示给用户的行数。

启用这些选项后，你的表格将现在跟踪当前页面；我们可以在查询中使用这些信息来仅带回相关行进行显示。

打开查询编辑器并返回到q_allFlights。我们现在将更新LIMIT语句以反映表格中配置的页面大小，并添加OFFSET语句以请求 Postgres 提供给我们正确的结果页面。

使用与我们用于将查询数据包含到表格微件中的相同 Handlebars 语法，从查询内部引用表格微件的状态：

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
SELECT
    flight_id, -- 航班ID
    carrier_code, -- 航空公司代码
    tail_num, -- 飞机尾号
    origin, -- 起始地
    dest, -- 目的地
    dep_ts_utc, -- 出发时间（UTC）
    arr_ts_utc, -- 到达时间（UTC）
    distance, -- 航程距离
    actual_elapsed_time -- 实际飞行时间
FROM "foundry_sync"."{{v_flightTable}}" -- 从指定的航班表中选择数据
LIMIT {{w_flightTable.gridOptions.pagingOptions.pageSize}} -- 限制返回结果的行数
OFFSET {{w_flightTable.gridOptions.pagingOptions.currentOffset}} -- 从指定的偏移量开始返回结果
```

现在，您的表格一次显示20行，您可以选择下一个按钮或跳转到特定页面。现在，让表格微件知道总行数，以便正确显示“总条目”。

为此，创建一个名为q_flightCount的新查询并计算行数：

```
Copied!1
2
3
SELECT
    COUNT(flight_id) as num_flights -- 计算航班的数量，并将结果命名为 num_flights
FROM "foundry_sync"."{{v_flightTable}}" -- 从指定的动态表中查询数据，该表名由变量 v_flightTable 确定
```

选择更新以保存查询并返回到表格微件Misc选项卡。在Server Total输入中，使用 Handlebars 引用我们查询中的计数：

```
Copied!1
2
{{q_flightCount.num_flights.[0]}}
# 访问 `q_flightCount` 字典中 `num_flights` 列表的第一个元素
```

现在，我们的表格知道我们正在显示特定的一组行，来自于总条目（对于flights数据集为4.2M，或者对于last-mile-flights为73,946）。

这解决了分页问题，并允许我们遍历大型数据集，而不会使用户浏览器负担过重或查询超时。我们仍然必须开启服务器端排序，以便我们的查询响应用户与表格的交互。

返回到q_allFlights并在我们的查询中添加一个ORDER BY子句。就像您参考pagingOptions.pageSize和pagingOptions.currentOffset一样，参考.sortOptions.columnId和.sortOptions.isAscending以创建正确的SQL语句：

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
-- 根据 w_flightTable.gridOptions.sortOptions.columnId 指定的列进行排序
ORDER BY {{w_flightTable.gridOptions.sortOptions.columnId}}
    -- 如果 isAscending 为 true，则按升序排序
    {{#if w_flightTable.gridOptions.sortOptions.isAscending}}
        ASC
    -- 否则按降序排序
    {{else}}
        DESC
    {{/if}}
```

您应该会看到一个新可用的条件 Handlebars 块语句。此语句允许您将逻辑注入到文本插值中。在这种情况下，我们可以根据用户在表中的选择选择ASC或DESC。

尽管 Handlebars 易于用于在 Slate 应用中注入简单逻辑，但我们通常建议使用函数为大型应用添加更复杂的逻辑。

现在，您的完整查询应如下所示：

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
SELECT
    flight_id,          -- 航班编号
    carrier_code,       -- 航空公司代码
    tail_num,           -- 飞机尾号
    origin,             -- 出发地机场代码
    dest,               -- 目的地机场代码
    dep_ts_utc,         -- 出发时间（UTC）
    arr_ts_utc,         -- 到达时间（UTC）
    distance,           -- 飞行距离
    actual_elapsed_time -- 实际飞行时间
FROM "foundry_sync"."{{v_flightTable}}"
ORDER BY {{w_flightTable.gridOptions.sortOptions.columnId}} -- 根据指定列排序
    {{#if w_flightTable.gridOptions.sortOptions.isAscending}}
        ASC             -- 升序排列
    {{else}}
        DESC            -- 降序排列
    {{/if}}
LIMIT {{w_flightTable.gridOptions.pagingOptions.pageSize}} -- 限制返回的行数
OFFSET {{w_flightTable.gridOptions.pagingOptions.currentOffset}} -- 设置返回结果的偏移量
```

该SQL查询从foundry_sync数据库的{{v_flightTable}}表中选择航班相关信息。结果根据{{w_flightTable.gridOptions.sortOptions.columnId}}指定的列进行排序，可以升序或降序排列。返回的行数由{{w_flightTable.gridOptions.pagingOptions.pageSize}}限制，并从{{w_flightTable.gridOptions.pagingOptions.currentOffset}}偏移量开始。
为表格添加一个标题，以便一目了然地解释其显示的信息。

选择微件按钮，从选项中选择一个简单的文本微件。

在文本微件中填写表格的标题：All Flights或Last Mile Flights，根据具体情况选择。

将文本微件移动到表格的左上角，使用网格线确保一切对齐。

现在，将表格正确地排列在标题和副标题下方。按住Cmd键选择表格及其标题（或拖动选择）两个微件，然后移动两个微件，使它们在应用程序标题下正确对齐。

您的应用程序现在应如下面所示，带有完成的表格微件。注意，现在您可以选择一行并对表格进行排序。

## Toast

下表提供了有关 Toast 微件可用属性的使用详情。表后跟随几个示例。

### 属性

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| actionText | 在操作按钮中显示的文本 | 字符串 | 是 | 直接编辑 |
| hasAction | 指定 Toast 是否有操作按钮。 | 布尔值 | 是 | 直接编辑 |
| intent | Toast 的视觉意图颜色。 | 字符串 | 是 | 直接编辑 |
| message | Toast 的消息内容。 | 字符串 | 是 | 直接编辑 |
| timeout | Toast 自动消失前等待的毫秒数。提供值 <= 0 将禁用超时。 | 数字 | 是 | 直接编辑 |

#### 操作

| 操作名称 | 描述 |
| --- | --- |
| close | 触发此操作会关闭 Toast。 |
| open | 触发此操作会打开 Toast。 |

#### 事件

| 事件名称 | 描述 |
| --- | --- |
| didClose | 当 Toast 完全关闭时触发此事件。 |
| didOpen | 当 Toast 完全打开时触发此事件。 |
| click | 当点击 Toast 操作按钮时触发此事件。 |

### 示例

#### Toast

```
Copied!1
2
3
4
5
6
7
{
  "actionText": "Toast Example",  // 操作按钮的文本，"Toast Example"是示例文本
  "hasAction": false,             // 是否包含操作按钮，false表示没有
  "intent": -1,                   // 意图值，-1通常表示没有特定的意图
  "message": "Toast Message",     // 显示的消息文本，"Toast Message"是示例消息
  "timeout": 600                  // 消息显示的持续时间，以毫秒为单位，这里是600毫秒
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
{
  "actionText": "Action!", // 行动按钮的文本
  "hasAction": false,      // 是否具有行动按钮
  "intent": -1,            // 意图标识符，-1表示没有特定意图
  "message": "Message",    // 消息内容
  "timeout": 3000          // 超时时间，单位为毫秒
}
```

## 树

下表提供了有关树微件可用属性的使用详情。

### 属性

| 属性 | 描述 | 类型 | 必填 | 更改者 |
| --- | --- | --- | --- | --- |
| contents | 包含使用Blueprint的ITreeNode组件结构的JSON数据层级。 | json | 是 | 直接编辑 |
| selected | 被选中的节点ID | json | 是 | 直接编辑 |
| selectionType | 确定选择类型 - ‘none’，‘single’或‘multiple’。 | 字符串 | 是 | 直接编辑 |

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
{
  "contents": [
                {
                  "childNodes": [
                      {id: 3, label: "bar 1"},
                      {id: 4, label: "bar 2"}
                  ],
                  "iconName": "folder-close", // 图标名称，表示文件夹关闭状态
                  "id": 1, // 节点唯一标识符
                  "label": "bars", // 节点标签名称
                },
                {
                  "id": 2, // 节点唯一标识符
                  "label": "foo" // 节点标签名称
                }
              ],
  "searchText": "", // 搜索文本，当前为空
  "selectedNodes": [], // 当前选中的节点列表，当前为空
  "selectionType": SelectionType.SINGLE // 选择类型，单选
}
```
