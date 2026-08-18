来源: https://palantir.com/docs/zh/foundry/geotemporal-series/integrating-geotemporal-series-with-the-ontology/

# 将地理时间序列与Ontology集成

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 将地理时间序列与Ontology集成

在您的Ontology中设置地理时间序列需要创建一个地理时间序列Object类型，该类型引用地理时间序列同步中的单个序列，并具有地理时间序列引用属性。这些Object类型将支持在Foundry应用中的分析和可视化。

地理时间序列同步在Pipeline Builder中使用地理时间序列输出类型进行配置，并可能使用Object输出类型。
