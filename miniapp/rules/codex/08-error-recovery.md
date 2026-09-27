# 08 Error Recovery

涉及弱网、离线、接口失败、登录过期、支付中断时：

1. 读 `shared/22-error-recovery-offline.md`。
2. 禁止每页复制 401 跳转；走 `auth` / 统一 recovery。
3. 列表/表单须有 error + 重试；弱网须 offline 提示。
