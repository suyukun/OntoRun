来源: https://palantir.com/docs/zh/foundry/foundryts/foundryts/

# foundryts.FoundryTS

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.FoundryTS

## classfoundryts.FoundryTS(*args, **kwargs)

在后台向FoundryTS后端发送查询的单例。

此单例通过环境变量自动初始化，用户无需初始化实例即可调用FoundryTS支持的函数。

## 示例

```
Copied!1
>>> fts = FoundryTS()  # 创建一个FoundryTS对象的实例
```

#### property搜索

用于以foundryts.search.Search搜索Ontology的属性。

我们建议使用此属性进行搜索，因为它在Foundry生态系统中执行搜索时提供了保护措施。

## 示例

```
Copied!1
2
3
4
>>> fts = FoundryTS()
>>> objects = fts.search.series(metadata.property == 'value')
# 执行搜索，查找元数据中属性等于'value'的时间序列
NodeCollection(...)
```
