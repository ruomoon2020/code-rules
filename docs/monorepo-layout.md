# 全栈 Monorepo 推荐布局

```text
product/
├─ common-governance/          # 可分发治理包；业务仓 CI 验证版本与清单
├─ contracts/
│  ├─ openapi.yaml              # SSOT：后端 + 管理端 + 小程序共用
│  └─ openapi.baseline.yaml     # CI diff 基线（契约变更后由 Owner 更新）
├─ web-front/
│  ├─ src/                      # Vue 管理端工程
│  └─ rules/                    # 前端规则包
├─ web-backend/
│  ├─ src/main/java/            # Spring Boot 工程
│  └─ rules/                    # 后端规则包
├─ miniapp/
│  ├─ src/                      # uni-app 小程序工程
│  └─ rules/                    # 小程序规则包（miniapp/rules）
├─ docs/                         # 治理维护 SSOT，生成 common-governance/docs
├─ AGENTS.md                    # 可选：索引各端；或各子工程独立 AGENTS
└─ README.md
```

## 契约流

```text
contracts/openapi.yaml
  ├─► 后端：实现 + springdoc 校验 + MockMvc 测试
  ├─► 管理端：openapi-generator / schema.json → src/api/generated
  └─► 小程序：api:gen → src/api/generated + api:check
```

## 规则包路径

| 端 | 规则目录 | Codex 入口 |
|---|---|---|
| 管理端 | `web-front/rules/` | 复制 `codex/AGENTS.md` 到工程根 |
| 后端 | `web-backend/rules/` | 同上 |
| 小程序 | `miniapp/rules/` | 同上 |

Cursor：各工程 `.cursor/rules/*.mdc` 来自对应 `rules/cursor/`。

## 联调字段

见 `web-backend/rules/docs/fullstack-contract.md` 与 `web-front/rules/shared/18-logging-observability.md`。

## 规则包版本

本源仓使用统一四段版本号；仓库根 `VERSION`、前端、后端、小程序和 `common-governance` 的 `VERSION` 必须一致。业务仓单独采用规则包时，以复制或发布时记录的包内 `VERSION` 为准。

## 规则包 CI（本 monorepo）

改规则包、治理文档或脚本时，GitHub Actions（`.github/workflows/validate-rules-packages.yml`）至少覆盖：

```bash
python web-backend/rules/scripts/validate-rules-package.py
python web-front/rules/scripts/validate-rules-package.py
python miniapp/rules/scripts/validate-rules-package.py
python scripts/sync-common-governance.py
python common-governance/scripts/validate-package.py
python -m unittest discover -s scripts/tests -v
```

另含：rules-only fixture（`--strict`）与治理 fixture（复制 `common-governance/` 后 `--level 2`）。

企业级治理维护 SSOT 位于仓库根 [`definition-of-done.md`](definition-of-done.md)；业务仓应引入由它生成的 `common-governance/`，企业项目推荐：

```bash
python common-governance/scripts/validate-package.py
python common-governance/scripts/check-project-adoption.py --repo . --stack frontend --level 2
```

`--level 2` 已隐含完整治理包校验；仅当 Level < 2 仍要强制校验治理包时，再显式加 `--require-governance`。

成熟后台全栈新增业务：后端 `shared/43` + `docs/business-feature-playbook.md`；管理端 `shared/22` + `docs/business-feature-playbook-frontend.md`；小程序 `shared/18` + `docs/business-feature-playbook-miniapp.md`；evals **B55–B63** / **E32–E40** / **M21–M29**（均建议 9/9）。管理端 i18n/实时/富文本另跑 E41–E43；受监管 Web 另跑 E44–E49；联调见 `web-backend/rules/docs/fullstack-contract.md`。

## 脚手架

- 后端 Java 样板：`web-backend/rules/examples/scaffold/`
- 前端工程样板：`web-front/rules/examples/scaffold/`
- 后端配置/SQL：`web-backend/rules/examples/config/`、`examples/db/`
- 备份恢复 Runbook：`web-backend/rules/docs/backup-restore-runbook.md`
