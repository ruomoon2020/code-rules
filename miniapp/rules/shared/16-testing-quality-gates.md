# 16 Testing Quality Gates

## 必跑检查

按项目实际脚本运行；不存在时如实说明。

```bash
pnpm lint
pnpm type-check
pnpm test
pnpm build:mp-weixin
pnpm api:check
pnpm size:check
pnpm audit
```

## 测试分层（金字塔）

| 层级 | 范围 | 工具建议 |
|---|---|---|
| 单测 | `assertAllowedUrl`、金额工具、scene 解析、composables | Vitest |
| 集成 | request 封装、auth logout 清理、错误 recovery | Vitest + mock uni |
| E2E | 登录 → 列表 → 下单沙箱（支付 mock） | miniprogram-automator / 云测 |
| 契约 | OpenAPI vs generated | `api:check` |

## 组件测试规范

1. Base 组件覆盖默认渲染、关键 props、emits payload、slots、`v-model`、禁用/加载/错误状态和主要交互。
2. Vue Test Utils 按用户可见行为断言，优先通过文本、可访问名称或稳定 `data-testid` 查询。
3. uni API、时间、网络和随机数可注入或 mock；每个用例后恢复 timer、mock、EventBus 和全局监听。
4. Provide/Inject 覆盖有 provider 与缺少 provider 的路径；Pinia 组件使用独立 testing store。
5. 生命周期测试覆盖监听注册/注销、异步竞态、卸载后不更新和 KeepAlive 激活/停用（若使用）。
6. 快照只用于稳定、低变化结构或主题变量输出，并配合行为断言；快照变化必须人工审阅。
7. 组件 bug 先补复现测试；新增 Base 组件需要测试，例外记录 Owner 和到期时间。

推荐 Vitest + Vue Test Utils；小程序环境使用项目统一的 uni API mock 或 adapter 替身。E2E 工具由项目覆盖层按目标平台选择。

### 快照测试

快照仅作为行为测试的补充；保持结构小而稳定，变更必须人工审阅，不为通过 CI 盲目更新。

## 覆盖与稳定性

1. 覆盖率阈值由项目覆盖层定义，同时关注 statements / branches / functions / lines；覆盖率不能替代有效断言。
2. 核心 Base 组件、登录、权限、提交与支付链路的分支覆盖不低于项目全局阈值。
3. flaky test 应固定时钟、网络、数据和平台版本后修复，不以增加重试掩盖。
4. E2E 至少覆盖主成功、拒绝/失败和弱网恢复链路；交易使用沙箱或后端 mock。
5. 临时隔离用例须记录原因、Owner、到期日和补跑计划；首次失败与重试结果都要保留。
6. CI 失败须保留测试报告、原始输出和 run/test id；有请求上下文时同时保留 traceId。端到端测试按平台能力保留截图、视频、console 或网络记录。
7. 并行用例隔离账号、租户、storage、业务数据和平台会话；清理动作可重复执行，不能只依赖事务回滚。
8. 测试数据优先使用 synthetic fixture；禁止直接使用未脱敏生产 PII。确需生产样本时须审批、最小化并设置到期清理。

## 并发、契约与兼容

1. 提交、支付、上传和订阅覆盖重复点击、请求重试、取消/超时、回调重放、旧响应覆盖新响应和多次进入页面。
2. API / generated 变更验证字段可空性、枚举新增、默认值、错误码和旧服务端响应；滚动发布按项目窗口验证 N/N-1。
3. 支付与消息回调以后端最终状态为准；测试须断言幂等后的业务状态，不能只断言客户端回调成功。
4. 属性测试、模糊测试和变异测试仅对 scene 解析、金额、导入、权限等高风险模块按需启用，不作为所有页面统一门禁。

## 测试重点

1. 登录态：未登录、过期、刷新失败、退出登录。
2. 授权：拒绝、再次授权、平台不可用。
3. 分页：刷新、加载更多、筛选变化、删除末条。
4. 支付：成功、取消、失败、处理中、重复点击。
5. 分享：参数校验、分享打开、非法 scene。
6. 分包：页面可进入、公共依赖不越界、主包体积不超预算。
7. 隐私：实际调用能力和隐私说明一致。
8. 弱网/错误恢复：offline 提示、重试、登录过期统一跳转（`22`）。
9. 富文本/UGC：消毒或拒绝不可信 HTML（`23`）。
10. 兼容升级：旧服务端、新客户端、平台基础库差异和灰度开关安全默认值。

## CI 门禁

1. lint / type-check / build 必须在 PR 运行。
2. API 契约变化必须跑 generated 与 api check。
3. 主包体积超过阈值必须失败或要求人工审批。
4. 生产构建不得包含 mock、console、调试入口。
5. 建议 `pnpm audit` 无高危漏洞或经审批例外（`25`）。
6. AI / 工具输出须核对不可信内容、最小权限、外部写入授权、敏感数据出站和真实执行证据（`17`）。
7. 修改 Base 组件时运行组件测试；修改主题基础值时运行主题/关键组件测试和目标平台视觉验证。
8. CI 分离快速门禁与构建/E2E；必需 job 返回确定状态，不允许失败后仍视为通过。
9. Required 测试重跑通过时不得丢弃首次失败；若判定 flaky，必须进入有期限的治理清单。
