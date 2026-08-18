来源: https://palantir.com/docs/zh/foundry/automate/concept-activity/

# 活动

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 活动

基于条件自动记录活动，并在某些元数据属性更改或更新时记录。

基于自动化条件的活动，如Automation triggered和Automation recovered，是以用户级别保存的。这意味着即使您创建了自动化，您也无法看到其他用户的自动化是否触发和执行。您只能看到是否为您触发了自动化。

与用户相关的所有自动化活动时间线显示在Automate应用程序的概览页面上。

单个自动化的活动时间线显示在各个自动化视图的历史选项卡下。

## 活动事件类型

### Automation triggered

当自动化条件满足或阈值条件状态从false变为true时，记录Automation triggered。

### Automation recovered

当阈值条件状态从true变为false时，记录Automation recovered。只有对象集阈值条件可以导致automation recovered活动。

### Condition edited

当任何用户更新自动化条件时，记录Condition edited。

### Subscribed

当您订阅自动化时，记录Subscribed。在您未订阅期间的活动不会被记录或显示。

### Unsubscribed

当您取消订阅自动化时，记录Unsubscribed。在您未订阅期间的活动不会被记录或显示。

### Evaluation failed

当自动化因任何原因评估出错时，记录Evaluation failed。关于失败的详细信息可以从该自动化的活动历史视图中查看。在自动化条件成功评估但通知或操作效果出错的情况下，也可能显示Evaluation failed。

### Paused

当任何用户暂停自动化或由于活动过多自动暂停自动化时，记录Paused。暂停适用于整个自动化。暂停的自动化不会被评估。

### Resumed

当自动化不再暂停时，记录Resumed。恢复适用于整个自动化。

### Muted

当任何用户静音自动化时，记录Muted。静音适用于所有订阅者。静音的自动化仍会被评估，但不会触发任何效果（例如通知或操作）。

### Unmuted

当自动化不再静音时，记录Unmuted。静音适用于所有订阅者，自动化将在静音时间段过后自动解除静音。

## 保留

自动化的历史活动保留六个月，并在此时间后永久删除。如果必须在此日期之后存储历史活动，您可以使用操作将数据存储在一个长期存在的对象中，该对象像任何其他用户创建的对象一样进行管理和控制，参见Foundry Ontology。

当数据被删除时，它也会从Automate应用程序的自动化活动历史选项卡中移除。您可以通过首先单击一个自动化来展开概览面板，然后单击历史来找到历史选项卡。
