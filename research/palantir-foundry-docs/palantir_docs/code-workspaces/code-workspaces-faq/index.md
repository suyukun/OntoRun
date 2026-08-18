来源: https://palantir.com/docs/zh/foundry/code-workspaces/code-workspaces-faq/

# 常见问题

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 常见问题

### 我可以在 Code Workspaces 中使用对象吗？

目前无法直接在 Code Workspaces 中使用对象。用户可以通过工作区内的数据菜单导入支持对象的数据集。

### 我可以在 Code Workspaces 中使用 PySpark 吗？

可以，PySpark 可以在 Code Workspaces 中使用，但请注意，它不会利用分布式的 Spark 基础设施，因为 Code Workspaces 当前在单节点上运行。如果您想利用 Spark 基础设施，我们推荐使用 Foundry 应用程序，如Pipeline Builder和Code Repositories。

要在您的 JupyterLab® Notebook 中安装 PySpark，请转到Packages选项卡，搜索并安装openjdk（来自 Conda）和pyspark（来自 PyPI）。

### 哪些 IDEs 受到 Code Workspaces 的支持？

Code Workspaces 目前支持 JupyterLab® 和 RStudio® Workbench。

### 哪些软件包不受 Code Workspaces 的支持？

出于安全原因，以下 Python 软件包不受支持：

- folium
- pandasgui
如果您对上述软件包有任何疑虑，请联系您的 Palantir 代表。

### 我可以在 Code Workspaces 中进行 API 调用吗？

可以，在Settings菜单中定义网络策略后，您可以在 Code Workspaces 中进行 API 调用。请注意，外部 API 必须注册为控制面板中批准的网络出口策略。

### 为什么我的代码库中的代码是 JSON 格式？

Code Repositories 应用程序从关联的 Code Workspaces 接收代码，以 IPython 格式呈现代码，这会将代码在单元级别渲染为 JSON 格式。

### 我可以使用自己的软件包吗？

可以；请参阅有关导入软件包的文档。如果您的软件包托管在组织的 Conda/PyPI/CRAN 频道上，Foundry 可以代理该频道并使其对您的项目可用。请联系您的 Palantir 代表以获取更多信息。

### 为什么支持我的 Code Workspace 的 Code Repository 没有Libraries选项卡？

要将库导入您的 Code Workspace，请使用工作区左侧面板中的Packages选项卡。

### 我可以在 Code Repositories 中编写或编辑不来自于我的 Code Workspace 的代码吗？

可以，当代码源自 Code Workspaces 时，您可以直接在 Code Repositories 中编辑代码。提交后，您可以使用 Code Workspace 中的Sync或Reset changes功能来获取工作区中的远程更改。

概念上，您可以将 Code Repositories 视为 Code Workspaces 的版本控制管理器，处理拉取请求、冲突解决和管理，而代码开发可以在 Code Workspaces 中进行。

### 为什么我的同事看到的视图与我不同？

出于安全目的，用户在 JupyterLab® 或 RStudio® 中工作时是隔离的。这意味着每个访问同一 Code Workspace 的用户将拥有自己的环境。协作通过 git 工作流程进行：如果您希望让您的最新代码对同事可用，请选择Sync Changes以同步您的更改到支持的代码库，当同事选择Sync或Reset changes时，这些更改将对他们可用。当多个用户在同一工作区工作时，我们建议他们在独立的分支上工作。

请注意，我们默认使用.gitignore忽略某些文件，以确保没有数据同步到 git 仓库，并限制 git 仓库的大小。我们还会删除所有 JupyterLab®.ipynb文件的输出。

### 我可以导入额外的 LaTeX 软件包来渲染我的 R Markdown 文件吗？

可以。默认情况下，Code Workspaces 仅预安装渲染常见 R Markdown 文件（如TinyTex-1 ↗中定义）的要求，但您可以自行安装其他 LaTeX 软件包：

- 下载或创建 TDS 存档。例如，您可以从CTAN ↗下载一个.tds.zip文件。
- 将 TDS 存档上传到新的或现有的 Foundry 数据集中。您可以将文件拖放到文件夹中以上传到新的 Foundry 数据集。
- 选择Upload to a dataset without a schema。您可以同时将多个 TDS 存档上传到同一数据集中。
- 在 Code Workspaces 中，转到数据选项卡，然后读取现有数据集。选择包含 TDS 存档的数据集。
- 可选，更新数据集别名。在此示例中，我们假设您将数据集别名命名为my_latex_packages。
- 复制代码片段，将其粘贴到您的.Rprofile中，并更新它以将文件提取到正确的位置。您需要在以下片段中将my_latex_packages替换为您的数据集别名：
```
# 加载foundry库
library(foundry)

# 列出"my_latex_packages"数据集中的所有文件
my_latex_packages_files <- datasets.list_files("my_latex_packages")

# 下载"my_latex_packages"数据集中的所有文件到本地
my_latex_packages_local_files <- datasets.download_files("my_latex_packages", my_latex_packages_files)

# 获取TEXMFLOCAL目录的路径
texmflocal <- system("kpsewhich --var-value TEXMFLOCAL", intern = TRUE)

# 将下载的每一个tds文件解压到TEXMFLOCAL目录下
sapply(my_latex_packages_local_files, function(tds_file) { unzip(tds_file, exdir = texmflocal) })
```

