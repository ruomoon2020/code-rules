# 小程序工程与 CI 样板

本目录提供小程序业务仓可采用的脚本、CI、本地覆盖层和运行边界样板，目标是把分包、契约、域名、登录、构建和包体积要求落实为可执行检查。

## 推荐使用顺序

1. 复制 `99-project-local.mdc.sample`，填写目标平台、分包、合法域名、隐私路径和预算。
2. 将 `package-scripts.sample.json` 中需要的脚本合并进现有 `package.json`。
3. 按需采用 `scaffold/`，替换所有示例配置和占位实现。
4. 本地验证后复制规则包校验 workflow，并把真实构建与包体积检查接入 PR CI。

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

业务验收还应覆盖登录过期、授权拒绝、支付回调重放、弱网恢复、非法域名和目标平台真机行为；规则包一致性校验不能替代这些场景测试。
