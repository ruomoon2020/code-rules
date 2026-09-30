# 发布检查清单（模板）

> 与 `22-operability.md`、`32-service-reliability.md`、`31-production-data-ops.md` 配合。复制到业务仓或纳入变更工单。

## 发布前

- [ ] 固定版本 `oasdiff breaking --fail-on WARN` 已相对上一已发布 baseline / PR base Review；baseline 仅在变更获批并合并后由 Owner 更新，禁止在 PR 中提前覆盖以隐藏差异
- [ ] OpenAPI 已声明 `x-api-style`、认证、主要错误响应、正确的 `201/202/204`，且 Controller / DTO 与所选 GET/POST 或资源型风格对齐
- [ ] Flyway 已在目标库 validate；破坏性变更走 expand → migrate → contract
- [ ] Feature Flag / 灰度 / 实验配置通过 `common-governance/docs/environment-promotion.md` 的统一生命周期清单
- [ ] 核心链路监控看板与告警已确认（SLO、5xx、慢 SQL、外部依赖）
- [ ] 失败请求可用响应 traceId 找到诊断主事件；401/403/404/429 不误记为 5xx
- [ ] 测试失败可凭报告和 run/test id 定位；flaky 有期限，禁止重试洗绿
- [ ] 若改写链路、契约或迁移：并发幂等与 N/N-1 兼容用例已运行
- [ ] 回滚版本可读新 schema / 新字段（旧实例兼容）
- [ ] 高风险变更已威胁建模（`35-threat-modeling`）
- [ ] 使用 AI 工具且属发版 / 高风险 AI 变更时，AI Tool Safety 结果为 5/5，并绑定套件摘要、模型版本和评测人
- [ ] Level 2+ 平台控制快照不超过 90 天，组织权限、主干保护与生产非自审通过校验

## 发布中

- [ ] 灰度 / 金丝雀（若采用）比例与观察窗口已定义
- [ ] 发布关联 Git tag / 镜像 digest / SPDX SBOM / provenance 或 attestation
- [ ] 发布证据已通过真实产物摘要绑定校验，信任材料引用与验证命令可追溯

## 发布后

- [ ] 冒烟：登录、核心列表、核心写接口
- [ ] 错误率、延迟、业务指标在阈值内
- [ ] 无未关闭 P0 告警
- [ ] 需通知前端 / 调用方的契约变更已同步

## 回滚触发（任一满足考虑回滚）

- 核心接口错误率超 SLO 预算
- DB 迁移导致旧版本不可读
- 安全事件或数据错误
