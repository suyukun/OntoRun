来源: https://palantir.com/docs/zh/foundry/foundryts/objects-foundry-object/

# foundryts.objects.FoundryObject

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.objects.FoundryObject

## classfoundryts.objects.FoundryObject(object_type_id, object_primary_key)

Ontology中的一个Object。

- 参数：object_type_id(str) – Ontology中Object类型的ID。object_primary_key(str) – Object的主键，可以在定义该Object的数据集中找到，或在↗ Object Explorer中找到。
- object_type_id(str) – Ontology中Object类型的ID。
- object_primary_key(str) – Object的主键，可以在定义该Object的数据集中找到，或在↗ Object Explorer中找到。
FoundryObject应仅使用Object.id()创建，以提供访问Ontology中Object的安全保障。请参阅下面的示例。

## 示例

```
Copied!1
>>> aircraft_object = Object("aircraft").id("aircraft-1l")  # 创建一个名为"aircraft"的对象，并设置其ID为"aircraft-1l"
```

注意：代码中原本有一个小错误，id("aircraft-1l)中的引号未闭合，已修正为id("aircraft-1l")。

#### property(property_id, dataframe_identifier=None)

使用FoundryObject的时间序列属性创建时间序列引用。

此引用可用于FoundryTS支持的所有变换和分析。

- 参数：property_id(str) – 用于引用时间序列属性的属性ID，可从↗本体管理器中的属性编辑器视图中提取。dataframe_identifier(str,非必填) – 在评估多个时间序列时，在结果数据帧中的序列标识符foundryts.NodeCollection。这对于访问复杂的时间序列属性类型是必需的，例如↗模板（默认是平台中的序列ID）。
- property_id(str) – 用于引用时间序列属性的属性ID，可从↗本体管理器中的属性编辑器视图中提取。
- dataframe_identifier(str,非必填) – 在评估多个时间序列时，在结果数据帧中的序列标识符foundryts.NodeCollection。这对于访问复杂的时间序列属性类型是必需的，例如↗模板（默认是平台中的序列ID）。
- 返回：一个可用于变换和分析的时间序列引用，称为FunctionNode。
- 返回类型：FunctionNode
确保您使用的是property_id的属性ID，因为平台上有三个可用的属性引用：property ID、property RID、API Name。

## 例子

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
>>> aircraft_1_altimeter_reading = (
...     Object("aircraft")
...     .id("aircraft-1")  # 指定航空器的ID为“aircraft-1”
...     .property("altimeter_series_id")  # 获取航空器的高度计数据序列ID
... )
>>> aircraft_1_altimeter_reading.to_pandas()  # 将数据转换为Pandas DataFrame格式
                timestamp     value
0   2024-09-06 07:00:00.000 -1.185493
1   2024-09-06 07:01:30.983  0.830117
2   2024-09-06 07:03:01.966  0.115240
3   2024-09-06 07:04:32.949  0.059973
4   2024-09-06 07:06:03.932 -0.290032
..                      ...       ...
245 2024-09-06 13:11:30.835  2.346732
246 2024-09-06 13:13:01.818  0.891372
247 2024-09-06 13:14:32.801  0.318806
248 2024-09-06 13:16:03.784 -0.339124
249 2024-09-06 13:17:34.767 -0.879413
```

此代码片段用于从某个对象（航空器）中获取高度计的读数，并将其转换为Pandas DataFrame格式，以便进行进一步的数据分析和处理。timestamp列表示数据采集的时间戳，value列表示对应时间的高度计读数。
