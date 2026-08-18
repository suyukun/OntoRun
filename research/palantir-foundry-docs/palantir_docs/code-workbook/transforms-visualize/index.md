来源: https://palantir.com/docs/zh/foundry/code-workbook/transforms-visualize/

# 可视化数据

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 可视化数据

在Code Workbook中，您可以使用开源可视化库来展示数据的可视化效果。然后可以将这些可视化与他人共享，例如在记事本文档中。

## Python可视化

在Python中，Code Workbook支持使用Matplotlib、Seaborn和Plotly进行可视化。

### 使用Matplotlib和Seaborn

使用Matplotlib时，调用matplotlib.pyplot.show()会将生成的图像保存到变换输出中并返回到用户界面，从而允许创建自定义图。与任何可视化一样，您可以通过右键点击图中的变换并选择下载图像来下载此图像。

以下是一个使用Matplotlib渲染可视化的变换示例：

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
def viz_plot_univariate_distribution_using_histogram(input_dataset):
    import matplotlib.mlab as mlab
    import matplotlib.pyplot as plt

    INPUT_DF = input_dataset
    SELECTED_COLUMN = "column_to_plot" # 注意，这里应该是一个数值型列
    NUM_BINS = number_of_bins # number_of_bins 需要在函数之外定义

    # 使用直方图对选定的列进行分布可视化
    bins, counts = INPUT_DF.select(SELECTED_COLUMN).rdd.flatMap(lambda x:x).histogram(NUM_BINS)

    # 绘制直方图
    fig, ax = plt.subplots()
    ax.hist(bins[:-1], bins, weights=counts, density=True)

    ax.set_xlabel(SELECTED_COLUMN) # 设置X轴标签
    ax.set_ylabel('Probability density') # 设置Y轴标签
    ax.set_title(r'Histogram of ' + str(SELECTED_COLUMN)) # 设置图表标题

    # 调整图表布局以防止Y轴标签被截断
    fig.tight_layout()
    plt.show() # 显示图表
```

### 代码说明

这段代码用于对输入数据集中的某个数值型列绘制直方图，以可视化该列的单变量分布。请注意，SELECTED_COLUMN需要在使用前设置为目标列的名称，而number_of_bins则需要在函数调用之前定义为所需的直方图柱子数量。
当使用基于Matplotlib的数据可视化库Seaborn时，您必须调用matplotlib.pyplot.show()以将图像返回到前端。

您可以通过编辑您的配置文件或自定义您的工作簿环境来将Seaborn添加到您的环境中。

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
def seaborn_example(pandas_df):
    import seaborn as sns
    import matplotlib.pyplot as plt

    sns.set_theme()  # 设置Seaborn的主题风格

    # 创建一个可视化图表
    sns.relplot(
        data=pandas_df,
        x="price", y="minimum_nights"  # 使用pandas数据框中的"price"和"minimum_nights"列绘制关系图
    )

    # 显示绘制的图表
    plt.show()
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
def seaborn_violinplot(pandas_df):
    import seaborn as sns
    import matplotlib.pyplot as plt

    # 使用seaborn库绘制小提琴图
    # x: 横轴数据的列名 "col_A"
    # y: 纵轴数据的列名 "col_B"
    # data: 传入的数据集，类型为pandas DataFrame
    sns.violinplot(x="col_A", y="col_B", data=pandas_df);

    # 显示图表
    plt.show()
```

默认情况下，Matplotlib 和 Seaborn 在 Code Workbook 中的可视化输出将以 PNG 格式显示。要以 SVG 格式输出 Matplotlib 和 Seaborn 的可视化，请在绘图前使用以下代码：

set_output_image_type('svg')

或者，使用提示以提高可见性：

```
Copied!1
2
3
4
@output_image_type('svg')
def chart(input):
    # 在此处创建图表
    pass  # 用于占位，没有实际功能，通常在定义函数但不实现时使用
```

在这个代码片段中，@output_image_type('svg')是一个装饰器，用于指定函数输出图像的类型为 SVG 格式。在函数chart中，你可以添加创建图表的代码逻辑。

## 使用Matplotlib绘制不同语言和字体

要在Matplotlib中使用非罗马字符（如日语或韩语）或非默认字体绘制标签和文本，您必须具体指定希望Matplotlib在渲染图像时使用的字体系列。有关更多信息，请参阅默认安装的可用字体列表。

