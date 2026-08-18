来源: https://palantir.com/docs/zh/foundry/integrate-models/upload-image-container-model/

# 以容器模型上传图像

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 以容器模型上传图像

本页面指导您完成使用容器支持的模型上传图像的过程。在此工作流程中，您将创建一个模型，将图像推送到模型资源，并配置模型版本。

## 1. 创建模型

要创建一个容器支持的模型，首先创建一个将要推送图像的资源。此资源将控制模型权限；在此资源上具有只读权限的用户将能够从Foundry中提取图像。

通过导航到任何建模目标并选择+添加模型，然后选择导入容器化模型来创建新模型。

## 2. 向模型推送图像

您推送的图像必须符合Foundry的图像要求。

在Palantir中创建模型资源后，按照说明将图像推送到资产中。

选择生成词元，然后复制默认命令块并编辑它们，将example-package:<TAG>替换为您本地Docker存储库中存在的图像名称和标签（或摘要）。请注意，标签不允许为“latest”，具体要求参见图像要求。执行这些命令将把相关图像推送到模型中，任何具有只读权限的人都可以访问它。

一旦图像成功推送并在容器图像列表中可用，选择创建模型版本以开始配置版本。为此，您必须首先创建一个使用模型适配器库模板创建的容器模型适配器。

根据图像的大小，您的容器图像可能需要几分钟才能在模型中可用。

在发布之前迭代您的模型适配器实现，使用sidecar装饰器测试逻辑如何与模型中已经存在的容器一起工作。按照sidecar变换装饰器文档中的步骤，使用您刚创建的模型作为支持Artifacts存储库，创建一个启用装饰器的新变换存储库。然后，在变换存储库中定义一个本地Python文件，实现适配器并按如下所示手动实例化它：

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
11
12
13
14
15
16
17
18
19
20
from transforms.api import transform, Input, Output
from transforms.sidecar import sidecar, Volume
# 假设您在`myproject`文件夹下创建了一个Python类testAdapter.py，并定义了一个实现palantir_models的ModelAdapter类的TestModelAdapter类。
from myproject.testAdapter import TestModelAdapter
import palantir_models.transforms

# 使用sidecar装饰器指定镜像和共享卷
@sidecar(image='image-name', tag='1.0.0', volumes=[Volume("shared")])
@transform(
    output=Output("ri.foundry.main.dataset.<RID>"),
    source_df=Input("ri.foundry.main.dataset.<RID>"),
)
def compute(source_df, output):
    # 实例化TestModelAdapter类，传入共享卷路径和监听的端口
    testingEntrypoint = TestModelAdapter(
       "/opt/palantir/sidecars/shared-volumes/shared",
       # 注意，这里的端口应该是您的镜像正在监听的端口。
       "localhost:PORT")
    # 使用transform_write方法将输入数据集转换并写入输出数据集
    testingEntrypoint.transform_write(source_df, output)
```

以上代码使用了Palantir Foundry的变换API，并假设存在一个自定义的模型适配器TestModelAdapter。这个适配器用来将数据从输入数据集转换并写入输出数据集。代码中的sidecar装饰器用于指定使用的Docker镜像、版本标签以及共享卷。

## 3. 配置模型版本

在配置模型版本页面上，选择一个或多个容器镜像以包含在特定的模型版本中。选择下一步以继续进行模型版本配置。

在配置模型对话框的模型详情页面上，配置要进行的语义版本更改类型。然后，添加一个非必填描述和配置文件，并选择您创建的适配器。在模型适配器配置部分中选择您的模型适配器库，选择模型适配器下拉菜单将填充库中定义的任何有效适配器的最新版本。

最后，为每个镜像配置任何非必填的运行时信息，包括内存约束、参数、任何环境变量或新的执行命令。请注意，如果您的适配器使用请求库，则指定镜像监听的端口至关重要。您可以为模型版本选择的每个镜像配置运行时信息。

模型可以配置为生成遥测日志。如果您的容器支持遥测，您可以在下面截图中显示的步骤中为模型版本启用它。

## 4. 查看模型版本

一旦模型版本创建，其元数据将显示在模型页面的模型概览标签中。在那里，使用左侧面板查看和导航到过去的版本。

在此页面中，您可以使用右上角的+图标或操作下拉菜单提交到建模目标。您还可以将模型用作Python变换的输入。请注意，如果模型由容器支持，您需要在 ModelInput 类中指定第二个非必填参数，选择一个版本 RID 以用于变换。您还必须在您的变换库中添加对模型适配器的依赖。示例如下：

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
11
12
from transforms.api import transform, Input, Output
from palantir_models.transforms import ModelInput

@transform(
    output=Output("/path/to/output/output_dataset"),  # 输出数据集路径
    model=ModelInput(
        "ri.models.main.model.<RID>",  # 模型资源ID
        "ri.models.main.model-version.<RID>"),  # 模型版本资源ID
    source_df=Input("/path/to/input/input_dataset"),  # 输入数据集路径
)
def compute(model, source_df, output):
    model.transform_write(source_df, output)  # 使用模型对输入数据进行转换并写入输出数据集
```
