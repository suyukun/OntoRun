来源: https://palantir.com/docs/zh/foundry/transforms-python/debugging/

# 调试

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 调试

本指南概述了在Transforms Python中可用的调试技术。有关错误和异常的更多信息可以在Python 文档 ↗中找到。

## 使用调试器

调试Python变换的一个有用工具是代码库调试器。了解更多关于调试器的信息。

## 阅读Python追溯

在Python中，追溯相当于Java中的堆栈跟踪。在Python中，任何未处理的异常都会导致追溯，其中包括带有错误消息的堆栈跟踪。
大多数Transforms Python运行时失败会以追溯的形式出现，因此了解如何阅读追溯非常重要。

请考虑以下代码示例：

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
class Stats(object):

    nums = []

    def add(self, n):
        self.nums.append(n)

    def sum(self):
        return sum(self.nums)

    def avg(self):
        return self.sum() / len(self.nums)


def main():
    # 这里应该是Stats类，而不是Statistics
    stats = Stats()
    stats.add(1)
    stats.add(2)
    stats.add(3)
    print(stats.avg())  # 打印平均值
```

### 修改说明

- 修正了main()函数中创建对象时的类名错误，将Statistics改为Stats。
- 在print语句中添加括号以符合Python 3的语法。
运行此代码会导致以下追溯：
```
Copied!1
2
3
4
5
6
Traceback (most recent call last):
  File "test.py", line 26, in <module>
    main()
  File "test.py", line 16, in main
    stats = Statistics()
NameError: global name 'Statistics' is not defined  # NameError 表示代码中使用了一个未定义的名称。在这里，'Statistics' 类或函数没有定义或没有正确导入。
```

与Java堆栈跟踪不同，Python回溯显示最近的调用在最后。因此，从下往上阅读，回溯显示：

- 异常名称：NameError↗。
有许多内置Python异常类 ↗，但代码也可以定义自己的异常类。
- 异常消息：全局名称 'Statistics' 未定义。
此消息包含用于调试目的的最有用信息。
- 导致抛出异常的函数调用序列：File "test.py", line 26, in <module>，随后是相关的代码行（第16行）。
使用此回溯，我们可以看到异常发生在test.py的第16行的main方法中。具体来说，导致错误的代码行是stats = Statistics()，抛出的异常是NameError。由此，我们可以推断出名称“Statistics”不存在。回顾我们的示例代码，似乎我们是想使用名称“Stats”而不是“Statistics”。

## 日志记录

您应该使用标准的Python日志模块 ↗。

有关读取日志的更多详细信息，请参阅日志阅读信息部分。

仅保存INFO级别及更高级别的日志。

以下代码示例展示了如何输出日志以帮助调试：

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
 from transforms.api import transform_df, Input, Output
 from myproject.datasets import utils
 import logging

 log = logging.getLogger(__name__)  # 创建一个日志记录器

 @transform_df(
     Output("/path/to/output/dataset"),  # 指定输出数据集的路径
     my_input=Input("/path/to/input/dataset"),  # 指定输入数据集的路径
 )
 def my_compute_function(my_input):
     log.info("Input size: %d", my_input.count())  # 记录输入数据集的大小
     return my_input  # 返回输入数据集
```
