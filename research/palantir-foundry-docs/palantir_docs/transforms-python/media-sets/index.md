来源: https://palantir.com/docs/zh/foundry/transforms-python/media-sets/

# 使用媒体集与Python变换

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 使用媒体集与Python变换

您可以在Python变换中使用媒体集进行PDF文本提取、光学字符识别（OCR）、图像切割、元数据解析等。以下部分解释了如何在您的Python代码库中设置媒体集以及如何通过Python变换读取和写入媒体集。

## 在您的代码库中添加对transforms-media的依赖。

当处理媒体集时，您必须使用@transform装饰器。媒体集输入和输出可以通过使用transforms.mediasets.MediaSetInput和transforms.mediasets.MediaSetOutput规范传入。在搭建过程中，这些规范分别被解析为transforms.mediasets.MediaSetInputParam和transforms.mediasets.MediaSetOutputParam对象。这些MediaSetInputParam和MediaSetOutputParam对象提供了在计算函数中访问媒体集的功能。可以将任意数量的媒体集输入或输出与其他任何有效的变换输入和输出（例如表格数据集）结合使用。例如：

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
from transforms.api import transform
from transforms.mediasets import MediaSetInput, MediaSetOutput

@transform(
    images=MediaSetInput('/examples/images'),  # 输入的媒体集路径
    output_images=MediaSetOutput('/examples/output_images')  # 输出的媒体集路径
)
def translate_images(images, output_images):
    ...
    # 此函数用于处理输入的图像，并将结果输出到指定的输出路径
```

## 从媒体集读取

您可以通过文件路径或RID访问单个媒体项：

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
from transforms.api import transform
from transforms.mediasets import MediaSetInput, MediaSetOutput

@transform(
    images=MediaSetInput('/examples/images'),  # 从路径'/examples/images'输入图像数据
    output_images=MediaSetOutput('/examples/output_images')  # 输出处理后的图像数据到路径'/examples/output_images'
)
def translate_images(images, output_images):
    image1 = images.get_media_item_by_path("image1")  # 使用图像路径获取媒体项
    image2 = images.get_media_item("ri.mio.main.media-item.123")  # 使用媒体项ID获取媒体项
    ...
```

这里的代码定义了一个数据转换函数translate_images，用于处理图像数据。该函数通过路径和ID从输入媒体集中获取图像，然后将处理后的图像输出到指定的路径。
然而，您可能希望变换媒体集中的所有项目。为此，您必须首先使用listing方法将项目提取到一个数据框中。在下面的示例中，我们列出输入媒体集中的所有项目，并将生成的数据框写入表格输出：

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
from transforms.api import transform, Output
from transforms.mediasets import MediaSetInput

@transform(
    images=MediaSetInput('/examples/images'),
    listing_output=Output('/examples/listed_images')
)
def translate_images(ctx, images, listing_output):
    # 列出媒体项并附带媒体引用
    media_items_listing = images.list_media_items_by_path_with_media_reference(ctx)

    # 你可以在 media_items_listing 上执行常规的 PySpark 转换操作

    # 定义列类型类，其中 'mediaReference' 列为引用类型
    column_typeclasses = {'mediaReference': [{'kind': 'reference', 'name': 'media_reference'}]}
    # 将 DataFrame 写入 listing_output，指定列类型类
    listing_output.write_dataframe(media_items_listing, column_typeclasses=column_typeclasses)
```

### 代码解释

- MediaSetInput用于输入媒体数据集的路径。
- Output用于定义输出路径。
- list_media_items_by_path_with_media_reference(ctx)方法用于列出媒体项，并附带一个媒体引用。
- write_dataframe方法将 DataFrame 写入输出路径，并可以指定列的类型类。
如果媒体集中的多个项目位于特定路径，则仅会在列表中包含最新的项目。该列表将具有以下架构：
```
+--------------------------+-----------+-------------------+
|        mediaItemRid      |    path   |  mediaReference  |
+--------------------------+-----------+-------------------+
| ri.mio.main.media-item.1 | item1.jpg |  {{reference1}}   |
| ri.mio.main.media-item.2 | item2.jpg |  {{reference2}}   |
| ri.mio.main.media-item.3 | item3.jpg |  {{reference3}}   |
+--------------------------+-----------+-------------------+

