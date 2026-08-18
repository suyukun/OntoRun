来源: https://palantir.com/docs/zh/foundry/notepad/widgets-quiver-dashboard/

# Quiver仪表盘

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Quiver仪表盘

在Notepad文档中嵌入Quiver仪表盘允许您以PDF格式导出仪表盘或打印它。
嵌入仪表盘还允许您将数据锁定在某个时间点。

您可以通过点击+ 微件在Notepad文档中嵌入Quiver仪表盘。

## 微件属性

- 仪表盘：选择您想要嵌入的仪表盘。
- 版本：选择仪表盘的版本，或切换自动更新以始终显示最新版本。
## 模板配置

- 仪表盘输入：如果您的仪表盘定义了输入，输入将在此部分显示。您可以使用下表将输入映射到Notepad文档中的变量。
| Quiver输入类型 | Notepad输入类型 |
| --- | --- |
| Boolean | 字符串 |
| Number | Number |
| 字符串 | 字符串 |
| Time | Timestamp |
| Time Range | 字符串,ISO format - ISO format |
| Time Series | 不支持 |
| Object | Object |
| 对象集 | 对象集 |
| 字符串列表 | 字符串:["option_1","option_2"] |

在下面的示例中，仪表盘有一个在编辑器中直接配置的对象输入。
