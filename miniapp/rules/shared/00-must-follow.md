# 00 Must Follow

以下 15 条是小程序项目的 Level 0 不变量。支付、分包、UGC 等能力的细则在命中场景时按下文路由执行，不因规则包包含该文件就要求项目实现这些能力。

## 架构与契约

1. 页面通过项目统一 request 封装访问 API，不直接调用 `uni.request`。
2. 页面通过 `src/platform/`、`src/auth/` 或 `src/privacy/` 等边界调用平台能力，不散落平台 API 与条件编译。
3. 页面负责 UI 状态与事件编排，复杂业务流程放在 service 或 composable。
4. API 字段以项目声明的 OpenAPI、schema 或 generated 类型为准，不虚构后端字段。
5. generated 代码由契约重新生成，不直接手改。
6. 不使用显式 `any` 掩盖未知数据；使用 `unknown` 并在边界收窄。
7. 新依赖说明用途、平台兼容性、体积影响和替代方案。

## 安全与体验

8. 凭据与敏感个人信息按项目安全策略保护，不以明文持久化或写入日志。
9. 用户可见错误提供可理解提示，技术细节进入受控日志。
10. 用户输入或外部内容经校验后进入路由、网络请求或渲染；不直接渲染不可信 HTML。
11. 客户端展示和本地状态不能替代服务端鉴权、业务状态校验。
12. 生产构建不包含 mock、调试入口、测试账号、硬编码密钥或公开的 source map。
13. 已注册的 timer、监听器和长连接在对应生命周期清理，异步写操作防重复提交。
14. 已使用的隐私能力、埋点字段与项目隐私声明一致。
15. 完成前运行项目已配置的 lint、type-check、test、构建及契约检查；未配置或未运行的检查如实说明。

## 条件触发路由

以下规则命中场景后即为强制要求。Codex 按 `codex/AGENTS.md`、Cursor 按 `cursor/` 的触发规则读取对应 shared 全文。

- 登录态、授权、手机号、位置、相机、相册等能力：`06-login-auth-session.md`、`09-privacy-permission.md`；处理拒绝、过期、解绑和重新授权。
- 页面、列表、表单、图片与生命周期：`04-page-ui-lifecycle.md`、`12-list-form-pagination.md`、`10-performance-package-size.md`；覆盖加载、空、错误、刷新与请求竞态。
- 新页面、分包及包体积：`07-pages-routing-subpackages.md`、`10-performance-package-size.md`；按项目预算决定主包与分包，不把低频大资源放进主包。
- 支付、退款、余额、优惠券、订阅消息或分享：`14-payment-subscribe-share.md`；支付最终状态以后端订单为准，金额计算不用浮点数，分享参数不携带敏感信息。
- 网络、web-view、上传下载与媒体：`21-network-security.md`、`13-upload-download-media.md`；使用项目域名白名单并校验外部目标。
- 体验版、审核版、灰度与生产发布：`19-release-ops.md`、`26-security-hardening-risk.md`；隔离环境，核对远程开关和发布资源。
- 弱网、离线、登录过期及错误恢复：`22-error-recovery-offline.md`；采用统一恢复入口。
- 富文本、UGC 与外部展示内容：`23-content-safety.md`；消毒或白名单渲染。
- App 级异常、关键业务漏斗与日志：`15-logging-observability.md`、`20-app-runtime.md`；按实际链路设置指标与兜底。
- 第三方 SDK、高风险操作、远程配置与多平台矩阵：`25-dependency-supply-chain.md`、`26-security-hardening-risk.md`；记录数据流、Owner、回滚与风控边界。
