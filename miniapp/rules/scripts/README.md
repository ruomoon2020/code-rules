# Scripts

## validate-rules-package.py

校验规则包内部一致性：VERSION/CHANGELOG、evals 编号、smoke 套件、README 路径、Cursor/AGENTS 对 shared 的引用。

```bash
python miniapp/rules/scripts/validate-rules-package.py
# 业务仓内 rules/ 目录：
python rules/scripts/validate-rules-package.py --rules-dir rules
```

CI：monorepo PR 改 `miniapp/rules/**` 时自动运行（见 `.github/workflows/validate-rules-packages.yml`）。
