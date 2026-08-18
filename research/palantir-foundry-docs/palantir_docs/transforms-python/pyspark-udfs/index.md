来源: https://palantir.com/docs/zh/foundry/transforms-python/pyspark-udfs/

# 概念: 用户定义函数

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 概念: 用户定义函数

用户定义函数允许您在 PySpark 中使用您自己的任意 Python 代码。例如，您可以使用 UDF 从数据集中每行的复杂文本格式中解析信息。

声明后，UDF 的工作方式类似于内置的 PySpark 函数，如concat、date_diff、trim等。

### 动机

不直观的是，在正常情况下，数据实际上从未进入您的 Python 代码中。当您使用 PySpark 操作数据帧时，您是在描述 Spark 集群应以分布式、并行方式采取的步骤，以获得最终的数据帧。这使得 Spark 和 Foundry 可以几乎无限制地扩展，但引入了 UDF 的小设置，用于注入代码在集群内实际数据上运行。PySpark 将您的 UDF 代码发送到运行查询的每台服务器。

#### 考虑不使用 UDFs

Python 相对于 Spark 优化的内置功能的开销使得 UDFs 相对较慢。考虑使用 PySpark 的内置函数表达您的逻辑。

## 示例

```
Copied!1
2
"Weather report: rain 55-62"
# 天气报告：降雨量55-62
```

假设我们想从以下天气格式中获取低温，在这种情况下为55。我们可以编写以下普通Python函数，

```
Copied!1
2
3
4
5
6
def extract_low_temperature(weather_report):
    # 从天气报告字符串中提取最低温度
    return int(weather_report.split(' ')[-1].split('-')[0])
    # 1. 使用split方法按空格分割字符串，取最后一个元素。
    # 2. 对最后一个元素再次使用split方法按'-'分割，取第一个元素。
    # 3. 将提取的字符串转换为整数后返回。
```

我们将围绕我们的函数extract_low_temperature创建一个UDF，以将其集成到我们的PySpark查询中。创建UDF涉及在PySpark的类型系统中提供我们的函数及其预期返回类型。

```
Copied!1
2
3
4
5
# 导入必要的类型
from pyspark.sql.types import IntegerType

# 将我们的函数包装为一个UDF（用户自定义函数）
low_temp_udf = F.udf(extract_low_temperature, IntegerType())
```

现在可以在DataFrame上使用UDF，将整列作为参数。

```
Copied!1
2
# 使用用户定义函数（UDF）将'df'数据框中'weather_report'列的值转换为'low'列
df = df.withColumn('low', low_temp_udf(F.col('weather_report')))
```

| id | weather_report | low |
| --- | --- | --- |
| 1 | 天气报告: 雨 55-62 | 55 |
| 2 | 天气报告: 晴 69-74 | 69 |
| 3 | 天气报告: 云 31-34 | 31 |

## 从多个列中读取

一个UDF可以接受任意列参数。这些列参数对应于函数参数。

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
from pyspark.sql.types import StringType
import pyspark.sql.functions as F  # 添加导入pyspark.sql.functions模块

def weather_quality(temperature, windy):
    # 定义天气质量函数，判断温度大于70且无风时，返回“good”，否则返回“bad”
    if temperature > 70 and windy == False:
        return "good"
    else:
        return "bad"

# 将Python函数转换为Spark的用户自定义函数（UDF），输出类型为StringType
weather_udf = F.udf(weather_quality, StringType())

# 使用withColumn方法在DataFrame中添加一个新列'quality'，并应用UDF
df = df.withColumn('quality', weather_udf(F.col('temp'), F.col('wind')))
```

| id | 温度 | 风 | 质量 |
| --- | --- | --- | --- |
| 1 | 73 | false | 好 |
| 2 | 36 | false | 差 |
| 3 | 90 | true | 差 |
