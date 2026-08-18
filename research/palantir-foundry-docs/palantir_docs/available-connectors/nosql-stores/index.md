来源: https://palantir.com/docs/zh/foundry/available-connectors/nosql-stores/

# NoSQL 存储

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# NoSQL 存储

数据连接可以配置为从各种 NoSQL 数据库同步数据。之前集成的一些 NoSQL 存储示例包括：

- Amazon DynamoDB
- Apache HBase
- Azure Cosmos DB
- Cassandra
- Cockroach DB
- CouchDB
- Elasticsearch
- InfluxDB
- MarkLogic
- MongoDB
- Neo4j
- OrientDB
- Redis
推荐的配置方法可能会因 NoSQL 数据库而异：

- 一些系统有专用的连接器，可以直接在新源页面上选择。当有专用连接器时，我们建议直接选择它。
- 一些系统有一个 REST API，可以从外部变换和/或REST API 源使用。
- 一些系统提供一个 JDBC 驱动程序，可以与通用JDBC 连接器一起使用。
- 对于不属于上述类别的系统，请联系 Palantir 客服支持。