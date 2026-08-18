来源: https://palantir.com/docs/zh/foundry/code-repositories/readme/

# 文档

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 文档

您可以通过添加README文件，为Code Repositories中的项目提供文档。Code Repositories中的README文件支持Markdown，以实现灵活、易用的格式和样式。

编辑或添加README.md文件到您的代码库以开始。此页面包含可用于定制README文件的其他功能信息。

## 功能

Code Repositories为README提供了多种格式选项。

### 行内图片预览

您可以通过使用以下语法，将代码库中的图片与Markdown文件的文本行内显示：

![文件名](/transforms-python/path/to/my/file.jpeg)

为了上传图片到代码库，您需要在本地克隆您的代码库，将图片文件添加到本地代码库，然后推送更改到服务器。

### 提及Foundry用户

要在Markdown文件中提及Foundry用户，请在他们的用户名前加上@符号。这将创建对被提及用户的引用，并生成指向其个人资料的直接链接。

@用户名

### 参考Foundry资源

您可以通过将资源ID直接粘贴到README的Markdown文件中来引用任何Foundry资源。这样引用的资源将自动命名并链接到平台中的相应资源。

此代码库将被部署到ri.foundry.main.deployed-app.a00000aa-a000-000a-0000-000a0aa0a00a

### 链接代码库中的文件

要创建指向代码库中文件的链接，请使用repo://协议后跟文件路径；例如，repo://transforms-python/src/myproject/datasets/examples.py。这样引用的文件在点击时将自动打开。这使您可以轻松引用和导航到代码库中的其他文件。

### 语法高亮

README文件支持代码块中的语言语法高亮，以提高代码的可读性。要使用语法高亮，请在打开代码块定界符后指定语言，如下所示：

```
Copied!1
2
3
def hello_world():
    # 打印“Hello, World!”到控制台
    print("Hello, World!")
```

### 表格

您还可以使用标准Markdown表格语法创建表格：

```
| Header 1 | Header 2 |
| -------- | -------- |
| Cell 1   | Cell 2   |

# 这是一个Markdown表格示例
# 'Header 1' 和 'Header 2' 是表头
# 'Cell 1' 和 'Cell 2' 是数据单元格
```

### 链接

README 中的 URL 和电子邮件地址将自动转换为可点击的链接。
