来源: https://palantir.com/docs/zh/foundry/workshop/widgets-image-annotation/

# 图像标注

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 图像标注

图像标注微件用于通过在感兴趣的区域周围绘制矩形来标注图像。

下面的截图展示了一个配置好的图像标注微件在创建标注过程中的示例：

## 配置选项

下面是新添加的图像标注微件的初始状态及其初始配置面板的截图：

- 输入数据图像来源：图像可以通过媒体URL或媒体引用显示。目前此微件接受以下图像文件类型：媒体URL：选择一个有效媒体URL的字符串变量，以渲染媒体的预览。如果从数据集中引用媒体URL，URL应为以下格式之一：.png，.jpg，.jpeg，.bmp，或.webp，https://{my-foundry-url}/foundry-data-proxy/api/web/dataproxy/datasets/{dataset rid}/transactions/{transaction rid}/{filename}https://{my-foundry-url}/foundry-data-proxy/api/web/dataproxy/datasets/{dataset rid}/views/{branch name}/{filename}。否则，如果引用外部媒体URL，请在您的注册的内容安全策略设置中配置访问。媒体引用：以单个对象定义对象集，并选择媒体引用类型属性以渲染该对象的媒体预览。当前多边形选择：跟踪活动多边形选择坐标的字符串变量，存储为"x1, y1, x2, y2"，其中(x1, y1)是框的左上角像素坐标，(x2, y2)是框的右下角像素坐标。活动标注对象：表示当前选择的标注的对象。
- 图像来源：图像可以通过媒体URL或媒体引用显示。目前此微件接受以下图像文件类型：媒体URL：选择一个有效媒体URL的字符串变量，以渲染媒体的预览。如果从数据集中引用媒体URL，URL应为以下格式之一：.png，.jpg，.jpeg，.bmp，或.webp，https://{my-foundry-url}/foundry-data-proxy/api/web/dataproxy/datasets/{dataset rid}/transactions/{transaction rid}/{filename}https://{my-foundry-url}/foundry-data-proxy/api/web/dataproxy/datasets/{dataset rid}/views/{branch name}/{filename}。否则，如果引用外部媒体URL，请在您的注册的内容安全策略设置中配置访问。媒体引用：以单个对象定义对象集，并选择媒体引用类型属性以渲染该对象的媒体预览。
- 媒体URL：选择一个有效媒体URL的字符串变量，以渲染媒体的预览。如果从数据集中引用媒体URL，URL应为以下格式之一：.png，.jpg，.jpeg，.bmp，或.webp，https://{my-foundry-url}/foundry-data-proxy/api/web/dataproxy/datasets/{dataset rid}/transactions/{transaction rid}/{filename}https://{my-foundry-url}/foundry-data-proxy/api/web/dataproxy/datasets/{dataset rid}/views/{branch name}/{filename}。否则，如果引用外部媒体URL，请在您的注册的内容安全策略设置中配置访问。
- https://{my-foundry-url}/foundry-data-proxy/api/web/dataproxy/datasets/{dataset rid}/transactions/{transaction rid}/{filename}
- https://{my-foundry-url}/foundry-data-proxy/api/web/dataproxy/datasets/{dataset rid}/views/{branch name}/{filename}。
- 否则，如果引用外部媒体URL，请在您的注册的内容安全策略设置中配置访问。
- 媒体引用：以单个对象定义对象集，并选择媒体引用类型属性以渲染该对象的媒体预览。
- 当前多边形选择：跟踪活动多边形选择坐标的字符串变量，存储为"x1, y1, x2, y2"，其中(x1, y1)是框的左上角像素坐标，(x2, y2)是框的右下角像素坐标。
- 活动标注对象：表示当前选择的标注的对象。
- 标注标注对象：表示要叠加在图像上的标注的对象集。目前，每个图像支持最多1000个标注。多边形属性：标注对象集的字符串属性，表示点向量。颜色属性：标注对象集的字符串属性，表示要绘制为十六进制代码的颜色。此字段为非必填。标注创建时：启用模块搭建者配置工作坊事件，以在用户创建标注时触发。
- 标注对象：表示要叠加在图像上的标注的对象集。目前，每个图像支持最多1000个标注。
- 多边形属性：标注对象集的字符串属性，表示点向量。
- 颜色属性：标注对象集的字符串属性，表示要绘制为十六进制代码的颜色。此字段为非必填。
- 标注创建时：启用模块搭建者配置工作坊事件，以在用户创建标注时触发。