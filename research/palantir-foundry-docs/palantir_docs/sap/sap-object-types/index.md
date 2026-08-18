来源: https://palantir.com/docs/zh/foundry/sap/sap-object-types/

# SAP 对象类型

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# SAP 对象类型

Palantir Foundry Connector 2.0 以SAP应用程序为对象的连接器（以下简称“连接器”）支持在Foundry中导入各种SAP对象类型：

- ERP表
- BW InfoProvider
- BW BEx 查询
- SLT
- BW 内容提取器
- 函数
- ERP 表数据模型
- 远程对象
## ERP表

table对象类型被用于在SAP应用服务器中从数据库表和视图中提取数据。SAP ABAP数据字典中的所有表和视图都被支持。也可以从自定义的Z*表中提取。

示例同步配置：

```
Copied!1
2
3
type: magritte-sap-source-adapter  # 指定适配器类型为 Magritte SAP 源适配器
sapType: table                     # SAP 对象类型为表
obj: MARA                          # SAP 表对象名称为 MARA，通常用于存储物料主数据
```

## BW InfoProvider

infoproviderObject类型被用于从SAP BW系统中提取数据。InfoProvider是以下对象的通用描述：

- InfoCube (Cube)
- DataStore Object (DSO)
- Advanced DataStore Object (–DSO)
- MultiProvider (MultiCube)
InfoProvider Object使用标准的SAP BW访问方法；所有来自SAP BW的授权概念都会被继承。

示例同步配置：

```
Copied!1
2
3
type: magritte-sap-source-adapter  # 类型: Magritte SAP 源适配器
sapType: infoprovider              # SAP 类型: 信息提供者
obj: Z3_C01                        # 对象: Z3_C01
```

在这个 YAML 配置中，我们定义了一个 SAP 源适配器，它的类型是infoprovider，并且对象标识符为Z3_C01。

## BW BEx 查询

bexObject 类型被用于在从 BEx 查询中提取数据。

查看如何配置 BEx 查询以获取更多详细信息。

示例同步配置：

```
Copied!1
2
3
type: magritte-sap-source-adapter # 类型：magritte SAP源适配器
sapType: bex # SAP类型：BEx（Business Explorer）
obj: ZCM_COMM_PRI # 对象：ZCM_COMM_PRI
```

## SLT

sltObject类型用于从SLT ODP队列中提取数据。SLT是一个基于触发器的复制工具，用于从SAP应用程序复制到目标系统。在此Object中，SLT ODP队列是一个目标系统。SLT中内置了CDC（变更数据捕获）机制。Connector仅向来自SLT的记录添加时间戳信息。

示例同步配置：

```
Copied!1
2
3
4
5
type: magritte-sap-source-adapter
sapType: slt
obj: MARA
context: SLT~P40
incrementalField: pointer
```

```
Copied!1
2
3
4
5
# type: 指定适配器的类型，这里是 magritte-sap-source-adapter。
# sapType: 指定 SAP 类型，这里是 SLT (SAP Landscape Transformation)。
# obj: 指定要处理的 SAP 对象，这里是 MARA (物料主数据)。
# context: 指定上下文信息，这里是 SLT 环境的标识符。
# incrementalField: 指定用于增量提取的字段，这里是 pointer。
```

## BW 内容提取器

extractorObject 类型被用于在从 SAP ERP 商业内容提取器中提取数据。商业内容提取器是用于从 SAP 应用程序中提取数据的现成结构。所有业务逻辑以及 CDC（更改数据捕获）机制都包含在提取器中。如果提取器支持增量提取，则应使用APPEND事务类型以增量方式摄取数据。

有关详细信息，请参阅如何配置提取器。

示例同步配置：

```
Copied!1
2
3
type: magritte-sap-source-adapter  # 适配器类型：magritte SAP源适配器
sapType: extractor  # SAP类型：数据提取器
obj: 0GL_ACCOUNT_ATTR  # 对象：0GL_ACCOUNT_ATTR（可能是SAP中的一个数据对象或属性）
```

## 函数

functionObject 类型被用于在通过远程启用的函数和BAPIs（业务API）从SAP应用中提取数据。SAP 函数是一组用于执行 SAP 中某些任务的指令，例如货币转换、主数据列表等。

查看如何配置函数提取以获取更多详细信息。

示例同步配置：

## ERP 表数据模型

数据模型对象类型被用于提取ERP表之间的关系。这些表关系基于标准的主键/外键模型。可以设置一个深度参数，以指示在为给定表提取数据模型时要遵循多少级关系。

同步配置示例：

```
Copied!1
2
3
type: magritte-sap-source-adapter  # 类型：magritte SAP 源适配器
sapType: datamodel                 # SAP类型：数据模型
obj: T006                          # 对象：T006
```

## 事务代码

tcodeObject类型用于提取由SAP报表生成的数据。

仅支持使用ABAP列表查看器（ALV）的报表。

tcode同步只能从同步配置UI的高级选项卡中创建。

有关详细信息，请参见如何配置事务代码提取。

如果您知道事务代码名称，请将其作为值提供给obj参数。
示例同步配置：

```
Copied!1
2
3
type: magritte-sap-source-adapter # 类型：Magritte SAP 源适配器
sapType: tcode # SAP 类型：事务代码
obj: ZTEST_ALV # 对象：ZTEST_ALV 事务代码
```

如果您只知道报告的程序名称，可以将程序名称作为obj参数提供，并将programType参数设置为program。 示例同步配置：

```
Copied!1
2
3
4
type: magritte-sap-source-adapter
sapType: tcode  # SAP事务码类型
obj: RSUSR200   # SAP对象名称，此处为RSUSR200
programType: program  # 程序类型
```

## HANA 视图

hanaviewObject 类型被用于在应用层从启用的 HANA 视图中提取数据。

有关更多详细信息和先决条件，请参阅如何配置 HANA 视图提取。

hanaview同步只能在同步配置 UI 的高级选项卡中创建。

```
Copied!1
2
3
type: magritte-sap-source-adapter  # 类型：Magritte SAP 源适配器
sapType: hanaview                 # SAP 类型：HANA 视图
obj: ZEXT_SBOOK                   # 对象：ZEXT_SBOOK
```

## CDS视图

CDS视图Object类型被用于在从ABAP CDS（核心数据服务）视图中提取数据。ABAP CDS使得可以在应用服务器的中央数据库上定义语义数据模型。与在ABAP字典中定义的现有数据库表和视图相比，这些模型的实体提供了增强的访问函数，使得可以优化基于Open SQL的应用程序。

## 远程Object

通过远程连接连接时，可以以与“非远程”等效Object相同的方式访问Object，具有相同的功能。唯一需要更改的是：

- 在Object类型前加上remote
- 提供一个context参数以识别远程系统
远程表的示例同步配置：

```
Copied!1
2
3
4
type: magritte-sap-source-adapter  # 指定适配器类型为 magritte 的 SAP 数据源适配器
sapType: remotetable               # 指定 SAP 数据源类型为远程表
obj: MARA                          # 指定 SAP 对象为 MARA 表，通常用于存储物料主数据
context: T50                       # 指定上下文为 T50，可能代表特定的配置或环境
```

远程BEx查询的示例同步配置：

```
Copied!1
2
3
4
type: magritte-sap-source-adapter  # 类型：马格利特 SAP 源适配器
sapType: remotebex  # SAP 类型：远程 BEx（Business Explorer）
obj: PAL16Q  # 对象名称：PAL16Q
context: T50  # 上下文：T50
```