- 现在可以在 R Markdown 头部中包含您的包以使用它：
```
Copied!1
2
headers-include:
 - \usepackage{my_package} % 引入自定义包 my_package
```

### 我可以在我的 R Markdown 文件中使用自定义字体吗？

可以。

- 下载或创建您想使用的 TTF 文件。
- 将 TTF 文件上传到一个新的或现有的 Foundry 数据集。您可以通过拖放文件到文件夹中，将它们上传到一个新的 Foundry 数据集。
- 选择上传到没有架构的数据集。您可以同时将多个 TTF 文件上传到同一个数据集中。
- 在 Code Workspaces 中，进入数据标签，然后读取现有数据集。选择包含 TTF 文件的数据集。
- 非必填，更新数据集别名。在此示例中，我们假设您将数据集别名命名为my_fonts。
- 复制代码片段，在 R 控制台中运行，并将文件复制到您的仓库中，以便可以通过版本控制进行跟踪。您需要在下面的代码片段中将my_fonts替换为您的数据集别名：
```
# 获取 "my_fonts" 数据集中的文件列表
my_fonts_files <- datasets.list_files("my_fonts")

# 下载 "my_fonts" 数据集中的文件到本地
my_fonts_local_files <- datasets.download_files("my_fonts", my_fonts_files)

# 创建一个名为 "fonts" 的目录
dir.create("fonts")

# 将下载的文件复制到 "fonts" 目录中
file.copy(unlist(my_fonts_local_files), "fonts")
```

- 现在，您可以引用/home/user/repo/fonts目录中的字体，以便根据 R Markdown 的建议在您的 HTML 或 PDF 输出中使用它们。
要更改 HTML 的字体，请在自定义 CSS ↗中设置font-family。

要更改 PDF 的字体，您可以在 LaTeX 的前导中使用\newfontfamily加载字体，使用自定义 LaTeX 代码 ↗。

### 如何防止我的 Jupyter® 工作区在代码运行时暂停？

您可以利用%%keep_alive单元魔术命令来防止 Code Workspaces 在单元中的代码运行时暂停 Jupyter® notebook。

```
Copied!1
2
3
%%keep_alive

long_running_process()
```

%%keep_alive是一个魔法命令，用于确保在执行长时间运行的进程时，Jupyter Notebook不会因为空闲超时而自动断开连接。long_running_process()是一个示例函数，代表需要保持活动状态的长时间运行的过程。
这将使单元格在代码运行时保持活跃状态长达24小时。如果您的浏览器标签页关闭或闲置时间过长，JupyterLab® 将停止显示和持久化单元格的输出。如果您希望稍后查看单元格的输出，可以使用%%capture单元格魔法将输出存储在一个变量中：

```
Copied!1
2
3
4
%%keep_alive  # 确保长时间运行的进程不会超时
%%capture cell_output  # 捕获单元格的输出到变量cell_output中

long_running_process()  # 执行长时间运行的进程
```

在不同的单元格中，将上述变量的输出写入文件，以便稍后查看：

```
Copied!1
2
3
4
5
with open('cell_output.txt', 'w+') as f:
    # 将标准输出写入文件
    f.write(cell_output.stdout)
    # 将标准错误输出写入文件
    f.write(cell_output.stderr)
```

### 如何从我的 Jupyter 或 RStudio 代码工作区下载文件？

为了确保管理员配置的下载限制得到执行，Palantir 平台中已禁用 IDE 原生文件下载功能。

要下载文件，请将文件写回 Foundry 数据集。为此，在代码工作区侧边栏中，导航到数据选项卡，然后选择将数据写入新数据集，并为新数据集输入名称。在确认数据集的别名后，选择非表格数据集作为数据集类型，输入要上传的文件或目录的位置并运行生成的代码片段。

一旦文件上传到 Foundry 数据集，您可以选择数据集链接导航到数据集预览，并从那里下载文件。
请记住，您的管理员可能会要求在从平台导出数据之前提供理由或限制导出的数据量。

RStudio® 和 Shiny® 是 Posit™ 的商标。

Jupyter®、JupyterLab® 和 Jupyter® 徽标是 NumFOCUS 的商标或注册商标。

提到的所有第三方商标（包括徽标和图标）仍然是其各自所有者的财产。不暗示任何关联或背书。
