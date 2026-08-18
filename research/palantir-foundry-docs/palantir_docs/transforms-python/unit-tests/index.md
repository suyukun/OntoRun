来源: https://palantir.com/docs/zh/foundry/transforms-python/unit-tests/

# 单元测试

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 单元测试

此页面描述的Python库单元测试仅适用于批处理管道，不支持流处理管道。

Python库可以选择将测试作为检查的一部分运行。这些测试使用流行的Python测试框架PyTest ↗运行。

## CI任务: condaPackRun

所有CI检查中都包含condaPackRun及其他任务。

condaPackRun负责安装环境。每个工件从适当的通道检索，Conda使用这些工件来构建环境。此任务包含三个阶段：

- 下载并提取解决环境中的所有软件包。
- 验证软件包内容。根据配置，Conda将使用校验和或验证文件大小是否正确。
- 将软件包链接到环境中。
环境规范存储在隐藏文件中，作为下一次构建的缓存：

- conda-version-run.linux-64.lock
- conda-version-test.linux-64.lock
缓存存储7天。如果meta.yaml文件发生任何更改，则重新缓存。

此任务在很大程度上依赖于添加到库中的软件包数量。添加的软件包越多，任务运行得越慢。

## 启用风格检查

可以通过在Python项目的build.gradle文件中应用com.palantir.conda.pep8和com.palantir.conda.pylintGradle插件来启用PEP8 / PyLint风格检查。对于变换库，这个文件位于Python子项目中。对于库库，这个文件位于根文件夹中。
变换的build.gradle文件看起来可能是这样的：

```
Copied!1
2
3
4
5
6
apply plugin: 'com.palantir.transforms.lang.python'
apply plugin: 'com.palantir.transforms.lang.python-defaults'

// 应用 pep8 代码风格检查插件
apply plugin: 'com.palantir.conda.pep8'
apply plugin: 'com.palantir.conda.pylint' // 应用 pylint 代码检查插件
```

在您的Python项目中，可以在src/.pylintrc中配置PyLint。例如，可以禁用特定消息：

```
Copied!1
2
3
4
[MESSAGES CONTROL]
disable =
    missing-module-docstring,  # 禁用模块缺少文档字符串的警告
    missing-function-docstring  # 禁用函数缺少文档字符串的警告
```

并非所有PyLint配置都能在Foundry中正常工作。如果src/.pylintrc中的某个功能未显示在Checks中，则表明该功能不被支持。

## 启用Spark反模式插件

可以通过在Python项目的build.gradle文件中应用com.palantir.transforms.lang.antipattern-linterGradle插件来启用Spark反模式linter。

```
Copied!1
2
// 应用反模式代码检查插件
apply plugin: 'com.palantir.transforms.lang.antipattern-linter'
```

Spark反模式插件将警告在Spark中使用常见的反模式，例如正确性问题、糟糕的Spark性能和安全隐患。

## 启用测试

可以通过在Python项目的build.gradle文件中应用com.palantir.transforms.lang.pytest-defaultsGradle插件来启用测试。对于变换库，这在Python子项目中。对于库库，这在根文件夹中。
变换的build.gradle文件看起来像这样：

```
Copied!1
2
3
4
5
apply plugin: 'com.palantir.transforms.lang.python' // 应用Python转换插件
apply plugin: 'com.palantir.transforms.lang.python-defaults' // 应用Python默认设置插件

// Apply the testing plugin
apply plugin: 'com.palantir.transforms.lang.pytest-defaults' // 应用Pytest默认测试插件
```

一个库build.gradle看起来像这样：

```
Copied!1
2
3
4
5
6
7
8
apply plugin: 'com.palantir.transforms.lang.python-library'
apply plugin: 'com.palantir.transforms.lang.python-library-defaults'

// 应用测试插件
apply plugin: 'com.palantir.transforms.lang.pytest-defaults'

// 仅对标记的版本（距离上次git标签无提交）进行发布
condaLibraryPublish.onlyIf { versionDetails().commitDistance == 0 }
```

在meta.yaml中定义的运行时需求将在您的测试中可用。其他需求也可以在conda test section ↗中指定。

## 编写测试

完整文档可在https://docs.pytest.org ↗找到。

PyTest 会在任何以test_开头或以_test.py结尾的 Python 文件中找到测试。建议将所有测试放在项目的src目录下的test包中。测试是以test_前缀命名的 Python 函数，断言使用 Python 的assert语句。PyTest 还会运行使用 Python 内置的unittest↗模块编写的测试。
例如，在transforms-python/src/test/test_increment.py中，一个简单的测试如下所示：

