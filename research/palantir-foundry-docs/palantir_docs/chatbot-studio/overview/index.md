来源: https://palantir.com/docs/zh/foundry/chatbot-studio/overview/

# 概述

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 概述

请联系您的Palantir代表以安装此测试版产品。

AIP Chatbot Studio允许用户搭建互动助手，称为AIP Agents，这些助手配备了企业特定的信息和工具，可以在平台内部和通过OSDK（即将推出）外部部署。

AIP Chatbot Studio 提供了一个自然语言界面，以利用Ontology、文档和LLM通过AIP Agents来获取和更新参数（例如Ontology对象或文本字符串）。在以下示例中，下图展示了一个由LLM驱动的AIP Agent，它使用一个参数来获取筛选的客户支持记录对象集作为上下文，以回答用户关于当前产品问题的问题。

上述AIP Agent可以部署在Workshop应用程序中。

AIP Chatbot Studio 构建在与Palantir平台其他部分相同的严格安全模型之上。这些平台安全控制仅授予LLM完成任务所需的访问权限。

## 适用性

要了解AIP Chatbot Studio是否是您工作流的最佳Palantir平台工具，请考虑以下问题：

- “我如何希望将我的工作流进行操作化？”，以及
- “我如何使用AI自动化工作流，以从非结构化数据中获取洞见？”
如果您的工作流不需要“对话式”界面，我们建议您使用AIP Logic或Workshop中的AIP Generated Content微件。

不推荐使用对话界面的示例包括：

- 具有重复性、定义明确的任务的工作流
- 需要速度和精确性的工作流；对话是一种固有的开放式沟通方法，可能缺乏您直接设置参数的界面的具体性
如果对话界面更为适用（通常用于临时或人力增强的知识检索任务），请考虑以下逐级增加复杂性的层次。

- 临时检索增强生成（RAG）新接触AIP或大型语言模型（LLM）？请从AIP Threads开始，以更好地了解LLM如何帮助您提高生产力。通过拖放文档来进行临时文档分析，以获取相关的LLM驱动的答案。
临时检索增强生成（RAG）

新接触AIP或大型语言模型（LLM）？请从AIP Threads开始，以更好地了解LLM如何帮助您提高生产力。通过拖放文档来进行临时文档分析，以获取相关的LLM驱动的答案。

- 可共享的RAG / 基础代理将AIP Threads的临时线程配置升级为AIP Agents，以提高可重用性，并在AIP Chatbot Studio中提供细粒度的权限和配置选项。您还可以在AIP Chatbot Studio中创建基于Ontology的RAG风格的基础代理。您可以在AIP Threads或OSDK（即将推出）中使用AIP Agents。
可共享的RAG / 基础代理

将AIP Threads的临时线程配置升级为AIP Agents，以提高可重用性，并在AIP Chatbot Studio中提供细粒度的权限和配置选项。您还可以在AIP Chatbot Studio中创建基于Ontology的RAG风格的基础代理。您可以在AIP Threads或OSDK（即将推出）中使用AIP Agents。

- 更大工作流的一部分将AIP Agents与使用AIP Agent Widget或OSDK（即将推出）的应用程序特定上下文集成到Workshop应用程序中，使用例如对象集变量这样的参数。
更大工作流的一部分

将AIP Agents与使用AIP Agent Widget或OSDK（即将推出）的应用程序特定上下文集成到Workshop应用程序中，使用例如对象集变量这样的参数。

- 复杂信息检索和操作（即将推出）在AIP Logic或Functions-on-Objects中定义更复杂或确定性的逻辑，并让AIP Agent管理对话状态。使用AIP Agent Widget或OSDK（即将推出）。
复杂信息检索和操作（即将推出）

在AIP Logic或Functions-on-Objects中定义更复杂或确定性的逻辑，并让AIP Agent管理对话状态。使用AIP Agent Widget或OSDK（即将推出）。

了解更多关于AIP Chatbot Studio的核心概念或开始搭建AIP Agent。
