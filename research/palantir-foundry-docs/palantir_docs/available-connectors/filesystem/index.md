来源: https://palantir.com/docs/zh/foundry/available-connectors/filesystem/

# 代理级文件系统

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 代理级文件系统

存储在代理磁盘上的文件可以使用文件系统源类型同步到Foundry中。

这种源类型可以通过在代理主机上挂载NFS或NAS并适当地配置根目录，将数据从网络文件系统↗(NFS) 或网络附加存储↗(NAS) 同步到Foundry中。

## 支持的功能

| 功能 | 状态 |
| --- | --- |
| 探索 | 🟢 一般可用 |
| 批量导入 | 🟢 一般可用 |
| 增量 | 🟢 一般可用 |
| 文件以导出 | 🟢 一般可用 |

## 配置

| 参数 | 必需? | 默认值 | 描述 |
| --- | --- | --- | --- |
| rootDirectory | Y |  | 包含数据的根目录。 |
| fileMustNotChangeDuration | N | PT2.0S | 文件在被考虑上传之前必须保持不变的时间量（以ISO-8601 ↗）。注意：如果可能，使用更高效的lastModifiedBefore处理器。 |

示例：

```
Copied!1
2
3
myDirectorySource:
    type:           directory  # 数据源类型为目录
    rootDirectory:  /foo/bar   # 根目录路径
```

数据连接排除所有符号链接，无论这些链接是指向文件还是文件夹。
