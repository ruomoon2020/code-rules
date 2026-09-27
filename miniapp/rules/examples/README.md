# Examples

可复制到业务仓的脚本、CI 与脚手架样板。

| 路径 | 说明 |
|---|---|
| `package-scripts.sample.json` | `lint`、`build:mp-weixin`、`api:check`、`size:check` |
| `99-project-local.mdc.sample` | Cursor 本地路径、环境、白名单、18 适用边界、26 安全加固登记项 |
| `ci/rules-package-validate.yml` | 嵌入 `rules/` 时 PR 校验规则包 |
| `scripts/check-miniapp-size.mjs.sample` | 主包体积门禁 |
| `scripts/api-check.stub.mjs.sample` | 契约检查占位（替换为项目实现） |
| `scaffold/` | request、登录、App、web-view、域名白名单 |
| `.github/pull_request_template.md` | 小程序 PR 检查项 |

## 规则包一致性

```bash
python rules/scripts/validate-rules-package.py --rules-dir rules
```

Monorepo：`python miniapp/rules/scripts/validate-rules-package.py`。

## 业务仓 CI 建议

```json
{
  "scripts": {
    "lint": "eslint .",
    "type-check": "vue-tsc --noEmit",
    "build:mp-weixin": "uni build -p mp-weixin",
    "api:check": "node scripts/api-check.mjs",
    "size:check": "node scripts/check-miniapp-size.mjs"
  }
}
```

PR 改 `rules/**` 时复制 `ci/rules-package-validate.yml` 到 `.github/workflows/`。
