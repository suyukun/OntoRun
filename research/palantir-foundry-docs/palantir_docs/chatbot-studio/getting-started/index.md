来源: https://palantir.com/docs/zh/foundry/chatbot-studio/getting-started/

# 入门指南

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 入门指南

请联系您的 Palantir 代表以安装此测试版产品。

本指南演示了如何访问 AIP Chatbot Studio，介绍了 AIP Chatbot Studio 界面，描述了如何设置一个基本的 AIP Agent，并部署和监控该 AIP Agent 在生产中的运行。

## 访问 AIP Chatbot Studio

AIP Chatbot Studio 可以通过平台的工作区导航栏访问，或者使用快捷搜索键CMD + J（macOS）或CTRL + J（Windows）。或者，您可以通过选择+ New然后选择AIP Agent从您的文件中创建一个新的 AIP Agent，如下图所示。

打开 AIP Chatbot Studio 后，您可以创建一个新的 AIP Agent 文件。

## 创建一个 AIP Agent

AIP Agents 是 Palantir 文件系统资源，具有细粒度的访问控制，可以像任何其他文件系统资源一样创建，如上图所示，在前一节中。

您还可以在 AIP Chatbot Studio 中选择New AIP Agent选项。

或者，在 AIP Threads 中创建一个 AIP Agent。

## 设置 AIP Agent

以下描述了“标准代理”的设置，与"AIP Assist Agent"不同。

为您的 AIP Agent 添加名称、描述和一张照片作为头像。这使您可以将代理品牌化以适应您的应用程序上下文。如果没有提供头像，将使用灰色机器人图标作为默认。

根据您是完成向导中的设置还是跳转到配置面板，您的创建工作流程会有所不同。无论哪种方式，您都需要配置将装备给您的 AIP Agent 的企业特定信息和工具，如以下章节所述。

### 信息和工具的类型

- 检索上下文：简单快速，推荐用于大多数应用案例。
- 参数：用于在Workshop中为代理提供上下文。
- 工具：用于复杂和执行操作的代理。首次词元时间较慢time to first token。
这些配置使得 LLM 对您的企业、工作流程和任务变得有用。

### 选择大型语言模型 (LLM)

可用给您的模型是在您的堆栈上启用的模型的子集。

### 修改系统提示

系统提示应该概述 AIP Agent 在当前应用程序上下文中的函数。通过按下键盘上的/，您可以引用已配置的工具和参数，并指导 AIP Agent 如何协调它们的使用。确保描述底层的业务逻辑以及在上下文中使用正确工具的适当情况。

### 设置温度

用户可以修改模型温度以确定在聚焦、确定性输出（默认值0）和随机输出（最大值1）之间的平衡。

### 添加对话启动器

您还可以设置输入占位符和建议提示，以根据您预期的工作流程自定义代理。

### 保存、查看和发布 AIP Agent

配置好您的 AIP Agent 后，可以使用界面右上角的保存来保存您的进度。要从终端用户交互的角度查看您的 AIP Agent 的运行效果，请使用查看并选择所需的版本。

当您准备好部署您的 AIP Agent 时，选择✅ 发布以使您的代理在生产环境中可用。您可以通过监控和使用选项卡监控代理的性能和使用情况，在那里您可以看到指标和用户反馈。

在AIP Threads、Workshop、查看模式或（即将推出的）OSDK 中使用。

### 跟踪 AIP Agent 的反馈和使用情况

在 AIP Chatbot Studio 的监控和使用选项卡中查看您的 AIP Agent 的使用情况，并记录反馈数据。反馈数据来自用户在对话中给代理的点赞或点踩。
