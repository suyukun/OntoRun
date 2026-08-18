来源: https://palantir.com/docs/zh/foundry/geospatial/ontology/

# 在Ontology中使用地理空间数据

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 在Ontology中使用地理空间数据

## 如何配置具有矢量数据的Ontology数据集

强烈建议您使用Foundry的geospatial-tools库来解析、清理和转换矢量数据格式（如shapefiles和geoJSON）为可以添加到Ontology的数据集。在变换中使用矢量数据的文档提供了关于使用该库的重要指导，应在尝试将数据添加到Ontology之前阅读。

### 点

可以使用geohash属性类型指定点几何体。geohash属性的内容应为以下字符串之一：

- latitude,longitude：例如，57.64911,10.40744。坐标必须使用WGS 84 CRS（标准纬度和经度）。
- 一个Geohash ↗：例如，u4pruydqqvj。Geohash将被转换为点，使用Geohash矩形的左下角。
具有geohash属性的对象会被索引以进行地理空间搜索。

### 多边形和线

可以使用geoshape属性类型指定多边形和线几何体。geoshape属性的内容必须是符合以下要求的GeoJSON几何字符串：

- 必须是GeoJSON LineString、Polygon、MultiLineString、MultiPolygon、MultiPoint或Point。然而，点几何体不应使用geoshape属性类型；对于点几何体，请使用geohash属性类型。
- 必须不是Feature、FeatureCollection或GeometryCollection。
- 必须符合GeoJSON规范（RFC 7946）↗。
- 必须使用WGS 84坐标。
- 多边形和多多边形必须根据GeoJSON规范有效。多边形和多多边形必须闭合，使用右手/逆时针顺序用于外环，并且没有自相交。
这是一个geoshape属性的有效GeoJSON示例：

```
Copied!1
2
3
4
5
6
7
{
  "type": "LineString",  // 表示几何类型为线段
  "coordinates": [       // 线段的坐标数组
    [100.0, 0.0],        // 第一个点的坐标
    [101.0, 1.0]         // 第二个点的坐标
  ]
}
```

具有geoshape属性的对象被索引以用于地理空间搜索。

## 如何可视化、探索和发布地理空间数据

一旦你的地理空间数据加载到Ontology中，有两个主要的Ontology映射工具可以使用你的数据：

- 地图应用程序提供沉浸式地理空间分析和调查功能，包括时间序列叠加、链接分析和仿真。
- Workshop是一个为操作用户设计的应用程序搭建框架，并包含一个强大的地图微件。了解更多关于在Workshop中创建地图。
地理空间功能也可在其他Foundry应用程序中使用，包括Slate、Quiver、对象探索器和Contour。

### 在地图中使用外部图层

在某些情况下，Foundry也支持在地图中添加外部图层；例如，在你拥有一个外部功能服务或瓦片服务器并希望直接连接到Foundry地图而不需要先将所有数据加载到数据集中时。

请联系你的Palantir代表获取更多详情，因为这需要额外的配置来启用。

## Mapbox Boundaries

通过与Mapbox ↗的合作，Foundry提供内置支持，使用多种定义区域边界的可用选项来创建等值线样式的图层。

使用Boundaries，你可以将Foundry数据集和/或Ontology连接到一组管理的地理特征，代表各种类型的边界，例如行政区划或邮政编码区域。Mapbox Boundaries中的多边形是边缘匹配的，实现无缝的全局覆盖，因此你可以创建精确的数据可视化和准确的分析。

### 图层类型、级别和世界观

Mapbox提供跨多种类型、级别和世界观的边界数据。你可以使用Boundaries Explorer应用程序 ↗来探索可用的边界类型和级别，以及关于不同类型边界的其他文档 ↗。

### 使用Mapbox Boundaries

以下说明用于利用Mapbox Boundaries最新版本（v4）。如果你已经在使用早期版本，请首先迁移你的管道和应用程序。

#### 安装Mapbox Boundary定义

