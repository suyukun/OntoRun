来源: https://palantir.com/docs/zh/foundry/time-series/sensor-object-end-to-end-ontology/

# 使用Ontology Manager创建传感器Object类型

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 使用Ontology Manager创建传感器Object类型

本指南解释了如何使用Ontology Manager创建传感器Object类型并将其链接到根Object类型。完成以下步骤后，您将能够在平台中与传感器Object类型进行交互。在此示例中，您将创建一个Flight SensorObject类型，并将其链接到一个Flight根Object类型。

## 第一部分：创建传感器Object类型

- 导航到Ontology Manager，并从左侧面板中选择Object类型。
- 从屏幕右上角选择新建Object类型。
- 在出现的配置对话框中，配置您的Object类型元数据。
- 在属性步骤中，选择使用您通过传感器数据管道创建的[Example] Sensors数据集作为Object类型的支持。
- 然后，在属性字段中，选择字符串类型unique_sensor_flight_id属性作为主键。如果这些选项可用，您也可以选择从数据源同步所有列或映射所有列。
- 选择Title列作为标题属性，这使得Flight SensorObject类型在应用中以人类可读的名称出现。
- 根据您平台的版本，您可能会看到配置Flight SensorObject类型权限和操作的选项。我们的示例不需要额外的权限或操作配置。
根据您平台的版本，您可能会看到配置Flight SensorObject类型权限和操作的选项。我们的示例不需要额外的权限或操作配置。

- 完成对话框中的所有步骤后，选择创建。
完成对话框中的所有步骤后，选择创建。

在新[Example] SensorsObject类型的属性标签中，属性应如下图所示：

## 第二部分：为传感器Object类型配置时间序列属性

- 导航到Ontology Manager中的[Example] Flight SensorObject类型，并从左侧面板中选择能力标签。
- 从时间序列属性部分选择**+ 添加**。
- 选择现有的Flight Sensor Series Id属性作为时间序列属性，然后选择设置为默认时间序列属性，以便它自动出现在Quiver中。
- 选择您在Pipeline Builder中创建的时间序列同步。在我们的示例中，它被称为[Example] Time Series Sync | Sensor Readings。
- 选择添加属性以保存时间序列属性配置。
## 第三部分：将传感器Object类型链接到根Object类型

使用以下步骤在[Example] Flight Sensor和[Example] FlightObject类型之间添加链接。

- 在Ontology Manager的[Example] Flight Sensor视图中，选择新建下拉菜单并选择链接类型。
- 在链接的左侧，选择[Example] Flight SensorObject类型。在右侧，选择[Example] FlightObject类型。
- 设置左侧Flight SensorObject类型的基数为多个，右侧FlightObject类型的基数为一个，这意味着FlightObject类型与Flight SensorObject类型具有一对多关系。
- 将flight_id列设置为Flight SensorObject类型的外键，这将设置flight_id为FlightObject类型的主键。
了解更多关于链接类型的信息。

## 第四部分：配置传感器Object类型

在时间序列部分，确保传感器Object类型切换为开启状态。设置Sensor link以使用最近创建的Flight到Flight Sensor链接。

- 将链接名称设置为Series Name列。应用程序将在该系列名称下显示传感器Object数据。
将链接名称设置为Series Name列。应用程序将在该系列名称下显示传感器Object数据。

- 通过在传感器Object类型设置中选择单位下拉菜单来配置单位。
通过在传感器Object类型设置中选择单位下拉菜单来配置单位。

是否分类和内部插值可以从传感器Object类型上的属性推断，但对于此应用案例不是必需的。只有在需要将分类时间序列值与数值时间序列值区分开时，才需要是否分类。

内部插值用于启用像Quiver这样的应用程序推断相邻数据点之间的系列值。查看我们的Quiver插值文档以获取更多信息。

- 从屏幕右上角选择保存以查看Ontology和整个平台中的更改。
现在，您已准备好在操作环境中使用Flight Sensor和FlightObject类型。继续阅读文档以了解如何在Workshop和Quiver中使用传感器Object类型时间序列数据。

我们的示例应用案例不需要配置是否为枚举。Is deprecated和Sparkline preview属性应被忽略。
