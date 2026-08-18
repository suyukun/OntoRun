来源: https://palantir.com/docs/zh/foundry/transforms-python/project-structure/

# 项目结构

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 项目结构

## 默认引导存储库

以下是引导变换Python存储库的标准结构：

```
transforms-python
├── conda_recipe
│   └── meta.yaml
└── src
    ├── myproject
    │   ├── __init__.py        # 包初始化文件
    │   ├── datasets
    │   │   ├── __init__.py    # 数据集模块初始化文件
    │   │   └── examples.py    # 数据集示例代码文件
    │   └── pipeline.py        # 数据处理流水线代码文件
    ├── setup.cfg              # 配置文件，通常用于定义项目的构建和元数据
    └── setup.py               # 安装脚本，用于定义如何构建和安装项目
```

在代码仓库的文件资源管理器选项卡中，通过进入设置齿轮并选择显示隐藏文件和文件夹，可以查看仓库中的其他文件。在几乎所有情况下，这些隐藏文件不应被编辑；Palantir不支持对这些隐藏文件进行自定义更改的仓库。

您可以在下面了解更多有关以下文件的信息：

- pipeline.py
- setup.py
- examples.py
- meta.yaml
在继续阅读之前，请确保您已阅读入门指南。此外，本页假设您正在使用引导的Transforms Python仓库中包含的默认项目结构。

## 仓库升级文件更改

当您首次创建仓库时，它会使用当时最新的Transforms Python模板版本的默认内容进行引导。在随后的仓库升级过程中，仓库中的文件会升级以与最新的Transforms Python模板版本的内容保持一致。对这些文件的用户自定义更改可能会在新的升级模板中被覆盖，以确保一致性。我们不支持对这些文件进行自定义更改，因为这可能导致意外行为。

以下文件在仓库升级时不会被覆盖：

- conda_recipe和src文件夹中的默认文件
- 内部和外部build.gradle文件
以下文件将在仓库升级期间与最新的Python模板文件合并。如果存在任何公共键，则选择Python模板的版本：

- gradle.properties
- versions.properties
其余文件将通过升级被覆盖，以匹配最新Python模板版本的文件。

## pipeline.py

在此文件中，您定义项目的Pipeline，这是与您的数据变换相关联的Transform对象的注册表。以下是默认的src/myproject/pipeline.py文件：

```
Copied!1
2
3
4
5
6
7
8
from transforms.api import Pipeline
from myproject import datasets

# 创建一个新的数据处理管道实例
my_pipeline = Pipeline()

# 自动发现并注册数据集中的转换（transforms）
my_pipeline.discover_transforms(datasets)
```

请注意，默认的pipeline.py文件使用自动注册将您的变换Object添加到项目的Pipeline中。自动注册会发现项目datasets包中的所有变换Object。因此，如果您重新构建项目，使得变换逻辑不包含在datasets文件夹中，请确保适当更新src/myproject/pipeline.py文件。

或者，您可以使用手动注册显式地将每个变换Object添加到项目的Pipeline中。除非您的工作流程要求您显式地将每个变换Object添加到Pipeline中，否则推荐使用自动注册。有关Pipeline Object的更多信息，请参阅描述Pipelines的部分。

## setup.py

在此文件中，您定义了一个名为root的transforms.pipeline入口点，该入口点与项目的Pipeline关联——这允许Transforms Python发现项目的Pipeline。以下是默认的src/setup.py文件：

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
23
import os
from setuptools import find_packages, setup

setup(
    name=os.environ['PKG_NAME'],  # 从环境变量中获取包名
    version=os.environ['PKG_VERSION'],  # 从环境变量中获取包版本

    description='Python data transformation project',  # 项目描述

    # 修改此项目的作者
    author='{{REPOSITORY_ORG_NAME}}',  # 使用模板变量来指定作者名

    packages=find_packages(exclude=['contrib', 'docs', 'test']),  # 查找并打包除了指定目录之外的所有子包

    # 相反，在 conda_recipe/meta.yml 中指定依赖项
    install_requires=[],  # 安装依赖项列表，这里为空列表

    entry_points={
        'transforms.pipelines': [
            'root = myproject.pipeline:my_pipeline'  # 定义入口点，指定数据转换流水线的起始点
        ]
    }
)
```

如果您更改了默认项目结构，您可能需要更改src/setup.py文件中的内容。有关更多信息，请参阅描述变换.管道入口点的部分。

## examples.py

此文件包含您的数据变换代码。以下是默认的src/myproject/datasets/examples.py文件：

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
"""
from transforms.api import transform_df, Input, Output
from myproject.datasets import utils

@transform_df(
    Output("/path/to/output/dataset"),
    my_input=Input("/path/to/input/dataset"),
)
def my_compute_function(my_input):
    # 调用 utils 模块中的 identity 函数，返回输入数据不做任何更改
    return utils.identity(my_input)
"""
```

在取消注释示例代码后，您可以将/path/to/input/dataset和/path/to/out/dataset替换为输入和输出数据集的完整路径。如果您的数据变换依赖于多个数据集，可以提供额外的输入数据集。您还必须更新my_compute_function以包含将输入数据集变换为输出数据集的代码。此外，请记住，一个Python文件支持创建多个输出数据集。

请注意，示例代码使用了DataFrame变换装饰器。或者，您可以使用：

