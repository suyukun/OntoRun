来源: https://palantir.com/docs/zh/foundry/foundryts/interval/

# foundryts.Interval

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.Interval

## classfoundryts.Interval(start=None, end=None, name=None, metadata=None)

一个由起始和结束时间定义的区间。

区间对于在NodeCollection中分割时间序列为每个区间的时间范围或表示FoundryTS区间函数的结果（例如foundryts.functions.time_series_search()）非常有用。

区间可以包含非必填元数据。

- 参数:start(int|datetime|str,非必填) – 区间的起始时间戳（包含）（默认为pandas..Timestamp.min）。end(int|datetime|str,非必填) – 区间的结束时间戳（不包含）（默认为pandas..Timestamp.min）。name(int|datetime|str,非必填) – 区间的非必填名称（默认为None）。metadata(Dict[str,Any],非必填) – 区间的非必填元数据字典（默认为None）。
- start(int|datetime|str,非必填) – 区间的起始时间戳（包含）（默认为pandas..Timestamp.min）。
- end(int|datetime|str,非必填) – 区间的结束时间戳（不包含）（默认为pandas..Timestamp.min）。
- name(int|datetime|str,非必填) – 区间的非必填名称（默认为None）。
- metadata(Dict[str,Any],非必填) – 区间的非必填元数据字典（默认为None）。
## 示例

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
>>> from foundryts import Interval
>>> interval = Interval(start='2018-01-01', end='2018-02-01', name='january', metadata={'days': 31})
# 创建一个时间区间对象，开始时间为2018年1月1日，结束时间为2018年2月1日，名称为“january”，附加元数据为一个包含天数的字典。
>>> interval
Interval(start='2018-01-01 00:00:00', end='2018-02-01 00:00:00', name='january', metadata={'days': 31})
# 输出interval对象的详细信息，包括开始时间、结束时间、名称和元数据。
>>> interval.name
'january'
# 获取interval对象的名称属性。
>>> interval.metadata['days']
31
# 获取interval对象的元数据中“days”键对应的值。
```

#### 属性end

结束时间为codex_core.Timestamp。

#### 属性end_codex

Interval.end()的副本，未来将迁移为返回Python本地的非codex Conjure类型。

#### 属性end_native

结束时间为int | datetime | str。

#### 属性end_ns

以纳秒为单位的结束时间。

#### 属性metadata

返回元数据字典。

#### 属性name

区间的名称。

#### 属性start

起始时间为codex_core.Timestamp。

#### 属性start_codex

Interval.start()的副本，未来将迁移为返回Python本地的非codex Conjure类型。

#### 属性start_native

起始时间为int | datetime | str。

#### 属性start_ns

以纳秒为单位的起始时间。
