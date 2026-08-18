来源: https://palantir.com/docs/zh/foundry/code-workspaces/security/

# 安全性

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 安全性

Code Workspaces 确保 Foundry 的安全性和权限模型应用于连接到 Foundry 的第三方 IDE。这一安全层覆盖于由 Code Workspaces 提供服务的第三方应用程序之上，提供了许多好处：

- 在 Code Workspaces 中加载的数据由 Foundry 跟踪。除了由 Foundry 的数据治理和访问控制管理的方法外，在 Code Workspaces 中的数据下载和上传受到限制。
- 每个对 Code Workspaces 的请求都会根据 Foundry 的治理框架进行验证。这意味着如果用户对 Code Workspace 的访问被撤销，或者对工作空间中导入数据的任何权限标记的访问被撤销，该用户将立即失去对应用程序的访问权限。
- 从 Code Workspaces 产生的数据由 Foundry 跟踪，因此如果用户失去对可能用于生成输出数据的数据的访问权限，访问输出数据将受到限制。
- 用户完全隔离。每个打开特定 Jupyter® 或 RStudio® Code Workspace 的用户将获得自己的隔离环境。
- R 和 Python 包只能从支持存储库的 Foundry Artifacts 渠道加载，这使得能够控制在特定 Code Workspace 中可以使用的 Conda、PyPI 或 CRAN 包。
- 外部 API 调用只能对已添加到 Code Workspace 中的网络策略配置的 URL 进行。
RStudio® 和 Shiny® 是 Posit™ 的商标。

Jupyter®、JupyterLab® 和 Jupyter® 徽标是 NumFOCUS 的商标或注册商标。

所有提及的第三方商标（包括徽标和图标）仍为其各自所有者的财产。不暗示任何隶属或认可关系。
