# Palantir 文档精读摘要（A 栏：机制事实）

> 编制：Rose ｜ 日期：2026-08-21 ｜ 来源：Palantir Foundry 官方中文文档

## chatbot-studio 模块
- 定位：AIP Chatbot Studio = 搭建互动助手（AIP Agents）的产品，借 Ontology/文档/LLM 获取和更新参数；可内嵌 Workshop。
- 对话流：信息与工具三类 = 检索上下文（RAG，简单快速）/参数（Workshop 提供上下文）/工具（复杂执行，TTFT 慢）；LLM 选择；温度默认 0；对话启动器；发布后监控反馈。
- 提示策略：单次完成（TTFT 快）vs 思维链（配置工具后自动采用，多次迭代）。
- 检索上下文（RAG）：每次收到新消息**确定性**取数据源信息（grounding）；Ontology 上下文要求对象集仅一种类型且含向量属性才能语义搜索；最大对象数 1-25（默认 5）、1-5 内容属性。
- 工具五种：操作（Ontology 编辑）/Object 查询（限定对象类型+属性，更词元高效，支持筛选聚合链接遍历）/函数/语义搜索（思维链时才触发）/请求澄清。
- 防幻觉：检索上下文确定性注入 + "LLM 只能访问特别提供的信息" + 超上下文报错 + 参数读写模式显式声明 + 温度默认 0 + 请求澄清工具。
- 反模式：官方不推荐对话界面用于"重复性/定义明确/需精确性"场景；复杂确定性逻辑放 Functions，Agent 只管对话状态。
- 来源：research/palantir_foundry_docs/palantir_docs/chatbot-studio/（6 文件全读）
