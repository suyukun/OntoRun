来源: https://palantir.com/docs/zh/foundry/sap/uninstall-sap/

# 卸载 Palantir Foundry Connector 2.0 for SAP Applications 或远程代理

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 卸载 Palantir Foundry Connector 2.0 for SAP Applications 或远程代理

在卸载之前，运行SA38，然后运行/PALANTIR/UNINSTALL_CORR程序，以更正 Palantir Foundry Connector 2.0 for SAP Applications（“Connector”）组件（PALANTIR、PALCONN、PALAGENT）的目录条目。

使用SAINT（SAP 附加组件安装工具）卸载 Connector。请注意，根据您的具体情况，PALAGENT可能在 Connector 安装中不可用。

先卸载PALCONN和PALAGENT，或者一起卸载所有组件。如果您尝试单独卸载PALANTIR（Palantir Foundry Foundation）组件，SAINT将会出错，因为PALAGENT和PALCONN依赖于PALANTIR。
