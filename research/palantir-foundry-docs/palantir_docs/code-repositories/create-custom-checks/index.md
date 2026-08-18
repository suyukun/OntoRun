来源: https://palantir.com/docs/zh/foundry/code-repositories/create-custom-checks/

# 创建自定义检查

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 创建自定义检查

可以创建自定义检查作为Gradle ↗任务。这些任务应该添加到适当的内部build.gradle文件中，在语言子文件夹内。以下是一个 Gradle 任务的示例，当执行时打印Hello World（请注意，doLast方法创建了一个在任务执行时运行的任务操作，而不是在配置时运行）：

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
// 定义自定义任务
task customTask {
    doLast {
        println "Hello World" // 打印 "Hello World"
    }
}

// 为了让任务在CI检查期间执行，必须有一个CI任务依赖于你的自定义任务。
// 这同样在同一个 `build.gradle` 文件中定义。
// 在下面的例子中，`check` 任务将在 CI 中在 `customTask` 之后执行；这就是 `Hello World` 消息将出现在CI日志中的地方。
```

为了使任务在任务列表的末尾执行，您可以使用以下语法。

```
Copied!1
2
3
// 在CI检查结果发布后执行自定义任务
// 使用finalizedBy方法确保customTask在publish任务完成后执行
project.tasks.publish.configure { finalizedBy customTask }
```

要添加依赖项，您可以使用以下CI任务：project.tasks.check、project.tasks.test和project.tasks.publish。我们强烈建议您不要使用或依赖其他CI任务（例如，内部任务），因为这些任务不受保证且可能会更改。

有关Gradle构建脚本提供的功能的更多文档，请参见Gradle 文档 ↗。

不建议向ci.yml文件添加自定义CI检查，因为每次仓库升级时该文件都会被覆盖。
