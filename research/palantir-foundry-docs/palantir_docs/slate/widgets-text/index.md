来源: https://palantir.com/docs/zh/foundry/slate/widgets-text/

# 文本

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 文本

文本微件类别包括以下微件：

- 卡片
- 可点击
- HTML
- 图像
- 链接
- 列表
- 文本
## 图像微件

图像微件是文本微件的简单扩展。此微件使用HTML图像标签来创建图像。您需要先将图像上传到Foundry或将其托管在Slate可以访问的其他位置，然后设置图像标签的src属性为图像URL。对于托管在Foundry中的图像，图像URL为https://<FOUNDRY_URL>/blobster/api/salt/<RID>。您可以通过在Foundry中打开图像，右键点击图像，然后复制图像地址来访问此URL。请在您的图像微件配置中按照以下示例进行操作：

<img src="https://<FOUNDRY_URL>/blobster/api/salt/<RID>">

## 卡片微件

卡片微件是文本微件的扩展。此微件使用HTML divs创建卡片，并使用each语句来填充它们。当您向应用程序添加卡片微件时，微件会预填充一些可以替换以自定义卡片的基础代码。

- #each:集合是迭代以创建卡片数量的对象列表。您还需要在文本末尾取消注释/each。
- 项目键:设置为双大括号中的this以允许选择卡片。
- 标题:这是每张卡片上显示为标题的文本。要从查询中选择项目，您可以在handlebars中使用lookupquery.value@index语法。
- 内容:这是每张卡片上标题后面的文本，可以像标题一样从查询中提取。
一个完整的卡片微件可能如下所示：

### 常见CSS

以下是可以应用于卡片微件的常见CSS覆盖。

卡片颜色：

```
Copied!1
sl-text .cards .card {background: #f5f9fa;} /* 设置 .card 元素的背景颜色为 #f5f9fa */
```

选择颜色：

```
Copied!1
2
sl-text .cards .card.selected {background: #fff;}
/* 选中的卡片背景色设为白色 */
```

```
Copied!1
2
3
4
5
6
7
sl-text .cards .card:hover {
   background: #fff; /* 鼠标悬停在.card元素上时，将背景颜色设置为白色 */
}

sl-text .cards .card.selected:hover {
   background: #f5f9fa; /* 鼠标悬停在.selected类的.card元素上时，将背景颜色设置为浅灰色 */
}
```

## 列表微件

列表微件与卡片非常相似，但使用divmclass=lists而不是div class=cards。在下面的示例中，请注意，当选择设置为多选时，您可以一次选择列表中的多个项目。

### 常用CSS

以下是可以应用于列表微件的常用CSS覆盖。

列表颜色：

```
Copied!1
sl-text .lists .lists {background: #f5f9fa;} /* 设置嵌套的 .lists 元素的背景颜色为 #f5f9fa */
```

```
Copied!1
sl-text .lists .lists.selected {background: #fff;} /* 为选中的列表项设置背景色为白色 */
```

悬停颜色：

```
Copied!1
2
3
4
5
6
7
sl-text .lists .lists:hover {
   background: #fff; /* 鼠标悬停时，背景色变为白色 */
}

sl-text .lists .lists.selected:hover {
   background: #f5f9fa; /* 选中状态下鼠标悬停时，背景色变为淡蓝色 */
}
```

## 文本微件

文本微件是Slate微件中最通用的微件之一。它也是许多其他微件的基础，例如HTML、图像、卡片和列表。这些微件只是一些默认代码开始的文本微件，以便为您提供正确的选项。

文本微件有两种模式：Markdown模式和HTML模式。Markdown是一种轻量级标记语言，可呈现为HTML，因此在HTML模式下可以完成的任何操作，也可以在Markdown模式下完成。Markdown模式让您可以利用更简单、非常易读的Markdown语法。例如，要将一些文本设置为标题（H1），只需在它前面添加一个#符号：

有关其他Markdown语法，请参考Markdown文档 ↗。

### 示例

#### 文本微件中的Handlebars

您可以在文本微件中使用Handlebars来显示动态文本（例如，在另一个微件中选择的内容或查询）。

#### 工具提示

文本微件支持用户定义的工具提示。当用户将鼠标悬停在微件内容中的sl-tooltipHTML元素上时，会出现工具提示。

- 静态工具提示：
- 使用sl-tooltip元素内部文本内容的工具提示：
- 具有自定义值的多个工具提示：
### 属性

| 属性 | 描述 | 类型 | 必需 | 更改者 |
| --- | --- | --- | --- | --- |
| markupLanguage | 指定微件的标记语言，可以是Markdown ↗或HTML。 | 字符串 | 是 | 直接编辑 |
| selectedValues | 如果处于选择模式，则为所有已选项目的选定值 | 字符串[] | 是 | 用户交互 |
| selectionType | 确定选择的类型 - ‘无’、‘单选’或‘多选’ | 字符串 | 是 | 直接编辑 |
| selectionRequired | 指定是否可以取消选择所有值。启用后，此标志会阻止用户取消选择微件中最终选择的值。如果微件开始时未选择任何值，则在用户进行初始选择后阻止取消选择。 | 布尔值 | 是 | 直接编辑 |
| text | 渲染并显示给用户的内容 | 字符串 | 是 | 直接编辑 |
| tooltipText | 在&元素中的工具提示中显示的文本。支持HTML。 | 字符串 | 是 | 直接编辑 |
| tooltipsEnabled | 指定是否启用工具提示。工具提示将应用于&标签的内容。 | 布尔值 | 是 | 直接编辑 |
| clickEvents | 此文本微件公开的点击事件名称列表。 | 布尔值 | 是 | 直接编辑 |

### ITextHover

| 属性 | 描述 | 类型 | 必需 | 更改者 |
| --- | --- | --- | --- | --- |
| hoverValue | 用户定义的与工具提示关联的值。此值通过将悬停属性添加到工具提示标签来定义。 | 字符串 | 是 | 用户交互 |
| textContent | 指定工具提示标签的内容。 | 字符串 | 是 | 用户交互 |
