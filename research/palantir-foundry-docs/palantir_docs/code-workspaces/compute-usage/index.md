来源: https://palantir.com/docs/zh/foundry/code-workspaces/compute-usage/

# 使用Code Workspaces的计算用量

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 使用Code Workspaces的计算用量

使用Code Workspaces，用户可以通过Foundry的访问控制和数据权限，安全地连接到现有内部系统，并在数据上搭建分析、模型、应用程序或整个工作流。

Code Workspaces启动专用的Foundry计算模块进行执行，在使用时利用Foundry计算秒。

## 定价

Code Workspaces的使用情况被记录为Foundry计算秒（请参阅使用类型）。只要工作区正在起始或活跃，计算秒就会被计量。有几个因素决定了使用的计算秒：

- 虚拟CPU（vCPUs）的数量。
- RAM的gibibits（GiB）。
- 正在使用的工作区。
- GPU的数量和类型。
在支付Foundry使用费用时，默认费率如下：

| 工作区 | GPU类型 | 使用费率 |
| --- | --- | --- |
| VS Code | 无GPU | 0.1 |
| JupyterLab® | 无GPU | 0.5 |
| RStudio® | 无GPU | 0.5 |
| Dash | 无GPU | 0.5 |
| Streamlit | 无GPU | 0.5 |
| Shiny® | 无GPU | 0.5 |
| 任意工作区 | T4 GPU | 1.2 |
| 任意工作区 | A10G GPU | 1.5 |
| 任意工作区 | V100 GPU | 3.0 |

如果您与Palantir签订了企业合同，请在进行计算用量计算之前，联系您的Palantir代表。

```
Copied!1
2
3
4
5
6
7
8
# 计算虚拟CPU的计算秒数
# vcpu_compute_seconds：虚拟CPU的计算总秒数
# vCPUs：虚拟CPU的数量
# GiB_RAM：内存的大小，单位为GiB
# vcpu_usage_rate：虚拟CPU的使用率
# time_active_in_seconds：活跃时间，以秒为单位

vcpu_compute_seconds = max(vCPUs, GiB_RAM / 7.5) * vcpu_usage_rate * time_active_in_seconds
```

以下公式衡量GPU计算秒数：

```
Copied!1
2
3
4
5
# 计算 GPU 使用的总秒数
# GPUs 表示使用的 GPU 数量
# gpu_usage_rate 表示每个 GPU 的使用率
# time_active_in_seconds 表示 GPU 活动的时间（单位为秒）
gpu_compute_seconds = GPUs * gpu_usage_rate * time_active_in_seconds
```

每个代码工作区配有一个Foundry边车，会引入0.25 vCPUs和3 GiB RAM的小开销。

| 工作区 | 计算配置 | 时长 | 产生的使用量 |
| --- | --- | --- | --- |
| VS Code | 1 CPU/8 GiB | 1 小时 | 528 计算秒 |
| VS Code | 1 CPU/8 GiB | 4 小时 | 2112 计算秒 |
| VS Code | 4 CPUs/32 GiB | 1 小时 | 1680 计算秒 |
| JupyterLab® | 1 CPU/8 GiB | 1 小时 | 2640 计算秒 |
| 任意工作区 | 1 T4 GPU | 1 小时 | 4320 计算秒 |
| 任意工作区 | 1 A10G GPU | 1 小时 | 5400 计算秒 |
| 任意工作区 | 1 V100 GPU | 1 小时 | 10800 计算秒 |

## 查看工作区使用情况

CPU、内存和磁盘使用的实时工作区使用指标可用。要查看这些指标，请展开设置侧面板中的工作区使用情况部分。

## 测量Foundry计算

当打开一个代码工作区时，Foundry会为工作区启动一个专用计算会话。会话的状态是STARTING，直到会话可用，变为INITIALIZING，然后是RUNNING。当用户手动停止会话，或者当检测不到用户交互超过自动关闭超时时间时，会话将变为STOPPING，然后是IDLE。Foundry计算秒只在会话为INITIALIZING或RUNNING时使用。

工作区的所有可能状态如下所列。代码工作区使用计算的状态以右箭头（→）表示。

- STARTING：请求了一个新会话
- →INITIALIZING：会话可用并正在配置中
- →RUNNING：会话可用且可用
- STOPPING：会话正在停止
- IDLE：会话已停止
- FAILED：发生错误
- TERMINATING：会话正在永久删除
- NOT STARTED：此工作区没有可用会话
代码工作区以与平台上其他扩展计算相同的方式测量计算秒。查看一般的Foundry计算文档以了解测量方式的描述。

## 使用代码工作区调查Foundry计算使用情况

Foundry代码工作区将所有相关计算归因于文件系统中的工作区资源。您可以随时在资源管理应用中查看所有会话的使用情况。

## 了解代码工作区中Foundry计算使用的驱动因素

代码工作区会话的计算使用量与会话可用的专用计算资源和会话的长度成正比。

要管理会话的硬件大小，请转到设置 > 计算资源。您可以从多种不同的会话大小中进行选择。请参阅下面的截图，以了解如何选择大小并非必填地为您的工作区分配GPU。项目中包含的资源队列决定了可用的GPU。了解更多关于在项目中使用GPU的信息。

长时间运行的会话比短时间运行的会话使用更多的计算。确保调整您的自动关闭时间以与您的工作风格一致，以避免使用不必要的计算。您应该在知道完成时手动停止会话。
