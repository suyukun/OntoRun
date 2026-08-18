来源: https://palantir.com/docs/zh/foundry/notepad/widgets-contour-chart/

# Contour图表

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Contour图表

来自Contour分析的图表和表格可以通过Contour图表部分嵌入。您可以通过点击 + 添加微件或在段落字段中输入 / 来打开微件插入菜单，也可以直接通过Contour分析本身上的复制到Notepad按钮来添加。

请注意，当您打开带有Contour面板的Notepad文档时，源数据会由Notepad更新。

Contour微件上的锁定数据功能与其他微件不同。应用时，它会锁定Contour微件的可视化和数据，同时仍允许用户交互。另一方面，锁定其他微件会产生微件的非交互式快照。如果支持的交易已被手动或通过保留策略删除，交互式锁定的微件将不会加载锁定的可视化。有关更多信息，请参阅锁定数据功能的文档。

### 微件属性

- 路径：指定所选Contour分析中的路径。
- 面板：定义从所选路径中显示哪个面板。
- 参数：（视情况而定）参数配置仅在源Contour分析定义和使用参数时显示。该配置允许分别覆盖这些参数变量值。如果未指定值，将使用Contour分析中的默认参数值。
### 模板配置

- 参数覆盖：（非必填）指定Contour参数及关联覆盖值的JSON字符串。值将传递给嵌入的Contour图表，以覆盖Contour图表的外部参数。请参阅下表中的示例，了解如何提供所需的JSON字符串。
| Contour输入类型 | 示例Contour参数名称 | 示例JSON字符串 |
| --- | --- | --- |
| 字符串 | carrier_code | {"carrier_code": "OO"} |
| 字符串数组 | carrier_codes | {"carrier_codes": ["OO", "MQ"]} |
| 数字 | booking_class | {"booking_class": 2} |
| 数字数组 | booking_classes | {"booking_classes": [1,2]} |
| 日期 | departure_date | {"departure_date": "2022-09-01T00:00:00+02:00"} |

多个值可以组合成一个单一的JSON字符串，如下所示：{"carrier_code": "OO", "booking_class": 2}。请参阅下面的示例，了解如何提供具有预览值的模板输入并将其连接到Contour参数。
