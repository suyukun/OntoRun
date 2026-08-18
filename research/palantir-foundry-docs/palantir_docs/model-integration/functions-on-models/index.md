来源: https://palantir.com/docs/zh/foundry/model-integration/functions-on-models/

# 模型上的函数

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 模型上的函数

模型上的函数允许您通过编写在其运行时调用模型的函数，将模型在Ontology的上下文中实现操作化。模型可以通过实时部署提供，并导入到函数库中用于代码中使用。

一旦函数发布，您可以在Foundry中已使用函数的任何地方使用您的模型，包括Workshop、Slate、操作和更多。

下面是一个调用实时部署的函数的简化示例，它接受一个输入Double[]并返回一个输出Double[]：

```
Copied!1
2
3
4
5
6
7
8
9
10
import { Function, Double } from "@foundry/functions-api";
import { ModelDeployment } from "@foundry/models-api/deployments";

@Function()
public async predictValues(inputs: Double[]): Promise<Double[]> {
    // 使用 ModelDeployment 的 transform 方法对输入数据进行预测
    const modelOutput = await ModelDeployment.transform(inputs);
    // 返回预测结果
    return modelOutput.outputValues;
}
```

代码说明：

- @Function()注解用于标识predictValues是一个函数。
- inputs: Double[]表示输入参数是一个Double类型的数组。
- Promise<Double[]>表示该函数返回一个Double类型的数组的 Promise 对象。
- ModelDeployment.transform(inputs)异步调用模型部署中的 transform 方法对输入进行预测。了解更多关于模型上的函数，并了解它们如何被用于在创建端到端语义搜索工作流。