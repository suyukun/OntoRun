来源: https://palantir.com/docs/zh/foundry/code-workspaces/jupyterlab/

# JupyterLab®

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# JupyterLab®

代码工作区使您可以在Foundry中使用JupyterLab® ↗。代码工作区中的JupyterLab®支持：

- 读取和写入表格数据集。
- 从非结构化数据集中下载或上传文件。
- 从Conda或PyPI导入Python包。
- 预览Dash、Streamlit或TensorBoard™应用程序以促进迭代。
- 发布Dash或Streamlit应用程序。
- 与Ontology互动。
代码工作区目前支持用于Python应用程序的Dash ↗和Streamlit ↗。用户可以直接在代码工作区中创建应用程序，Foundry的版本控制、分支和数据治理功能已内置。

代码工作区应用程序支持分支。如果您创建一个新的工作区分支，发布一个新应用程序或同步更改将在该分支上发布应用程序的新版本。这允许您在将应用程序公开给用户之前进行预览。要在主分支上发布，只需将您的分支合并到主分支。

## Dash应用程序

发布的Dash应用程序有30秒超时限制，这意味着Dash服务器必须在执行您的Dash应用程序Python文件后的30秒内启动。否则，您的Dash应用程序将无法启动。

要创建Dash ↗应用程序，请按照以下说明进行操作：

- 在JupyterLab®工作区中打开应用程序选项卡。
- 选择发布应用程序，在您的文件和项目中为新应用程序选择一个位置，并提供模块名称和变量名称。将在与所提供模块名称对应的路径自动创建一个文件。
- 非必填:配置高级设置。默认情况下，应用程序设置将匹配Jupyter®工作区的设置。
- 选择发布并同步以注册您的新Dash应用程序并将代码同步到支持代码库中。CI检查和发布完成后，您可以在应用程序面板中选择链接以查看发布的应用程序。
Dash应用程序的模块名称应作为点路径输入，相对于存储库的根（例如，app，或者如果您的模块在文件夹中，folder.app）。变量名称是模块文件中声明的Dash应用程序服务器的Python变量，通常称为server。

要在本地开发现有Dash应用程序：

- 打开终端窗口并执行您新创建的文件，例如，python app.py。
- 在应用程序选项卡的Dash部分选择预览以预览应用程序。
您可以确保JupyterLab®工作区中的Conda/PyPI环境将在您发布的Dash应用程序中自动恢复，使用托管的Jupyter®笔记本中的Conda/PyPI环境。

## Streamlit应用程序

发布的Streamlit应用程序有30秒超时限制，这意味着Streamlit服务器必须在执行您的Streamlit应用程序Python文件后的30秒内启动。否则，您发布的Streamlit应用程序将无法启动。

要创建Streamlit ↗应用程序，请按照以下说明进行操作：

- 选择发布应用程序，在您的文件和项目中为新应用程序选择一个位置，并输入相对于存储库根的Python文件名称，例如，app.py。
- 非必填:配置高级设置。默认情况下，应用程序设置将匹配JupyterLab®工作区的设置。
- 选择发布并同步以注册您的新Streamlit应用程序并将代码同步到支持代码库中。CI检查和发布完成后，您可以在应用程序面板中选择链接以查看发布的应用程序。
要在本地开发现有Streamlit应用程序：

- 打开终端窗口并使用streamlit run app-name.py运行代码。
- 在JupyterLab®代码工作区中打开应用程序选项卡，并在Streamlit部分选择预览以预览您在本地开发的应用程序。
您可以确保JupyterLab®工作区中的Conda/PyPI环境将在您发布的Streamlit应用程序中自动恢复，使用托管的Jupyter®笔记本中的Conda/PyPI环境。

## TensorBoard™

您可以直接从代码工作区预览TensorBoard™ ↗。为此，从终端运行tensorboard --logdir=<$PATH_TO_LOGS_DIRECTORY>，填写包含TensorFlow日志的目录路径。然后，在Jupyter®工作区的应用程序选项卡中打开并在TensorBoard™部分选择预览。

