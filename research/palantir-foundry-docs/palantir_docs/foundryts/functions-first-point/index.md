来源: https://palantir.com/docs/zh/foundry/foundryts/functions-first-point/

# foundryts.functions.first_point

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.functions.first_point

## foundryts.functions.first_point()

返回一个提取单个时间序列中最早点的函数。

返回的点是给定时间序列范围内首次出现的点。
当序列为空时，返回一个空的汇总。

- 返回:一个接受单个时间序列并返回提供的序列中第一个点的函数。数据帧包含一行记录了第一个点。
- 返回类型:(函数节点) -> 汇总节点
## 数据帧模式

| 列名 | 类型 | 描述 |
| --- | --- | --- |
| timestamp | pandas.Timestamp | 点的时间戳 |
| value | Union[float, str] | 点的值 |

time_extent(),last_point()

## 示例

```
Copied!1
2
3
4
>>> fp = F.first_point()(series)  # 调用first_point函数获取序列中的第一个数据点
>>> fp.to_pandas()  # 将结果转换为Pandas DataFrame格式
                      timestamp  value
0 1970-01-01 00:00:00.000000001    0.0
```
