来源: https://palantir.com/docs/zh/foundry/slate/applications-style-text/

# 微件上的自定义样式

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 微件上的自定义样式

微件上的自定义样式允许用户在单个微件上应用自定义CSS。这些样式不会与应用程序中的其他微件共享。选择微件时，可以从右侧边栏访问自定义样式。导航到侧边栏的样式标签，在面板底部找到自定义样式部分。

微件上的自定义样式是测试和开发样式的好方法。可以快速轻松地设置背景颜色、字体大小、边框半径等。在单个微件上进行更改并在画布中预览结果，而无需冒着更改应用程序其他部分的风险。

自定义样式可能与样式表中的样式发生冲突，从而导致意外结果。当两者都尝试更改同一类的相同CSS属性时（例如，样式表和自定义样式都更改微件的背景颜色），就会发生这种情况。为了避免这些冲突，自定义样式应仅用于开发和迭代，而样式表则是管理复杂样式的理想选择。

本指南将带您完成为文本微件设置样式的过程。

- 添加一个文本微件并输入Hello World。
添加一个文本微件并输入Hello World。

- 常见的更改文本微件的内容包括颜色、字体、对齐方式和边框。Copied!12345678#w1 {
  background: #d9eef2;
  font-size: 30px;
  color: #1685ca;
  border: 2px solid #89bff5;
  font-family: Times;
  text-align: center
}
常见的更改文本微件的内容包括颜色、字体、对齐方式和边框。

```
Copied!1
2
3
4
5
6
7
8
#w1 {
  background: #d9eef2;
  font-size: 30px;
  color: #1685ca;
  border: 2px solid #89bff5;
  font-family: Times;
  text-align: center
}
```

- 添加另一个文本微件并输入Slate is awesome。
添加另一个文本微件并输入Slate is awesome。

- 注意到样式没有应用到这个新的文本微件，因为我们使用了选择器#w1来指定我们只希望这些更改应用于第一个微件。我们可以简单地将CSS更改为#w1,#w2，以便我们的样式应用于两个文本微件。但是，当我们添加另一个文本微件并希望应用相同的样式时会发生什么？
注意到样式没有应用到这个新的文本微件，因为我们使用了选择器#w1来指定我们只希望这些更改应用于第一个微件。我们可以简单地将CSS更改为#w1,#w2，以便我们的样式应用于两个文本微件。但是，当我们添加另一个文本微件并希望应用相同的样式时会发生什么？

- 在样式编辑器中进行以下更改：Copied!12345678sl-markdown {
  background: #d9eef2;
  font-size: 30px;
  color: #1685ca;
  border: 2px solid #89bff5;
  font-family: Times;
  text-align: center
}sl-markdown是元素标签，代码表示将此样式应用于所有markdown微件。
在样式编辑器中进行以下更改：

```
Copied!1
2
3
4
5
6
7
8
sl-markdown {
  background: #d9eef2;
  font-size: 30px;
  color: #1685ca;
  border: 2px solid #89bff5;
  font-family: Times;
  text-align: center
}
```

sl-markdown是元素标签，代码表示将此样式应用于所有markdown微件。

- 添加第三个文本微件。注意它会自动应用样式。
添加第三个文本微件。注意它会自动应用样式。

- 最后，保留当前CSS并添加#w1的CSS。Copied!12345678910111213141516sl-markdown {
  background: #d9eef2;
  font-size: 30px;
  color: #1685ca;
  border: 2px solid #89bff5;
  font-family: Times;
  text-align: center
}
#w1 {
  background: #f1cbd5;
  font-size: 30px;
  color: #ca1629;
  border: 2px solid #eb5c81;
  font-family: Helvetica;
  text-align: center
}注意这会正确地将w1的样式与其他两个微件区分开来。
最后，保留当前CSS并添加#w1的CSS。

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
sl-markdown {
  background: #d9eef2;
  font-size: 30px;
  color: #1685ca;
  border: 2px solid #89bff5;
  font-family: Times;
  text-align: center
}
#w1 {
  background: #f1cbd5;
  font-size: 30px;
  color: #ca1629;
  border: 2px solid #eb5c81;
  font-family: Helvetica;
  text-align: center
}
```

注意这会正确地将w1的样式与其他两个微件区分开来。
