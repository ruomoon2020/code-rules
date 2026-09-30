# 验证清单

完成改动或声称「已完成」前，执行本清单。命令以项目 `package.json` 中实际 scripts 为准。

## 自动化命令

```bash
pnpm lint
pnpm type-check
pnpm test
pnpm build
```

API / schema 相关改动额外运行（若存在）：

```bash
pnpm api:check
```

脚本不存在时，在回复中写明「项目未配置该门禁」，不得伪造通过。

## 手工检查

1. `src/views/**` 无 `el-*`、无 denylist 内 EP PascalCase（如 `<ElButton>`），无 `element-plus` / `element-plus/*` import；已跑 `lint:views-el`（若配置）。
2. 无新增显式 `any`。
3. 组件内无 `axios` / `fetch`。
4. 无裸 `v-html`。
5. 已处理 loading、empty、error、permission、提交 loading。
6. 破坏性操作有确认。
7. `keepAlive` 页面 `defineOptions({ name })` 与路由 `name` 一致。
8. 新增目录、文件、变量、enum、样式类、环境变量符合 `02-naming.md`。
9. 表单 / 表格字段先以 `contracts/openapi.yaml` 为准，再核对由它同步生成的 schema、generated 类型；禁止把生成物当作字段定义入口。
10. 日志无敏感信息；错误日志含 `event` 与 traceId / requestId / route / release（见 `18-logging-observability.md`）。
11. 列表页：筛选或 pageSize 变化回第一页、删当前页最后一条回退、批量操作后清空 selection 并修正页码、批量部分失败有明确反馈、请求竞态已处理（见 `19-list-pagination.md`）。
12. 大依赖懒加载、搜索 debounce、大表格分页或虚拟滚动（见 `07-security-performance.md`）。
13. 新增 / 升级依赖已说明原因、替代方案、体积、维护状态、许可证与加载策略（见 `20-dependency-governance.md`）。
14. 全局错误、路由 chunk 失败、白屏、登录过期、页面重试路径已按 `21-error-recovery.md` 检查。
15. 文件导入 / 导出：模板、字段、权限、脱敏、错误明细、异步任务、幂等标识、下载鉴权、审计日志已按 `14-upload-import-export.md` 检查。
16. 未提交密钥、mock handler。
17. 列表页使用 `useTable`（或项目等价封装）时包含 error 态与重试。
18. 成熟后台新增业务页按 `22-business-module-extension.md` 检查：复用平台菜单 / 权限 / 字典；路由 `name` 与按钮权限码与后端一致；`api:gen` 后未手改 generated；列表四态与分页竞态；导入导出与操作记录刷新；树表 / 主子表 UI 与后端数据范围一致。
19. i18n / 区域格式：用户可见文案与枚举走 i18n 或字典；金额、日期、时区用统一 formatter；`errorCode` 映射为用户文案（见 `23-i18n-locale.md`）。
20. WebSocket / SSE：鉴权不走 URL query 长期 Token；卸载取消订阅；未知消息禁止未校验 DOM 插入（见 `24-realtime-rich-content.md`）。
21. 富文本 / 编辑器：禁止裸 `v-html`；须 sanitizer；重型编辑器按需加载（见 `24-realtime-rich-content.md`）。
22. AI / 工具：外部内容未被当作授权；工具调用范围最小；无未授权外部写入或敏感数据出站；所有“已通过”结论均有本次证据（见 `09-ai-generation.md`）。
23. 测试已固定时钟、网络和数据；无重试洗绿，失败证据可诊断；写链路竞态与 API 兼容窗口按 `15-testing.md` 验证。

## 最终回复应包含

- 改了什么、动了哪些文件
- 运行了哪些命令及结果
- 未运行的命令及原因

Codex 详见 `rules/codex/05-verification.md`；质量门禁详见 `shared/08-quality-gates.md`。

跨端发版与合并标准见 `docs/enterprise-governance.md`（monorepo `docs/definition-of-done.md`）。