```
Copied!1
2
3
4
5
6
7
def increment(num):
    # 将输入的数字加1
    return num + 1

def test_increment():
    # 测试increment函数是否正确：3加1应等于4
    assert increment(3) == 4
```

运行此测试将导致检查失败，并显示如下消息：

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
# 这是一个测试会话的输出，显示测试失败的情况。

============================= test session starts =============================
collected 1 item  # 收集了1个测试项

test_increment.py F                                                       [100%]  # 测试失败

# 详细的失败信息
================================== FAILURES ===================================
_______________________________ test_increment ________________________________

def test_increment():
    # 这里的断言期望increment(3)应该等于5
>   assert increment(3) == 5
    # 但是实际结果是increment(3)返回了4
E       assert 4 == 5
E        +  where 4 = increment(3)

test_increment.py:5: AssertionError  # 失败发生在test_increment.py文件的第5行
========================== 1 failed in 0.08 seconds ===========================  # 总共1个失败，测试耗时0.08秒
```

## 使用PySpark进行测试

PyTest fixtures ↗是一个强大的功能，通过添加同名参数，可以将值注入到测试函数中。此功能被用于在测试函数中提供一个spark_sessionfixture。例如：

```
Copied!1
2
3
4
5
6
def test_dataframe(spark_session):
    # 使用 SparkSession 创建一个 DataFrame，包含两列：'letter' 和 'number'
    df = spark_session.createDataFrame([['a', 1], ['b', 2]], ['letter', 'number'])

    # 断言 DataFrame 的 schema 名称与预期的列表 ['letter', 'number'] 相同
    assert df.schema.names == ['letter', 'number']
```

## 从CSV创建测试输入

CSV文件可以存储在代码库中，并作为测试数据变换的测试输入。

以下部分展示了一个示例，假设以下数据变换在transforms-python/src/myproject/datasets/中编写

find_aircraft.py

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
from pyspark.sql import functions as F
from transforms.api import transform_df, Input, Output


@transform_df(
    Output("<output_dataset_rid>"),
    aircraft_df=Input("<input_dataset_rid>"),
)
def compute(aircraft_df):
    # 过滤条件：只保留座位数大于300且运营状态为"Yes"的航班数据
    return aircraft_df.filter((F.col("number_of_seats") > F.lit(300)) & (F.col("operating_status") == F.lit("Yes")))
```

以下是文件夹中的两个CSV文件及其各自的内容：transforms-python/src/test/resources/：

aircraft_mock.csv

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
tail_number,serial_number,manufacture_year,manufacturer,model,number_of_seats,capacity_in_pounds,operating_status,aircraft_status,acquisition_date,model_type
AAA1,20809,1990,Manufacturer_1,M1-100,1,3500,Yes,Owned,13/8/90,208
# tail_number: 飞机尾号
# serial_number: 序列号
# manufacture_year: 制造年份
# manufacturer: 制造商
# model: 型号
# number_of_seats: 座位数量
# capacity_in_pounds: 载重量（磅）
# operating_status: 运营状态（Yes/No）
# aircraft_status: 飞机状态（Owned/Leased）
# acquisition_date: 购置日期
# model_type: 型号类型

