来源: https://palantir.com/docs/zh/foundry/sap/install-sap-remote-agent-620/

# 为 4.6C/620/640 安装远程代理

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 为 4.6C/620/640 安装远程代理

Palantir Foundry Connector 2.0 以 SAP 请求的形式提供的远程代理，用于 4.6C/620/640，通过 SAP 传输管理系统进行传输。您可以按照以下步骤将请求导入 SAP 系统。

## 安装步骤

- 下载安装包。
- 将 Connector 远程代理 4.6c, 4.70 (620/640) 解压到一个文件夹中。如果 SAP 系统是 Unicode，则应使用 Unicode 请求；否则应使用非 Unicode 请求。文件如下（请求编号可能因所安装版本而异）：
- Connector 文件K900xxx.C46R900xxx.C46
- K900xxx.C46
- R900xxx.C46
- 远程代理文件K900xxx.C46R900xxx.C46
- K900xxx.C46
- R900xxx.C46
- 以 "R" 开头的文件名是数据文件；以 "K" 开头的文件名是协同文件。将文件复制到 SAP 应用服务器上对应的文件夹中：
```
/usr/sap/trans/cofiles
    /usr/sap/trans/data
```

这些路径指向的是SAP系统中的传输目录：

- /usr/sap/trans/cofiles：存储传输请求的控制文件。
- /usr/sap/trans/data：存储传输请求的数据文件。
- 使用被授权使用 STMS (SAP 传输管理系统) 的用户登录 SAP 系统。
- 运行STMS事务。
- 选择传输的目标系统。
- 从工具栏菜单中选择Extras>Other Requests>Add，然后输入请求编号。（请求编号如下：C46K9000xx。前 3 位是请求文件扩展名；剩余数字是提取文件中看到的 K 文件名。）
- 请求列在导入队列中。现在通过点击请求编号选择请求，然后在工具栏上选择Import。
- 转到Options选项卡，选择Leave Transport Request in Queue for Later Import和Ignore Invalid Component Version。然后开始传输。
- 通过点击工具栏上的日志按钮检查导入日志。
- 检查是否有任何错误信息。成功导入应在没有错误的情况下完成。
- 转到PFCG事务代码并生成以下角色的授权配置文件：/PALAGT47/SERVICE_USER/PALAGT47/CONTENT_RTABLE_ALL
- /PALAGT47/SERVICE_USER
- /PALAGT47/CONTENT_RTABLE_ALL
## 配置

Connector 和 Connector 远程代理通过 SAP 远程函数调用 (RFCs) 进行通信。因此，需要两个 RFC 连接：一个从 Connector 到远程代理，另一个从远程代理到 Connector。下一节详细介绍如何创建这些 RFC 连接。

### RFC 配置

RFC 配置需要四个步骤：

- 创建到 SAP 系统的 RFC 连接。
- 创建从 Connector 到远程 SAP 系统 (SOURCE) 的 RFC。
- 创建从远程 SAP 系统到 Connector (TARGET) 的 RFC。
- 通过网页浏览器测试 Connector 远程代理。
### 创建到源/目标系统的 RFC 目标连接

在本节中，需要两个 RFC 连接：一个从 Connector 到远程代理，另一个从远程代理到 Connector。查看创建 RFC 连接指南。

为从远程 SAP 系统到 Connector 的目标 RFC 定义重复相同的步骤。可以将其命名为SAP\_TARGET，而不是SAP\_SOURCE。（这些名称可以自由定义。）

#### 配置远程代理并注册 Connector

- 登录主 Connector 系统。
- 运行事务/n/PALANTIR/PARAM_A1。
- 输入以下参数值：Agent ID: AGENT 标识符（也称为 CONTEXT）Is 4.7 or older: AGENT 版本标志Agent Desc: AGENT 描述（供参考使用）
- Agent ID: AGENT 标识符（也称为 CONTEXT）
- Is 4.7 or older: AGENT 版本标志
- Agent Desc: AGENT 描述（供参考使用）
- 运行事务/n/PALANTIR/PARAM_A2并输入以下参数：Agent ID: AGENT ID（如上一步定义）Param ID: PARAM ID（参数分类）Param Name: 参数名称（AGENT 使用）Param Value: 参数值（AGENT 使用）
- Agent ID: AGENT ID（如上一步定义）
- Param ID: PARAM ID（参数分类）
- Param Name: 参数名称（AGENT 使用）
- Param Value: 参数值（AGENT 使用）
| Param Id | Param Name | Param Values | Description |
| --- | --- | --- | --- |
| RFC | SOURCE |  | 从 Connector 到远程 SAP 系统的 RFC 连接。 |
| RFC | TARGET |  | 从远程 SAP 系统到 Connector 的 RFC 连接。 |
| SYSTEM | CPU_CHECK | TRUE/FALSE | 启用或禁用 CPU 检查。 |
| SYSTEM | MEMORY_CHECK | TRUE/FALSE | 启用或禁用内存检查。 |
| SYSTEM | RESOURCE_CHECK | TRUE/FALSE | 启用或禁用资源检查。如果为FALSE，则禁用所有检查；如果为 TRUE，则检查其他参数 (CPU_CHECK和MEMORY_CHECK)。 |
| SYSTEM | CONTINUOUS_RESOURCE_CHECK | TRUE/FALSE | 启用所有请求（初始化和所有分页请求）的资源检查。如果为FALSE，资源检查仅针对初始化请求进行。 |
| SYSTEM | PROCESS_CHECK | TRUE/FALSE | 启用对允许的最小工作进程数量的检查；与PROCESS_MIN_BG和PROCESS_MIN_DIA结合使用。 |
| SYSTEM_THRESHOLD | PROCESS_MIN_BG | 数字 | SAP 应用服务器上可用的后台进程的最低要求数量。 |
| SYSTEM_THRESHOLD | PROCESS_MIN_DIA | 数字 | SAP 应用服务器上可用的对话进程的最低要求数量。 |

## 限制

Connector 远程代理对于 4.6C/620/640 具有以下限制：

- 仅支持table接口。
- 仅支持single增量类型。
- 在 Foundry 的数据连接源配置中应设置useTsvFormat:true。因此，即使在 Foundry 中已经有可用的主 Connector 实例源，也推荐为 4.6C/620/640 提供单独的源。