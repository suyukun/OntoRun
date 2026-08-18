来源: https://palantir.com/docs/zh/foundry/automate/example-relative-time-condition/

# 示例：在指定时间后自动关闭未处理的票据

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 示例：在指定时间后自动关闭未处理的票据

在此示例中，我们希望自动关闭在过去365天内没有更新的未处理客服支持票据。我们将使用Support Ticket对象类型，这是我们为此示例创建的自定义对象类型。

## 条件

我们在自动化创建向导中通过选择Object added to set条件开始。首先，我们需要定义旧的、未关闭问题的对象集。我们首先选择Support Ticket类型。接下来，我们在对象集上添加两个筛选：一个是票据的status不为关闭，另一个是last update至少发生在365天前。由于我们使用的是相对时间筛选，条件将通过计划监控进行评估。我们保持每日评估的默认设置。

通过此配置，自动化将每日检查是否有新的客服支持票据在过去365天内没有更新且未关闭。

## 效果

要自动关闭Support Tickets，必须在我们标识为未处理的对象上运行一个操作效果。

为此，我们使用已经在Ontology Manager中预配置的Close Support Tickets操作。

对于Support Tickets参数，使用我们的对象集条件中的New Support Tickets added条件效果输入，如下所示。这样，触发自动化的对象将被传递到close-ticket操作。对于执行模式，保持默认的Execute once for all Support Tickets added，以便即使多个Support Ticket对象同时触发条件，效果也仅执行一次。

## 总结

要完成此过程，请为自动化提供一个名称，选择保存位置，将到期日期调整为永不过期，并保存自动化。
