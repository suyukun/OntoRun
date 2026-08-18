来源: https://palantir.com/docs/zh/foundry/compute-modules/authoring-foundry/

# 在 Foundry 中创作计算模块

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 在 Foundry 中创作计算模块

计算模块功能处于测试阶段，可能无法在所有注册中使用。如果您的注册中提供了计算模块，请导航至计算模块应用以获取最新文档。

要在 Foundry 中编写用于计算模块的代码，首先导航至您希望保存存储库的项目。然后，选择新建并选择代码存储库。点击计算模块，选择您希望使用的语言，以模板启动您的存储库。最后，选择初始化存储库。

对于 Python，app.py将是最相关的文件。您在此文件中定义的每个函数在部署计算模块时将被挂载为端点。

您不得更改app.py文件的名称或位置。文件根目录中定义的任何函数将通过其大小写敏感的名称进行“调用”。您可以在此文件中编写所有代码，或将其分散在多个文件中。如果确实创建了多个文件，您必须仅使用相对导入。例如，如果您在与app.py相同的目录中创建了另一个名为myExampleLib.py的文件，并带有一个名为ExampleClass的类，您可以如下方式将其导入app.py：

```
Copied!1
2
from .myExampleLib import ExampleClass # 这将有效，'.'表示相对路径
from myExampleLib import ExampleClass # 这将无效
```

最终要求是Python函数必须返回一个可进行JSON序列化的Object。

在app.py文件中编写您的新函数，选择提交以保存，当您准备好后，选择标记版本。标记将触发对您的存储库的检查，这将搭建一个新的Docker镜像，您可以在计算模块中部署该镜像。一旦检查通过，您将拥有一个可以在计算模块中使用的Docker镜像。

有关详细指南，请参阅部署计算模块的文档。

## 依赖

您可以通过调整meta.yaml文件来管理依赖，例如在运行部分添加包名称和版本（固定版本将提高搭建性能）。默认情况下，这些存储库有external-conda-forge作为支持存储库。如果您需要来自不同制品存储库的包，可以随意添加一个。

## 搭建配置

隐藏文件gradle.properties允许您管理一些搭建配置。以下是一些重要字段：

```
Copied!1
2
userImageName = myimage  # 用户图像名称
baseImageTag = xyz       # 基础图像标签
```

userImageName字段将决定此仓库在搭建时生成的镜像名称。如果您不在两次搭建之间手动更改标签，先前版本将被覆盖。如果发生这种情况，请重新启动您的搭建以快速应用您的更新代码；否则，代码将在大约24小时内更新。

baseImageTag控制将在搭建时使用的Conda基础镜像的版本。版本低于0.15.0需要选择No Runtime，版本>=0.15.0需要选择COMPUTE_MODULE_RUNTIME_V1。通常，安全更改此版本。
