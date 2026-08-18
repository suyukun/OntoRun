来源: https://palantir.com/docs/zh/foundry/building-pipelines/compass-file-lister/

# Compass 文件列出器

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Compass 文件列出器

Compass 文件列出器是一种自动化工具，用于将给定输入文件夹中资源的 rid（资源标识符）列入代码库中。运行时，将在输出库中打开一个新的拉取请求，它将创建文件或覆盖现有文件。生成的文件默认存储在以下路径：compass-lister/rids.json。查看创建连接流以获取逐步指南。

## 配置选项

- 你可以通过在配置块中设置generated_file_path来覆盖输出库中的基本路径。如果将其设置为transforms-python/generated，则输出将写入transforms-python/generated/rids.json。
你可以通过在配置块中设置generated_file_path来覆盖输出库中的基本路径。如果将其设置为transforms-python/generated，则输出将写入transforms-python/generated/rids.json。

- 如果在配置块中将merge_when_ready设置为true，则可以允许生成的 PR 自动合并。查看你的输出库设置以审查允许 PR 合并的条件。
如果在配置块中将merge_when_ready设置为true，则可以允许生成的 PR 自动合并。查看你的输出库设置以审查允许 PR 合并的条件。

### 配置示例

```
Copied!1
2
3
4
{
  "generated_file_path": "transforms-python/generated", // 生成文件的路径
  "merge_when_ready": true // 当准备好时自动合并
}
```
