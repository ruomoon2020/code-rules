# 前端接入测试夹具

本目录是 `scripts/check-project-adoption.py` 与仓库 CI 的最小化测试输入，用于验证前端规则入口、本地覆盖层、Review 资产和 Level 2 治理包检查。它不是可运行的前端项目，也不作为业务脚手架分发。

目录内**不常驻** `common-governance/`，避免与仓库根发布包形成第二份治理来源。

## 验证路径

| 路径 | 命令 / 位置 | 测什么 |
|---|---|---|
| rules-only | `check-project-adoption.py --repo examples/adoption-fixture/frontend --stack frontend --strict` | 仅规则包入口、本地覆盖与严格 Review 资产 |
| 治理接入 | workflow「Strict governance adoption fixture」：先 `cp -R common-governance` 到本目录，再 `--level 2` | 完整治理包 + Level 2 控制声明 |

命令通过只证明接入材料满足静态规则，不证明页面、接口或权限业务正确。单测等价路径位于 `scripts/tests/test_governance_scripts.py`：测试运行时临时复制本夹具与 `common-governance/`，再执行 `--level 2`。

修改校验器时应同步维护本夹具和单元测试。真实业务仓接入方式见 `docs/project-adoption-guide.md`，monorepo 布局见 `docs/monorepo-layout.md`。
