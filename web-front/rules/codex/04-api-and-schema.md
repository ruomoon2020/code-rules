# Codex API 与 Schema 规则

用于编辑 API 文件、请求封装、schema、generated 客户端，或依赖 API 字段的页面。

同时阅读 `rules/shared/12-schema-ssot.md`。

## 单一事实来源

按以下顺序：

```text
contracts/schema.json
  -> src/api/generated
  -> src/api/* 薄封装
  -> views / components
```

## 编辑规则

1. 禁止手改 `src/api/generated`。
2. generated 类型有误时，先改契约源再重新生成。
3. 手写 API 文件保持薄封装：组合 generated 客户端并补充业务友好命名。
4. 请求拦截器负责 token、traceId、错误归一化与下载处理。
5. 底层 API 层不得弹出 UI 提示。

## Schema 变更审查

schema 变更时检查：

- 删除字段
- 重命名字段
- 必填项变化
- 枚举增删
- 响应包装结构变化
- 分页结构变化

破坏性变更须附迁移说明与回滚意识。

## 命令

项目已配置时运行：

```bash
pnpm schema:sync
pnpm api:gen
pnpm api:check
pnpm type-check
```

若某命令不存在，须说明项目尚未接入对应门禁，不得伪造通过。