// 这是一个表格，包含三个列：mediaItemRid、path 和 mediaReference。
// - mediaItemRid 是媒体项目的唯一标识符。
// - path 表示媒体文件的路径。
// - mediaReference 是一个模板引用，可能用于动态生成或替换相应的媒体链接。
```

请注意，上述示例仅显示列表的前三行。

通过设置mediaReference列的类型类，我们允许将该列读取为媒体引用。

调用get_media_item()、get_media_item_by_path()等函数返回一个类似Python文件的流对象。所有io.open()↗接受的选项也都支持。请注意，项目是作为流读取的，这意味着不支持随机访问。

您还可以在不下载完整项目的情况下返回单个媒体项目的元数据。元数据将包括图像的维度、音频的长度等信息。有关可用元数据的完整参考，请参见下面的附录。下面的示例在媒体项目列表中添加了一列，每个图像的元数据。

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
25
26
27
28
29
30
from transforms.api import transform, Output
from transforms.mediasets import MediaSetInput
from pyspark.sql import functions as F
from pyspark.sql.types import StringType
from conjure_python_client import ConjureEncoder

# 定义transform装饰器，用于处理输入和输出
@transform(
    images=MediaSetInput('/examples/images'),  # 输入的媒体集路径
    listing_output_with_metadata=Output('/examples/listed_images_with_metadata')  # 输出路径
)
def translate_images(ctx, images, listing_output_with_metadata):

    # 获取媒体项的元数据
    def get_metadata(media_item_rid):
        metadata = images.get_media_item_metadata(media_item_rid)
        return ConjureEncoder().default(metadata)

    # 定义一个用户自定义函数(UDF)用于处理元数据
    metadata_udf = F.udf(get_metadata, StringType())

    # 列出媒体项并获取其引用
    media_items_listing = images.list_media_items_by_path_with_media_reference(ctx)
    # 为每个媒体项添加元数据列
    listing_with_metadata = media_items_listing.withColumn('metadata', metadata_udf(F.col('mediaItemRid')))

    # 定义列类型用于输出数据框架
    column_typeclasses = {'mediaReference': [{'kind': 'reference', 'name': 'media_reference'}]}
    # 写入数据框架到输出
    listing_output_with_metadata.write_dataframe(listing_with_metadata, column_typeclasses=column_typeclasses)
```

这段代码主要用于从媒体集中读取媒体项，获取其元数据，并将带有元数据的列表输出到指定位置。使用了Spark的DataFrame操作和用户自定义函数（UDF）来处理数据。
媒体集开箱即用地支持一定数量的内置变换。请参阅下面的附录以获取API和支持的变换列表。对这些变换的调用也将返回一个类似Python文件流的对象。要使用这些内置变换，请对媒体集输入调用相应的方法。例如：

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
@transform(
    images=MediaSetInput('/examples/images'),
    image_text_output=Output('/examples/listed_images_with_text')
)
def translate_images(ctx, images, image_text_output):

    def get_ocr_on_image(media_item_rid):
        # 使用 OCR 技术将图片转换为文本
        return images.transform_image_to_text_ocr_output_text(media_item_rid).read().decode('utf-8')

    ocr_on_image_udf = F.udf(get_ocr_on_image, StringType())

    # 列出媒体项并获取其参考
    media_items_listing = images.list_media_items_by_path_with_media_reference(ctx)
    # 为每个媒体项添加 OCR 文本列
    listing_with_ocr = media_items_listing.withColumn('text', ocr_on_image_udf(F.col('mediaItemRid')))
    column_typeclasses = {'mediaReference': [{'kind': 'reference', 'name': 'media_reference'}]}
    # 将结果写入输出
    image_text_output.write_dataframe(listing_with_ocr, column_typeclasses=column_typeclasses)
```

该代码的功能是将一组图片进行 OCR（光学字符识别）处理，并将识别出的文本与图片的其他信息一起存储。

## 写入媒体集

媒体集可以通过使用MediaSetOutput规范作为变换的输出。与常规数据集不同，媒体集必须在被用作输出之前_已经存在_。这可以通过在 Foundry 文件系统界面中导航到您希望媒体集存在的文件夹来完成。

要上传一个项目，请在输出媒体集上调用put_media_item()端点。此端点接受任何类似文件的对象和一个路径，该路径将用于识别输出媒体集中的项目。以下是一个基本示例：

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
from transforms.api import transform
from transforms.mediasets import MediaSetInput, MediaSetOutput

@transform(
    images=MediaSetInput('/examples/images'),  # 从指定路径读取输入图像集
    output_images=MediaSetOutput('/examples/output_images')  # 指定输出图像集的路径
)
def upload_images(images, output_images):
    # 使用图像路径获取媒体项，并进行处理
    with images.get_media_item_by_path("image1.jpg") as input_image:
        # 将输入图像复制到输出路径，并重命名为“copied_image1.jpg”
        output_images.put_media_item(input_image, "copied_image1.jpg")
```

