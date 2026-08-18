来源: https://palantir.com/docs/zh/foundry/available-connectors/other-source-types/

# 其他数据源类型

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 其他数据源类型

Foundry的数据连接框架使您能够配置与各种企业数据系统的同步。这包括在特定行业领域中常用的数据源，例如制造业、公用事业和医疗保健。本页提供了一些已与Foundry集成的行业特定数据源的参考。

如果您有兴趣将某个数据系统与Foundry集成，请联系您的Palantir代表以获取更多详细信息。

## IOT / IIOT

物联网（IOT）和工业物联网（IIOT）系统通常生成数据流和时间序列，这些数据可以同步到Foundry中以进行分析和操作流程。IOT数据源最常通过数据连接的流数据支持进行集成。Foundry已集成的一些IOT / IIOT系统示例包括：

- Amazon IoT Core
- Azure Event Hub
- Google IoT Core
- OPC-UA
- OSI PI
## 地理空间系统

一些常与Foundry集成的地理空间数据系统示例包括：

- ESRI / ArcGIS
- PostGIS
- Oracle Spatial DBs
此外，导出为多种文件格式的地理空间数据可以通过数据连接的文件系统和大对象存储源类型（如Amazon S3）轻松集成。Foundry中常用的地理空间文件格式包括：

- Shapefiles
- KMZ / KML
- FGDB
- Geojson
最后，数据连接对REST APIs的支持可以用于与常用服务集成，例如Web Feature Service ↗(WFS)。

## EHRs / EMRs

数据连接已被用于连接到国际范围内的各种电子健康记录（EHR）和电子病历（EMR）系统。请联系您的Palantir代表以获取更多详细信息。

## 生产力工具

通过数据连接对REST APIs的支持，通常可以配置与生产力和任务管理工具的连接。以前集成的一些生产力工具示例包括：

- Artifactory
- Asana
- Github
- JIRA
- PagerDuty
- ServiceNOW
- Slack