## Jupyter®笔记本变换

Jupyter笔记本变换目前不支持向外部服务发出API调用，即使在代码工作区中添加了网络策略也是如此。要运行可重现的向互联网发出API调用的管道，您应该使用外部变换。

代码工作区可以将Jupyter®笔记本发布为数据变换管道，并为笔记本生成的输出数据集注册变换任务规范。

按照以下步骤为输出数据集注册变换：

- 将您的Jupyter®笔记本保存为工作区中的文件。
将您的Jupyter®笔记本保存为工作区中的文件。

- 在数据面板中选择数据集旁边的蓝色搭建图标。
在数据面板中选择数据集旁边的蓝色搭建图标。

- 按照界面配置您的变换。代码工作区将推断使用的Jupyter®笔记本以及添加的输入以生成输出数据集。如果推断错误，您可以手动编辑输入和输出。
- 选择同步并运行以保存变换配置并触发CI检查以在输出数据集上发布变换和任务规范。
一旦CI检查完成，您的变换就可以准备搭建。您可以使用其他Foundry数据集成工具来管理您的变换及其所属的数据管道。

变换不会自动使用代码工作区的环境。您应该在脚本文件的顶部安装运行时所需的所有包。可以在包面板中找到安装包的代码片段。
例如，要在您的变换中使用scikit-learn和scikit-image，请将此代码片段添加到文件顶部：

```
Copied!1
2
3
!mamba install -y -q scikit-learn scikit-image
# 这个命令使用 mamba 包管理器来静默安装 scikit-learn 和 scikit-image 两个库。
# -y 参数表示自动确认安装，而 -q 参数则用于静默模式，不显示安装过程的详细信息。
```

## 在 Jupyter® 笔记本中管理 Conda/PyPI 环境

管理的 Conda/PyPI 环境现已普遍可用。

Jupyter® Conda/PyPI 环境可以通过管理环境功能在 Jupyter® 工作区、应用程序、变换和模型输出中一致地恢复。

管理的环境在 Code Workspace 工作流中保持一致，无需在每次重新启动工作区、启动应用程序或运行 Jupyter® Notebook 变换时重新运行相同的mamba和pip命令。

通过管理的环境，工作环境中安装的库通过/home/user/repo文件夹中的文件进行跟踪，使环境能够在各个工作流中恢复到其原始状态。

以下两个文件用于跟踪您的管理环境：

- /home/user/repo/.envs/maestro/meta.yaml: 被称为环境清单，它包含环境中请求的库和版本集。了解更多关于 meta.yaml 文件的信息。
- /home/user/repo/.envs/maestro/hawk.lock- 被称为环境锁定文件，它包含从清单中指定的约束解决的环境中已解决的库和版本集。hawk.lock文件取代了已弃用的conda.lock。了解更多关于hawk.lock文件的信息。
我们不建议修改hawk.lock锁定文件。相反，依赖安装命令为您更新文件。除非有 git 冲突，否则您也不需要修改meta.yaml文件；当包被交互式安装时，它会自动更新。

您的管理环境安装在/home/user/envs/default文件夹中。在以下阶段之前，该环境将被恢复：

- 启动您的 Jupyter® 工作区
- 启动从您的工作区生成的应用程序
- 运行从您的工作区生成的 Jupyter® Notebook 变换
- 运行模型
### 使用方法

要启用此功能，请在工作区设置的左侧边栏中切换Managed Conda environments实验功能。然后，重新启动工作区：

一旦启用该功能，一个名为default的管理环境将可供您使用：

要更新您的管理环境，请导航到左侧边栏中的Packages选项卡，并按照说明添加新包。

通过Packages选项卡安装包时，安装命令直接在 Jupyter® 终端中执行，而不是在您的笔记本或应用程序代码中执行。每次运行安装命令时，meta.yaml清单将更新您请求的包，并且hawk.lock文件将反映当前环境中安装的包。

### 查看管理环境中当前安装的包