当从一个媒体集复制项目到另一个媒体集时，您可以在输出上使用fast_copy_media_item()方法。这比下载和重新上传媒体项目更快且更高效：

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
@transform(
    images=MediaSetInput('/examples/images'),
    output_images=MediaSetOutput('/examples/output_images')
)
def upload_images(images, output_images):
    # 获取名为 "image1.jpg" 的媒体项的资源ID
    origin_media_item_rid = images.get_media_item_rid_by_path("image1.jpg").item
    # 快速复制媒体项到输出集合，命名为 "fast_copied_image1.jpg"
    output_images.fast_copy_media_item(images, origin_media_item_rid, "fast_copied_image1.jpg")
```

可以将项目上传到用户定义函数（UDFs）的媒体集，以实现更高的并行性。在下面的示例中，我们将输入媒体集中的PDF变换为JPEG，使用内置的PDF到JPEG变换，并将这些JPEG上传到一个新的输出媒体集。然后，我们写出一个包含这些上传的JPEG媒体引用的表格数据集：

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
25
26
27
28
29
30
31
32
33
34
35
36
37
from transforms.api import transform, Output
from transforms.mediasets import MediaSetInput, MediaSetOutput
from pyspark.sql import functions as F
from pyspark.sql.types import StringType

# 定义transform装饰器，用于指定输入和输出路径
@transform(
    pdfs=MediaSetInput('/examples/PDFs'),  # 输入的PDF文档路径
    output_images=MediaSetOutput('/examples/JPEGs'),  # 输出的JPEG图像路径
    output_references=Output('/examples/JPEG listing')  # JPEG列表的输出路径
)
def upload_images(ctx, pdfs, output_images, output_references):

    # 定义一个将PDF转换为JPEG并上传的函数
    def upload_jpg(media_item_rid, path):
        with pdfs.transform_document_to_jpg(media_item_rid, 0) as jpeg:
            response = output_images.put_media_item(jpeg, path)  # 上传JPEG文件
        return response.media_item_rid  # 返回上传JPEG的媒体项ID

    # 创建一个UDF（用户定义函数）以便在DataFrame操作中使用
    upload_udf = F.udf(upload_jpg, StringType())

    # 列出PDF媒体项并获取JPEG媒体引用模板
    listed_pdfs = pdfs.list_media_items_by_path(ctx)
    media_reference_template = output_images.media_reference_template()

    # 将PDF转换为JPEG并生成相应的媒体引用
    uploaded_jpegs = listed_pdfs\
        .withColumn('uploaded_media_item_rid', upload_udf(F.col('mediaItemRid'), F.col('path')))\
        .select('path', 'uploaded_media_item_rid')\
        .withColumn("mediaReference", F.format_string(media_reference_template,
                                                      'uploaded_media_item_rid'))

    # 定义媒体引用的列类型
    column_typeclasses = {'mediaReference': [{'kind': 'reference', 'name': 'media_reference'}]}
    # 将上传结果写入输出路径
    output_references.write_dataframe(uploaded_jpegs, column_typeclasses=column_typeclasses)
```

此代码用于将PDF文件转换为JPEG图像，并生成JPEG图像的引用列表。通过使用Spark DataFrame和自定义UDF（用户定义函数），实现了批量PDF转换和JPEG上传的功能。

## 从文件系统（目录）数据集上传

Python 媒体集 SDK 内置工具，可以将 Palantir 文件系统（称为目录）中常规数据集的文件上传到媒体集中。例如：

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
from transforms.api import transform, Input
from transforms.mediasets import MediaSetOutput

@transform(
    pdfs_dataset=Input('/examples/PDFs'),  # 定义输入数据集路径
    pdfs_media_set=MediaSetOutput('/examples/PDFs mediaset')  # 定义输出媒体集路径
)
def upload_to_media_set(pdfs_dataset, pdfs_media_set):
    # 将数据集文件上传到媒体集中，不忽略不匹配架构的项目
    pdfs_media_set.put_dataset_files(pdfs_dataset, ignore_items_not_matching_schema=False)
```

此变换会将数据集中的所有项目上传到媒体集。如果任何项目不符合媒体集的架构（例如，如果数据集中有JPEG），那么搭建将失败。通过设置ignore_items_not_matching_schema=True，任何此类不匹配将被忽略。

文件也可以一个一个地上传。例如：

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
from transforms.api import transform, Input, Output, incremental
from transforms.mediasets import MediaSetInput, MediaSetOutput
import os

@transform(
    output_mediaset=MediaSetOutput("/path/mediaset_output", should_snapshot=False),
    input_dataset=Input("/path/dataset_of_raw_files"),
)
def compute(input_dataset, output_mediaset):
    # 获取所有输入数据集中的文件
    all_files = list(input_dataset.filesystem().ls())
    # 遍历每一个文件
    for current_file in all_files:
        # 打开当前文件以二进制模式读取
        with input_dataset.filesystem().open(current_file.path, 'rb') as f:
            # 获取文件的基本名称，不包括路径
            filename = os.path.basename(current_file.path)
            # 将文件内容写入到输出媒体集
            output_mediaset.put_media_item(f, filename)
```

