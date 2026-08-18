来源: https://palantir.com/docs/zh/foundry/foundryts/search-property/

# foundryts.search.Property

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.search.Property

## classfoundryts.search.Property(name, property_type, field, should_normalize=False, force_analyze=False)

用于Ontology对象属性的FoundryTS封装器。

此类在内部用于评估Search查询。作为ontology()的结果，Property的实例将被用于评估Search表达式。

- 参数:name(str) – Ontology对象属性的名称。property_type(type) – 属性中值的类型，作为Python类型。查看对应支持的类型在↗ 平台文档。should_normalize(bool,非必填) – 是否规范化Ontology属性的名称。（默认值为false）。force_analyze(bool,非必填) – （已弃用）是否引用原始属性。（默认值为false）。
- name(str) – Ontology对象属性的名称。
- property_type(type) – 属性中值的类型，作为Python类型。查看对应支持的类型在↗ 平台文档。
- should_normalize(bool,非必填) – 是否规范化Ontology属性的名称。（默认值为false）。
- force_analyze(bool,非必填) – （已弃用）是否引用原始属性。（默认值为false）。