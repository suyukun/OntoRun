来源: https://palantir.com/docs/zh/foundry/sap/configure-bex-query/

# BEx 查询

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# BEx 查询

## 概述

BEx 是一个基于 SAP BW InfoProvider 的多维查询框架。BEx 查询使用标准的 SAP BW 访问方法，并继承了所有 SAP BW 的授权概念。BEx 查询表示应用于 InfoProvider 视图的业务逻辑，因此元数据对于理解筛选、变量、行、列、基于单元格的公式、异常和条件至关重要。

如果 BEx 查询具有动态列（列上具有关键值的特征，每个关键值与特征值一起重复），则这将创建一个动态输出。Foundry 不支持动态列，因此如果是这种情况，请相应地调整您的查询。

## 提取数据

使用bexObject 类型从 BEx 查询中提取数据。

示例同步配置：

```
Copied!1
2
3
4
5
6
7
type: magritte-sap-source-adapter
sapType: bex
obj: PALQ16

# type: 表示使用的适配器类型，这里是 magritte-sap-source-adapter。
# sapType: 指定SAP的类型，这里是 BEx（Business Explorer）。
# obj: 指定要连接的SAP对象，这里是 PALQ16。
```

## 支持的参数

在配置事务代码提取时支持其他参数：

- 筛选
- charFilter
- freeChars
- dropColumns
- technicalNames
可以在同一个同步中定义多个参数。

### 筛选

为BEx查询变量提供筛选值。

同步配置示例：

```
Copied!1
2
3
4
type: magritte-sap-source-adapter  # 指定适配器类型为 magritte-sap-source-adapter
sapType: bex  # SAP 类型设置为 BEx（Business Explorer）
obj: PALQ16  # 对象标识符为 PALQ16
filter: VAR006=A;VAR006=B  # 过滤条件，VAR006 等于 A 或 B
```

### charFilter

在查询执行后筛选数据。

```
Copied!1
2
3
4
type: magritte-sap-source-adapter  # 类型：magritte-sap-source-adapter
sapType: bex                       # SAP类型：bex
obj: PALQ16                        # 对象：PALQ16
charFilter: PMAT=M001              # 字符过滤器：PMAT=M001
```

### freeChars

为输出添加特征。这些特征需要在 BEx 查询中定义为自由特征。

以下示例将 PAL01 添加到输出中：

```
Copied!1
2
3
4
type: magritte-sap-source-adapter  # 类型：magritte SAP 源适配器
sapType: bex                      # SAP 类型：bex（Business Explorer）
obj: PALQ16                       # 对象：PALQ16
freeChars: PAL01                  # 自由字符：PAL01
```

### dropColumns

从输出中移除关键特征。

以下示例将PAL01从输出中移除：

```
Copied!1
2
3
4
type: magritte-sap-source-adapter  # 定义源适配器类型为magritte-sap-source-adapter
sapType: bex  # 指定SAP类型为BEx（Business Explorer）
obj: PALQ16  # 定义对象名称为PALQ16
dropColumns: PAL01  # 指定要删除的列为PAL01
```

### technicalNames

允许在技术名称和人类可读（语言相关）的列名之间切换。

示例同步配置：

```
Copied!1
2
3
4
type: magritte-sap-source-adapter
sapType: bex
obj: PALQ16
technicalNames: true
```

这是一个用于配置 SAP 数据源适配器的 YAML 文件。以下是每个字段的说明：

- type: 指定适配器的类型，这里是magritte-sap-source-adapter，用于连接 SAP 数据源。
- sapType: 表示 SAP 的类型，这里是bex，通常指的是 SAP 的 Business Explorer。
- obj: 目标对象的名称，这里是PALQ16，可以是查询、信息对象等。
- technicalNames: 布尔值，表示是否使用技术名称，true表示使用技术名称。