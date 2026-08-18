来源: https://palantir.com/docs/zh/foundry/sap/backup-restore/

# 备份和恢复 Palantir Foundry Connector 2.0 以用于 SAP 应用程序

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 备份和恢复 Palantir Foundry Connector 2.0 以用于 SAP 应用程序

Palantir Foundry Connector 2.0 以用于 SAP 应用程序的认证保证在系统迁移或卸载时可以进行备份和恢复。以下部分解释了如何在需要时备份和恢复 Connector。

## 先决条件

- Palantir Foundry Connector 2.0 以用于 SAP 应用程序 SP13 或更高版本
## 备份重要表

要将表备份为 .zip 文件并下载到文件系统以供后续使用，请运行/n/palantir/backup事务代码。这将备份所有 Connector 表及其内容。

以下表包含在 Connector 备份中：

- /PALANTIR/AGT_01：远程代理配置头表。包含代理 ID 和描述。
- /PALANTIR/AGT_02：远程代理配置项表。包含所有代理特定参数，如到代理的 RFC 连接、资源检查设置、页面大小等。
- /PALANTIR/CFG_01：Connector 参数。包含 Connector 特定参数，如提取器默认值、对象类型设置、资源检查等。
- /PALANTIR/CFG_02：敏感数据配置表。包含关于数据掩码、哈希和加密的对象和字段级设置。
- /PALANTIR/CFG_03：预筛选配置表。包含 Connector 的对象级筛选，独立于 Foundry 同步上的筛选。
- /PALANTIR/ENC_01：加密密钥
- /PALANTIR/INC_01：增量数据流头表。包含增量设置，如增量字段、增量类型等。
- /PALANTIR/INC_02：增量数据流项目表。包含 Foundry 请求的历史增量值，以及这些请求是否成功提取到 Foundry。
- /PALANTIR/JOB：未来页面 ID 的任务
- /PALANTIR/PAG_01：页面头表
## 恢复重要的 Connector 表

完成 SAP 系统迁移或维护后，可以再次安装 Connector。为了使数据提取正常继续，需要恢复 Connector 指针和系统设置。

- 要恢复这些表，请运行/n/palantir/restore事务代码。这将从备份中恢复所有 Connector 表及其内容。
- 检查表的配置参数和内容。