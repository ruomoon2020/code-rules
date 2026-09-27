<!-- 复制到业务仓 .github/pull_request_template.md；细则见 rules/docs/pull-request-template.md。 -->

## 变更与契约

- [ ] schema / generated 已同步，未手改 generated
- [ ] 菜单、路由、按钮权限与后端一致（若适用）

## 验证

- [ ] lint / type-check / test / build
- [ ] api:check（若适用）
- [ ] Smoke / Business Extension / Platform Extension / Full eval（按场景）

## 企业 DoD（monorepo）

- [ ] Required CI 全绿（`docs/definition-of-done.md`）
- [ ] 改 `package.json` / lockfile：供应链 audit（`docs/supply-chain-baseline.md`）
- [ ] 新 PII / 埋点字段：`docs/data-classification-matrix.md`
- [ ] 跳过门禁：豁免单 `docs/rule-exception-process.md`
- [ ] CODEOWNERS：`docs/codeowners-matrix.md`
