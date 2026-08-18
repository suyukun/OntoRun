来源: https://palantir.com/docs/zh/foundry/analytics-connectivity/tableau-setup/

# 设置

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 设置

您可以从Tableau访问Palantir Foundry数据集，并使用它们搭建交互式仪表盘。要在Tableau Desktop中使用Foundry，您必须在计算机上安装Foundry数据集JDBC驱动程序和Tableau连接器文件。

请按照以下指南完成此安装。

## 步骤1：安装Foundry数据集的JDBC驱动程序

导航到下载：Foundry数据集JDBC驱动程序，下载.jar文件，并将其放置在操作系统的正确目录中。如该目录不存在，请创建。

- 如果使用Windows：C:\Program Files\Tableau\Drivers
- 如果使用Mac：~/Library/Tableau/Drivers
## 步骤2：安装Tableau连接器文件

导航到下载：Foundry数据集Tableau连接器，下载.taco文件，并将其放置在计算机上的My Tableau Repository\Connectors目录中。

- 如果使用Windows：C:\Users\[Windows User]\Documents\My Tableau Repository\Connectors
- 如果使用Mac：~/Documents/My Tableau Repository/Connectors
如果您无法在上述位置找到My Tableau Repository文件夹，或者在打开Tableau后无法看到Foundry by Palantir连接器，则您的连接器文件夹位于其他位置。打开Tableau并选择文件->存储库位置以找到正确的位置。您不应自己创建文件夹。

## 步骤3：开始搭建交互式仪表盘

现在您已经安装了JDBC驱动程序和Tableau连接器文件，您可以按照Tableau：入门指南中的说明，开始搭建由Foundry数据支持的第一个交互式仪表盘。
