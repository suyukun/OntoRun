来源: https://palantir.com/docs/zh/foundry/transforms-r/getting-started/

# 起始

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 起始

本页面解释了在 Foundry 中使用 Palantir R SDK 编写数据变换时可用的结构和配置选项。

## 仓库结构

每个 R 变换通过一个变换规范来定义和配置，定义以 YAML 格式编写并保存在.transforms文件夹中。仓库项目的全部内容将在运行时可用，并可用于变换。

```
.
├── .transforms
|    └── happiness_ranking.yml  # 配置文件，用于定义幸福指数排名的转换规则
|
├── project
|    └── src
|        └── top_10.R           # R语言脚本，可能用于计算或展示前10名的幸福指数数据
└── .Rprofile                     # R的配置文件，用于设置R环境的启动选项或加载特定的库
```

对于从代码工作区发布的R变换，变换规范文件可以通过UI呈现和配置。

## 编写和配置一个简单的R变换

在下面的示例中，我们编写了一个简单的数据变换，该变换读取一个表格数据集，使用R包dplyr应用一个筛选，并生成一个包含筛选结果的输出数据集。

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
library(foundry)
library(dplyr)

# 读取2019年幸福感数据表
happiness_2019 <- datasets.read_table("happiness_2019")

# 过滤出排名前10的国家
top_10 <- happiness_2019 %>% filter(Overall_rank <= 10)

# 将前10名的幸福国家数据写入新表
datasets.write_table(top_10, "top_10_happiest_countries")
```

这里有相应的变换规范文件，包含变换的定义：

将dataset.rid字段替换为您的输入和输出数据集的 RID。请注意，输出数据集必须首先手动创建，因为我们目前不支持在检查期间创建新的输出数据集。

您可以通过在inputs或outputs列表中添加新项来添加其他输入和输出。

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
21
22
inputs:
- alias: "happiness_2019"  # 输入数据集的别名，用于表示2019年幸福指数的数据集
  properties:
    type: "dataset"  # 输入类型为数据集
    dataset:
      rid: "<input dataset rid here>"  # 输入数据集的资源ID
outputs:
- alias: "top_10_happiest_countries"  # 输出数据集的别名，用于表示幸福指数排名前10的国家
  properties:
    type: "dataset"  # 输出类型为数据集
    dataset:
      rid: "<output dataset rid here>"  # 输出数据集的资源ID
- alias: "second-output"  # 另一个输出数据集的别名
  properties:
    type: "dataset"  # 输出类型为数据集
    dataset:
      rid: "<second output dataset rid here>"  # 第二个输出数据集的资源ID
runtime:
  type: "rscript"  # 运行时环境类型为R脚本
  rscript:
    identifier: "R.4.1.x"  # R脚本的版本标识符
    filePath: "project/src/top_10.R"  # R脚本的文件路径
```

这段YAML配置文件定义了一个数据处理任务，其中包括输入和输出数据集的信息以及运行时环境的设置。
运行时配置：

- identifier: 用于识别变换的运行时；例如，R.4.1.x 指的是 R 小版本发布 4.1。
- filePath: 从项目根目录到将要执行的 R 脚本文件的相对文件路径。
## 写入非结构化数据

在此示例中，我们使用ggplot2生成带有线性回归线的图，并将该图保存为 PNG 格式到输出数据集中。

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
library(foundry)
library(ggplot2)

# 读取2019年幸福感数据表
happiness_2019 <- datasets.read_table("happiness_2019")

# 输出图片到指定路径
png("/tmp/model_plot.png")
# 创建一个散点图，X轴为人均GDP，Y轴为总体排名
plot <- ggplot(happiness_2019, aes(GDP_per_capita, Overall_rank)) + geom_point()
# 添加线性回归平滑曲线
plot + stat_smooth(method = "lm", formula = y ~ x, geom = "smooth")
# 关闭图形设备
dev.off()

# 上传生成的图片文件
datasets.upload_files("/tmp/model_plot.png", "happinessGDP_plot")
```

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
inputs:
- alias: "happiness_2019"
  properties:
    type: "dataset"  # 输入数据集类型
    dataset:
      rid: "<input dataset rid here>"  # 输入数据集的资源标识符
outputs:
- alias: "happinessGDP_plot"
  properties:
    type: "dataset"  # 输出数据集类型
    dataset:
      rid: "<output dataset rid here>"  # 输出数据集的资源标识符
runtime:
  type: "rscript"  # 指定运行时类型为 R 脚本
  rscript:
    identifier: "R.4.1.x"  # 使用的 R 版本标识符
    filePath: "project/src/gdp_plot.R"  # R 脚本文件路径
```

## 管理R软件包和环境

默认情况下，R变换库配置有与Posit™ Package Manager和Bioconductor镜像的Artifacts Repositories。我们建议用户使用renv ↗来安装R软件包并管理其变换的R环境。

在代码工作区RStudio®工作台中，renv默认已安装并可用。用户可以在软件包面板中搜索可用软件包，并生成相应的R代码来安装它们。

R变换还支持从renv.lock恢复。如果库中存在renv.lock文件，您可以在变换开始时或在.Rprofile中运行renv.restore()来恢复R环境。

以下示例展示了可以运行的R命令，用于安装R变换所需的软件包，并生成一个renv.lock文件以保存项目库的状态。生成的锁定文件可以提交并用于稍后恢复项目。

```
Copied!1
2
3
4
5
6
# 使用renv包安装dplyr和arrow包
renv::install("dplyr")
renv::install("arrow")

# 创建或更新renv的快照，以确保项目的依赖关系被记录在lock文件中
renv::snapshot()
```

RStudio® 是 Posit™ 的商标。

所有提及的第三方商标（包括标识和图标）仍然是其各自所有者的财产。未暗示任何从属关系或认可。