Mapbox Boundary定义v4可在Foundry Marketplace中下载。要从你的Foundry实例访问：

- 在Foundry实例上导航到/workspace/marketplace/discovery。
- 搜索“Mapbox”或使用左侧面板中的Store筛选到“Foundry Store”。
- 选择Mapbox Boundary Definitions v4产品。
- 点击Install。如果有人已经安装了这些边界，你会看到Open，从中你可以导航到当前的安装。
- 安装时：选择一个空间进行安装。由于产品只包含数据集，不需要Ontology。启用Installation suffix以自定义安装数据集的项目名称。在左侧面板底部选择Install。
- 选择一个空间进行安装。
- 由于产品只包含数据集，不需要Ontology。
- 启用Installation suffix以自定义安装数据集的项目名称。
- 在左侧面板底部选择Install。
- 安装任务完成后，点击产品名称右侧的View installation，导航到安装位置。
- 你可以通过选择右侧面板中的位置链接来访问已安装的边界数据集。默认情况下，只有你将拥有该项目的访问权限，但你可以在右侧项目详情面板中添加其他用户和组。
当新的次要边界数据集版本可用时，你可以通过安装顶部出现的横幅进行升级。主要版本发布将作为新的数据源产品提供。

请注意，产品安装到默认禁用编辑的新项目中，以确保安全升级（例如，如果有额外的边界数据集可用）。因此，我们建议将利用这些数据集的内容（例如，分析、管道等）保存到不同的项目中。如果需要编辑项目本身，可以选择左侧面板中的Settings，然后选择Unlock来启用编辑，如下图所示。

#### 将Mapbox ID集成到管道中

为了利用Mapbox Boundaries，你需要一个mapbox ID来识别特定边界类型和级别的区域。这些ID可以在边界元数据文件 ↗中找到，这些文件作为Mapbox Boundary定义产品的一部分自动提供。请参阅安装Mapbox定义获取说明。

安装元数据文件后，将它们与Foundry中的数据合并，以添加mapbox_id列。根据边界的类型和级别，元数据文件将包含其他ID和/或名称列，可以用作与你自己的数据合并的键。

此mapbox_id列将用于配置下游应用程序以显示基于边界的地图。

#### 配置下游应用程序

Mapbox Boundaries目前可以在以下产品中用于生成等值线样式的可视化：

- Workshop
- Contour
- 地图应用程序
- 对象视图
- 对象探索器
- Quiver
具体的配置选项可能会因每个消费应用程序而略有不同，但常见的配置选项包括：

- 数据中包含mapbox_id的字段或属性
- 选择你希望显示数据的特定世界观 ↗
- 使用的边界类型和级别
然后你可以使用数据集和/或Ontology中的数据来驱动这些边界的样式化，例如多边形的颜色。有关这些额外样式选项的更具体文档，请访问特定下游应用程序的文档。

#### 从Mapbox Boundaries v3迁移到v4

如果你目前使用的是旧版本的Mapbox Boundaries数据（如V2或V3），我们强烈推荐升级到v4。除了获得边界本身的更新，V4版本还包括更可靠的支持显示工具提示中的区域名称，以及支持自动缩放以适应Mapbox边界支持的地图图层等改进。

从v3迁移到v4时，有一些边界有重大变化。在继续之前，请查看重大变化的详细变更日志 ↗。

要迁移管道中的数据，你可以：

- 利用从V3到V4的ID映射表 ↗，这些表包含在Mapbox boundary definitions V4产品中。使用V3中的feature_id列将它们与现有边界数据合并，并引入V4添加的新mapbox_id列。确保手动处理上述提到的任何重大变化。
- 或者，你可以简单地遵循上述说明，使用边界元数据CSV文件从头开始合并mapbox_id列。
一旦在你的管道/Ontology中添加了mapbox_id列，重新配置下游应用程序以利用v4边界，并选择这个新列和相应的边界类型/级别。
