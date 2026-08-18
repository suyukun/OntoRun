来源: https://palantir.com/docs/zh/foundry/transforms-java/unit-tests/

# 单元测试

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 单元测试

Java变换支持在CI检查中运行单元测试。

Java变换目前不支持交互式单元测试或调试。如果您的应用案例需要此功能，请考虑使用Python变换。

此页面描述的Java单元测试仅适用于批处理管道，不支持流处理管道。

当您将com.palantir.transforms.lang.java-defaults插件应用于Java变换子项目时，单元测试环境会默认设置。它将流行的Java单元测试库JUnit ↗、Mockito ↗和AssertJ ↗添加到子项目的testCompile配置中。您应该将测试文件放在src/test/java下，以便Gradle自动识别它们。有关如何向环境中添加插件的更多详细信息，请参阅Python测试中的步骤。

## 使用Spark进行测试

我们提供了一个JUnit5扩展和一个JUnit4规则，以帮助您轻松访问托管的SparkSession。

如果您使用JUnit5，请像声明常规扩展一样声明扩展：

```
Copied!1
2
3
4
5
6
import com.palantir.transforms.lang.java.testing.api.SparkSessionExtension;
import org.junit.jupiter.api.extension.RegisterExtension;

// 使用 @RegisterExtension 注册一个 SparkSessionExtension 对象
@RegisterExtension
public static SparkSessionExtension sparkSession = new SparkSessionExtension();
```

这段代码中，SparkSessionExtension是一个用于测试的 Spark 会话扩展，@RegisterExtension注解用于在 JUnit 5 中注册一个扩展。
如果您使用的是已弃用的JUnit4，您可以在测试文件中将SparkSession声明为ClassRule或Rule。例如：

```
Copied!1
2
3
4
5
6
import com.palantir.transforms.lang.java.testing.api.SparkSessionResource;
import org.junit.ClassRule;

// @ClassRule注解用于JUnit测试框架，表示该规则在所有测试方法之前和之后运行
@ClassRule
public static SparkSessionResource sparkSession = new SparkSessionResource(); // 初始化SparkSessionResource用于测试
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
import com.palantir.transforms.lang.java.testing.api.SparkSessionResource;
import org.junit.Rule;

// @Rule 注解用于JUnit测试中，用于管理测试的生命周期
@Rule
public static SparkSessionResource sparkSession = new SparkSessionResource();
// SparkSessionResource 用于在测试中提供 SparkSession 实例，
// 这对于需要测试 Spark 应用的 Java 代码非常有用
```

在这两种情况下，您可以在测试中正常使用扩展或规则，如以下代码片段所示：

```
Copied!1
2
3
4
5
@Test
public void myUnitTest() {
    // 获取 SparkSession 实例
    SparkSession sparkSession = sparkSession.get();
}
```

请注意，在 JUnit4 中，ClassRule和Rule是不同的：如果将SparkSession声明为ClassRule，则同一SparkSession会在测试类中的所有测试之间共享。这将为您节省一些重建SparkSession的时间，但类路径将继承自之前运行的测试。

相比之下，如果将SparkSession声明为Rule，则每个单独的测试都会获得一个新的独立的SparkSession。如果在一个类中有许多测试使用SparkSession，这可能会导致显著的性能下降。

如果在一个类中有很多测试使用SparkSession，将其声明为Rule可能会导致显著的性能下降。因此，我们强烈建议尽可能使用ClassRule，或者使用 JUnit5 的Extension而不是 JUnit4 的规则。
