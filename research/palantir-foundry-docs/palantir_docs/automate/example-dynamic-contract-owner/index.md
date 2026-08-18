来源: https://palantir.com/docs/zh/foundry/automate/example-dynamic-contract-owner/

# 示例：通知合同所有者合同审查

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 示例：通知合同所有者合同审查

在此示例中，我们希望在合同状态更改为需要审查时通知合同所有者。我们将使用Contract对象类型，这是我们为此示例创建的自定义对象类型。

## 条件

我们在自动化创建向导中通过选择Object added to set条件开始。由于我们希望在合同状态更改为需要审查时收到通知，因此我们可以在contract status上对选定对象集添加一个筛选，如下所示。每当一个对象进入筛选后的对象集时，无论是因为创建了状态为需要审查的新对象，还是因为现有对象更改了其状态为需要审查，此自动化都会被触发。

## 效果

接下来，我们选择通知作为效果。

为了确保合同所有者为每个需要审查的合同收到单独的电子邮件，请选择为每个添加的合同发送一次通知选项。为了动态地向相应的合同所有者发送电子邮件，使用Object-property-backed收件人功能，并选择Contract Owners属性作为用户属性。Contract owners是Contract对象上的一个属性，其中包含相关所有者的Foundry用户ID数组（类似于1234a567-8bc9-12ab-3456-7ca89b1c234a）。请注意，所有收件人至少需要在自动化上具有只读权限，否则将不会收到通知。

接下来，我们需要定义我们的通知内容。为了为我们的收件人配置更复杂的通知，我们将使用函数生成的通知内容功能。函数生成的通知在如何构建我们的通知内容方面提供了更多的灵活性，并支持使用HTML内容 (<html>)。

为了支持我们的函数生成的通知，我们在代码库中创建了一个函数，该函数以收件人和合同对象作为输入并返回一个通知。

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
import { Function, Notification, User, ShortNotification, EmailNotificationContent } from "@foundry/functions-api";
import { _automateExampleContract } from "@foundry/ontology-api";

@Function()
public createContractStatusChangeNotification(user: User, contract: _automateExampleContract): Notification | undefined {

    const shortNotification = ShortNotification.builder()
        .heading("Contract change")
        .content(`The contract "${contract.title}" changed its status to ${contract.contractStatus}`)
        .addObjectLink("View contract", contract)
        .build();

    // 定义邮件正文。邮件正文可能包含无头HTML，例如数据表格
    // 注意我们可以在内容中访问用户和合同的属性
    const emailBody = `Hello, ${user.firstName}!
    The contract "${contract.title}" that you are owning changed its status to "${contract.contractStatus}".

    Check the contract details. View more customer information <a href="${contract.customerUrl}">here</a>.
    `;

    const emailNotificationContent = EmailNotificationContent.builder()
        .subject(`Contract change - ${contract.customerName}`)
        .body(emailBody)
        .addObjectLink("View contract", contract)
        .build();

    return Notification.builder()
        .shortNotification(shortNotification)
        .emailNotificationContent(emailNotificationContent)
        .build();
}
```

这个代码片段定义了一个名为createContractStatusChangeNotification的函数，用于生成合同状态更改的通知。它使用了ShortNotification和EmailNotificationContent来构建短通知和电子邮件通知内容。短通知和电子邮件通知都包括合同的标题和状态变更的信息，并提供了查看合同的链接。
发布函数后，我们可以在自动化创建向导中选择该函数，并将函数连接到我们的效果输入中。对于user属性，我们选择通知的Recipient。对于contract，我们选择New Contract added，这是通过我们的对象集条件暴露为条件效果输入的。

## 设置

为防止合同所有者接收有关自动化的状态通知，我们可以在自动化创建向导的设置选项卡中，将自动化管理员组添加到Automation administrators设置中。

## 总结

要完成此过程，我们为自动化提供一个名称，选择一个保存位置，将到期日期调整为“永不过期”，然后保存自动化。
