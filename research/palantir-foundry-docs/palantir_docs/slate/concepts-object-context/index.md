来源: https://palantir.com/docs/zh/foundry/slate/concepts-object-context/

# 检索单个Object

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 检索单个Object

Object上下文面板允许您：

- 使用{{o_object_context1.property1}}表示法直接访问Object的属性，而无需操作JSON。
- 创建一个Slate应用程序，该应用程序将依赖于单个Object，这是使用Slate搭建选项卡或自定义微件以嵌入到Object视图中的常见模式。
## 构建Object上下文

要构建一个Object上下文o_object_context1，您需要通过以下方式输入一个单个Object RID：

- 参考返回单个RID的函数或Object查询（如{{return_single_object}}），或
- 直接输入一个静态Object RID，例如ri.phonograph2-objects.main.object.09d2e0e9-dd3c-49b2-8b96-0cb1bf005c1d。
一旦Object上下文被定义，您将能够：

- 访问其属性（例如，o_object_context1.title或o_object_context1.property1）并
- 在Slate的其他函数、变量、事件或微件属性中使用此输出。