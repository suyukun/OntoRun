来源: https://palantir.com/docs/zh/foundry/geospatial/raster_data/

# 使用栅格数据

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 使用栅格数据

Foundry 通过媒体集以一流的方式支持大规模处理栅格数据。文件级别变换也支持自定义图像预处理，或处理当前媒体集不支持的任何文件格式。

了解有关不同类型地理空间数据的更多信息。

## 数据格式和来源

支持的媒体集栅格文件格式：

- TIFF / GeoTIFF
- NITF
- JPEG2000
只能在文件级别处理的其他栅格文件格式：

- PNG
- JPEG
## 在媒体集中使用栅格数据

- 将支持的栅格文件格式导入为媒体集。您可以通过数据连接或本地机器上传创建新的媒体集。了解不同的导入媒体方法。
将支持的栅格文件格式导入为媒体集。您可以通过数据连接或本地机器上传创建新的媒体集。了解不同的导入媒体方法。

- 导入后，您可以通过媒体引用利用媒体集。通过Pipeline Builder或变换选择媒体引用。
导入后，您可以通过媒体引用利用媒体集。通过Pipeline Builder或变换选择媒体引用。

- 在Ontology中创建一个Object类型，可以作为Pipeline Builder中的管道输出或直接在Ontology Manager中创建。确保Object类型具有媒体引用属性作为媒体引用类型，并且您已在Capabilities中声明了支持的媒体集，以便平台知道在哪里以及如何引用您的媒体项。
在Ontology中创建一个Object类型，可以作为Pipeline Builder中的管道输出或直接在Ontology Manager中创建。确保Object类型具有媒体引用属性作为媒体引用类型，并且您已在Capabilities中声明了支持的媒体集，以便平台知道在哪里以及如何引用您的媒体项。

一旦您有了一个Object类型，您可以将其导入到地图应用程序中进行查看。在地图上显示大于67 MB的栅格文件不受支持。

## 在变换中使用栅格数据

对于当前媒体集不支持的栅格文件类型，您仍然可以在变换中处理它们。您可以在下面的部分中查看推荐的库和代码示例。

变换也非常适合预处理支持的媒体集文件类型。例如，您可以使用变换通过MediaSetInput更新图像的大小，并使用MediaSetOutput输出一个媒体集，如下例所示。了解更多关于如何编写媒体集批处理管道。

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
from transforms.api import transform
from transforms.mediasets import MediaSetInput, MediaSetOutput

@transform(
    images=MediaSetInput('/examples/images'),  # 输入媒体集路径
    output_images=MediaSetOutput('/examples/output_images')  # 输出媒体集路径
)
def translate_images(images, output_images):
    ...
```

以上代码使用了一个装饰器@transform，定义了一个用于处理图片的函数translate_images。该函数接受images作为输入，并将处理后的图片输出到output_images。路径/examples/images和/examples/output_images分别指定了输入和输出的媒体集路径。

### 推荐的Python库

有几个常见的开源库在Foundry中处理栅格数据时效果很好，包括：

- Rasterio ↗
- PIL ↗
### 代码示例

#### 使用Rasterio从数据集中打开一个GeoTIFF文件

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
from transforms.api import transform, Input, Output, FileSystem
import rasterio
import tempfile
import shutil
import math

@transform(
    output=Output("OUTPUT_DATASET"),
    my_input=Input("INPUT_DATASET"),
)
def my_compute_function(output, my_input):
    def process_file(file_status):
        # 使用临时文件下载文件以便 Image 可以正确打开
        with tempfile.NamedTemporaryFile() as tmp:
            with my_input.filesystem().open(file_status.path, 'rb') as f:
                shutil.copyfileobj(f, tmp)
                tmp.flush()
                # 使用 rasterio 打开文件
                with rasterio.open(tmp.name, driver='GTiff') as dataset:
                    """ 在此处填写 rasterio 逻辑 """

    # 列出输入数据集中的所有文件
    files = list(my_input.filesystem().ls())
    # 对每个文件应用 process_file 函数
    map(process_file, files)
    return
```
