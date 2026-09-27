# 规则包发布前 Checklist

维护者发版 `rules/` 时按序执行。

> 维护者完整清单见 `docs/contributing-rules-package.md`。

## 必做

- [ ] 更新 `VERSION`
- [ ] 更新 `CHANGELOG.md`（含破坏性变更说明）
- [ ] 运行 `node rules/examples/run-ci-scan-fixtures.mjs`（全部通过）
- [ ] 核对 `README.md`「完整文件清单」与磁盘文件一致
- [ ] 确认 Node 与 TypeScript 可用；校验器已执行 `examples/scaffold/` 语法、strict 编译和 bundle 正反 smoke
- [ ] 核对 `codex/AGENTS.md` 任务表与 `shared/` 文件存在性一致
- [ ] 核对 `cursor/*.mdc` 中的 `rules/shared/...` 引用均存在，且 frontmatter `globs` 能覆盖目标场景
- [ ] 核对 `evals` 用例数与门槛（**计数 SSOT**：`prompts.md` + `rubric.md` + `results-template.md`；`smoke-prompts.md` **只校验 E 编号覆盖**）
- [ ] 运行 `python scripts/validate-rules-package.py` 通过
- [ ] 若改核心 P1 / 套件：同步 `evals/smoke-prompts.md` 与 `evals/README.md`（含 Platform E41–E43、Enterprise Hardening E44–E49、Testing Governance E31/E50）
- [ ] 改 eval 主题后：运行 monorepo `python scripts/generate-eval-topic-manifest.py --rules-dir web-front/rules` 并提交 `evals/topic-manifest.yaml`
- [ ] 若改 AI / 工具安全：确认 E13 语义未漂移，并跑 `evals/ai-tool-safety.md` EAT01–EAT05 **5/5**
- [ ] 测试规则变更已核对确定性、flaky 治理、失败证据、竞态恢复与兼容窗口，并运行 Testing Governance E31/E50 **2/2**

## 大版本 / 改 ci-scan 或 Hard Rules 时追加

- [ ] 在测试业务仓跑 `evals/prompts.md` **E01–E50**，P0 **8/8**、P1 **至少 39/42**；成熟后台业务 PR 加 Business E32–E40；i18n/实时/富文本加 Platform E41–E43；受监管 Web 加 Enterprise Hardening E44–E49；测试治理变更加 E31/E50
- [ ] 通知业务仓同步 `rules/` 或升级 submodule 版本

## 不要做

- [ ] 不要在业务仓 CI 的 `lint:views-el` 上使用 `--allow-empty`
