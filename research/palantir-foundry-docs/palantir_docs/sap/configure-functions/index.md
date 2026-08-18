来源: https://palantir.com/docs/zh/foundry/sap/configure-functions/

# 函数

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 函数

## 概述

SAP 函数模块允许用户在 SAP 系统中封装和重用全局函数。函数在中央函数库中管理。SAP 系统包含几个可以调用的预定义函数模块。用户还可以根据业务需求创建自定义函数。 SAP 函数具有输入变量、输出变量、变化变量和异常。变量可以是单个值、字典（称为“结构”）或字典列表（称为“表”）。 函数模块是双向的：它们既可以提取数据，也可以将数据写回 SAP 系统。

## 先决条件

为了提取函数结果，Foundry 技术用户需要以下授权角色（或具有与以下角色相同授权对象的自定义角色）：

- /PALANTIR/SERVICE_USER
- /PALANTIR/CONTENT_FUNCTION_ALL
- 运行特定 SAP 函数所需的任何特定授权角色或对象
## 配置

Connector 只能从至少有一个表格输出参数的函数中提取数据。如果函数返回多个输出参数，用户需要使用paramName参数指定将哪个输出写入 Foundry 数据集。

### 简单示例

此示例同步配置返回BAPI_USER_GETLIST函数的USERLIST参数：

```
Copied!1
2
3
4
type: magritte-sap-source-adapter
sapType: function
obj: BAPI_USER_GETLIST
paramName: USERLIST
```

这个配置文件是用于定义一个SAP源适配器，其中包含以下几个字段：

- type: 表示适配器的类型，这里是magritte-sap-source-adapter，意味着这是一个用于连接SAP系统的适配器。
- sapType: 指定SAP对象的类型，这里是function，表示这是一个SAP函数。
- obj: 指定具体的SAP对象，这里是BAPI_USER_GETLIST，这是一个用于获取用户列表的BAPI（Business Application Programming Interface）。
- paramName: 定义用于接收数据的参数名称，这里是USERLIST。
### 使用输入参数

需要输入参数的函数可以使用inputParams定义输入参数。输入参数可以有不同的类型：

- 单值类型
```
Copied!1
2
inputParams:
  singleValueType_key : 'value' # 这是一个键值对，其中键为singleValueType_key，值为字符串'value'
```

- 结构类型
```
Copied!1
2
inputParams:
  structureType_key : '{"key1": "value1", "key2": "value2"}' # 这是一个JSON格式的字符串，包含两个键值对：key1和key2
```

- 表类型
```
Copied!1
2
3
4
inputParams:
  tableType_key : '[{"key1": "value1", "key2": "value2"},{"key1": "value3", "key2": "value4"}]'
  # 这里定义了一个名为 `tableType_key` 的参数，它的值是一个JSON格式的字符串。
  # 这个JSON字符串表示一个包含多个字典的列表，每个字典有两个键值对：key1 和 key2。
```

在以下示例同步配置中，函数EM_GET_NUMBER_OF_ENTRIES需要一个表类型的输入参数IT_TABLES：

```
Copied!1
2
3
4
5
6
type: magritte-sap-source-adapter
sapType: function
obj: EM_GET_NUMBER_OF_ENTRIES
inputParams:
  IT_TABLES: '[{"TABNAME":"TSTC"}]' # 输入参数，指定表名为TSTC的SAP表
paramName: IT_TABLES # 参数名称
```

此代码片段定义了一个SAP源适配器配置，用于调用SAP函数EM_GET_NUMBER_OF_ENTRIES，并传递一个输入参数IT_TABLES，其中包含了一个表名TSTC。
