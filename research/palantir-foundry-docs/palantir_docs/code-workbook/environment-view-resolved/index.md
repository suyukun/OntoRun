来源: https://palantir.com/docs/zh/foundry/code-workbook/environment-view-resolved/

# 查看已解析的环境

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 查看已解析的环境

获得Spark环境后，您可以在已解析依赖关系对话框中查看Spark环境中安装的确切软件包。要打开对话框，请选择环境 > 查看已解析的软件包。该对话框将显示直接和传递依赖关系的列表。

直接依赖是用户明确指定要包含在Spark环境中的软件包。您可以在自定义Spark环境菜单中指定直接依赖。

传递依赖是直接依赖所依赖的软件包。例如，依赖statsmodels会传递性地导入NumPy、SciPy、MatPlotLib及其依赖项。