已安装的包可在Packages选项卡中查看：

### 在 JupyterLab® 界面中查看环境文件

导航到工作区中的View下拉菜单并选择Show Hidden Files。

然后，导航到.envs/maestro文件夹以查看meta.yaml和hawk.lock文件。

### 将您的管理环境与hawk.lock文件的更改同步

在检出新分支或拉取新的 git 更改后，您的 hawk.lock 文件的内容可能会发生变化。

要同步您的管理环境，请在工作区终端中执行以下命令：

```
maestro env install
```

此命令用于安装maestro环境。maestro是一种用于管理和部署数据管道的工具，env install则是安装或设置该工具所需的环境。

maestro是更新托管环境的命令行界面。上述命令从清单中重新解析锁文件并将环境安装到/home/user/envs/default文件夹中。

### 解决环境文件中的 git 冲突

要解决托管环境中的 git 冲突，首先删除hawk.lock文件。导航到meta.yaml文件以解决任何冲突，然后合并您的分支。

合并后，在终端中运行maestro env install命令以重新生成hawk.lock文件并重新安装您的托管环境。

### 升级您的托管环境

要更新您的托管环境，首先删除hawk.lock文件。然后，删除您的/home/user/envs/default文件夹 (rm -rf /home/user/envs/default)。最后，在终端中运行maestro env install命令以重新生成您的hawk.lock文件。您的环境将重新安装升级后的包版本。

### 示例:meta.yaml文件

meta.yaml文件表示请求包的规范。此文件符合Conda 元数据规范 ↗，并且可以包含 Conda 和 PyPI 依赖项的规范。只有在requirements.run和requirements.pip部分指定的包用于 Jupyter® 托管环境。

以下是一个meta.yaml文件的示例：

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
package:
  name: '{{ PACKAGE_NAME }}'  # 包名称
  version: '{{ PACKAGE_VERSION }}'  # 包版本
requirements:
  build: []  # 构建时的依赖
  run:
    - ipykernel
    - pip
    - foundry-transforms-lib-python
    - pandas
    - polars
    - dash
    - streamlit
    - tensorboard
  pip:
    - Flask-Testing  # 通过 pip 安装的依赖
  run_constrained: []  # 运行时的限制性依赖
source:
  path: ../src  # 源代码路径
