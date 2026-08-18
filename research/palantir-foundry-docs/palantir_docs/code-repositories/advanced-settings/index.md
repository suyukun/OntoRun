来源: https://palantir.com/docs/zh/foundry/code-repositories/advanced-settings/

# 高级存储库设置

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 高级存储库设置

大多数代码存储库设置可以在设置选项卡中找到。一些额外的值通过存储库根目录下的repoSettings.json文件进行配置。如果文件不存在，您可以在存储库根目录下创建一个名为repoSettings.json的文件。

## 自定义标签名称验证

为了强制存储库中所有新创建的标签遵循特定命名方案，除了代码存储库强制执行的默认约束外，您可以配置自定义正则表达式和一个错误消息，当正则表达式不满足时显示给用户。例如：

```
Copied!1
2
3
4
5
6
"tagNameValidation": {
    "regex": "^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)(-rc\\d+)?$",
    // 正则表达式：验证标签名称格式为 x.x.x 或 x.x.x-rcx，其中 x 为非负整数
    "errorMessage": "Tag name must have the format x.x.x or x.x.x-rcx"
    // 错误信息：标签名称必须符合格式 x.x.x 或 x.x.x-rcx
}
```

如果为tagNameValidation设置一个值，必须同时配置regex和errorMessage。

## 拉取请求描述模板

为了在打开新的拉取请求时保持最佳实践，您可以配置一个描述模板，该模板将在创建拉取请求时预填充Description字段：

```
Copied!1
"prDescriptionTemplate": "First line of the description template\nAnd another line with instructions"
```

这个 JSON 片段定义了一个 PR（Pull Request）描述模板，其中包含两个文本行，用于指导 PR 描述的撰写。

## 新变换的输出数据集路径

默认情况下，新变换文件的模板使用文件路径作为初始输出数据集路径。例如，对于一个Python变换/path/to/your/repository/transforms-python/src/myproject/datasets/name_of_file。您可以通过配置outputPathPrefix将其更改为一个更方便的位置，例如项目中的特定文件夹：

```
Copied!1
2
"outputPathPrefix": "/My/Custom/Prefix"
// 指定输出路径的前缀，输出文件将存储在这个自定义路径下
```

在上述设置中，输出数据集路径将被设置为/My/Custom/Prefix/name_of_file。

## 拉取请求验证规则

可以通过在repoSettings.json文件中添加prValidation条目来对存储库内的拉取请求实施规则。当创建拉取请求时，它将根据基础分支上的repoSettings.json文件进行验证。

一个拉取请求验证规则由一个正则表达式、一个拉取请求字段列表（用来匹配表达式）以及一个当字段不符合规则时要显示的错误消息组成。

## 示例：repoSettings.json

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
{
    "tagNameValidation": {
        "regex": "^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)(-rc\\d+)?$",  // 正则表达式用于验证标签名，格式为 x.x.x 或 x.x.x-rcx
        "errorMessage": "Tag name must have the format x.x.x or x.x.x-rcx"  // 错误信息：标签名必须符合 x.x.x 或 x.x.x-rcx 的格式
    },
    "prDescriptionTemplate": "First line of the description template\nAnd another line with instructions",  // PR描述模板的第一行和说明的另一行
    "outputPathPrefix": "/My/Custom/Prefix",  // 输出路径前缀
    "prValidation": [
        {
            "regex": "TEST-\\d{3}",  // 正则表达式用于验证字段中是否包含有效的 TEST-XXX 票号，例如 'TEST-123'
            "fields": ["title", "branchName"],  // 需要验证的字段：标题和分支名
            "errorMessage": "This field must contain a valid TEST-XXX ticket, such as 'TEST-123'."  // 错误信息：此字段必须包含有效的 TEST-XXX 票号，例如 'TEST-123'
        },
        {
            "regex": "This is the description",  // 正则表达式用于检查描述中是否包含 'This is the description'
            "fields": ["description"],  // 需要验证的字段：描述
            "errorMessage": "Please enter 'This is the description' somewhere in the description."  // 错误信息：请在描述中输入 'This is the description'
        }
    ]
}
```