BBB1,46970,2013,Manufacturer_2,M2-300,310,108500,No,Owned,10/15/14,777
CCC1,44662,2013,Manufacturer_2,M2-300,310,108500,Yes,Owned,6/23/13,777
DDD1,58340,2014,Manufacturer_3,M3-200,294,100000,Yes,Leased,11/21/13,330
EEE1,58600,2013,Manufacturer_2,M2-300,300,47200,Yes,Leased,12/2/13,777
```

这个CSV文件包含了飞机的基本信息，包括飞机尾号、序列号、制造年份、制造商、型号、座位数量、载重量、运营状态、飞机状态、购置日期和型号类型。这些信息可以用于管理和追踪飞机的运营和维护情况。expected_filtered_aircraft.csv

```
Copied!1
2
tail_number,serial_number,manufacture_year,manufacturer,model,number_of_seats,capacity_in_pounds,operating_status,aircraft_status,acquisition_date,model_type
CCC1,44662,2013,Manufacturer_2,M2-300,310,108500,Yes,Owned,6/23/13,777
```

这个数据是一组航空器的信息，字段解释如下：

- tail_number：飞机尾号
- serial_number：序列号
- manufacture_year：制造年份
- manufacturer：制造商
- model：型号
- number_of_seats：座位数
- capacity_in_pounds：载重量（以磅为单位）
- operating_status：运营状态（是/否）
- aircraft_status：飞机状态（拥有/租赁）
- acquisition_date：获取日期
- model_type：型号类别
给出的示例数据表示一架由Manufacturer_2制造的M2-300型号飞机，制造于2013年，拥有310个座位，载重量为108500磅，该飞机在2013年6月23日被获取，目前处于运营状态并为自有资产。型号类别为777。
以下测试可以在路径transforms-python/src/test/编写：

test_find_aircraft.py

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
import os
from pathlib import Path
from myproject.datasets.find_aircraft import compute

# 定义测试资源目录的路径
TEST_RESOURCES_DIRECTORY_PATH = Path(os.path.dirname(__file__)).joinpath('resources')

def test_find_aircrafts(spark_session):
    # 读取模拟的飞机数据CSV文件为DataFrame
    aircraft_mock_df = spark_session.read.csv(
       str(TEST_RESOURCES_DIRECTORY_PATH.joinpath('aircraft_mock.csv')),
       inferSchema=True,  # 自动推断数据类型
       header=True  # 第一行作为列名
    )

    # 读取期望的过滤后飞机数据CSV文件为DataFrame
    expected_filtered_aircraft_df = spark_session.read.csv(
       str(TEST_RESOURCES_DIRECTORY_PATH.joinpath('expected_filtered_aircraft.csv')),
       inferSchema=True,
       header=True
    )

    # 调用compute函数进行实际数据处理
    result_df = compute(aircraft_mock_df)

    # 验证处理后的DataFrame列名与期望的DataFrame列名一致
    assert result_df.columns == expected_filtered_aircraft_df.columns
    # 验证处理后的DataFrame行数与期望的DataFrame行数一致
    assert result_df.count() == expected_filtered_aircraft_df.count()
    # 验证处理后的DataFrame与期望的DataFrame内容一致
    assert result_df.exceptAll(expected_filtered_aircraft_df).count() == 0
    assert expected_filtered_aircraft_df.exceptAll(result_df).count() == 0
```

在这个Python代码中，我们利用了Apache Spark的DataFrame来测试一个函数compute，确保其返回的结果与期望的数据一致。通过读取CSV文件，我们可以将数据载入DataFrame，并进行列名、行数和内容的逐一比较。
最终的代码库结构将如下图所示：

测试位于transforms-python/src/test/test_find_aircraft.py中。输入和预期输出的 CSV 资源位于transforms-python/src/test/resources中。

## 拦截transform()装饰器中的已写入数据框

当变换函数使用transform()装饰而不是transform_df时，变换函数将不再返回结果数据框，而是使用作为参数传递给函数的Output对象之一在数据集中物化结果。为了测试逻辑，您需要对Output参数使用模拟，以拦截要物化的值。

假设上述数据变换更改为使用transform()装饰器：

find_aircraft_transform_decorator.py

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
from pyspark.sql import functions as F
from transforms.api import transform, Input, Output

# 定义一个转换函数，装饰器指定了输入和输出的数据集
@transform(
    results_output=Output("<output_dataset_rid>"),  # 输出数据集的标识符
    aircraft_input=Input("<input_dataset_rid>"),    # 输入数据集的标识符
)
def compute(results_output, aircraft_input):
    # 从输入数据集中获取DataFrame
    aircraft_df = aircraft_input.dataframe()

    # 过滤出座位数量大于300且运营状态为"Yes"的航班记录
    results_df = aircraft_df.filter((F.col("number_of_seats") > F.lit(300)) & (F.col("operating_status") == F.lit("Yes")))

    # 将过滤后的DataFrame写入到输出数据集中
    results_output.write_dataframe(results_df)
