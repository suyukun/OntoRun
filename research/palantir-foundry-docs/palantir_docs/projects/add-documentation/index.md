来源: https://palantir.com/docs/zh/foundry/projects/add-documentation/

# 添加文档

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 添加文档

您可以通过将名为README.md的 Markdown 文件拖放到文件夹中，或从文件夹的操作菜单中选择添加描述来向任何文件夹添加文档。标准 Markdown ↗是支持的，但有一些与安全相关的限制：

- 行内 HTML 被禁用。
- 除非另有配置，否则只有上传到 Foundry 的图像文件会被渲染。Foundry 托管图像的 Markdown 格式如下：![Alt text](link to image in Foundry)。
链接到 Foundry 资源也是支持的。使用以下语法可以自动添加带有图标和文件名的链接：[非必填链接文本](rid)。

即使现有的.md文件在项目中正确命名为README.md，也不会自动转换为就地渲染。下载现有的README.md，从文件夹中删除它，然后重新上传即可显示。
