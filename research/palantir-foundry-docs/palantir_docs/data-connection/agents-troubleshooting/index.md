来源: https://palantir.com/docs/zh/foundry/data-connection/agents-troubleshooting/

# 故障排除参考

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 故障排除参考

Agent Manager 在其安装的服务器上被称为 "bootvisor"。

本页面包含如何配置代理日志的信息，描述了几个代理配置的常见问题，并提供调试指南。
描述的步骤必须在通过SSH进入安装代理的主机后执行。
在探讨其他故障排除主题之前，我们建议首先检查./var/diagnostic/launch.yml以确认代理是否成功连接到Foundry。如果连接不成功，请按照字段enhancedMessage中描述的说明进行操作。

代理配置的常见问题

- 代理和Agent Manager显示为"离线"状态，但在代理主机上返回"运行中"
- Agent Manager显示为"离线"状态
- Bootstrapper显示为"从未报告"状态
- 代理显示为"在线"，但不响应重启
- 代理状态显示为"不健康"
- 无法下载代理包
- 无法管理代理
代理配置参考

- 使用不安全的TLSv1.0和TLSv1.1协议连接到数据源
- 配置代理日志
- 当安装代理的主机崩溃时，缓存文件会发生什么？
## 代理配置的常见问题

#### 代理和Agent Manager显示为"离线"状态，但在代理主机上返回"运行中"

- 第一步是检查代理安装的主机是否可以访问Foundry。为此，请在代理安装的主机上运行curl -s https://<your domain name>/magritte-coordinator/api/ping > /dev/null && echo pass || echo fail。如果一切正常，你应该看到输出为pass。在这种情况下，你应该：确定是否需要代理以访问Foundry，如果需要，请检查代理是否已配置为使用它（如何配置代理使用代理的说明可以在代理配置页面找到）。你可以通过在基于Unix的机器的命令行上运行echo $http_proxy来验证是否正在使用代理。如果你认为不需要代理，或者你已经配置了一个代理，请联系你的Palantir代表。如果主机无法访问Foundry，你可能会看到如下错误：curl: (6) Could not resolve host: ...。在这种情况下，很可能有东西阻止了连接（例如防火墙或代理），你应该联系你的Palantir代表。
- 如果一切正常，你应该看到输出为pass。在这种情况下，你应该：确定是否需要代理以访问Foundry，如果需要，请检查代理是否已配置为使用它（如何配置代理使用代理的说明可以在代理配置页面找到）。你可以通过在基于Unix的机器的命令行上运行echo $http_proxy来验证是否正在使用代理。如果你认为不需要代理，或者你已经配置了一个代理，请联系你的Palantir代表。
- 确定是否需要代理以访问Foundry，如果需要，请检查代理是否已配置为使用它（如何配置代理使用代理的说明可以在代理配置页面找到）。你可以通过在基于Unix的机器的命令行上运行echo $http_proxy来验证是否正在使用代理。
- 如果你认为不需要代理，或者你已经配置了一个代理，请联系你的Palantir代表。
- 如果主机无法访问Foundry，你可能会看到如下错误：curl: (6) Could not resolve host: ...。在这种情况下，很可能有东西阻止了连接（例如防火墙或代理），你应该联系你的Palantir代表。
#### Agent Manager显示为"离线"状态

