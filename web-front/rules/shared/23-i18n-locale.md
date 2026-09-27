# 国际化与区域格式规则

用户可见文案、金额、日期、时区须可维护、可测试、可审计。禁止在 `views` 硬编码稳定业务语义。

## 1. 文案 SSOT

| 来源 | 用途 |
|---|---|
| 项目 i18n 资源（如 `locales/zh-CN.json`） | 固定 UI 文案、按钮、提示 |
| 后端字典 / 枚举服务 | 业务状态、类型、可配置标签 |
| `errorCode` → i18n 映射 | 接口错误用户文案 |

**禁止**：在页面写死中文业务句、枚举展示名、金额单位拼接（除非项目明确仅单语言且已 ADR）。

新增 key 须命名空间清晰（如 `crm.customer.status.pending`）；与 `02-naming.md` 一致。

## 2. Vue / 管理端约定

- 使用项目既定方案（如 `vue-i18n`）；`t()` / `$t()` 包裹用户可见字符串。
- 路由 `title`、面包屑、表格列头、空态、校验 message 均须 i18n。
- `keep-alive` 页面切换语言后须刷新依赖 locale 的列定义与格式化列。
- 富文本 / 模板内用户内容：**不**走 i18n 文件，走内容安全与 sanitizer（见 `24-realtime-rich-content.md`）。

## 3. 金额、数量、日期、时区

| 类型 | 传输（API） | 展示（前端） |
|---|---|---|
| 金额 | 整数分 / 字符串 decimal（与后端一致） | `Intl.NumberFormat` 或项目 `formatMoney` |
| 日期时间 | ISO-8601 + 明确时区或 UTC | `Intl.DateTimeFormat`；带时区缩写或说明 |
| 数量 | number | 千分位 formatter |
| 百分比 | 0–1 或 0–100（OpenAPI 注明） | 统一 formatter，禁止手写 `%` |

**禁止**：用 `new Date()` 本地解析无时区字符串作为账期截止；跨日筛选须与后端约定闭开区间（见 `fullstack-contract`）。

## 4. errorCode 与 fallback

1. 未知 `errorCode`：展示通用错误文案 + `traceId`（可折叠），禁止裸抛后端 message。
2. 未知 locale：回退默认语言（如 `zh-CN`），记录监控事件。
3. 缺翻译 key：开发环境 warn；生产 fallback 到 key 末段或默认文案，**禁止白屏**。

## 5. 语言切换

- 切换语言：**不**清登录态；**不**丢未提交表单（须提示或暂存策略）。
- 须失效：字典缓存、格式化 memo、页面 `document.title`、依赖 locale 的 Pinia 切片。
- 持久化用户语言偏好：走用户设置 API 或受控 storage；禁止未授权写 cookie。

## 6. RTL 与无障碍（若启用）

- 启用 RTL 时检查表格、表单、图标方向；禁止仅 `margin-left` 硬编码。
- 关键操作须满足项目 a11y 基线（见 `07-security-performance`、eval E31）。

## 7. 与后端 / 小程序对齐

| 字段 | 要求 |
|---|---|
| `errorCode` | 三端映射表一致；禁止前端自造码 |
| 枚举值 | API 值稳定；展示名由字典或 i18n |
| 时区 | 列表筛选、报表周期与后端同一时区口径 |
| 小程序 | 微信端语言包 + 必要时同步后端字典；见 `miniapp` 分包内文案同样禁止硬编码 |

## 8. 验证清单

- [ ] 无新增硬编码用户可见业务文案
- [ ] 金额 / 日期 / 时区走 formatter
- [ ] 未知 errorCode / locale 有 fallback
- [ ] 语言切换不丢表单、不重复登录
- [ ] 改 i18n PR 建议跑 eval **E41**（Platform Extension）

关联：`12-schema-ssot.md`、`13-form-and-detail.md`、`21-error-recovery.md`、`docs/fullstack-contract.md`（跨端 errorCode）。
