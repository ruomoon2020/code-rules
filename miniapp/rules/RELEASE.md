# 规则包发布前 Checklist

维护者发版 `miniapp/rules/` 时按序执行。

> 维护者完整清单见 `docs/contributing-rules-package.md`。

## 必做

- [ ] 更新 `VERSION`
- [ ] 更新 `CHANGELOG.md`（含破坏性变更说明）
- [ ] 核对 `README.md`「完整文件清单」与磁盘文件一致
- [ ] 核对 `codex/AGENTS.md` 任务表与 `shared/` 文件存在性一致
- [ ] 核对 `cursor/*.mdc` 中的 `rules/shared/...` 引用均存在，且 frontmatter `globs` 能覆盖目标场景
- [ ] 核对 `evals` 用例数与门槛（**计数 SSOT**：`prompts.md` + `rubric.md` + `results-template.md`；`smoke-prompts.md` **只校验 M 编号覆盖**）
- [ ] 运行 `python scripts/validate-rules-package.py` 通过
- [ ] 核对 `docs/rules-package-index.md` 与 `shared/00–26` 一致
- [ ] 核对 `examples/README.md` 与脚手架/脚本样板一致
- [ ] 若改核心 P1 / 套件：同步 `evals/smoke-prompts.md` 与 `evals/README.md`
- [ ] 改 eval 主题后：运行 monorepo `python scripts/generate-eval-topic-manifest.py --rules-dir miniapp/rules` 并提交 `evals/topic-manifest.yaml`
- [ ] 若改 AI / 工具安全：确认 M13 语义未漂移，并跑 `evals/ai-tool-safety.md` MAT01–MAT05 **5/5**
- [ ] 确认 `tsc` 可用；校验器已执行 `examples/scaffold/` TypeScript 语法 smoke
- [ ] 测试规则变更已核对确定性、flaky 治理、失败证据、回调重放与兼容窗口，并运行 Testing Governance M49/M52 **2/2**

## 大版本 / 改 Hard Rules 时追加

- [ ] 在测试业务仓跑 `evals/prompts.md` **M01–M52**，P0 **8/8**、核心 P1 **至少 10/12**；按需加 Business / Security / Resilience / Enterprise Hardening / Component Engineering / Testing Governance Extension 套件（见 `evals/README.md`）
- [ ] 通知业务仓同步 `rules/` 或升级 submodule 版本

## 不要做

- [ ] 不要在业务仓 CI 的包体积检查上使用「仅 warning、永不 fail」且无 Owner 审批