以下是如何为Matplotlib指定字体的示例：

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
def japanese_korean_matplotlib_example():
    import matplotlib.mlab as mlab
    import matplotlib.pyplot as plt
    from matplotlib import rcParams
    # 设置字体为 Noto Sans CJK 字体包，以支持日文和韩文显示
    rcParams['font.family'] = 'Noto Sans CJK JP'

    # 创建数据
    x = [10,20,30,40,50]
    y = [30,30,30,30,30]

    # 绘制线条
    plt.plot(x, y, label = "ライン１")  # 日文标签：线1
    plt.plot(y, x, label = "선2")       # 韩文标签：线2
    plt.xlabel("X-軸")                 # X轴标签为日文
    plt.ylabel("Y-축")                 # Y轴标签为韩文
    plt.legend()                      # 显示图例
    plt.title("日本語ラベル図の例 // 한글 라벨 도표의 예시")  # 图表标题包含日文和韩文
    plt.show()                        # 显示图形
```

对于Matplotlib 2.*，.ttc字体文件不会被Matplotlib自动检测到。可以升级到3.*或直接将字体文件路径添加到Matplotlib的字体管理器中。

```
Copied!1
2
3
4
5
6
7
8
from matplotlib import rcParams
import matplotlib.font_manager as fm

# 添加指定字体文件到字体列表
fm.fontManager.ttflist += fm.createFontList(["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"])

# 设置全局字体为Noto Sans CJK JP
rcParams['font.family'] = 'Noto Sans CJK JP'
```

### 使用Plotly

Plotly是一个可视化库，允许您创建交互式图像。要使用Plotly，请首先确保它已包含在您的环境中。

调用fig.show()会将生成的图像保存为变换输出的一部分并返回到用户界面。以下是一个使用Plotly Express渲染可视化的变换示例。Plotly Express预装了iris数据集。

```
Copied!1
2
3
4
5
6
7
8
def plotly_example():
    import plotly.express as px
    # 使用Plotly Express库导入示例数据集鸢尾花数据
    df = px.data.iris()
    # 创建一个散点图，x轴为萼片宽度，y轴为萼片长度，并根据种类进行着色
    fig = px.scatter(df, x = "sepal_width", y = "sepal_length", color = "species")
    # 显示图表
    fig.show()
```

运行变换后，Plotly可视化将出现在可视化选项卡中。我们建议以全屏模式查看可视化。您可以使用放大和缩小、在图表上进行选择等功能。

这里是一个更复杂的示例，它生成了一个动画可视化。

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
def plotly_example_2():
    import plotly.graph_objects as go
    # 创建一个图形对象
    fig = go.Figure(
        # 设置初始数据为一个简单的散点图，x和y坐标分别为[0, 1]
        data=[go.Scatter(x=[0, 1], y=[0, 1])],
        # 设置图形布局
        layout=go.Layout(
            # 设置x轴范围为[0, 5]，不自动调整
            xaxis=dict(range=[0, 5], autorange=False),
            # 设置y轴范围为[0, 5]，不自动调整
            yaxis=dict(range=[0, 5], autorange=False),
            # 设置初始标题
            title="Start Title",
            # 添加按钮用于触发动画
            updatemenus=[dict(
                type="buttons",
                buttons=[dict(label="Play",
                          method="animate",
                          args=[None])])]
        ),
        # 定义动画帧
        frames=[go.Frame(data=[go.Scatter(x=[1, 2], y=[1, 2])]),
            go.Frame(data=[go.Scatter(x=[1, 4], y=[1, 4])]),
            go.Frame(data=[go.Scatter(x=[3, 4], y=[3, 4])],
                     layout=go.Layout(title_text="End Title"))]
        )

    # 显示图形
    fig.show()
```

## R 可视化

在 R 中，Code Workbook 支持使用 ggplot2 和 plotly 进行可视化。

### 使用 ggplot2

```
Copied!1
2
3
4
5
6
fare_distribution <- function(titanic_dataset) {
    # 绘制票价分布的直方图
    hist(titanic_dataset$Fare)
    # 返回原始数据集
    return(titanic_dataset)
}
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
18
19
20
example_ggplot <- function() {
    library(ggplot2)  # 加载ggplot2库
    theme_set(theme_bw())  # 设置默认主题为黑白主题
    data("midwest", package = "ggplot2")  # 加载midwest数据集

    # 散点图
    gg <- ggplot(midwest, aes(x=area, y=poptotal)) +  # 创建ggplot对象，设置x轴为area，y轴为poptotal
        geom_point(aes(col=state, size=popdensity)) +  # 添加散点，颜色表示州，大小表示人口密度
        geom_smooth(method="loess", se=F) +  # 添加平滑曲线，使用loess方法，se=F表示不显示置信区间
        xlim(c(0, 0.1)) +  # 设置x轴范围
        ylim(c(0, 500000)) +  # 设置y轴范围
        labs(subtitle="Area Vs Population",  # 设置副标题
            y="Population",  # 设置y轴标签
            x="Area",  # 设置x轴标签
            title="Scatterplot",  # 设置图标题
            caption = "Source: midwest")  # 设置图说明

    plot(gg)  # 绘制图形
    return(NULL)  # 返回NULL
}
```

