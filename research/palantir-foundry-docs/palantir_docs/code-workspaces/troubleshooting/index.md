来源: https://palantir.com/docs/zh/foundry/code-workspaces/troubleshooting/

# 故障排除

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 故障排除

本页面包含在使用Code Workspaces时可能遇到的错误的故障排除提示。如果您遇到其他问题或无法通过本指南解决您的问题，请联系您的Palantir代表。

## 错误消息和建议的解决方案

### 错误：未经授权 - 会话已不再有效。可能已超时。请刷新页面。

如果您遇到“未经授权”错误并提示您的会话可能已超时，请按照以下步骤进行修复：

- 刷新页面。
- 确保您使用的是Google Chrome访问Code Workspaces。Safari浏览器不支持。
- 如果之前在此Code Workspace中加载了具有安全权限标记的数据，并且您失去了对标记数据的访问权限，您可能会收到此错误。如果是这种情况，选择运行然后重启工作区以获取一个没有数据的新会话。
- 如果这是您第一次使用Code Workspaces，您可能需要联系IT管理员以确保Code Workspaces已被正确列入白名单。
### 错误：内容被阻止。请联系网站所有者以解决此问题。

Foundry应用了严格的内容安全策略以确保在Code Workspaces中呈现的内容得到适当的控制。例如，Code Workspaces不允许从CDN加载任意JavaScript，这与某些Python包（如folium）的情况类似。

如果您在关键工作流程中收到此错误，请联系您的Palantir代表以讨论该工作流程的潜在支持。一些工作流程已经得到支持，但可能需要您运行略微不同的命令：

- 搭建Dash应用程序
- 搭建Streamlit应用程序
- 预览TensorBoard™
### 错误：包或命名空间加载失败

您可能会遇到如下所示的包或命名空间加载失败错误：

```
Copied!1
2
3
4
> library("hdf5r")
Error: package or namespace load failed for 'hdf5r' in dyn.load(file, DLLpath = DLLpath, ...):
 unable to load shared object '/home/user/libs/r/hdf5r/libs/hdf5r.so':
  libhdf5_serial_hl.so.100: cannot open shared object file: No such file or directory
```

这段代码尝试加载R语言中的hdf5r库，但失败了。错误信息指出无法加载共享对象文件，这通常是因为缺少依赖的动态链接库文件libhdf5_serial_hl.so.100。以下是一些可能的解决方案：

- 安装缺失的依赖项：确保系统上安装了所需的HDF5库文件。在大多数Linux系统上，可以通过包管理工具进行安装，如apt-get install libhdf5-dev。
安装缺失的依赖项：确保系统上安装了所需的HDF5库文件。在大多数Linux系统上，可以通过包管理工具进行安装，如apt-get install libhdf5-dev。

- 检查环境变量：确保库的路径在LD_LIBRARY_PATH环境变量中。
检查环境变量：确保库的路径在LD_LIBRARY_PATH环境变量中。

- 重新安装hdf5r：在R中尝试重新安装hdf5r包，可能会自动解决依赖关系：install.packages("hdf5r")。
重新安装hdf5r：在R中尝试重新安装hdf5r包，可能会自动解决依赖关系：install.packages("hdf5r")。

- 检查兼容性：确保R包和系统上的HDF5库版本是兼容的。
由于Foundry限制了服务器上预安装的Linux软件包数量，以减少潜在漏洞的暴露，因此可能会发生这种情况。然而，一些R库依赖于特定的系统Linux库，这些库可能未预安装在服务器上。
检查兼容性：确保R包和系统上的HDF5库版本是兼容的。
由于Foundry限制了服务器上预安装的Linux软件包数量，以减少潜在漏洞的暴露，因此可能会发生这种情况。然而，一些R库依赖于特定的系统Linux库，这些库可能未预安装在服务器上。

请注意，某些软件包不受Code Workspaces支持

请联系您的Palantir代表讨论所需Linux软件包的可用性。

### 出错：尝试同步数据到代码库失败

当正在同步的git提交过大时会发生此错误。如果提交包含非代码文件，如输出数据，就可能发生这种情况。Code Workspaces中的版本控制不支持大文件。相反，数据可以交互式地写回Foundry，让您能够轻松使用和分享代码工作区的输出。

要找出哪些文件导致了此错误，请在您的工作区内打开终端并执行以下命令：

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
git rev-list --objects --all |
   # 列出所有的对象（文件、目录、提交等）的哈希值
   git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' |
   # 获取对象的类型、名称、大小等信息
   sed -n 's/^blob //p' |
   # 过滤出 blob 类型的对象（即文件）
   awk '{sum[$3]+=$2} END {for (i in sum) print sum[i], i}' |
   # 累加相同文件名的大小
   sort --numeric-sort --key=1 |
   # 按文件大小排序
   $(command -v gnumfmt || echo numfmt) --field=1 --to=iec-i --suffix=B --padding=7 --round=nearest
   # 使用 gnumfmt（或 numfmt）将大小格式化为更容易阅读的形式
```

上述代码主要用于统计 Git 仓库中所有文件的大小，并将其格式化输出为易读的形式。
要解决此错误，请从git历史中删除任何大文件。例如，要删除所有大于10 MB的文件，可以运行终端命令：git filter-repo --strip-blobs-bigger-than 10M。或者，要从git历史中删除特定文件，请使用git filter-repo --path path/to/file.ext --invert-paths。

为防止再次发生此错误，请更新.gitignore文件，添加不应同步的任何大文件的路径或扩展名。例如，为防止任何输出的CSV文件被同步，可以添加*.csv。注意，您可能需要确保在您的IDE中可见隐藏文件，以查看.gitignore文件。

要应用这些更改，请在终端中运行git push --force。按照这些步骤之后，同步更改过程现在应该能够正常工作。

### 文件下载或上传出错

出于安全原因，Foundry通常限制文件下载和上传，以确保这些活动在适当的数据治理框架中进行。这意味着用户无法在Shiny®或Streamlit应用程序中添加“下载”按钮或等效功能。

要从Jupyter®或RStudio®工作区下载数据，首先将数据写入Foundry中的输出数据集。您可以使用Foundry的内置流程从输出数据集中下载数据，这确保了适当的数据治理限制的应用。

### 文件加载出错

如果用户对可以下载或在浏览器中渲染的数据量设置了限制，可能会发生文件加载出错。在这种情况下，尝试运行命令jupyter nbconvert --clear-output --inplace notebook.ipynb，将notebook.ipynb替换为错误消息中显示的文件名称：

但是，请注意此命令将清除所有单元格输出，包括图表。

RStudio®和Shiny®是Posit™的商标。

Jupyter®、JupyterLab®和Jupyter®徽标是NumFOCUS的商标或注册商标。

TensorBoard和任何相关标记是Google Inc.的商标。

所有提到的第三方商标（包括徽标和图标）仍然是其各自所有者的财产。不暗示任何附属关系或认可。
