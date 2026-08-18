来源: https://palantir.com/docs/zh/foundry/cross-app-interactivity/design-guidelines/

# 设计指南

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 设计指南

为放置区域添加适当的样式对于提高其可用性和用户可发现性至关重要。通过以一致的方式为放置区域设置样式，您可以清楚地表明应用程序中的哪些元素是有效的放置区域。在下面的示例中，如果放置区域没有通过“点亮”提供视觉反馈，用户将无法察觉到这个工作流程。

遵循推荐的样式可以确保用户在您的应用程序和Palantir平台之间拖动数据时获得一致的体验。这将明确并改善用户体验，因为应用自定义样式可能会对不同的放置区域状态和最终行为造成混淆。

我们为以下概念提供设计标准：

- 放置区域:向用户显示在哪里放置他们的拖动负载。
- 通知:提供放置成功或失败的反馈。
- 对话框:为用户决策提供选项，决定将放置的数据发送到哪里。
## 放置区域

我们建议为三种不同的状态应用样式：有效放置、无效放置和加载。对于所有这些状态，我们建议在拖动负载悬停在放置区域上时应用不同的样式。

### 放置区域状态

#### 有效放置

当您的放置区域接受当前拖动负载时，应应用此样式。例如，如果放置区域接受Gotham对象媒体类型，并且用户开始拖动Gotham对象，则应将“有效放置”样式应用于放置区域。

#### 无效放置

当您的放置区域不接受当前拖动负载时，应应用此样式。这让用户知道他们不能将当前拖动负载放置到给定的放置区域，因为它不包含有效的媒体类型。例如，如果放置区域仅接受Gotham对象媒体类型，而拖动负载包含text/html媒体类型，则应将“无效放置”样式应用于放置区域。

#### 加载

如果放置区域必须执行异步工作以确定是否接受当前拖动负载，则应应用此样式。在Palantir平台上，加载样式在数据被丰富时应用。

请参阅下方以获取我们放置区域样式的概述，并参阅Blueprint文档↗获取推荐的颜色。

### 小型放置区域

这些样式应应用于应用程序中的较小放置区域，例如选项卡栏或表单输入字段中的放置区域。

#### 加载

```
Copied!1
2
3
4
5
6
7
8
.loading-small {
    background: rgba(143, 153, 168, 0.5); // 灰色3 50%透明度
    border: 1px dashed #F6F7F9; // 浅灰色5
}

.loading-small-drag-hover {
    border: 1px solid #F6F7F9; // 浅灰色5
}
```

```
Copied!1
2
3
.not-valid-small {
    background: rgba(18, 21, 24, 0.6); // 黑色 60%
}
```

```
Copied!1
2
3
4
5
6
7
8
.valid-small {
    background: rgba(24, 74, 144, 0.5); // 半透明的蓝色背景
    border: 2px dashed #8ABBFF; // 虚线边框，颜色为蓝色
}

.valid-small-drag-hover {
    border: 2px solid #8ABBFF; // 实线边框，颜色为蓝色
}
```

### 中型投放区

这些样式应应用于您的应用程序中的中型投放区，例如Object卡片。

#### 加载中

```
Copied!1
2
3
4
5
6
7
8
.loading-medium {
    background: rgba(143, 153, 168, 0.5); // 灰色3 50%的透明度
    border: 1px dashed #F6F7F9; // 浅灰色5
}

.loading-medium-drag-hover {
    border: 1px solid #F6F7F9; // 浅灰色5
}
```

```
Copied!1
2
3
.not-valid-medium {
    background: rgba(18, 21, 24, 0.6); // 黑色，透明度为60%
}
```

#### 有效

```
Copied!1
2
3
4
5
6
7
8
.valid-medium {
    background: rgba(24, 74, 144, 0.2); // 背景设置为蓝色1，透明度为20%
    border: 2px dashed #8ABBFF; // 边框设置为蓝色5，虚线
}

.valid-medium-drag-hover {
    border: 2px solid #8ABBFF; // 边框设置为蓝色5，实线
}
```

### 大型投放区域

这些样式应应用于应用程序中的大型投放区域，例如整个地图。

对于大型投放区域样式，我们应用不同的内外样式。

#### 加载中

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
.loading-inner-large {
    background: rgba(143, 153, 168, 0.25); // 灰色3 25%
    border: 3px dashed #F6F8F9; // 浅灰色5
    border-radius: 5px;
    color: #F6F8F9; // 浅灰色5
}

.loading-inner-large-drag-hover {
    border: 3px solid #F6F8F9; // 浅灰色5
}

.loading-outer-large {
    background: rgba(143, 153, 168, 0.25); // 灰色 25%
    border-radius: 5px;
}
```

#### 无效

```
Copied!1
2
3
4
.not-valid-large {
    background: rgba(18, 21, 24, 0.6); // 黑色 60%
    color: rgba(246, 248, 249, 0.6); // 浅灰色5 60%
}
```

#### 有效

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
.valid-inner-large {
    background: rgba(24, 74, 144, 0.25); // 蓝色1 25%
    border: 3px dashed #8ABBFF; // 蓝色5，虚线边框
    border-radius: 5px; // 圆角
    color: #F6F7F9; // 浅灰色5
}

.valid-inner-large-drag-hover {
    border: 3px solid #8ABBFF; // 蓝色5，实线边框
}

.valid-outer-large {
    background: rgba(24, 74, 144, 0.25); // 蓝色1 25%
    border-radius: 5px; // 圆角
}
```

## 提示

我们建议使用以下提示来传达有关丢弃数据状态的信息。您可以使用Blueprint toast 组件 ↗实现这些提示。

### 丢弃后加载

如果丢弃的数据需要进行额外处理才能将传输的数据更新到应用程序中，请显示此提示。如果丢弃区域需要对数据进行丰富处理才能进行操作，可能会发生这种情况。当数据正在丰富时，加载提示应该出现。

### 数据丰富后有效丢弃

如果丢弃是有效的且应用程序能够利用丢弃的数据，请显示此提示。成功提示应在750毫秒后消失。

### 数据丰富后无效丢弃

如果丢弃区域最初接受了拖动负载，但在数据丢弃后无法使用数据，请显示此提示。此提示应保持显示，直到用户关闭。

### 丢弃的ID过多

如果丢弃区域只能处理一种丢弃的媒体类型实例，请显示此提示。应用程序将只使用丢弃数据中的第一项。此提示应保持显示，直到用户关闭。

## 对话框

对于需要用户进一步决策且有多个选项的丢弃项，请使用带有操作说明的对话框提示。根据应用案例和预期交互自定义对话框内容。以下是一些示例：
