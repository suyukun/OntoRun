来源: https://palantir.com/docs/zh/foundry/foundryts/functions-scale/

# foundryts.functions.scale

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.functions.scale

## foundryts.functions.scale(factor)

返回一个以指定因子将单个时间序列中的每个值相乘的函数。

对于具有点(timestamp, value)的源时间序列，在以factor进行缩放后，结果缩放的时间序列将具有点(timestamp, value * factor)。

- 参数:factor(float) – 与每个点的值相乘的缩放因子。
- 返回:一个以单个时间序列为输入并返回缩放后时间序列的函数。
- 返回类型:(FunctionNode) ->FunctionNode
## 数据框架模式

| 列名 | 类型 | 描述 |
| --- | --- | --- |
| timestamp | pandas.Timestamp | 点的时间戳 |
| value | float | 点的缩放值 |

timestamp_scale(),value_shift()

此函数仅适用于数值系列。

## 示例

```
Copied!1
2
3
4
5
6
7
>>> scaled = F.scale(1.5)(series)  # 将 series 数据按比例因子 1.5 进行缩放
>>> scaled.to_pandas()  # 将缩放后的数据转换为 pandas DataFrame 格式
                      timestamp     value
0 1970-01-01 00:00:00.000000100  0.000000
1 1970-01-01 00:00:00.000000200       inf  # 表示无穷大
2 1970-01-01 00:00:00.000000300  4.712385
3 1970-01-01 00:00:02.147483647  1.500000
```

这段代码展示了如何将一个数据序列进行缩放操作，并将结果转换为 pandas DataFrame 格式。注意inf表示无穷大的情况。
