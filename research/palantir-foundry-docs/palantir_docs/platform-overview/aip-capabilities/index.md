来源: https://palantir.com/docs/zh/foundry/platform-overview/aip-capabilities/

# AIP功能

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# AIP功能

Palantir平台上的应用程序配备了AIP驱动的功能。本页面描述了其中的一些功能。

AIP的AI功能可以分为三类：

- AIP Assist:一个由LLM驱动的支持工具，旨在帮助用户导航、理解并利用Palantir平台生成价值。用户可以用自然语言向AIP Assist提问，并实时获得查询帮助。
- 平台应用中的AIP助手功能:本地的LLM支持功能，旨在帮助终端用户在Palantir平台上执行常规工作流程。这些功能高度针对性地利用平台知识来加速用户的日常操作。
- 自定义工作流程的AIP功能:一组允许开发人员搭建自己的LLM支持工作流程或应用程序的功能。这些是为开发人员或数据科学家构建的开放式功能。
了解如何在平台中启用AIP功能。

了解AIP核心功能与自定义工作流程AIP功能的区别。

## AIP Assist侧边栏

AIP Assist侧边栏具备上下文感知功能，可以通过自然语言提示为用户提供支持。您可以从工作区导航栏中打开AIP Assist，或使用键盘快捷键（Cmd + Shift + U（macOS）或Ctrl + Shift + U（Windows））访问它。AIP Assist将显示在一个面板中，如下图所示。

了解更多关于AIP Assist侧边栏的信息。

## 平台应用中的AIP功能

AIP功能已嵌入核心应用程序中，帮助用户加速工作流程并在平台中解锁更多价值。以下是一些精选的AIP功能示例，并不是详尽列表。AIP的最新更新可以在文档的公告部分找到。

### Pipeline Builder

在Pipeline Builder中使用AIP，以帮助您更好地理解、搭建和管理您的管道。Pipeline Builder有一组核心的Assist功能和用于自定义工作流程的额外AIP功能。

Pipeline Builder中的核心Assist功能示例如下：

解释:了解管道开发步骤，并建议相关的名称和描述。

正则表达式助手:生成定制的正则表达式，适用于所有技能水平。

变换助手:创建和编辑正则表达式，并轻松将字符串转换为特定的时间戳格式。

此外，具有权限的情况下，您可以在Pipeline Builder中使用自定义工作流程的AIP功能，例如：

使用LLM节点，提供了一种方便的方法，在大规模数据上执行大语言模型（LLM）。提供了五个预先设计的模板，适合初学者使用LLM，利用经验丰富的提示工程师的专业知识。

您还可以在整个数据集上运行模型之前，通过几行输入数据集运行试验，以迭代您的提示。

### Notepad

AIP还为Notepad带来了LLM驱动的功能，您可以使用AIP自动拼写检查、缩短、修改或翻译文本，而不会影响文档的现有格式。

### Scheduler

您可以在Scheduler应用程序中使用AIP，在创建具有特定时间触发器的数据集搭建计划时生成计划配置。在新计划视图侧边栏中输入计划触发器提示，以生成复杂触发器的正确cron格式。

### AIP Threads [Beta]

AIP Threads使用户能够利用LLM的强大功能完成各种任务和临时分析。无需设置或技术专长即可与文档（例如PDF）和AIP Agents（配备企业特定信息和工具的互动助手）进行交互。开始时，您只需将文档拖放到界面中，选择您有权限访问的先前上传的文档，或选择您和您的组织创建的AIP Agent。

## 自定义工作流程的AIP功能

自定义工作流程的AIP功能允许开发人员和搭建者在Palantir平台中搭建自己的LLM支持工作流程或应用程序。这些功能包括但不限于AIP Logic、Pipeline Builder中的“使用LLM”节点和文本到嵌入、AIP Automate、AIP Chatbot Studio和AIP Workshop微件。这些功能本地支持大语言模型选项。

Palantir提供的LLM也可用于核心Foundry功能中，如函数、变换和通过Code Workspaces的Jupyter®笔记本。

此外，现有的Palantir功能模型集成允许用户连接自定义大语言模型，并从零独立搭建应用案例。

平台管理员可以通过Control Panel中的AIP设置管理这些功能的使用。

## 支持的LLM

Palantir平台提供对多种LLM（大语言模型）和文本嵌入模型的支持。

### Palantir提供的大语言模型（LLM）

我们提供了一组LLM，用于自定义工作流程的AIP功能，不同注册中的LLM选择和可用性有所不同。有关可用模型的详细信息如下：

- GPT-4o ↗
- GPT-4 Turbo ↗
- GPT-4 Turbo with Vision ↗
- GPT-4 ↗
- GPT-4 (32k) ↗
- GPT-3.5 ↗
- GPT-3.5 16k ↗
- Llama3 8B Instruct ↗
- Llama3 70B Instruct ↗
- Llama 3.1 8B Instruct ↗
- Llama 3.1 70B Instruct ↗
- Llama2 13B Chat ↗
- Llama2 70B Chat ↗
- Mixtral 8x7B Instruct ↗
- Mistral 7B Instruct ↗
- Anthropic Claude_2 ↗
- Anthropic Claude_Instant ↗
- Anthropic Claude 3 Sonnet ↗
- Anthropic Claude 3.5 Sonnet ↗
- Anthropic Claude 3 Haiku ↗
要了解LLM如何安全地处理用户提示，请通过选择Palantir AIP常见问题，查看常见问题：Palantir利用第三方托管LLM的AIP的安全性和隐私 ↗。

### 文本嵌入模型

我们也以相同的方式提供了一组文本嵌入模型。

- Text embedding ada-002 ↗
- Text embedding 3 small ↗
- Text embedding 3 large ↗
- Instructor Large ↗
- BGE Base ↗
了解如何配置您的注册中可用的LLM。

注意：AIP功能的可用性可能会发生变化，并且可能因客户而异。

Jupyter®、JupyterLab®和Jupyter®徽标是NumFOCUS的商标或注册商标。

“OpenAI”名称和“GPT”品牌属于OpenAI。

所有引用的第三方商标（包括徽标和图标）仍然是其各自所有者的财产。未暗示任何附属关系或认可。