```

在验证测试期间，变换函数现在期望Input()作为aircraft_input参数，并且需要拦截发送到results_output的result_df值。

MagicMock ↗可以被用于在两个实例上创建必要的包装器。

test_find_aircraft_transform_decorator.py

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
import os
from pathlib import Path
from unittest.mock import MagicMock
from myproject.datasets.find_aircraft_transform_decorator import compute
from transforms.api import Input

# 定义测试资源目录路径
TEST_RESOURCES_DIRECTORY_PATH = Path(os.path.dirname(__file__)).joinpath('resources')

def test_find_aircrafts(spark_session):
    # 读取飞机模拟数据集
    aircraft_mock_df = spark_session.read.csv(
       str(TEST_RESOURCES_DIRECTORY_PATH.joinpath('aircraft_mock.csv')),
       inferSchema=True,
       header=True
    )

    # 读取预期的过滤后的飞机数据集
    expected_filtered_aircraft_df = spark_session.read.csv(
       str(TEST_RESOURCES_DIRECTORY_PATH.joinpath('expected_filtered_aircraft.csv')),
       inferSchema=True,
       header=True
    )

    # 创建一个用于输出的模拟对象
    results_output_mock = MagicMock()

    # 创建输入的包装器并配置返回的数据集
    aircraft_mock_input = Input()
    aircraft_mock_input.dataframe = MagicMock(return_value=aircraft_mock_df)

    # 使用模拟输出对象运行转换
    compute(
        results_output=results_output_mock,
        aircraft_input=aircraft_mock_input
    )

    # 拦截调用模拟对象的write_dataframe时传递的参数，并提取准备写入的数据框
    args, kwargs = results_output_mock.write_dataframe.call_args
    result_df = args[0]

    # 断言结果数据框的列与预期的过滤后数据框的列相同
    assert result_df.columns == expected_filtered_aircraft_df.columns
    # 断言结果数据框的行数与预期的过滤后数据框的行数相同
    assert result_df.count() == expected_filtered_aircraft_df.count()
    # 断言结果数据框与预期的过滤后数据框之间没有差异
    assert result_df.exceptAll(expected_filtered_aircraft_df).count() == 0
    assert expected_filtered_aircraft_df.exceptAll(result_df).count() == 0
```

这段代码是一个基于 PySpark 的单元测试，用于验证compute函数的输出是否符合预期。它使用了模拟对象来替代实际的输入和输出，从而专注于逻辑验证。

## 查看测试输出

任何配置的测试输出将显示在Checks标签中，每个测试都有单独的输出。默认情况下，测试结果将以折叠状态显示，状态为：PASSED、FAILED 或 SKIPPED。展开每个测试（或展开所有测试）将显示测试输出以及StdOut和StdErr日志。

## 测试覆盖率

PyTest 覆盖率 ↗可以被用于在计算覆盖率并在你的存储库上强制执行最低百分比。

将以下内容添加到存储库的meta.yml中：

```
Copied!1
2
3
test:
  requires:
    - pytest-cov  # 需要安装 pytest-cov 库
```

在/transforms-python/src/pytest.ini创建一个pytest.ini文件，内容如下：

```
Copied!1
2
3
4
5
6
7
[pytest]
addopts = --cov=<<package name, e.g. myproject>> --cov-report term --cov-fail-under=100

# 该配置用于pytest测试框架中的代码覆盖率设置。
# --cov=<<package name, e.g. myproject>> 用于指定要测量覆盖率的包名。
# --cov-report term 指定将覆盖率报告输出到终端。
# --cov-fail-under=100 指定覆盖率低于100%时测试失败。
```

所需的覆盖率以使检查失败是可定制的；为--cov-fail-under参数选择一个百分比。

运行测试的覆盖率低于规定数量现在将失败，并显示此输出：

## 并行化测试

默认情况下，PyTest 顺序运行测试。可以通过调整变换中的build.gradle，将numProcesses设置为反映使用多少个进程的值，以将测试发送到多个 CPU，从而加快测试运行速度。

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
apply plugin: 'com.palantir.transforms.lang.python'
apply plugin: 'com.palantir.transforms.lang.python-defaults'

// 应用测试插件
apply plugin: 'com.palantir.transforms.lang.pytest-defaults'

tasks.pytest {
    numProcesses "3" // 设置pytest并发进程数为3
}
```

测试并行化是使用pytest-xdist ↗测试插件运行的。

并行化测试将涉及将待测测试发送到任何可用的工作者，没有任何顺序保证。任何需要全局/共享状态并预期其他先行测试更改的测试都应相应调整。

## 提示

- 启用这些测试后，当您提交时，您应该会在CI日志中看到:transforms-python:pytest任务正在运行。
- 测试是基于文件和函数名称开头的test_进行发现的。这是 PyTest 约定的标准。
- 获取示例记录的快捷方式是打开代码工作簿控制台中的数据集并调用.collect()。
- 要获取 Python 格式的模式，打开数据集预览，然后打开Columns选项卡，点击Copy，然后选择Copy PySpark Schema。