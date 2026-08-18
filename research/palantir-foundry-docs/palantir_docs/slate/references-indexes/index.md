来源: https://palantir.com/docs/zh/foundry/slate/references-indexes/

# 优化索引和模式设计

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 优化索引和模式设计

本页面的文档重点介绍如何调整索引以在 Postgres 和 ElasticSearch 中实现最佳性能。我们通常建议在 Ontology 功能之上搭建 Slate 应用程序，使用对象集和操作等特性来读取和写入数据。

一个高性能且易于维护的应用程序依赖于设计良好的数据集和适当的索引。

Postgres 的模式设计大多数方面与 Slate 完全无关。这些概念在其他地方有详细记录，数据库设计的通用最佳实践不在本讨论范围内。如果您尚不熟悉不同的模式模式或选择索引列的指导，Google 会迅速带您深入了解。

相反，我们将重点介绍一些与 Slate 和 Foundry 更具体相关的最佳实践。

#### 尽量将工作上移

在应用程序开发过程的每个阶段，都要问自己：“在哪里是完成这项工作的合适位置？”并始终倾向于将工作尽量上移。例如，如果您发现自己编写了一个复杂的 JavaScript 函数来聚合数据或提取指标，请问：“我能否在查询中完成这项工作？”

如果您在每次页面加载时都在查询中执行相同的工作，例如使用SUM()得出年度总数或使用DISTINCT()创建列表，请问自己：“我能否在派生数据集中完成这项工作？”

在 Foundry 中，分布式存储和计算相对于在查询或用户浏览器中完成的工作来说是“更便宜”的，因此尽可能预先计算。

#### Postgate（Postgres）

Postgate 将 Postgres 或 RDS 封装为通过 PostgreSQL 查询以只读方式访问 Foundry 数据集。请记住，应用程序查询的限制由关系数据库（而非平台中其他部分的 Spark/HDFS）的特性决定，特别是 Postgres 的特性。

在开发查询以检索数据时，使用 EXPLAIN ANALYZE 来分析查询并发现瓶颈。您可以在这篇Thoughtbot 博客文章 ↗中了解更多关于 Postgres 如何解释您的查询以及如何解释 EXPLAIN ANALYZE 请求的结果。您还可以阅读我们关于优化 Slate 的 Postgres 查询的更详细解释。

您可以使用部分查询构建模块化查询，以防止代码重用并更好地封装共享逻辑。我们建议使用部分查询和函数来在保持查询简洁和足够详细以便可读之间进行权衡。

#### Phonograph（ElasticSearch）

Phonograph 提供了一个读写数据存储，使用 ElasticSearch 风格的语法进行查询和聚合，同时允许在 Foundry 数据集上进行 CRUD 操作。有关 Phonograph 实践的更多信息，请参见从 Slate 向 Foundry 写回数据部分。
