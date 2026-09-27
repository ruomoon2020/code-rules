# 前端 Pull Request 模板

## 变更

- [ ] 页面 / 组件 / 契约 / 平台边界改动范围：
- [ ] 是否涉及菜单、路由、权限、字典、导入导出或异步任务：
- [ ] 需求 / Issue、逐条验收条件及测试证据已填写（`common-governance/docs/requirements-traceability.md`）

## 契约与安全

- [ ] 字段来自 schema / generated；未手改 generated
- [ ] 后端鉴权与前端权限展示一致
- [ ] 无密钥、生产地址、未脱敏敏感信息

## 验证

- [ ] `pnpm lint`
- [ ] `pnpm type-check`
- [ ] `pnpm test`
- [ ] `pnpm build`
- [ ] `pnpm api:check`（若适用）
- [ ] Rules eval（Smoke / Business Extension / Platform Extension / Full）：
- [ ] 业务工作流、数据、权限、API / UI 一致性和回归风险已人工复核

## 风险与回滚

- 主要风险、灰度 / Feature Flag：
- 回滚步骤与 Owner：

## 企业 DoD（monorepo）

- [ ] Required CI 全绿：lint / type-check / test / build（`docs/definition-of-done.md`）
- [ ] 改依赖 / 锁文件：已跑供应链门禁（`docs/supply-chain-baseline.md`）
- [ ] 新 PII / 日志字段：已对照 `docs/data-classification-matrix.md`
- [ ] 跳过门禁或超性能预算：豁免单（`docs/rule-exception-process.md`）
- [ ] CODEOWNERS Reviewer 已指派（`docs/codeowners-matrix.md`）
