来源: https://palantir.com/docs/zh/foundry/analytics-connectivity/power-bi-setup/

# 设置

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 设置

您现在可以从Power BI®访问Palantir Foundry数据集，并使用它们搭建Power BI®报告和可视化。要在Power BI® Desktop中使用Foundry，您必须在本地计算机上安装Foundry Connector和Foundry ODBC驱动程序。请按照以下指南完成Power BI® Desktop的安装。

### 第1步：验证连接器是否已安装

如果您使用的是2020年6月或更高版本的Power BI®，Palantir Foundry Connector应该已经安装在您的Power BI®版本中。您可以通过打开Power BI®，点击“获取数据”，并在在线服务列表中找到“Palantir Foundry”来验证这一点。

如果您在列表中看到Palantir Foundry，请继续到第2步安装ODBC驱动程序。

如果您在列表中没有看到Palantir Foundry，请联系您的Palantir代表获取下一步指导。您可能需要升级到最新的Power BI®版本。

### 第2步：安装Palantir Foundry ODBC驱动程序

要完成Foundry Power BI®集成的设置，您需要安装一个名为ODBC驱动程序的附加组件。导航到下载页面：ODBC驱动程序下载并安装驱动程序。

如果在安装过程中遇到任何问题，请联系您的Palantir代表。

或者，如果您无法安装ODBC驱动程序，可以按照说明使用基于REST的Palantir Foundry Power BI®连接器，该连接器仅需互联网连接即可将Palantir Foundry连接到Power BI®。请注意，该连接器有更多限制，性能预计不如利用ODBC驱动程序的内置Palantir Foundry连接器。因此，建议尽可能使用内置连接器。

### 第3步：开始搭建报告

现在您已经安装了ODBC驱动程序，您可以按照Power BI®：入门指南中的说明，开始搭建由Foundry数据支持的首个报告。

Power BI®和Power BI®标识是Microsoft公司集团的商标。
