来源: https://palantir.com/docs/zh/foundry/foundryts/objects-object/

# foundryts.objects.Object

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.objects.Object

## classfoundryts.objects.Object(object_type_id)

Ontology中的一种Object类型。

此类提供了创建对存储为Ontology中Object上的时间序列属性的时间序列的引用的方法。

- 参数:object_type_id(str) – Ontology中Object类型的ID。
请确保您使用的是object_type_id的ID，因为平台上有三种Object类型的引用可用：ID、API、RID。

## 示例

```
Copied!1
2
>>> aircraft_object_type = Object("aircraft") # 对象类型引用
>>> airplane = airplane_object_type.id("aircraft-1") # 现在可以使用主键获取对象引用
```

#### id(object_primary_key_value)

使用其主键创建对Ontology Object的引用。

- 参数：object_primary_key_value(str) – Object的主键，可以在定义Object的数据集中找到，也可以在↗ Object Explorer中找到。
- 返回：一个可以被用于在通过FoundryObject.property()访问时间序列属性的Ontology Object的引用。
- 返回类型：FoundryObject
## 示例

```
Copied!1
2
>>> aircraft_object_type = Object("aircraft")  # 创建一个类型为 "aircraft" 的对象
>>> airplane = airplane_object_type.id("aircraft-1") # 对象引用可用于访问 TSP（时间序列处理）
```
