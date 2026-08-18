来源: https://palantir.com/docs/zh/foundry/available-connectors/netsuite-overview/

# Oracle NetSuite 概述

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Oracle NetSuite 概述

Foundry支持以不同的方法连接到Oracle NetSuite，具体取决于您的应用案例：

- NetSuite SuiteAnalytics推荐用于提取大批量数据，因为它在读取操作上提供了更好的性能和可扩展性。SuiteAnalytics要求您提供Oracle NetSuite的JDBC驱动程序，并且仅支持用户名/密码身份验证。开始使用NetSuite SuiteAnalytics。
- NetSuite SuiteTalk (JDBC)广泛支持许多NetSuite实体。然而，SuiteTalk (JDCBC) 利用较旧的基于SOAP的服务 ↗，可能在处理大表时面临性能问题。SuiteTalk (JDBC) 仅支持基于词元的身份验证 (TBA) 。开始使用NetSuite SuiteTalk (JDBC)。
- NetSuite SuiteQL (JDBC)支持较小范围的NetSuite实体，但提供了更好的读取性能。SuiteQL (JDBC) 仅支持基于词元的身份验证。开始使用NetSuite SuiteQL (JDBC)。