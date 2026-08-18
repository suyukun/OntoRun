来源: https://palantir.com/docs/zh/foundry/workshop/widgets-media-preview/

# 媒体预览

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 媒体预览

媒体预览微件可以被用于在给定支持的媒体源的情况下显示图像、音频、视频和文档媒体。目前支持的媒体源包括媒体URL、附件属性和媒体引用属性。

## 配置选项

- 媒体字符串媒体字符串选项支持以下三种格式引用的图像来呈现媒体预览：Blobster RID，例如，ri.blobster.main.image.ab1c23d4-56ef-789g-h012-3456ij78k90l。媒体URL如果引用数据集中媒体的URL，URL应为以下格式：https://{my-foundry-url}/foundry-data-proxy/api/web/dataproxy/datasets/{dataset rid}/transactions/{transaction rid}/{filename}或https://{my-foundry-url}/foundry-data-proxy/api/web/dataproxy/datasets/{dataset rid}/views/{branch name}/{filename}。如果引用外部媒体URL，请确保在您的注册的内容安全策略设置中配置了访问。带有Base64编码媒体的数据URL，例如，data:image/png;base64,{base64-encoded image}。
- 媒体字符串选项支持以下三种格式引用的图像来呈现媒体预览：Blobster RID，例如，ri.blobster.main.image.ab1c23d4-56ef-789g-h012-3456ij78k90l。媒体URL如果引用数据集中媒体的URL，URL应为以下格式：https://{my-foundry-url}/foundry-data-proxy/api/web/dataproxy/datasets/{dataset rid}/transactions/{transaction rid}/{filename}或https://{my-foundry-url}/foundry-data-proxy/api/web/dataproxy/datasets/{dataset rid}/views/{branch name}/{filename}。如果引用外部媒体URL，请确保在您的注册的内容安全策略设置中配置了访问。带有Base64编码媒体的数据URL，例如，data:image/png;base64,{base64-encoded image}。
- Blobster RID，例如，ri.blobster.main.image.ab1c23d4-56ef-789g-h012-3456ij78k90l。
- 媒体URL如果引用数据集中媒体的URL，URL应为以下格式：https://{my-foundry-url}/foundry-data-proxy/api/web/dataproxy/datasets/{dataset rid}/transactions/{transaction rid}/{filename}或https://{my-foundry-url}/foundry-data-proxy/api/web/dataproxy/datasets/{dataset rid}/views/{branch name}/{filename}。如果引用外部媒体URL，请确保在您的注册的内容安全策略设置中配置了访问。
- 如果引用数据集中媒体的URL，URL应为以下格式：https://{my-foundry-url}/foundry-data-proxy/api/web/dataproxy/datasets/{dataset rid}/transactions/{transaction rid}/{filename}或https://{my-foundry-url}/foundry-data-proxy/api/web/dataproxy/datasets/{dataset rid}/views/{branch name}/{filename}。
- 如果引用外部媒体URL，请确保在您的注册的内容安全策略设置中配置了访问。
- 带有Base64编码媒体的数据URL，例如，data:image/png;base64,{base64-encoded image}。
- 附件属性定义一个包含单个对象的对象集，并选择附件类型的属性来呈现该对象的媒体预览。
- 定义一个包含单个对象的对象集，并选择附件类型的属性来呈现该对象的媒体预览。
- 媒体引用属性定义一个包含单个对象的对象集，并选择媒体引用类型的属性来呈现该对象的媒体预览。
- 定义一个包含单个对象的对象集，并选择媒体引用类型的属性来呈现该对象的媒体预览。