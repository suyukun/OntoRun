来源: https://palantir.com/docs/zh/foundry/transforms-python/transforms-python-foundry-connectors/

# Foundry 连接器

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Foundry 连接器

用于从变换API与Foundry交互的连接器。

连接器可以交互式地构建TransformInput和TransformOutput对象，还可以运行Transform。

## FoundryConnector

### classtransforms.foundry.connectors.FoundryConnector(service_config,auth_header,filesystem_id=None,fallback_branches=None,resolver=None)

- 访问Foundry服务的入口点。
- Foundry对象通过提供用于操作数据集的API来管理与Foundry服务的交互。
#### 参数

- service_config(dict ↗)一个符合Java类com.palantir.remoting.api.config.service.ServicesConfigBlock中的JSON规范的配置字典。
- 一个符合Java类com.palantir.remoting.api.config.service.ServicesConfigBlock中的JSON规范的配置字典。
- auth_header(str ↗)连接到Foundry服务时使用的授权字符串。
- 连接到Foundry服务时使用的授权字符串。
- filesystem_id(str ↗, 非必填)使用的支持文件系统。
- 使用的支持文件系统。
- fallback_branches(List[str ↗], 非必填)回退分支。
- 回退分支。
- resolver(Callable[[str ↗],str ↗], 非必填)用于将数据集别名解析为rid的函数。默认情况下，将别名解析为项目路径。
- 用于将数据集别名解析为rid的函数。默认情况下，将别名解析为项目路径。
### input(alias=None,rid=None,branch=None,end_txrid=None,start_txrid=None,schema_version=None)

- 从给定参数构建一个TransformInput。
- 用于构建TransformInput的资源标识符将从给定的alias解析，除非传递了rid参数。
#### 参数

- alias(str ↗, 非必填)数据集的别名。
- 数据集的别名。
- rid(str ↗, 非必填)数据集的资源标识符。
- 数据集的资源标识符。
- branch(str ↗, 非必填)从中读取数据集的分支。如果未设置，则选择Catalog中存在的fallbacks列表中的第一个分支。
- 从中读取数据集的分支。如果未设置，则选择Catalog中存在的fallbacks列表中的第一个分支。
- end_txrid(str ↗, 非必填)视图的结束事务，如果未设置，则默认为给定分支上的最新事务。
- 视图的结束事务，如果未设置，则默认为给定分支上的最新事务。
- start_txrid(str ↗, 非必填)视图的起始事务。
- 视图的起始事务。
- schema_version(str ↗, 非必填)读取时使用的架构版本，如果未设置，则默认为给定分支上的最新架构版本。
- 读取时使用的架构版本，如果未设置，则默认为给定分支上的最新架构版本。
#### 返回

- 表示请求数据集的输入对象。
#### 返回类型

- transforms.api.TransformInput
#### 抛出

- ValueError↗如果未指定alias或rid（但不是同时）。
- 如果未指定alias或rid（但不是同时）。
- ValueError↗如果未指定分支，并且在Catalog中找不到回退分支。
- 如果未指定分支，并且在Catalog中找不到回退分支。
### output(alias=None,rid=None,branch=None,txrid=None,filesystem_id=None)

- 从给定的别名或rid构建一个TransformOutput。
- 用于构建transforms.api.TransformOutput的资源标识符将从给定的alias解析，除非传递了rid参数。
#### 参数

- alias(str ↗, 非必填)数据集的别名。
- 数据集的别名。
- rid(str ↗, 非必填)数据集的资源标识符。
- 数据集的资源标识符。
- branch(str ↗, 非必填)将数据集写入的分支。如果未设置，则选择fallbacks列表中的第一个分支。
- 将数据集写入的分支。如果未设置，则选择fallbacks列表中的第一个分支。
- txrid(str ↗, 非必填)应写入数据的事务。
- 应写入数据的事务。
- filesystem_id(str ↗, 非必填)如果数据集尚不存在，则在其上创建数据集的文件系统。
- 如果数据集尚不存在，则在其上创建数据集的文件系统。
#### 返回

- 表示请求数据集的输出对象。
#### 返回类型

- transforms.api.TransformOutput
#### 抛出

- ValueError↗如果未指定alias或rid（但不是同时）。
- 如果未指定alias或rid（但不是同时）。
### run(transform)

- 使用最新的输入和输出运行给定的Transform。
#### 参数

- transform(transforms.api.Transform)要运行的变换。
- 要运行的变换。
### auth_header

- str用于联系Foundry的授权头。
- 用于联系Foundry的授权头。
### fallback_branches

- List[str]用于检索数据集的回退分支。
- 用于检索数据集的回退分支。
### spark_session

- pyspark.sql.SparkSession↗理解由FoundrySparkManager创建的SparkSession。
- 理解由FoundrySparkManager创建的SparkSession。