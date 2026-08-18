来源: https://palantir.com/docs/zh/foundry/available-connectors/amazon-kinesis/

# Amazon Kinesis

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Amazon Kinesis

将 Foundry 连接到 Amazon Kinesis，以实时从 Kinesis 流读取数据到 Foundry 流中。

## 支持的功能

| 功能 | 状态 |
| --- | --- |
| 探索 | 🟢 普遍可用 |
| 流同步 | 🟢 普遍可用 |
| 流导出 | 🟢 普遍可用 |

## 数据模型

| partition_key (字符串) | data (字符串) | kinesis_ingestion_timestamp (时间戳) | foundry_ingestion_timestamp (时间戳) |
| --- | --- | --- | --- |
| London | {"firstName": "John", "lastName": "Doe"} | 2023-07-12T15:12:42.371Z | 2023-07-12T15:12:42.512Z |
| Paris | {"firstName": "Jean", "lastName": "DuPont"} | 2023-07-12T15:12:42.418Z | 2023-07-12T15:12:42.512Z |

Kinesis 连接器将消息内容解析为 Unicode 字符串。使用下游流变换（例如，Pipeline Builder中的parse_json）解析结构化数据。

- partition_key列将包含用于将消息发布到 Kinesis 的分区键。
- kinesis_ingestion_timestamp列将包含将消息发布到 Kinesis 的时间戳。
- foundry_ingestion_timestamp列将包含消息被 Foundry 吸收的时间戳。
## 性能和限制

连接器始终在源 Kinesis 流的每个活动分片上使用单个消费者线程。

流同步旨在成为一致的、长期运行的任务。任何流同步的中断都是潜在的中断，具体取决于预期的结果。

目前，流同步有以下限制：

- 代理连接的任务在维护窗口期间重启（通常每周一次）以获取升级。预期停机时间少于五分钟。
- 直接连接的任务至少每48小时重启一次。预期停机时间为个位数分钟（假设资源可用允许任务立即重启）。
我们建议通过每个源的两个代理进行连接，以最小化停机时间。确保代理没有重叠的维护窗口。

## 消息顺序

Kinesis 连接器保证具有相同partition_key的消息的传递顺序。具有不同partition_key值的消息可能以任何顺序处理。

## 设置

- 打开数据连接应用程序，并在屏幕右上角选择**+ 新建源**。
- 从可用的连接器类型中选择Kinesis。
- 选择通过互联网使用直接连接或通过中介代理进行连接。我们建议通过每个源的两个代理进行连接，以最小化停机时间。确保代理没有重叠的维护窗口。
- 我们建议通过每个源的两个代理进行连接，以最小化停机时间。确保代理没有重叠的维护窗口。
- 根据下列部分的信息，按照其他配置提示继续设置连接器。
了解更多关于在 Foundry 中设置连接器的信息。

### 连接设置

| 参数 | 必填？ | 默认值 | 描述 |
| --- | --- | --- | --- |
| AWS 区域 | 是 | us-east-1 | 您的 Kinesis 流所在的 AWS 区域。 |

### 认证

为您的 Kinesis 连接选择一种认证方法：AWS 实例或静态凭证。

以下是一个 IAM 策略示例，包含从指定 kinesis 流读取和写入所需权限的示例。

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
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadKinesisStream",
      "Effect": "Allow",
      "Action": [
        "kinesis:ListShards", // 列出分片
        "kinesis:GetShardIterator", // 获取分片迭代器
        "kinesis:GetRecords", // 获取记录
        "kinesis:DescribeStream" // 描述流
      ],
      "Resource": "arn:aws:kinesis:us-east-1:123456789012:stream/read-stream-name" // 读取流的资源 ARN
    },
    {
        "Sid": "WriteKinesisStream",
        "Effect": "Allow",
        "Action": [
            "kinesis:PutRecords" // 写入记录
        ],
        "Resource": "arn:aws:kinesis:us-east-1:123456789012:stream/write-stream-name" // 写入流的资源 ARN
    }
  ]
}
```

此 JSON 配置定义了 AWS IAM 策略，用于 Kinesis 数据流的读取和写入权限。

#### AWS 实例

AWS 实例认证仅在通过代理连接时可用，不能直接连接。

当您的 Foundry 代理运行在具有预配置 IAM 角色的 AWS 资源（例如 EC2 实例）上时，Kinesis 连接器将使用预配置的 IAM 角色连接到 Kinesis 流。不需要额外的配置。

#### 静态凭证

静态凭证指的是标准的 AWS 认证，使用与 IAM 用户绑定的访问密钥 ID 和秘密访问密钥。

| 参数 | 是否必需 | 默认值 |
| --- | --- | --- |
| 访问密钥 ID | 是 | 无 |
| 秘密访问密钥 | 是 | 无 |

### STS 角色

Kinesis 连接器可以选择在连接到 Kinesis 流之前承担一个 STS 角色。有关这些参数的详细信息，请参考AWS 文档 ↗。

| 参数 | 是否必需 | 默认值 |
| --- | --- | --- |
| 角色 ARN | 是 | 无 |
| 角色会话名称 | 是 | 无 |
| 角色会话持续时间 | 是 | 900 |
| 外部 ID | 否 | 无 |

### 网络

连接器必须可以访问 AWS Kinesis API，如果使用 STS 角色，则还需访问 AWS STS API。

- Kinesis API:https://kinesis.<region>.amazonaws.com
- STS API:https://sts.<region>.amazonaws.com
## 从 Kinesis 同步数据

了解如何在设置流式同步教程中设置与 Kinesis 的同步。

## 以 Kinesis 格式导出数据

连接器支持在数据连接中以外部 Kinesis 流的方式导出。

要以 Kinesis 格式导出，首先为您的 Kinesis 连接器启用导出。然后，创建一个新的导出。

### 导出配置选项

| 选项 | 是否必需 | 默认值 | 描述 |
| --- | --- | --- | --- |
| 输出流 ARN | 是 | N/A | 您希望导出的 Kinesis 流的 ARN。 |
| 分区列 | 是 | 第一个字符串列 | 将用于确定数据记录在流中属于哪个分片的列。必须是一个字符串值，通常是主键。查看AWS 文档 ↗获取更多信息。 |
