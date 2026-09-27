# 业务仓规则落地 Checklist

复制到小程序业务仓 `docs/` 或 PR 描述中勾选。

## 必做

- [ ] `rules/` 整包（或 submodule）+ 根 `AGENTS.md` + `.cursor/rules/*.mdc`
- [ ] `99-project-local.mdc` 已填写：分包路径、主包预算、目标平台、契约路径
- [ ] OpenAPI / schema SSOT：`contracts/openapi.yaml`（或等价）+ `api:gen` / `api:check`
- [ ] 页面不走 `uni.request` / `uni.login` 直调；走 `api/`、`auth/`、`platform/`
- [ ] 新业务页默认 `src/subpackages/**`
- [ ] CI：`lint`、`type-check`、`build:mp-weixin`、`api:check`、`size:check`（以 `package.json` 为准）

## 推荐

- [ ] 跑 Smoke evals（M01–M08 + 核心 P1 ≥10/12）
- [ ] AI 读取外部内容或调用工具时，`evals/ai-tool-safety.md` MAT01–MAT05 **5/5**
- [ ] 隐私 / 支付 / 分享 / 上传媒体 PR 跑 Security + Contract 套件（Contract 含 M51）
- [ ] 测试稳定性、支付/回调重放或 API 兼容变更跑 Testing Governance M49/M52（建议 2/2）
- [ ] 新业务分包 PR 跑 Business Extension M21–M29
- [ ] UGC / 富文本 / 弱网恢复 PR 跑 Resilience Extension M35–M38（建议 4/4）
- [ ] 安全加固 / 无障碍 / 多平台 / 实验 PR 跑 Enterprise Hardening Extension M39–M44（建议 6/6）
- [ ] 组件 / 样式 / 生命周期 / 测试 / 性能 PR 跑 Component Engineering Extension M45–M50（建议 6/6）
- [ ] 管理端 evals **E41–E43** 不适用小程序（见 `docs/fullstack-contract.md` §与管理端 Platform Extension 的边界）
- [ ] 与后端 `web-backend/rules/docs/fullstack-contract.md` §小程序 对齐 traceId / errorCode / 分页
- [ ] 已复制 `examples/.github/pull_request_template.md`；可选 `examples/ci/rules-package-validate.yml`
- [ ] 声明采纳 Level（`docs/rule-maturity-model.md`）写入 `99-project-local.mdc`
- [ ] 已配置 `pnpm audit`（`25`）；错误恢复与 UGC 按 `22`/`23` 落地；安全加固按 `26` 落地

## 企业治理（monorepo）

- [ ] 已阅读 `docs/enterprise-governance.md`；SLO 见 monorepo `docs/slo-alerting-template.md`
- [ ] 已运行 `scripts/check-project-adoption.py --stack miniapp`