- 检查<agent-manager-install-location>/var/log/startup.log文件的内容。如果看到以下错误：Caused by: java.net.BindException: {} Address already in use，这意味着已经有一个进程在Agent Manager尝试绑定的端口上运行。要解决此问题，你应首先确定Agent Manager尝试绑定的端口。这可以通过检查<agent-manager-directory>/var/conf/install.yml文件的内容并寻找port参数来完成（例如，port: 1234- 这里1234是端口）。注意，如果没有定义端口参数，Agent Manager将使用默认端口7032。一旦知道Agent Manager尝试绑定的端口，你应该识别已经在其上运行的进程。这可以通过运行以下命令来实现：ps aux | grep $(lsof -i:<PORT> |awk 'NR>1 {print $2}' |sort -n |uniq)，其中<PORT>是Agent Manager尝试绑定的端口。如果上述命令返回的响应包含：com.palantir.magritte.bootvisor.BootvisorApplication，这意味着另一个Agent Manager已经在运行。在这种情况下，你应该确定这是否是故意的；如果是这样，你将需要更改配置中的端口以消除两个Agent Manager之间的冲突，按照以下步骤进行。否则，你需要确定你想在此主机上使用哪个特定的Agent Manager安装，停止运行的其他Agent Manager，并仅启动你打算继续使用的那个。要修复BindException错误，你需要为Agent Manager找到一个新的端口，该端口当前未被使用。端口号应在1025到65536之间（端口号0到1024保留用于特权服务，并指定为知名端口）。你可以通过执行以下命令来检查是否已经有进程在端口上运行：lsof -i :<PORT>，其中<PORT>是选择的端口号。找到可用端口后，你需要在存储于<agent-manager-directory>/var/conf/install.yml的配置中添加（或更新）port参数。以下是一个设置了端口为7032的Agent Manager配置片段：Copied!123...
port: 7032
auto-start-agent: true保存上述配置后，通过运行<agent-manager-root>/service/bin/init.sh stop && <agent-manager-root>/service/bin/init.sh start重启Agent Manager。
- 如果看到以下错误：Caused by: java.net.BindException: {} Address already in use，这意味着已经有一个进程在Agent Manager尝试绑定的端口上运行。要解决此问题，你应首先确定Agent Manager尝试绑定的端口。这可以通过检查<agent-manager-directory>/var/conf/install.yml文件的内容并寻找port参数来完成（例如，port: 1234- 这里1234是端口）。注意，如果没有定义端口参数，Agent Manager将使用默认端口7032。一旦知道Agent Manager尝试绑定的端口，你应该识别已经在其上运行的进程。这可以通过运行以下命令来实现：ps aux | grep $(lsof -i:<PORT> |awk 'NR>1 {print $2}' |sort -n |uniq)，其中<PORT>是Agent Manager尝试绑定的端口。如果上述命令返回的响应包含：com.palantir.magritte.bootvisor.BootvisorApplication，这意味着另一个Agent Manager已经在运行。在这种情况下，你应该确定这是否是故意的；如果是这样，你将需要更改配置中的端口以消除两个Agent Manager之间的冲突，按照以下步骤进行。否则，你需要确定你想在此主机上使用哪个特定的Agent Manager安装，停止运行的其他Agent Manager，并仅启动你打算继续使用的那个。
如果看到以下错误：Caused by: java.net.BindException: {} Address already in use，这意味着已经有一个进程在Agent Manager尝试绑定的端口上运行。

- 要解决此问题，你应首先确定Agent Manager尝试绑定的端口。这可以通过检查<agent-manager-directory>/var/conf/install.yml文件的内容并寻找port参数来完成（例如，port: 1234- 这里1234是端口）。注意，如果没有定义端口参数，Agent Manager将使用默认端口7032。
- 一旦知道Agent Manager尝试绑定的端口，你应该识别已经在其上运行的进程。这可以通过运行以下命令来实现：ps aux | grep $(lsof -i:<PORT> |awk 'NR>1 {print $2}' |sort -n |uniq)，其中<PORT>是Agent Manager尝试绑定的端口。如果上述命令返回的响应包含：com.palantir.magritte.bootvisor.BootvisorApplication，这意味着另一个Agent Manager已经在运行。在这种情况下，你应该确定这是否是故意的；如果是这样，你将需要更改配置中的端口以消除两个Agent Manager之间的冲突，按照以下步骤进行。否则，你需要确定你想在此主机上使用哪个特定的Agent Manager安装，停止运行的其他Agent Manager，并仅启动你打算继续使用的那个。
- 如果上述命令返回的响应包含：com.palantir.magritte.bootvisor.BootvisorApplication，这意味着另一个Agent Manager已经在运行。
- 在这种情况下，你应该确定这是否是故意的；如果是这样，你将需要更改配置中的端口以消除两个Agent Manager之间的冲突，按照以下步骤进行。否则，你需要确定你想在此主机上使用哪个特定的Agent Manager安装，停止运行的其他Agent Manager，并仅启动你打算继续使用的那个。
- 要修复BindException错误，你需要为Agent Manager找到一个新的端口，该端口当前未被使用。端口号应在1025到65536之间（端口号0到1024保留用于特权服务，并指定为知名端口）。你可以通过执行以下命令来检查是否已经有进程在端口上运行：lsof -i :<PORT>，其中<PORT>是选择的端口号。
要修复BindException错误，你需要为Agent Manager找到一个新的端口，该端口当前未被使用。