build: null
test: null
about: null
```

### 示例：hawk.lock文件

hawk.lock文件包含已解决的托管环境的已解析包、版本和通道。

下面是一个hawk.lock文件的示例：

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
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
83
84
85
86
87
88
89
90
91
92
93
94
95
96
97
98
99
100
101
102
103
104
105
106
107
108
109
110
111
112
113
114
115
116
117
118
119
120
121
122
123
124
125
126
127
128
129
130
131
132
133
134
135
136
137
138
139
140
141
142
143
144
145
146
147
148
149
150
151
152
153
154
155
156
157
158
159
160
161
162
163
164
165
166
167
168
169
170
171
172
173
174
175
176
177
178
179
180
181
182
183
184
185
186
187
188
189
190
191
192
193
194
195
196
197
198
199
200
201
202
203
204
205
206
207
208
209
210
211
212
213
214
215
216
217
218
219
220
# This file is autogenerated. Though not necessary, it can be committed to the git repository.
# To avoid build failures, we do not recommend changing this file,
# 该文件是自动生成的。虽然不是必须的，但可以提交到git仓库中。
# 为避免构建失败，建议不要修改此文件。

[conda]
_libgcc_mutex=0.1=conda_forge @ 16fe1c80
_openmp_mutex=4.5=2_gnu @ 16fe1c80
absl-py=2.1.0=pyhd8ed1ab_0 @ c7211bb6
altair=5.3.0=pyhd8ed1ab_0 @ c7211bb6
asttokens=2.4.1=pyhd8ed1ab_0 @ c7211bb6
attrs=23.2.0=pyh71513ae_0 @ c7211bb6
aws-c-auth=0.7.22=h96bc93b_2 @ e1c11c02
aws-c-cal=0.6.14=h88a6e22_1 @ e1c11c02
aws-c-common=0.9.19=h4ab18f5_0 @ e1c11c02
aws-c-compression=0.2.18=h83b837d_6 @ e1c11c02
aws-c-event-stream=0.4.2=ha47c788_12 @ e1c11c02
aws-c-http=0.8.1=h29d6fba_17 @ e1c11c02
aws-c-io=0.14.8=h21d4f22_5 @ e1c11c02
aws-c-mqtt=0.10.4=h759edc4_4 @ e1c11c02
aws-c-s3=0.5.9=h594631b_3 @ e1c11c02
aws-c-sdkutils=0.1.16=h83b837d_2 @ e1c11c02
aws-checksums=0.1.18=h83b837d_6 @ e1c11c02
aws-crt-cpp=0.26.9=he3a8b3b_0 @ e1c11c02
aws-sdk-cpp=1.11.329=hba8bd5f_3 @ e1c11c02
blinker=1.8.2=pyhd8ed1ab_0 @ c7211bb6
brotli-python=1.1.0=py310hc6cd4ac_1 @ e1c11c02
bzip2=1.0.8=hd590300_5 @ e1c11c02
c-ares=1.28.1=hd590300_0 @ e1c11c02
ca-certificates=2024.7.4=hbcca054_0 @ e1c11c02
cachetools=5.3.3=pyhd8ed1ab_0 @ c7211bb6
certifi=2024.7.4=pyhd8ed1ab_0 @ c7211bb6
cffi=1.16.0=py310h2fee648_0 @ e1c11c02
charset-normalizer=3.3.2=pyhd8ed1ab_0 @ c7211bb6
click=8.1.7=unix_pyh707e725_0 @ c7211bb6
comm=0.2.2=pyhd8ed1ab_0 @ c7211bb6
conjure-python-client=2.8.0=pyhd8ed1ab_0 @ c7211bb6
dash=2.17.1=pyhd8ed1ab_0 @ c7211bb6
debugpy=1.8.2=py310h76e45a6_0 @ e1c11c02
decorator=5.1.1=pyhd8ed1ab_0 @ fe451c34
exceptiongroup=1.2.0=pyhd8ed1ab_2 @ c7211bb6
executing=2.0.1=pyhd8ed1ab_0 @ c7211bb6
flask=3.0.3=pyhd8ed1ab_0 @ c7211bb6
foundry-data-sidecar-api=0.626.0=py_0 @ fe451c34
foundry-transforms-lib-python=0.639.0=py_0 @ fe451c34
freetype=2.12.1=h267a509_2 @ e1c11c02
gflags=2.2.2=he1b5a44_1004 @ 16fe1c80
gitdb=4.0.11=pyhd8ed1ab_0 @ c7211bb6
gitpython=3.1.43=pyhd8ed1ab_0 @ c7211bb6
glog=0.7.1=hbabe93e_0 @ e1c11c02
grpcio=1.62.2=py310h1b8f574_0 @ e1c11c02
h2=4.1.0=pyhd8ed1ab_0 @ fe451c34
hpack=4.0.0=pyh9f0ad1d_0 @ fe451c34
hyperframe=6.0.1=pyhd8ed1ab_0 @ fe451c34
idna=3.7=pyhd8ed1ab_0 @ c7211bb6
importlib-metadata=7.2.1=pyha770c72_0 @ c7211bb6
importlib_metadata=7.2.1=hd8ed1ab_0 @ c7211bb6
importlib_resources=6.4.0=pyhd8ed1ab_0 @ c7211bb6
ipykernel=6.29.5=pyh3099207_0 @ c7211bb6
ipython=8.26.0=pyh707e725_0 @ c7211bb6
ipywidgets=8.1.3=pyhd8ed1ab_0 @ c7211bb6
itsdangerous=2.2.0=pyhd8ed1ab_0 @ c7211bb6
jedi=0.19.1=pyhd8ed1ab_0 @ c7211bb6
jinja2=3.1.4=pyhd8ed1ab_0 @ c7211bb6
jsonschema=4.23.0=pyhd8ed1ab_0 @ c7211bb6
jsonschema-specifications=2023.12.1=pyhd8ed1ab_0 @ c7211bb6
jupyter_client=8.6.2=pyhd8ed1ab_0 @ c7211bb6
jupyter_core=5.7.2=py310hff52083_0 @ e1c11c02
jupyterlab_widgets=3.0.11=pyhd8ed1ab_0 @ c7211bb6
keyutils=1.6.1=h166bdaf_0 @ 16fe1c80
krb5=1.21.3=h659f571_0 @ e1c11c02
lcms2=2.16=hb7c19ff_0 @ e1c11c02
ld_impl_linux-64=2.40=hf3520f5_7 @ e1c11c02
lerc=4.0.0=h27087fc_0 @ 16fe1c80
libabseil=20240116.2=cxx17_h59595ed_0 @ e1c11c02
libarrow=16.1.0=hcb6531f_6_cpu @ e1c11c02
libarrow-acero=16.1.0=hac33072_6_cpu @ e1c11c02
libarrow-dataset=16.1.0=hac33072_6_cpu @ e1c11c02
libarrow-substrait=16.1.0=h7e0c224_6_cpu @ e1c11c02
libblas=3.9.0=22_linux64_openblas @ e1c11c02
libbrotlicommon=1.1.0=hd590300_1 @ e1c11c02
libbrotlidec=1.1.0=hd590300_1 @ e1c11c02
libbrotlienc=1.1.0=hd590300_1 @ e1c11c02
libcblas=3.9.0=22_linux64_openblas @ e1c11c02
libcrc32c=1.1.2=h9c3ff4c_0 @ 16fe1c80
libcurl=8.8.0=hca28451_1 @ e1c11c02
libdeflate=1.20=hd590300_0 @ e1c11c02
libedit=3.1.20191231=he28a2e2_2 @ 16fe1c80
libev=4.33=hd590300_2 @ e1c11c02
libevent=2.1.12=hf998b51_1 @ e1c11c02
libffi=3.4.2=h7f98852_5 @ 16fe1c80
libgcc-ng=14.1.0=h77fa898_0 @ e1c11c02
libgfortran-ng=14.1.0=h69a702a_0 @ e1c11c02
libgfortran5=14.1.0=hc5f4f2c_0 @ e1c11c02
libgomp=14.1.0=h77fa898_0 @ e1c11c02
libgoogle-cloud=2.24.0=h2736e30_0 @ e1c11c02
libgoogle-cloud-storage=2.24.0=h3d9a0c8_0 @ e1c11c02
libgrpc=1.62.2=h15f2491_0 @ e1c11c02
libjpeg-turbo=3.0.0=hd590300_1 @ e1c11c02
liblapack=3.9.0=22_linux64_openblas @ e1c11c02
libnghttp2=1.58.0=h47da74e_1 @ e1c11c02
libnsl=2.0.1=hd590300_0 @ e1c11c02
libopenblas=0.3.27=pthreads_hac2b453_1 @ e1c11c02
libparquet=16.1.0=h6a7eafb_6_cpu @ e1c11c02
libpng=1.6.43=h2797004_0 @ e1c11c02
libprotobuf=4.25.3=h08a7969_0 @ e1c11c02
libre2-11=2023.09.01=h5a48ba9_2 @ e1c11c02
libsodium=1.0.18=h36c2ea0_1 @ 16fe1c80
libssh2=1.11.0=h0841786_0 @ e1c11c02
libstdcxx-ng=14.1.0=hc0a3c3a_0 @ e1c11c02
libthrift=0.19.0=hb90f79a_1 @ e1c11c02
libtiff=4.6.0=h1dd3fc0_3 @ e1c11c02
libutf8proc=2.8.0=h166bdaf_0 @ 16fe1c80
libuuid=2.38.1=h0b41bf4_0 @ e1c11c02
libwebp-base=1.4.0=hd590300_0 @ e1c11c02
libxcb=1.15=h0b41bf4_0 @ e1c11c02
libzlib=1.2.13=h4ab18f5_6 @ e1c11c02
lz4-c=1.9.4=hcb278e6_0 @ e1c11c02
markdown=3.6=pyhd8ed1ab_0 @ c7211bb6
markdown-it-py=3.0.0=pyhd8ed1ab_0 @ c7211bb6
markupsafe=2.1.5=py310h2372a71_0 @ e1c11c02
matplotlib-inline=0.1.7=pyhd8ed1ab_0 @ c7211bb6
mdurl=0.1.2=pyhd8ed1ab_0 @ c7211bb6
ncurses=6.2=h58526e2_4 @ 16fe1c80
nest-asyncio=1.6.0=pyhd8ed1ab_0 @ c7211bb6
numpy=1.26.4=py310hb13e2d6_0 @ e1c11c02
openjpeg=2.5.2=h488ebb8_0 @ e1c11c02
openssl=3.3.1=h4ab18f5_1 @ e1c11c02
orc=2.0.1=h17fec99_1 @ e1c11c02
packaging=24.1=pyhd8ed1ab_0 @ c7211bb6
pandas=2.2.2=py310hf9f9076_1 @ e1c11c02
parso=0.8.4=pyhd8ed1ab_0 @ c7211bb6
pexpect=4.9.0=pyhd8ed1ab_0 @ c7211bb6
pickleshare=0.7.5=py_1003 @ fe451c34
pillow=10.3.0=py310hf73ecf8_0 @ e1c11c02
pip=24.0=pyhd8ed1ab_0 @ c7211bb6
pkgutil-resolve-name=1.3.10=pyhd8ed1ab_1 @ c7211bb6
platformdirs=4.2.2=pyhd8ed1ab_0 @ c7211bb6
plotly=5.22.0=pyhd8ed1ab_0 @ c7211bb6
polars=1.1.0=py310h3af5803_0 @ e1c11c02
prompt-toolkit=3.0.47=pyha770c72_0 @ c7211bb6
protobuf=4.25.3=py310ha8c1f0e_0 @ e1c11c02
psutil=6.0.0=py310hc51659f_0 @ e1c11c02
pthread-stubs=0.4=h36c2ea0_1001 @ 16fe1c80
ptyprocess=0.7.0=pyhd3deb0d_0 @ fe451c34
pure_eval=0.2.2=pyhd8ed1ab_0 @ fe451c34
pyarrow=16.1.0=py310h17c5347_1 @ e1c11c02
pyarrow-core=16.1.0=py310h6f79a3a_1_cpu @ e1c11c02
pycparser=2.22=pyhd8ed1ab_0 @ c7211bb6
pydeck=0.8.0=pyhd8ed1ab_0 @ fe451c34
pygments=2.18.0=pyhd8ed1ab_0 @ c7211bb6
pysocks=1.7.1=pyha2e5f31_6 @ fe451c34
python=3.10.2=h543edf9_0_cpython @ 16fe1c80
python-dateutil=2.9.0=pyhd8ed1ab_0 @ c7211bb6
python-tzdata=2024.1=pyhd8ed1ab_0 @ c7211bb6
python_abi=3.10=4_cp310 @ e1c11c02
pytz=2024.1=pyhd8ed1ab_0 @ c7211bb6
pyyaml=6.0.1=py310h2372a71_1 @ e1c11c02
pyzmq=26.0.3=py310h6883aea_0 @ e1c11c02
re2=2023.09.01=h7f4b329_2 @ e1c11c02
readline=8.1=h46c0cb4_0 @ 16fe1c80
referencing=0.35.1=pyhd8ed1ab_0 @ c7211bb6
requests=2.32.3=pyhd8ed1ab_0 @ c7211bb6
retrying=1.3.3=py_2 @ fe451c34
rich=13.7.1=pyhd8ed1ab_0 @ c7211bb6
rpds-py=0.19.0=py310h42e942d_0 @ e1c11c02
s2n=1.4.15=he19d79f_0 @ e1c11c02
setuptools=70.1.1=pyhd8ed1ab_0 @ c7211bb6
six=1.16.0=pyh6c4a22f_0 @ fe451c34
smmap=5.0.0=pyhd8ed1ab_0 @ fe451c34
snappy=1.2.1=ha2e4443_0 @ e1c11c02
sqlite=3.37.0=h9cd32fc_0 @ 16fe1c80
stack_data=0.6.2=pyhd8ed1ab_0 @ c7211bb6
streamlit=1.36.0=pyhd8ed1ab_0 @ c7211bb6
tenacity=8.5.0=pyhd8ed1ab_0 @ c7211bb6
tensorboard=2.17.0=pyhd8ed1ab_0 @ c7211bb6
tensorboard-data-server=0.7.0=py310h75e40e8_1 @ e1c11c02
tk=8.6.13=noxft_h4845f30_101 @ e1c11c02
toml=0.10.2=pyhd8ed1ab_0 @ fe451c34
toolz=0.12.1=pyhd8ed1ab_0 @ c7211bb6
tornado=6.4.1=py310hc51659f_0 @ e1c11c02
traitlets=5.14.3=pyhd8ed1ab_0 @ c7211bb6
typing-extensions=4.12.2=hd8ed1ab_0 @ c7211bb6
typing_extensions=4.12.2=pyha770c72_0 @ c7211bb6
tzdata=2024a=h0c530f3_0 @ c7211bb6
tzlocal=5.2=py310hff52083_0 @ e1c11c02
urllib3=2.2.2=pyhd8ed1ab_1 @ c7211bb6
validators=0.31.0=pyhd8ed1ab_0 @ c7211bb6
watchdog=4.0.1=py310hff52083_0 @ e1c11c02
wcwidth=0.2.13=pyhd8ed1ab_0 @ c7211bb6
werkzeug=3.0.3=pyhd8ed1ab_0 @ c7211bb6
wheel=0.43.0=pyhd8ed1ab_1 @ c7211bb6
widgetsnbextension=4.0.11=pyhd8ed1ab_0 @ c7211bb6
xorg-libxau=1.0.11=hd590300_0 @ e1c11c02
xorg-libxdmcp=1.1.3=h7f98852_0 @ 16fe1c80
xz=5.2.6=h166bdaf_0 @ 16fe1c80
yaml=0.2.5=h7f98852_2 @ 16fe1c80
zeromq=4.3.5=h75354e8_4 @ e1c11c02
zipp=3.19.2=pyhd8ed1ab_0 @ c7211bb6
zlib=1.2.13=h4ab18f5_6 @ e1c11c02
zstandard=0.22.0=py310hab88d88_1 @ e1c11c02
zstd=1.5.6=ha6fb4c9_0 @ e1c11c02

[pip]
brotli==1.1.0
importlib-resources==6.4.0
jupyter-client==8.6.2
jupyter-core==5.7.2
jupyterlab-widgets==3.0.11
pure-eval==0.2.2
stack-data==0.6.2

[conda-metadata]
16fe1c80 - linux-64 @ tar.bz2 @ ri.artifacts.repository.bundle.jupyter-default-environment
c7211bb6 - noarch @ conda @ ri.artifacts.repository.bundle.jupyter-default-environment
e1c11c02 - linux-64 @ conda @ ri.artifacts.repository.bundle.jupyter-default-environment
fe451c34 - noarch @ tar.bz2 @ ri.artifacts.repository.bundle.jupyter-default-environment

[conda lock version]
v3 - 0454ce4598cd475c502df1fe8a15b86ddae33cd74f97c833cb35f122e7555dfe
```

Jupyter®、JupyterLab® 和 Jupyter® 徽标是 NumFOCUS 的商标或注册商标。

TensorBoard 及任何相关标记是 Google Inc. 的商标。

所有提及的第三方商标（包括徽标和图标）均为其各自所有者的财产。不暗示任何关联或认可。