默认情况下，ggplot可视化将以PNG格式输出。要以SVG格式生成R ggplot可视化，请使用注释添加提示：

```
Copied!1
2
3
4
5
6
fare_distribution <- function(titanic_dataset) {
    # image: svg
    # 绘制票价的直方图
    hist(titanic_dataset$Fare)
    return(titanic_dataset)
}
```

要自定义PNG或SVG输出，可以使用内置的graphicsFile变量作为文件名调用png()或svg()函数。

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
unnamed_1 <- function() {
    # 创建一个PNG图像文件
    png(
      filename=graphicsFile, # 图像文件的名称
      width=800,             # 图像宽度，以像素为单位
      height=400,            # 图像高度，以像素为单位
      units="px",            # 指定尺寸单位为像素
      pointsize=4,           # 字体大小
      bg="white",            # 背景颜色为白色
      res=300,               # 图像分辨率为300 DPI
      type="cairo")          # 指定使用cairo类型的设备

    # 绘制简单的线性图，x和y轴从1到10
    plot(1:10, 1:10)
}
```

请注意，如果您想使用自定义的svg()函数，还需要提供上面描述的注释提示。

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
unnamed_1 <- function() {
    # 图像格式：svg
    svg(
      filename=graphicsFile, # 输出文件名
      width=5,               # 图像宽度
      height=9,              # 图像高度
      pointsize=4,           # 字体大小
      bg="white")            # 背景颜色

    plot(1:10, 1:10)         # 绘制图形
}
```

### 使用Plotly

Plotly ↗允许您制作交互式图表。要在R中使用Plotly，请将r-plotly包添加到您的环境中。使用plot()或print()来在前端显示图表。以下是一个简单的例子：

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
plotly_example <- function() {
    library(plotly)    # 加载plotly库，用于创建交互式图表

    scatter_plotly <- plot_ly (
        x = rnorm(1000),  # 生成1000个服从标准正态分布的随机数作为x坐标
        y = rnorm(1000),  # 生成1000个服从标准正态分布的随机数作为y坐标
        mode = "markers", # 设置显示模式为散点图
        type = "scatter"  # 指定图表类型为散点图
    )
    plot(scatter_plotly) # 绘制散点图
}
```

## Plotly 限制

以下说明适用于 Python 和 R。

- 在控制台中，Plotly 可视化将被转换为图像并显示为 PNG。它们将不具有交互性。要查看交互式可视化，请在变换中编写代码。
- 创建 Plotly 可视化时，由于浏览器性能下降，不推荐使用超过 20,000 个点的可视化。如果创建具有大量点的散点图，使用scattergl以获得更好的性能。
## Matplotlib 限制

以下 Matplotlib 的限制适用于 Python。

- Matplotlib 不是线程安全的。↗当运行多个节点时，Spark 将并行运行这些计算。因此，可能会以 Matplotlib 运行时异常的形式或在错误节点中创建的可视化形式显示出意外行为。
- 当运行多个节点时，Spark 将并行运行这些计算。因此，可能会以 Matplotlib 运行时异常的形式或在错误节点中创建的可视化形式显示出意外行为。
- 在单个 Code Workbook 中的不同节点中使用多个 Matplotlib 可视化时，必须锁定每个节点。可以使用线程安全的装饰器@synchronous_node_execution锁定每个节点，如下所示。
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
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from matplotlib import rcParams

@synchronous_node_execution
def thread_safe_node():
    # 设置字体为 Noto Sans CJK 字体包
    rcParams['font.family'] = 'Noto Sans CJK JP'

    # 创建数据
    x = [10,20,30,40,50]
    y = [30,30,30,30,30]

    # 绘制线条
    plt.plot(x, y, label = "라인１")  # 线1
    plt.plot(y, x, label = "선2")  # 线2
    plt.xlabel("X-軸")  # X轴
    plt.ylabel("Y-축")  # Y轴
    plt.legend()
    plt.title("日本語ラベル図の例 // 한글 라벨 도표의 예시")  # 示例图：日语标签和韩语标签
    plt.show()
```

这个代码使用了matplotlib库来绘制一张包含日语和韩语标签的简单图表。通过设置rcParams['font.family']，确保图表能够正确显示 CJK 字体。