- 端口号应在1025到65536之间（端口号0到1024保留用于特权服务，并指定为知名端口）。
- 你可以通过执行以下命令来检查是否已经有进程在端口上运行：lsof -i :<PORT>，其中<PORT>是选择的端口号。
- 找到可用端口后，你需要在存储于<agent-manager-directory>/var/conf/install.yml的配置中添加（或更新）port参数。
找到可用端口后，你需要在存储于<agent-manager-directory>/var/conf/install.yml的配置中添加（或更新）port参数。

- 以下是一个设置了端口为7032的Agent Manager配置片段：Copied!123...
port: 7032
auto-start-agent: true
以下是一个设置了端口为7032的Agent Manager配置片段：

```
Copied!1
2
3
...
port: 7032
auto-start-agent: true
```

- 保存上述配置后，通过运行<agent-manager-root>/service/bin/init.sh stop && <agent-manager-root>/service/bin/init.sh start重启Agent Manager。
保存上述配置后，通过运行<agent-manager-root>/service/bin/init.sh stop && <agent-manager-root>/service/bin/init.sh start重启Agent Manager。

#### Bootstrapper显示为"从未报告"状态

- 检查<agent-manager-directory>/var/data/processes/<latest-bootstrapper-directory>/var/log/startup.log文件的内容。如果看到以下错误：Caused by: java.net.BindException: {} Address already in use，这意味着已经有一个进程在Bootstrapper尝试绑定的端口上运行。为了解决此问题，你应首先确定Bootstrapper尝试绑定的端口。这可以通过导航到Data Connection应用程序中的代理概览页面来完成。从那里，你需要选择"高级"配置按钮，最后点击"Bootstrapper"选项卡。Bootstrapper将尝试绑定的端口在port参数下定义（例如，port: 1234- 这里1234是端口）。注意，Bootstrapper的默认端口是7002。一旦知道Bootstrapper尝试绑定的端口，你应识别已经在其上运行的进程。这可以通过运行以下命令来实现：ps aux | grep $(lsof -i:$PORT |awk 'NR>1 {print $2}' |sort -n |uniq)，其中$PORT是Bootstrapper尝试绑定的端口。如果上述命令返回的响应包含com.palantir.magritte.bootstrapper.MagritteBootstrapperApplication，这意味着另一个Bootstrapper已经在运行。在这种情况下，你应确定这是否是故意的；如果是这样，你将需要更改配置中的端口以消除两个Bootstrappers之间的冲突，按照以下步骤进行。否则，你需要确定你想在此主机上使用哪个特定的Bootstrapper安装，停止运行的其他Bootstrapper，并仅启动你打算继续使用的那个。要修复BindException错误，你需要为Bootstrapper找到一个新的端口，该端口当前未被使用。端口号应在1025到65536之间（端口号0到1024保留用于特权服务，并指定为知名端口）。你可以通过执行以下命令来检查是否已经有进程在端口上运行：lsof -i :<PORT>，其中<PORT>是选择的端口号。找到可用端口后，你需要在Bootstrapper的配置中设置port参数。这可以通过导航到Data Connection应用程序中的代理概览页面来完成。从那里选择高级配置按钮，最后导航到"Bootstrapper"选项卡。以下是一个设置了端口为7002的Bootstrapper配置片段：Copied!1234server:
  adminConnectors:
    ...
    port: 7002 #这是端口值更新配置后，你将需要保存更改并重启代理以使其生效。
检查<agent-manager-directory>/var/data/processes/<latest-bootstrapper-directory>/var/log/startup.log文件的内容。

