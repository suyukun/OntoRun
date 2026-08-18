来源: https://palantir.com/docs/zh/foundry/slate/widgets-container/

# 容器

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 容器

容器微件类别包括以下微件：

- 基本
- 对话框
- 弹性
- 重复
- 水平拆分
- 垂直拆分
- 标签页
下表提供了有关容器微件可用属性的使用详情。表格后面跟随几个示例。

### 属性

| 属性 | 描述 | 类型 | 必需 | 更改者 |
| --- | --- | --- | --- | --- |
| flex | 指定容器是否应自动对齐和分配子微件之间的空间。 | boolean | 是 | 直接编辑 |
| flexOptions | 配置子微件对齐方式的选项。 | boolean | 否 | 直接编辑 |
| lazyRenderingEnabled | 指定是否只渲染可见的子微件。 | boolean | 是 | 直接编辑 |
| selectedTabIndex | 当前显示的标签页索引。 | number | 是 | 直接编辑 |
| tabContents | 存储每个标签页中微件的内部数组。 | {children: IWidgetModel[]}[] | 是 | 用户交互 |
| tabTitles | 每个标签页的标题。 | ITabTitle[] | 是 | 直接编辑 |
| titlesEnabled | 指定是否在容器顶部显示可点击的标签页标题。 | boolean | 是 | 直接编辑 |
| scrollingEnabled | 指定是否可以滚动溢出的内容。 | boolean | 是 | 直接编辑 |
| splitDirection | 指定容器拆分的方向。 | number | 是 | 直接编辑 |
| splitMovableInConsumerMode | 指定在消费者模式下拆分容器是否可调整大小。 | boolean | 是 | 直接编辑 |
| splitPanel | 内部值，指示容器在拆分容器中是否为面板。 | boolean | 是 | 用户交互 |
| repeat | 指定内容重复的次数。 | number | 否 | 直接编辑 |
| repeating | 指定容器是否为重复容器。 | boolean | 是 | 直接编辑 |
| previewRepeating | 指定是否预览重复容器。 | boolean | 否 | 直接编辑 |

#### ITabTitle

| 属性 | 描述 | 类型 | 必需 | 更改者 |
| --- | --- | --- | --- | --- |
| title | 此标签页的标题。 | 字符串 | 是 | 直接编辑 |

#### IFlexOptions

| 属性 | 描述 | 类型 | 必需 | 更改者 |
| --- | --- | --- | --- | --- |
| justifyContent | 指定子微件在主轴上的布局方式。默认值为水平弹性容器的左侧和垂直弹性容器的顶部。 | 字符串 | 是 | 直接编辑 |
| flexDirection | 指定子微件对齐的主轴。默认值为水平。 | 字符串 | 是 | 直接编辑 |
| flexWrap | 指定子微件是否可以溢出到多行。默认值为未选中。 | 字符串 | 是 | 直接编辑 |

### 用法

通过拖动微件进出容器来添加和移除它们到当前选定的标签页中。tabContents属性在原始标签页中不支持，不应手动编辑，也不会响应用户交互的更改。

### 示例

#### 简单容器

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
{
  "selectedTabIndex": 0,  // 当前选中的标签页索引
  "tabContents": [        // 标签页内容数组
    {
      "children": []      // 每个标签页的子元素
    }
  ],
  "tabTitles": [          // 标签页标题数组
    {
      "title": "Title"    // 每个标签页的标题
    }
  ],
  "titlesEnabled": false  // 标题是否启用
}
```

#### 标签容器

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
{
  "selectedTabIndex": 1,  // 选中的标签索引
  "tabContents": [
    {
      "children": []  // 第一个标签的内容
    },
    {
      "children": []  // 第二个标签的内容
    },
    {
      "children": []  // 第三个标签的内容
    }
  ],
  "tabTitles": [
    {
      "title": "Title 1"  // 第一个标签的标题
    },
    {
      "title": "Title 2"  // 第二个标签的标题
    },
    {
      "title": "Title 3"  // 第三个标签的标题
    }
  ],
  "titlesEnabled": true  // 标题是否启用
}
```

#### 从其他微件驱动选定的选项卡

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
{
  "selectedTabIndex": "{{w8.selectedValue}}",  // 选中的选项卡索引，由变量 w8.selectedValue 动态决定
  "tabContents": [
    {
      "children": []  // 第一个选项卡的子元素，目前为空
    },
    {
      "children": []  // 第二个选项卡的子元素，目前为空
    },
    {
      "children": []  // 第三个选项卡的子元素，目前为空
    }
  ],
  "tabTitles": [
    {
      "title": "Title 1"  // 第一个选项卡的标题
    },
    {
      "title": "Title 2"  // 第二个选项卡的标题
    },
    {
      "title": "Title 3"  // 第三个选项卡的标题
    }
  ],
  "titlesEnabled": false  // 标题是否启用，当前设置为不启用
}
```

## 对话框微件

下表提供了对话框微件可用属性的使用详情。表格后面有几个示例。

### 属性

| 属性 | 描述 | 类型 | 必需 | 更改者 |
| --- | --- | --- | --- | --- |
| title | 对话框的标题。 | 字符串 | 否 | 直接编辑 |
| canEscapeKeyClose | 当使用Escape键时关闭对话框。 | boolean | 是 | 直接编辑 |
| canOutsideClickClose | 当用户点击覆盖背景时关闭对话框。 | boolean | 是 | 直接编辑 |

#### 操作

| 操作名称 | 描述 |
| --- | --- |
| close | 触发此操作将导致对话框关闭。 |
| open | 触发此操作将导致对话框打开。 |

#### 事件

| 事件名称 | 描述 |
| --- | --- |
| closed | 当对话框完全关闭时触发此事件。 |
| opened | 当对话框完全打开时触发此事件。 |

## 常用CSS

您可以使用以下CSS设置容器的背景颜色和边框：

```
Copied!1
2
3
4
5
sl-app-container {
  background: lightgrey; /* 设置背景颜色为浅灰色 */
  border-left:none; /* 去除左边框 */
  border-right:none; /* 去除右边框 */
}
```

虽然sl-app-container选择器和background属性可以正确设置容器微件的背景颜色和边框，但请在本地样式表中使用div.canvas-body选择器和background-color属性以调整 Slate 应用画布的颜色和边框。在下面的示例中，我们使用样式编辑器自定义了 Slate 画布、容器微件和条形图的颜色：

### 标签式容器

标签样式：

```
Copied!1
2
3
4
5
6
sl-app-container table.container-titles tbody tr td.tab-title {
  color: #2786c1; /* 设置字体颜色为#2786c1 */
  text-transform:uppercase; /* 将文本转换为大写 */
  border-left:none; /* 去掉左边框 */
  border-right:none; /* 去掉右边框 */
}
```

悬停样式：

```
Copied!1
2
sl-app-container table.container-titles tbody tr td.tab-title:hover {text-decoration:none;}
/* 当鼠标悬停在包含类 `tab-title` 的 `td` 元素上时，取消文本装饰效果 */
```

选择样式：

```
Copied!1
2
3
4
sl-app-container table.container-titles tbody tr td.tab-title.selected {
  color: #394B59; /* 设置选中标签标题的字体颜色 */
  border-bottom:4px solid #2786C1; /* 设置选中标签标题底部的边框颜色和宽度 */
}
```

单个标签样式：

```
Copied!1
2
3
4
sl-app-container table.container-titles tbody tr td.tab-title:last-child {
  border-left:none; /* 去掉最后一个单元格的左边框 */
  border-right:none; /* 去掉最后一个单元格的右边框 */
}
```
