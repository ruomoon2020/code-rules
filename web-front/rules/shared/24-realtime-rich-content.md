# 实时通信与富文本规则

## WebSocket / SSE

1. 鉴权优先走项目 request / 握手机制；禁止把长期 Token、密码或敏感参数放在 URL query。
2. 连接按页面或业务域管理，组件卸载必须取消订阅并关闭不再使用的连接；重连需指数退避、上限和网络恢复策略。
3. 消息必须有稳定事件类型、版本或 schema、资源 ID、顺序 / 去重策略；权限变化、401 / 403 和未知事件须安全降级。
4. 实时消息只能触发受控状态更新；不得直接把服务端 HTML、脚本或未校验字段插入 DOM。

## 富文本与编辑器

1. 富文本输入和展示使用项目认可的 sanitizer / renderer；禁止裸 `v-html`，禁止信任编辑器“已过滤”的默认承诺。
2. 编辑器、预览器、Markdown / Office / PDF 等重依赖按需加载；上传文件走鉴权、类型/大小校验和审计流程。
3. 保存内容使用稳定格式与版本；渲染失败、未知节点或资源加载失败须显示安全 fallback，不得白屏。

全文关联：`shared/05-api-contract.md`、`shared/07-security-performance.md`、`shared/18-logging-observability.md`。