- 如果看到以下错误：Caused by: java.net.BindException: {} Address already in use，这意味着已经有一个进程在Bootstrapper尝试绑定的端口上运行。为了解决此问题，你应首先确定Bootstrapper尝试绑定的端口。这可以通过导航到Data Connection应用程序中的代理概览页面来完成。从那里，你需要选择"高级"配置按钮，最后点击"Bootstrapper"选项卡。Bootstrapper将尝试绑定的端口在port参数下定义（例如，port: 1234- 这里1234是端口）。注意，Bootstrapper的默认端口是7002。一旦知道Bootstrapper尝试绑定的端口，你应识别已经在其上运行的进程。这可以通过运行以下命令来实现：ps aux | grep $(lsof -i:$PORT |awk 'NR>1 {print $2}' |sort -n |uniq)，其中$PORT是Bootstrapper尝试绑定的端口。如果上述命令返回的响应包含com.palantir.magritte.bootstrapper.MagritteBootstrapperApplication，这意味着另一个Bootstrapper已经在运行。在这种情况下，你应确定这是否是故意的；如果是这样，你将需要更改配置中的端口以消除两个Bootstrappers之间的冲突，按照以下步骤进行。否则，你需要确定你想在此主机上使用哪个特定的Bootstrapper安装，停止运行的其他Bootstrapper，并仅启动你打算继续使用的那个。
如果看到以下错误：Caused by: java.net.BindException: {} Address already in use，这意味着已经有一个进程在Bootstrapper尝试绑定的端口上运行。

- 为了解决此问题，你应首先确定Bootstrapper尝试绑定的端口。这可以通过导航到Data Connection应用程序中的代理概览页面来完成。从那里，你需要选择"高级"配置按钮，最后点击"Bootstrapper"选项卡。Bootstrapper将尝试绑定的端口在port参数下定义（例如，port: 1234- 这里1234是端口）。注意，Bootstrapper的默认端口是7002。
- 一旦知道Bootstrapper尝试绑定的端口，你应识别已经在其上运行的进程。这可以通过运行以下命令来实现：ps aux | grep $(lsof -i:$PORT |awk 'NR>1 {print $2}' |sort -n |uniq)，其中$PORT是Bootstrapper尝试绑定的端口。如果上述命令返回的响应包含com.palantir.magritte.bootstrapper.MagritteBootstrapperApplication，这意味着另一个Bootstrapper已经在运行。在这种情况下，你应确定这是否是故意的；如果是这样，你将需要更改配置中的端口以消除两个Bootstrappers之间的冲突，按照以下步骤进行。否则，你需要确定你想在此主机上使用哪个特定的Bootstrapper安装，停止运行的其他Bootstrapper，并仅启动你打算继续使用的那个。
- 如果上述命令返回的响应包含com.palantir.magritte.bootstrapper.MagritteBootstrapperApplication，这意味着另一个Bootstrapper已经在运行。
- 在这种情况下，你应确定这是否是故意的；如果是这样，你将需要更改配置中的端口以消除两个Bootstrappers之间的冲突，按照以下步骤进行。否则，你需要确定你想在此主机上使用哪个特定的Bootstrapper安装，停止运行的其他Bootstrapper，并仅启动你打算继续使用的那个。
- 要修复BindException错误，你需要为Bootstrapper找到一个新的端口，该端口当前未被使用。端口号应在1025到65536之间（端口号0到1024保留用于特权服务，并指定为知名端口）。你可以通过执行以下命令来检查是否已经有进程在端口上运行：lsof -i :<PORT>，其中<PORT>是选择的端口号。
要修复BindException错误，你需要为Bootstrapper找到一个新的端口，该端口当前未被使用。

- 端口号应在1025到65536之间（端口号0到1024保留用于特权服务，并指定为知名端口）。
- 你可以通过执行以下命令来检查是否已经有进程在端口上运行：lsof -i :<PORT>，其中<PORT>是选择的端口号。
- 找到可用端口后，你需要在Bootstrapper的配置中设置port参数。这可以通过导航到Data Connection应用程序中的代理概览页面来完成。从那里选择高级配置按钮，最后导航到"Bootstrapper"选项卡。
找到可用端口后，你需要在Bootstrapper的配置中设置port参数。这可以通过导航到Data Connection应用程序中的代理概览页面来完成。从那里选择高级配置按钮，最后导航到"Bootstrapper"选项卡。

