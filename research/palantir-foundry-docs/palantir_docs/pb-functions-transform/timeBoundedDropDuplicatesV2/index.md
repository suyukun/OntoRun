来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/timeBoundedDropDuplicatesV2/

# 时间限制去重

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 时间限制去重

> 支持于: 流处理

支持于: 流处理

从输入中删除给定列子集的重复行，已看到的行将在配置的事件时间后失效。超过配置的事件时间迟到的行将始终被删除。按指定的键进行分区。每个去重将针对不同的键列值分别计算。

变换类别: 其他

## 声明的参数

- Dataset- 要去重行的数据集。Table
- Key expiration time unit- 等待数据去重的时间单位。Enum<Days, Hours, Milliseconds, Minutes, Seconds, Weeks>
- Key expiration time value- 等待数据去重的时间值。Literal<Long>
- 非必填Column subset- 如果指定了任何列，则仅在确定唯一性时使用这些列。Set<Column<AnyType>>
- 非必填Key by columns- 用于按键对输入进行分区的列。每个去重将在每个不同的键值上并行分别计算。Set<Column<AnyType>>
## 示例

在所有表中，最近流入的行出现在较高位置。此外，每个示例都使用如下所示的时间限制去重节点：

### 流入记录更新水印

输入

| row_order | day | temperature | measurement_timestamp |
| --- | --- | --- | --- |
| 4 | Monday | 10.4 | 2024-09-30T00:00:28 |
| 3 | Monday | 10.3 | 2024-09-30T00:00:18 |
| 2 | Monday | 10.2 | 2024-09-30T00:00:09 |
| 1 | Monday | 10.1 | 2024-09-30T00:00:00 |

输出

| day | temperature | measurement_timestamp |
| --- | --- | --- |
| Monday | 10.4 | 2024-09-30T00:00:28 |
| Monday | 10.1 | 2024-09-30T00:00:00 |

解释: 温度为10.2和10.3的记录在与前一条记录的时间间隔10秒的阈值内到达。因此，这些额外的记录不会被发出。时间戳递增意味着水印为这些记录中的每一个都得到更新。这就是为什么温度为10.3的记录没有被发出，尽管它是在温度为10.1的第一条记录10秒后到达的。最后流入的行，温度为10.4，比最后更新水印的行（温度为10.3的行）晚10秒以上到达，因此被发出。

### 延迟事件被丢弃且不更新水印

输入

| row_order | day | temperature | measurement_timestamp |
| --- | --- | --- | --- |
| 4 | Monday | 10.4 | 2024-09-30T00:00:30 |
| 3 | Monday | 10.3 | 2024-09-30T00:00:00 |
| 2 | Monday | 10.2 | 2024-09-30T00:00:05 |
| 1 | Monday | 10.1 | 2024-09-30T00:00:20 |

输出

| day | temperature | measurement_timestamp |
| --- | --- | --- |
| Monday | 10.4 | 2024-09-30T00:00:30 |
| Monday | 10.1 | 2024-09-30T00:00:20 |

解释: 温度为10.2和10.3的记录在温度为10.1的记录之后到达，但它们的时间戳较早。因此，这些记录被丢弃且不推进水印。最后流入的行，温度为10.4，在更新水印的最后一行（温度为10.1的行）之后的10秒阈值时间间隔后到达，因此被发出。
