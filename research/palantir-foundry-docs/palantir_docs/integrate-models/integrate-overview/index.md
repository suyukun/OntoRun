来源: https://palantir.com/docs/zh/foundry/integrate-models/integrate-overview/

# 模型

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 模型

Palantir提供了一个通用接口，以整合来自不同来源的模型。模型可以从以下来源进行整合：

- 在Palantir中训练的模型。
- 在Palantir外部训练并作为非结构化数据集上传的模型文件。
- 在Palantir外部容器化并推送到Foundry Docker注册表的模型。
- 在Palantir外部训练和托管的模型。
所有模型都可以通过建模目标应用程序进行生产化并连接到运营应用程序。

## 模型适配器

Palantir中的模型由两个组件组成：

- 模型工件：保存已训练模型的模型文件、参数、权重、容器或凭据。
- 模型适配器：描述Foundry如何与模型工件交互以加载、初始化和执行模型推理的逻辑和环境依赖项。