- 以下是一个设置了端口为7002的Bootstrapper配置片段：Copied!1234server:
  adminConnectors:
    ...
    port: 7002 #这是端口值
以下是一个设置了端口为7002的Bootstrapper配置片段：

```
Copied!1
2
3
4
server:
  adminConnectors:
    ...
    port: 7002 #这是端口值
```

- 更新配置后，你将需要保存更改并重启代理以使其生效。
更新配置后，你将需要保存更改并重启代理以使其生效。

#### 代理显示为"在线"，但不响应重启

通常，这种情况是由运行的另一个"幽灵"实例的代理引起的，你需要找到并关闭它。

要查找并终止旧进程，请按照以下步骤操作：

- 通过运行<agent-manager-install-location>/service/bin/init.sh stop停止Agent Manager。
- 删除<agent-manager-install-location>/var/data/processes/index.json文件。
- 运行for folder in $(ls -d <agent-manager-root>/var/data/processes/*/); do $folder/service/bin/init.sh stop; done以关闭旧进程。
- 返回Data Connection并检查代理不再报告（需要2-3分钟）。
- 启动Agent Manager（<agent-manager-install-location>/service/bin/init.sh start）。
在安装代理的主机上手动启动代理（而不是通过Data Connection）可能导致创建"幽灵"进程。

#### 代理状态显示为"不健康"

通常当代理进程显示为"不健康"时，是因为它已崩溃或被操作系统或其他软件（例如防病毒软件）关闭。

操作系统可能关闭进程的原因有很多，但最常见的是操作系统没有足够的内存来运行它，这被称为OOM（内存不足）杀死。

要检查任何代理或Explorer子进程是否被操作系统OOM杀死，你可以运行以下命令：grep "exited with return code 137" -r <agent-manager-directory> --include=*.log。这将搜索Agent Manager目录内的所有日志文件，查找包含'exited with return code 137'的条目（返回代码137表示一个进程被OOM杀死）。

以下是上述命令产生的示例输出，显示代理子进程被OOM杀死。:./var/data/processes/bootstrapper~<>/var/log/magritte-bootstrapper.log:ERROR [timestamp] com.palantir.magritte.bootstrapper.ProcessMonitor: magritte-agent exited with return code 137。如果看到类似的输出，你应按照以下步骤调整堆大小。

你也可以通过运行以下命令检查操作系统日志中的OOM kill条目：dmesg -T | egrep -i 'killed process。此命令将搜索内核环缓冲区中的'killed process'日志条目，这表示一个进程被OOM杀死。

OOM杀死的进程的实际日志条目如下所示：

- [timestamp] Out of memory: Killed process 9423 (java) total-vm:2928192kB, anon-rss:108604kB, file-rss:0kB, shmem-rss:0kB, UID:0 pgtables:1232kB oom_score_adj:0
- 上述日志行显示被杀死的进程具有PID 9423（注意：你的日志消息可能会根据Linux发行版和系统配置而有所不同）。
- 在这种情况下，你应尝试验证被杀死的进程是否与代理有关。最简单的方法是对齐时间戳，即，如果一个条目的时间戳与代理变得不健康的时间一致，则可能两者相关。注意任何不包含(java)的条目可以忽略，因为它们与代理无关。
##### 调整堆大小

在更改任何堆分配之前，你应首先：

- 计算主机可用的内存量。
- 要查看主机可用的内存量，你可以运行free -h。在一个6 GB的系统上，输出可能类似于以下内容：
```
Copied!1
2
3
4
5
6
                total        used        free      shared  buff/cache   available
Mem:          5.8Gi       961Mi       2.8Gi       9.0Mi       2.1Gi       4.6Gi
# 内存（Mem）总量为5.8GiB，其中已用961MiB，空闲2.8GiB，共享9.0MiB，缓冲/缓存2.1GiB，可用4.6GiB

Swap:         1.0Gi          0B       1.0Gi
# 交换分区（Swap）总量为1.0GiB，已用0B，空闲1.0GiB
```

在free命令生成的输出中，available列显示了可以用于启动新应用程序的内存量。为了确定可以分配给代理的内存量，我们建议您停止代理并在系统负载正常到高的情况下运行free -h。可用值将告诉您可以用于所有代理进程的最大内存量。我们建议尽可能保留大约2 - 4GB的缓冲区，以考虑系统上其他进程需要更多内存，以及代理进程的堆外内存使用。请注意，并非所有版本的free都显示可用列，因此您可能需要检查系统上版本的文档以找到等效信息。

确定分配给以下每个子进程的内存量：Agent Manager、Bootstrapper、agent和Explorer。

要找出分配给agent和Explorer子进程的内存量，您应导航到Data Connection中的代理配置页面，选择高级配置按钮，并选择“Bootstrapper”选项卡。在这里，您将看到每个子进程都有自己的配置块；在每个块中，您应看到一个jvmHeapSize参数，该参数定义了分配给相关进程的内存量。

默认情况下，Bootstrapper子进程被分配512mb的内存。这可以通过首先导航到<agent-manager-directory>/var/data/processes/目录来确认；从那里，您需要运行ls -lrt以找到最近创建的bootstrapper~<uuid>目录。一旦进入最近创建的bootstrapper~<uuid>目录，您可以查看./var/conf/launcher-custom.yml文件的内容。这里的Xmx值是分配给Bootstrapper的内存量。

默认情况下，Agent Manager子进程也被分配512mb的内存。这可以通过查看文件<agent-manager-directory>/var/conf/launcher-custom.yml的内容来确认。这里的Xmx值是分配给Agent Manager的内存量。

安装在Windows机器上的代理不使用launcher-custom.yml文件，因此默认情况下，Java将为Agent Manager和Bootstrapper进程分配系统可用内存的25%。要解决此问题，您需要手动设置Agent Manager和Bootstrapper的堆大小，可以通过以下步骤完成：

- 确保您已经终止了所有代理进程，即： (Agent Manager, Bootstrapper, agent, 和 Explorer)。
- 设置 JAVA_HOME:setx -m JAVA_HOME "{BOOTVISOR_INSTALL_DIR}\jdk\{JDK_VERSION}-win_x64\"
- 设置 Agent Manager 堆大小:setx -m MAGRITTE_BOOTVISOR_WIN_OPTS "-Xmx512M -Xms512M"
- 设置 Bootstrapper 堆大小:setx -m MAGRITTE_BOOTSTRAPPER_OPTS "-Xmx512M -Xms512M"
- 关闭命令提示符并打开一个新的。这是为了使上述设置生效。
- 启动 Agent Manager:.\service\bin\magritte-bootvisor-win
一旦确定了主机可用的内存量以及分配给上述每个子进程的内存量，您应该决定是减少分配给上述进程的内存量还是增加主机的可用内存量。

是否可以安全地减少代理进程使用的内存量将取决于您的代理设置（例如，最大并发同步数和文件上传并行性）、正在同步的数据类型以及代理上的典型负载。减少堆大小会降低操作系统终止进程的可能性，但增加Java进程耗尽堆空间的可能性。您可能需要测试不同的值以找到适合的值。如果需要调整此值的帮助，请联系您的Palantir代表。

要减少分配给一个（或多个）子进程的内存量，请执行以下操作：

- 决定应为上述每个子进程分配多少内存。注意：我们不建议将堆大小减少到低于以下列出的默认值。
- 注意：我们不建议将堆大小减少到低于以下列出的默认值。
- 接下来，导航到Data Connection中的代理，选择高级配置按钮，并选择Bootstrapper选项卡。
- 在这里，您可以为每个单独的子进程设置jvmHeapSize参数。
- 以下是一个Bootstrapper 配置片段，其中agent的jvmHeapSize设置为3gb：Copied!123agent:
    ....
    jvmHeapSize: 3g #这是jvm堆大小值
```
Copied!1
2
3
agent:
    ....
    jvmHeapSize: 3g #这是jvm堆大小值
```

- 更新配置后，您需要保存更改并重新启动代理以使其生效。
默认堆分配

默认情况下，代理需要大约3gb的内存，分配如下：

- 1gb用于agent子进程
- 1gb用于Explorer子进程
- 512mb用于Bootstrapper子进程
- 512mb用于Agent Manager子进程
Java进程也使用一定量的堆外内存；因此，我们建议您确保至少有≥4gb的内存空闲。

#### 无法下载代理包

导致代理下载失败的两个主要原因是网络连接和过期链接。

如果您可以连接到Foundry但得到无效的tar.gz文件或下载时出现错误消息，您可能有一个过期或无效的链接。

- 过期链接：下载链接在十分钟后过期。
- 无效链接：下载链接通过一次性下载密钥保护。在Microsoft Teams等应用程序中粘贴代理下载链接可能会使链接无效，因为这些应用程序会尝试扫描链接以查看是否可以预览；此扫描会使一次性下载密钥失效。如果您有无效链接，请尝试在UI中重新生成链接并重新输入两个密钥单词而不是复制整个链接。
#### 无法管理代理

用户必须是项目的编辑者才能在该项目中创建代理，但必须是项目的所有者才能管理该项目中的代理。这意味着用户可以创建代理，但无法生成下载链接或对代理执行其他管理任务。有关代理权限的更多信息，请查看我们的权限参考文档。

### 代理配置参考

#### 使用不安全的TLSv1.0和TLSv1.1协议连接到数据源

TLSv.1.0和TLSv1.1不被Palantir支持，因为它们是过时且不安全的协议。Data Connection代理使用的Amazon Corretto构建的OpenJDK默认情况下通过java.security文件中的jdk.tls.disabledAlgorithms安全属性明确禁用TLSv1.0和TLSv1.1。

尝试连接到仅支持TLSv1.0和TLSv1.1的数据源系统将失败，并出现各种错误，包括Error: The server selected protocol version TLS10 is not accepted by client preferences。

我们强烈不建议使用已弃用的TLS版本。Palantir对与其使用相关的安全风险不承担责任。

如果有临时支持TLSv1.0和TLSv1.1的关键需求，请执行以下步骤：

- 从代理概览页面，导航到Agent settings并在Manage Configuration部分选择Advanced。然后，选择Bootstrapper选项卡。
- 在agent和explorer配置块中添加tlsProtocols条目，并后跟要启用的协议。确保还包括TLSv1.2，以免使用它的来源中断。例如：
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
agent:
    tlsProtocols:
      - TLSv1    # TLS版本1.0
      - TLSv1.1  # TLS版本1.1
      - TLSv1.2  # TLS版本1.2
...
explorer:
    tlsProtocols:
      - TLSv1    # TLS版本1.0
      - TLSv1.1  # TLS版本1.1
      - TLSv1.2  # TLS版本1.2
...
```

在此YAML配置中，tlsProtocols字段列出了支持的TLS协议版本。一般建议仅使用TLSv1.2及以上的版本，因为TLSv1和TLSv1.1被认为不再安全。

- 选择Restart agent。
通过此配置，代理将在代理升级和重启时继续支持TLSv1.0和TLSv1.1。一旦数据源迁移到新的TLS版本，请还原对高级代理配置所做的所有更改。

#### 配置代理日志

要调整代理在其主机上的日志存储设置，请按照以下步骤操作：

- 在Data Connection中，导航到Agents页面。选择要配置的代理名称。
- 在配置面板中，选择Advanced。
- 日志的配置选项可以在Logging块下找到。在这里，您可以配置何时开始丢弃日志的限制，是否以及如何存档日志，以及其他设置。请注意，配置应考虑分配的代理主机资源、您的日志级别粒度偏好，以及日志保留偏好。有关更多信息和指导，请参阅Dropwizard 配置参考 ↗。
- 请注意，配置应考虑分配的代理主机资源、您的日志级别粒度偏好，以及日志保留偏好。有关更多信息和指导，请参阅Dropwizard 配置参考 ↗。
- 在Foundry中通过选择屏幕右上角的Restart Agent重启代理。
您的新配置现在应已生效。

#### 当安装代理的主机崩溃时，缓存文件会发生什么？

这些文件将保留在磁盘上，直到Bootvisor清理旧的进程文件夹（30天或10个旧文件夹触发清理）。这些文件是加密的，解密它们的密钥仅存在于已终止的进程的内存中。
