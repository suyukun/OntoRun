"""契约错误类型（fail-closed 拒答语义，设计 §3.3）。

ContractError：契约校验/执行失败统一基类；PermissionDeniedError：读侧权限拒绝
（code=PERMISSION_DENIED，供上层映射错误码/拒答语义）。与 v0.1 单文件实现行为一致。
"""

PERMISSION_DENIED = "PERMISSION_DENIED"  # 读侧权限拒绝错误码（设计 §3.3，fail-closed 拒答）


class ContractError(Exception):
    """契约校验/执行失败（fail-closed 拒答，不降级为裸执行）。"""

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        # 未显式传 code 时回落到子类类属性（PermissionDeniedError.code=PERMISSION_DENIED）
        self.code = code if code is not None else getattr(type(self), "code", None)


class PermissionDeniedError(ContractError):
    """读侧权限拒绝（设计 §3.3：fail-closed 拒答，不静默裁剪防推断泄漏）。

    与 ContractError 同族（既有 pytest.raises(ContractError) 兼容不破坏）；
    附加 code=PERMISSION_DENIED 供上层映射错误码/拒答语义。
    """

    code = PERMISSION_DENIED