该代码的功能是从输入数据集（input_dataset）中读取所有文件，然后将每个文件的内容写入到输出媒体集（output_mediaset）中。评论用中文简要解释了代码的每个主要步骤。

## 参考：内置变换

### 将PDF文档转换为JPEG

将PDF文档的单个页面转换为JPEG并返回。

- 操作于：PDF文档
操作于：PDF文档

- 返回：JPEG图像
返回：JPEG图像

- 参数：media_item_rid：要变换的媒体项的RID。page_number：从零开始的页面编号。高度（非必填）：输出图像所需的高度，单位为像素。宽度（非必填）：输出图像所需的宽度，单位为像素。
参数：

- media_item_rid：要变换的媒体项的RID。
- page_number：从零开始的页面编号。
- 高度（非必填）：输出图像所需的高度，单位为像素。
- 宽度（非必填）：输出图像所需的宽度，单位为像素。
- 示例：
示例：

```
Copied!1
2
# 将PDF文档转换为JPEG格式的图片
input_pdfs.transform_document_to_jpg("ri.mio.main.media-item.1", 0)
```

### 将PDF文档变换为PNG

将PDF文档的单个页面变换为PNG并返回。

- 操作对象：PDF文档
操作对象：PDF文档

- 返回：PNG图像
返回：PNG图像

- 参数：media_item_rid: 要变换的媒体项的RID。page_number: 从零开始的页面编号。高度 (非必填): 输出图像所需的高度，以像素为单位。宽度 (非必填): 输出图像所需的宽度，以像素为单位。
参数：

- media_item_rid: 要变换的媒体项的RID。
- page_number: 从零开始的页面编号。
- 高度 (非必填): 输出图像所需的高度，以像素为单位。
- 宽度 (非必填): 输出图像所需的宽度，以像素为单位。
- 示例：
示例：

```
Copied!1
2
3
4
# 将PDF文档转换为PNG格式
# 参数 "ri.mio.main.media-item.1" 是文档的标识符
# 参数 0 表示转换的页码，通常从0开始计数
input_pdfs.transform_document_to_png("ri.mio.main.media-item.1", 0)
```

### 使用光学字符识别（OCR）将 PDF 文档按页转换为文本

OCR PDF 按页输出文本。

- 操作于：PDF 文档
操作于：PDF 文档

- 返回：以 utf-8 编码的非结构化文本
返回：以 utf-8 编码的非结构化文本

- 参数：media_item_rid: 要变换的媒体项目的 RID。page_number: 从零开始的页码。语言（非必填）：语言代码，默认为ENG。
参数：

- media_item_rid: 要变换的媒体项目的 RID。
- page_number: 从零开始的页码。
- 语言（非必填）：语言代码，默认为ENG。
- 示例：
示例：

```
Copied!1
2
3
4
# 将PDF文档转换为OCR输出文本
raw_output = input_pdfs.transform_document_to_text_ocr_output_text("ri.mio.main.media-item.1", 0)
# 读取并解码OCR输出文本为UTF-8格式的字符串
doc_text_ocr = raw_output.read().decode("utf-8")
```

### 将PDF文档通过OCR逐页转换为hOCR XML

OCR PDF至hOCR XML逐页。了解更多关于hOCR ↗。

- 操作对象:PDF文档
操作对象:PDF文档

- 返回:utf-8编码的hOCR xml
返回:utf-8编码的hOCR xml

- 参数:media_item_rid: 要变换的媒体项的RID。page_number: 从零开始的页码。语言 (非必填): 语言代码，默认为ENG。
参数:

- media_item_rid: 要变换的媒体项的RID。
- page_number: 从零开始的页码。
- 语言 (非必填): 语言代码，默认为ENG。
- 示例:
示例:

```
Copied!1
2
3
4
input_pdfs.transform_document_to_text_ocr_output_hocr("ri.mio.main.media-item.1", 0)
# 调用 transform_document_to_text_ocr_output_hocr 方法，将指定的 PDF 文档转换为文本。
# 参数 "ri.mio.main.media-item.1" 是文档标识符。
# 参数 0 可能表示第一页或特定页面。
```

