来源: https://palantir.com/docs/zh/foundry/data-integration/foundry-provided-drivers/

# Palantir 提供的 JDBC 源驱动程序

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Palantir 提供的 JDBC 源驱动程序

您可以使用 JDBC 驱动程序将您的 Foundry 注册连接到各种外部源，这些驱动程序在数据连接中显示为 Foundry 源。这些源是 JDBC 驱动程序的包装器，允许进行自定义，并附带推荐和必需的属性以及官方文档的链接。

如果您想将自己的 JDBC 驱动程序上传到 Foundry，请查看配置自定义 JDBC 驱动程序的文档。

## 设置

- 打开数据连接应用程序，并在屏幕右上角选择+新建源。
打开数据连接应用程序，并在屏幕右上角选择+新建源。

- 从列出的选项中找到您的特定源。查看 Palantir 提供的驱动程序的完整列表。
从列出的选项中找到您的特定源。查看 Palantir 提供的驱动程序的完整列表。

- 选择使用通过互联网的直接连接或通过中介代理进行连接。
选择使用通过互联网的直接连接或通过中介代理进行连接。

- 选择文档 ↗以查看驱动程序源的官方文档。
选择文档 ↗以查看驱动程序源的官方文档。

- 按照下面各节中的信息，继续进行连接器的其他配置提示。
按照下面各节中的信息，继续进行连接器的其他配置提示。

## 配置选项

| 参数 | 必需？ | 描述 |
| --- | --- | --- |
| URL | 是 | 驱动程序使用的 JDBC URL。预填充了一个模板，可能需要修改以确保正确行为。请参阅源系统的文档以了解 JDBC URL 格式，并查看Java 文档 ↗以获取更多信息。 |
| JDBC 属性 | 是 | 列出驱动程序需要的所有必需和推荐属性。将鼠标悬停在必需或推荐属性上将允许您导航到官方文档。您可以通过点击+ 添加属性按钮添加任何其他属性。 |

### JDBC 属性

您可以向 JDBC 连接添加属性 ↗以配置行为。某些属性对于特定驱动程序是强制性的。这些强制性属性是默认填充的，必须在您保存源之前设置。您还可以查看推荐的属性，您可以通过选择+添加属性并查看推荐部分来添加。

将鼠标悬停在必需或推荐属性的名称上，以访问所选驱动程序的官方文档页面。

## 配置 Palantir 提供的驱动程序同步

### SQL 查询

每次同步可以执行一个 SQL 查询。此查询应生成一个数据表作为输出，不应执行调用存储过程等操作。查询结果将保存到 Foundry 的输出数据集中。

## CData

许多 Palantir 提供的驱动程序是由CData ↗开发的。CData 为每个驱动程序提供完整的文档，包括有关在源系统上生成凭据的详细说明。您可以从任何 CData 驱动程序的文档页面导航到这些说明。

## 可用驱动程序

| 驱动程序 |
| --- |
| Act-On |
| Act! CRM |
| ActiveCampaign |
| Acumatica |
| Adobe Analytics |
| Adobe Commerce |
| ADP |
| Airtable |
| AlloyDB |
| Amazon DynamoDB |
| Amazon Marketplace |
| Apache CouchDB |
| Apache HBase |
| Apache Hive |
| Apache Phoenix |
| Authorize.Net |
| Avalara |
| Azure Active Directory |
| Azure Cosmos DB |
| Azure Data Catalog |
| Azure DevOps |
| Azure Synapse |
| Azure Table Storage |
| Basecamp |
| BigCommerce |
| Blackbaud Raisers Edge NXT |
| Box |
| Bugzilla |
| Bullhorn CRM |
| Cassandra |
| Certinia |
| ClickHouse |
| Cloudant |
| CockroachDB |
| Confluence |
| Couchbase |
| DocuSign |
| Domino |
| Dropbox |
| eBay |
| eBay Analytics |
| EnterpriseDB |
| Epicor Kinetic |
| Exact Online |
| Facebook |
| Facebook Ads |
| FreshBooks |
| Freshdesk |
| GitHub |
| Gmail |
| Google Campaign Manager |
| Google Contacts |
| Google Data Catalog |
| Google Directory |
| Google Drive |
| Google Search |
| Google Spanner |
| GraphQL |
| Greenplum |
| Highrise |
| IBM Cloud Data Engine |
| IBM Cloud Object Storage |
| Instagram |
| Jira Service Management |
| Kintone |
| LDAP |
| LinkedIn |
| LinkedIn Marketing Solutions |
| Mailchimp |
| Marketo |
| MarkLogic |
| Microsoft Access |
| Microsoft Ads |
| Microsoft Bing |
| Microsoft Dataverse |
| Microsoft Dynamics 365 |
| Microsoft Dynamics 365 Business Central |
| Microsoft Dynamics CRM |
| Microsoft Dynamics GP |
| Microsoft Dynamics NAV |
| Microsoft Excel |
| Microsoft Excel Online |
| Microsoft Exchange |
| Microsoft Office 365 |
| Microsoft OneDrive |
| Microsoft OneNote |
| Microsoft Planner |
| Microsoft Power BI®  XMLA |
| Microsoft Project |
| Microsoft SharePoint Excel |
| Microsoft SQL Server Analysis Services |
| Microsoft Teams |
| Monday |
| MYOB |
| OData |
| Odoo |
| Oracle |
| Oracle Eloqua |
| Oracle Fusion Cloud Financials |
| Oracle Fusion Cloud HCM |
| Oracle Fusion Cloud SCM |
| Oracle Sales |
| Oracle Service Cloud |
| Outreach |
| Paylocity |
| PayPal |
| Pinterest |
| Pipedrive |
| Postgres |
| Presto |
| Quickbase |
| QuickBooks Desktop |
| QuickBooks Online |
| QuickBooks POS |
| Raisers Edge NXT |
| Reckon |
| Reckon Accounts Hosted |
| Redis |
| RSS |
| Sage 200 |
| Sage 300 |
| Sage 50 UK |
| Sage Business Cloud Accounting |
| Salesforce Marketing Cloud |
| Salesforce Marketing Cloud Account Engagement |
| Salesloft |
| SAP Business One |
| SAP BusinessObjects BI |
| SAP ByDesign |
| SAP Cloud for Customer |
| SAP Concur |
| SAP Fieldglass |
| SAP HANA XSA |
| SAP SuccessFactors |
| SendGrid |
| Shopify |
| ShipStation |
| SingleStore |
| Snapchat Ads |
| Smartsheet |
| Spark SQL |
| Splunk |
| Streak |
| Stripe |
| SugarCRM |
| SuiteCRM |
| SurveyMonkey |
| SybaseIQ |
| Tableau CRM Analytics |
| Twitter Ads |
| Tally |
| TaxJar |
| Trello |
| TSheets |
| Twilio |
| Veeva Vault |
| Wave Financial |
| WooCommerce |
| WordPress |
| Xero |
| Xero WorkflowMax |
| YouTube Analytics |
| Zoho Books |
| Zoho CRM |
| Zoho Creator |
| Zoho Inventory |
| Zoho Projects |
| Zendesk |
| Zuora |
