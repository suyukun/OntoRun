来源: https://palantir.com/docs/zh/foundry/sap/ingest-hana-views/

# 从SAP导入HANA视图

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 从SAP导入HANA视图

要将数据从HANA视图提取到Foundry，HANA视图需要发布为外部视图。本文档描述了执行该操作的步骤。

## 先决条件

- SAP HANA Studio或SAP HANA Tools for Eclipse
- ABAP Development Tools for Eclipse
请注意，这些工具可以从SAP开发工具 ↗获取。

## 外部视图

外部视图是ABAP字典中定义SAP HANA视图的特殊视图，用于ABAP程序中。

外部视图只能使用ABAP Development Tools (ADT)创建，并且仅当当前数据库是SAP HANA数据库时才能创建。

当外部视图被激活时，会在SAP HANA数据库上创建一个与视图同名的别名，指向SAP HANA视图。外部视图的视图字段名称可以与SAP HANA视图的视图字段名称不同。这将HANA特定的数据类型映射到ABAP字典中的预定义类型。下表列出了当前支持的HANA特定数据类型，并指出它们默认映射到的ABAP字典类型。

| HANA Type | 含义 | 在ABAP字典中的类型 |
| --- | --- | --- |
| SMALLINT | 2字节整数 | INT2 |
| INTEGER | 4字节整数 | INT4 |
| BIGINT | 8字节整数 | INT8 |
| DECIMAL | 打包数字 | DEC |
| SMALLDECIMAL | 打包数字 | DEC |
| FLOAT | 二进制浮点数 | FLTP |
| NVARCHAR | Unicode字符字符串 | CHAR |
| VARBINARY | 字节字符串 | RAW |
| BLOB | 字节字符串 | RAWSTRING |
| NCLOB | Unicode字符字符串 | STRING |

外部视图可以使用SAP GUI基础的ABAP Workbench中的ABAP字典工具显示，但不能编辑。

### 在SAP HANA视图上创建外部视图

- 创建新的ABAP存储库Object并选择Dictionary View。
- 在下一个屏幕中，选择External View选项并为您的外部视图命名和描述。
- 接下来，您可以验证从SAP HANA视图到外部视图的列映射。
- 您可以通过使用SE16事务代码显示内容来测试您的外部视图。
### 在Foundry中导入HANA视图

Foundry可以通过sync导入您创建的外部视图。

HANA视图尚未在同步UI的支持SAP Object类型列表中。要配置它们，请导航到高级视图并按如下方式定义您的同步：

```
Copied!1
2
3
type: magritte-sap-source-adapter
sapType: hanaview
obj: <NAME_OF_VIEW>  # 在此处替换为实际的视图名称
```

此代码定义了一个SAP源适配器配置，sapType指定了适配器的类型为HANA视图。obj字段应该被替换为实际的HANA视图名称。
