# SLO 与告警模板（管理端 + 小程序）

> 后端 SLO 见 `web-backend/rules/shared/32-service-reliability.md`。本文补齐**管理端**与**小程序**可执行模板；数值写入业务仓 `PERFORMANCE_BUDGET.md` 或 `99-project-local.mdc`。

## 管理端

### 指标与建议阈值

| 指标 | 说明 | 建议阈值（P75 / 率） | 告警 Owner |
|---|---|---|---|
| **LCP** | 最大内容绘制 | ≤ 2.5s | 前端 Owner |
| **INP** | 交互延迟 | ≤ 200ms | 前端 Owner |
| **CLS** | 布局偏移 | ≤ 0.1 | 前端 Owner |
| **首屏 API** | 关键列表首请求 | ≤ 800ms（与后端对齐） | 前端 + 后端 |
| **JS error rate** | 未捕获错误 / PV | < 0.5% | 前端 Oncall |
| **API error rate** | 5xx + 业务失败 / 请求 | < 1%（排除取消） | 前端 + 后端 |
| **白屏率** | 首屏超时 / chunk 失败 | < 0.1% | 前端 Oncall |
| **资源加载失败** | 静态资源 4xx/5xx | < 0.2% | 前端 + DevOps |

细则：`web-front/rules/shared/07-security-performance.md`、`08-quality-gates.md`。

### 告警分级

| 级别 | 条件示例 | 响应 |
|---|---|---|
| P1 | 白屏率 > 1% 持续 5min | 15min 内响应；考虑回滚 |
| P2 | LCP P75 超预算 20% 持续 1h | 当日排查；排期优化 |
| P3 | 单路由 JS 错误突增 | 下工作日修复 |

### 发版后 24h 观察

- [ ] LCP / INP / CLS 无劣化 >10%
- [ ] JS / API 错误率无翻倍
- [ ] 新路由 chunk 加载失败有上报

---

## 小程序

### 指标与建议阈值

| 指标 | 说明 | 建议阈值 | 告警 Owner |
|---|---|---|---|
| **cold_start_ms** | 冷启动 | P95 < 2500ms | 小程序 Owner |
| **first_interactive_ms** | 首屏可交互 | P95 < 1800ms | 小程序 Owner |
| **first_api_ms** | 首屏关键 API | P95 < 800ms | 小程序 + 后端 |
| **white_screen** | 白屏 | 率 < 0.1% | 小程序 Oncall |
| **subpackage_load_fail** | 分包失败 | 率 < 0.1% | 小程序 Owner |
| **app_error** | onError / 未处理 Promise | 按会话 < 0.5% | 小程序 Oncall |
| **request_fail** | 按 errorCode 聚合 | 核心 API < 0.5% | 小程序 + 后端 |
| **main_package_size_kb** | 主包体积 | 项目预算内 | 小程序 Owner |

细则：`miniapp/rules/docs/observability-metrics.md`、`shared/15-logging-observability.md`。

### 字段规范（两端通用）

每条上报须含：`traceId`、`route`/`page`、`release`/`appVersion`；**禁止** Token、完整 PII。

---

## 与后端 SLO 对齐

| 维度 | 对齐方式 |
|---|---|
| traceId | 全链路同一 ID |
| errorCode | 前端映射用户文案；不吞后端码 |
| 可用性 | 后端 SLO 降级时前端须有错误态 + 降级文案 |
| 发布 | 前后端 + 小程序版本号写入监控维度 |

## 模板文件

| 端 | 复制到业务仓 |
|---|---|
| 管理端 | `web-front/rules/docs/PERFORMANCE_BUDGET.template.md` |
| 后端 | `web-backend/rules/docs/PERFORMANCE_BUDGET.template.md` |
| 小程序 | `miniapp/rules/examples/99-project-local.mdc.sample` 指标段 |

## 相关

- [`definition-of-done.md`](definition-of-done.md) §可观测门禁
- [`rule-exception-process.md`](rule-exception-process.md)（超预算豁免）
