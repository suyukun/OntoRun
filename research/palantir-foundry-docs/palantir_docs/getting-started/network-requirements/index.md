来源: https://palantir.com/docs/zh/foundry/getting-started/network-requirements/

# 客户端端点网络要求

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 客户端端点网络要求

由于主要的Foundry前端是一个Web应用程序，建议用户使用支持的浏览器以获得最佳操作效果。然而，在少数情况下，即使使用支持的浏览器，网络设置异常的用户可能会遇到问题。为了帮助调试，本页面记录了Foundry对客户端端点网络设置的一些假设。

## WebSocket支持

许多平台内的应用程序使用WebSockets ↗进行客户端与服务器之间的通信，并且Foundry假设WebSocket连接是可能的。某些代理服务器需要特殊配置或软件升级以支持WebSocket连接。如果用户通过不支持WebSockets的代理连接到Foundry，平台的大部分功能可能会变得不可用。

## HTTP/2支持

HTTP/2支持对Foundry平台的无缝性能至关重要，因为它有助于处理从Foundry应用程序到后端的大量并发请求。请注意，代理服务器可能会将HTTP/2连接降级为HTTP/1.1，这可能使Foundry应用程序变得缓慢，以至于妨碍使用。如果您在使用Foundry时遇到缓慢问题，并且您的连接通过代理连接到Foundry，您应该调查代理是否在降级连接的可能性。
