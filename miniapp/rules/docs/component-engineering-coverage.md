# 组件工程规范覆盖矩阵

本矩阵用于确认组件、样式、生命周期、测试和性能规则均有执行入口与验收证据。

| 主题 | 规则来源 | 项目覆盖 | 验证证据 |
|---|---|---|---|
| 文件、组件、变量、CSS 命名 | `shared/02-naming.md` | Base 前缀、BEM、变量前缀 | lint + rules validator |
| SFC 结构与 TypeScript | `shared/03-vue3-typescript-uniapp.md` | 项目目录、generated 路径 | type-check |
| Props/Emits 与 v-model | `shared/03-vue3-typescript-uniapp.md` | 受控值契约 | 组件测试 |
| Provide/Inject、Pinia、EventBus | `shared/03-vue3-typescript-uniapp.md` | store 和 EventBus 边界 | 单测 + 清理测试 |
| Vue/页面/App 生命周期 | `shared/04-page-ui-lifecycle.md`、`shared/20-app-runtime.md` | 刷新、缓存、资源 owner | 集成测试 + 启动指标 |
| SCSS、BEM 与主题 | `shared/24-design-system-mobile.md` | 样式目录、主题集 | 组件测试 + 视觉证据 |
| 组件文档与版本 | `shared/24-design-system-mobile.md` | 组件目录、废弃策略 | 文档检查 + migration note |
| 单元、组件、快照、E2E | `shared/16-testing-quality-gates.md` | 工具与阈值 | CI 测试报告 |
| 启动、渲染、图片 | `shared/10-performance-package-size.md` | P50/P95、低端设备档位 | 性能对比证据 |
| 包体积与分包加载 | `shared/07-pages-routing-subpackages.md`、`shared/10-performance-package-size.md` | 分包目录、主/分/总包阈值 | size check + 构建 |

## 合并口径

1. 组件、主题或性能改动必须命中 Codex 与 Cursor 对应路由。
2. 项目路径、平台、阈值和工具写在项目覆盖层，不写死在通用规则。
3. 缺少测试或性能基础设施时标记未配置并建立迁移任务，不声称门禁已通过。
