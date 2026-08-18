来源: https://palantir.com/docs/zh/foundry/foundryts/search-ontology/

# foundryts.search.ontology

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.search.ontology

## foundryts.search.ontology(name, should_normalize=False, force_analyze=False)

创建用于搜索的Ontology属性引用。

以此来创建可以在Search.series()中比较值的Ontology属性。

- 参数：name(str) – 在Ontology中显示的Ontology属性名称。should_normalize(bool,非必填*(*默认值为 false)) – 是否规范化Ontology属性的名称。force_analyze(bool,非必填) – (已弃用) 是否引用原始属性。(默认值为 false)。
- name(str) – 在Ontology中显示的Ontology属性名称。
- should_normalize(bool,非必填*(*默认值为 false)) – 是否规范化Ontology属性的名称。
- force_analyze(bool,非必填) – (已弃用) 是否引用原始属性。(默认值为 false)。
- 返回：可在Search.series中使用的Ontology属性引用。
- 返回类型：Property
Search.series()

## 示例

```
Copied!1
2
3
4
5
>>> from foundryts.search import ontology
>>> ontology('some-property-name')
Property['some-property-name']  # 这是用来获取某个属性名称对应的属性对象
>>> fts.search.series(ontology('my_prop') == 'my_value')
NodeCollection([...](1000))  # 使用属性过滤搜索符合条件的时间序列数据
```

以上代码展示了如何使用foundryts库中的ontology函数来获取某个属性的对象，然后利用这个属性对象与特定值进行比较，以搜索匹配条件的时间序列数据。