### 将PDF文档转换以提取原始文本

从PDF中提取字段并返回。这是一种解析方法，不需要像OCR那样进行图像处理。

- 作用于：PDF文档
作用于：PDF文档

- 返回：UTF-8编码的非结构化文本
返回：UTF-8编码的非结构化文本

- 参数：media_item_rid: 要变换的媒体项的RID。page_number: 从零开始的页码。
参数：

- media_item_rid: 要变换的媒体项的RID。
- page_number: 从零开始的页码。
- 示例：
示例：

```
Copied!1
2
3
4
5
# 将输入的PDF文档转换为原始文本
raw_output = input_pdfs.transform_document_to_text_raw("ri.mio.main.media-item.1", 0)

# 从raw_output中读取字节内容并解码为UTF-8格式的字符串
doc_text_extraction = raw_output.read().decode("utf-8")
```

### 提取PDF文档中的表单字段

从整个PDF中提取所有表单字段并返回。

- 操作于：PDF文档
操作于：PDF文档

- 返回：JSON
返回：JSON

- 参数：media_item_rid: 要变换的媒体项的RID。
参数：

- media_item_rid: 要变换的媒体项的RID。
- 示例：
示例：

```
Copied!1
2
3
# 调用 transform_document_to_text_extract_field 方法，将 PDF 文档转换为文本并提取指定字段
# 这里 "ri.mio.main.media-item.1" 可能是一个特定的字段标识符，用于提取该字段内容
input_pdfs.transform_document_to_text_extract_field("ri.mio.main.media-item.1")
```

### 变换PDF文档以提取目录

从PDF中提取字段并返回。

- 适用于：PDF文档
适用于：PDF文档

- 返回：JSON
返回：JSON

- 参数：media_item_rid: 要变换的媒体项的RID。
参数：

- media_item_rid: 要变换的媒体项的RID。
- 示例：
示例：

```
Copied!1
2
input_pdfs.transform_document_to_text_extract_table_of_contents("ri.mio.main.media-item.1")
# 将PDF文档转换为文本，并提取目录
```

### 将图像转换为 hOCR XML

将图像OCR为hOCR XML。了解更多关于hOCR ↗的信息。

- 操作于：图像
操作于：图像

- 返回：JSON
返回：JSON

- 参数：media_item_rid: 要变换的媒体项的 RID。
参数：

- media_item_rid: 要变换的媒体项的 RID。
- 示例：
示例：

```
Copied!1
2
3
input_pdfs.transform_image_to_text_ocr_output_hocr("ri.mio.main.media-item.1")
# 该函数将图像转换为文本，使用OCR（光学字符识别）技术并输出为HOCR格式。
# 参数"ri.mio.main.media-item.1"可能是用于标识特定PDF的标识符或路径。
```

### 将图像转换为文本

将图像OCR为文本。

- 操作于：图像
操作于：图像

- 返回：utf-8编码的非结构化文本
返回：utf-8编码的非结构化文本

- 参数：media_item_rid: 要变换的媒体项目的RID。
参数：

- media_item_rid: 要变换的媒体项目的RID。
- 示例：
示例：

```
Copied!1
2
3
# 调用 transform_image_to_text_ocr_output_text 方法，将输入的图片转换为文本
# 参数 "ri.mio.main.media-item.1" 代表待处理的图像标识符
input_images.transform_image_to_text_ocr_output_text("ri.mio.main.media-item.1")
```

### 将音频转录为文本

将带有语音的音频文件转录为文本。

- 作用于：音频
作用于：音频

- 返回：带有转录的非结构化纯文本文件
返回：带有转录的非结构化纯文本文件

- 参数：media_item_rid: 要变换的媒体项的RID。语言 (非必填)：用于转录音频的语言代码。如果留空，语言将从音频文件的起始部分推断。请使用集合1或ISO语言名称：https://en.wikipedia.org/wiki/List\_of\_ISO\_639\_language\_codes
参数：

- media_item_rid: 要变换的媒体项的RID。
- 语言 (非必填)：用于转录音频的语言代码。如果留空，语言将从音频文件的起始部分推断。请使用集合1或ISO语言名称：https://en.wikipedia.org/wiki/List\_of\_ISO\_639\_language\_codes
- 示例：
示例：

```
Copied!1
2
3
4
5
# 将音频文件进行转录，使用默认语言
input_audio_files.transcribe("ri.mio.main.media-item.1")

# 将音频文件进行转录，指定使用阿拉伯语进行转录
input_audio_files.transcribe("ri.mio.main.media-item.1", TranscriptionLanguage.ARABIC)
```