- 变换装饰器——如果您编写的变换依赖于文件访问而不是数据集，应该使用此装饰器，或者
- Pandas变换装饰器——如果您专门使用Pandas库并且输入数据可以放入内存中，应该使用此装饰器。
有关创建变换Object的更多信息，这些Object描述了您的输入和输出数据集以及变换逻辑，请参阅描述变换的部分。

## meta.yaml

一个conda搭建配方是一个包含搭建conda ↗包所需的所有元数据和脚本的目录。搭建配方中的一个文件是meta.yaml——此文件包含所有元数据。有关此文件结构的更多信息，请参阅conda关于meta.yaml文件的文档 ↗。
这是默认的conda_recipe/meta.yaml文件：

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
23
24
25
26
27
28
29
# 如果需要修改包的运行时需求，请更新此文件中的 'requirements.run' 部分

package:
  name: "{{ PACKAGE_NAME }}" # 包的名称
  version: "{{ PACKAGE_VERSION }}" # 包的版本

source:
  path: ../src # 源代码路径

requirements:
  # 构建包所需的工具。这些软件包在构建系统上运行，包括版本控制系统（如 Git, SVN），
  # 构建工具（如 GNU make, Autotool, CMake）和编译器（真正交叉编译，伪交叉编译或本地编译），
  # 以及任何源代码预处理器。
  # 更多信息请参考：https://docs.conda.io/projects/conda-build/en/latest/resources/define-metadata.html#build
  build:
    - python 3.9.* # 构建环境需要的 Python 版本
    - setuptools # 用于打包和分发 Python 包的工具

  # 运行包所需的工具。这些是安装包时自动安装的依赖项。
  # 更多信息请参考：https://docs.conda.io/projects/conda-build/en/latest/resources/define-metadata.html#run
  run:
    - python 3.9.* # 运行环境需要的 Python 版本
    - transforms {{ PYTHON_TRANSFORMS_VERSION }} # 依赖的 transforms 包及其版本
    - transforms-expectations # 依赖的 transforms-expectations 包
    - transforms-verbs # 依赖的 transforms-verbs 包

build:
  script: python setup.py install --single-version-externally-managed --record=record.txt
  # 构建脚本，使用 setup.py 安装包，并管理版本记录
```

如果您的变换Python项目需要任何额外的搭建依赖项，可以使用软件包选项卡来发现可用的软件包，并自动将其添加到您的meta.yml文件中，如共享Python库的文档中所述。此步骤将自动检测您尝试导入的软件包的生成渠道，并将其添加为支持的代码库。

也可以手动更新此文件中的“requirements”部分。然而，强烈建议不要手动更改，因为您可能会请求不可用的软件包和版本，随后会导致您的代码库上的检查出错。对于您添加的任何依赖项，请确保您的依赖项所需的软件包是可用的。

请注意，您不太可能需要修改“requirements”以外的部分。

### 支持的 Python 3 版本

Palantir支持Python的活跃版本，遵循Python软件基金会的生命周期终止计划。更多细节请参考Python版本支持页面。

用法示例：

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
requirements:
  build:
    - python 3.9.*  # 指定 Python 版本为 3.9.x，用于构建环境
    - setuptools    # 构建和安装 Python 包的工具

  # 运行此包所需的额外软件包。
  run:
    - python 3.9.*  # 指定 Python 版本为 3.9.x，用于运行环境
    - transforms {{ PYTHON_TRANSFORMS_VERSION }}  # 运行时所需的 transforms 包，其版本由变量 PYTHON_TRANSFORMS_VERSION 确定
```

- 确保搭建和运行部分的Python依赖项是相同的。Python依赖项之间的不匹配可能导致不期望的结果和失败。
- 不支持python >=3.9或python >3.9,<=3.10.11这样的Python版本范围。
### 固定运行时版本

如果你的变换需要固定特定的库版本，并且你想手动添加而不是使用推荐的package tab，可以在requirements块中明确指定库名称及版本。以下是一个固定版本的示例：

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
requirements:
  run:
    # The below pins an explicit version
    # 以下指定了一个明确的版本
    - mylibrary 1.0.1

    # The below specifies a maximum version (version equal or lower):
    # 以下指定了一个最大版本（版本等于或小于指定版本）：
    - scipy <=1.4.0
```

注意：

- 操作符后不允许有空格。例如scipy <= 1.4.0将会导致CI检查失败。
- Foundry尚不支持版本操作符>=。
### 使用pip管理的依赖项

如果您的变换需要一个特定的库，而该库无法通过Conda获取，但可以使用pip ↗安装，那么您可以在额外的pip部分中声明这些依赖项。该依赖项将安装在您的Conda环境之上。以下是添加pip依赖项的示例：

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
requirements:
  build:
    - python 3.9.*  # 构建时所需的 Python 版本
    - setuptools   # 构建时使用的 setuptools 工具

  run:
    - python 3.9.*  # 运行时所需的 Python 版本
    - transforms {{ PYTHON_TRANSFORMS_VERSION }}  # 使用指定版本的 transforms 库

  pip:
    - pypicloud  # 使用 pip 安装 pypicloud 包
```

注意：

- 添加到pip部分的依赖项安装在从run部分的包派生的Conda环境之上。因此，移除run或搭建将导致失败。
- pip部分只能用于变换Python存储库，不能用于Python库。