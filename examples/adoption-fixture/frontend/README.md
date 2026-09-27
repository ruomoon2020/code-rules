# 最小前端接入样板

供 `scripts/check-project-adoption.py` 与 CI 自测使用。目录内**不常驻** `common-governance/`，避免与根发布包双维护。

## CI 覆盖两条路径

| 路径 | 命令 / 位置 | 测什么 |
|---|---|---|
| rules-only | `check-project-adoption.py --repo examples/adoption-fixture/frontend --stack frontend --strict` | 仅规则包入口、本地覆盖与严格 Review 资产 |
| 治理接入 | workflow「Strict governance adoption fixture」：先 `cp -R common-governance` 到本目录，再 `--level 2` | 完整治理包 + Level 2 控制声明 |

单测等价路径：`scripts/tests/test_governance_scripts.py` 中临时复制本 fixture 与 `common-governance/` 后跑 `--level 2`。

详见 monorepo `scripts/check-project-adoption.py`、`docs/monorepo-layout.md`。
