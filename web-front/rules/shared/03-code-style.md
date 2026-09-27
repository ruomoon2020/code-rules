# 代码风格规则

适用于 Vue 3 + TypeScript + Vite 企业后台项目。

## TypeScript

1. 开启 `strict`，提交前必须通过 `vue-tsc --noEmit` 或项目等价命令。
2. 禁止显式 `any`；确实未知的输入使用 `unknown`。
3. `unknown` 必须通过类型守卫、schema parser 或运行时校验后再使用。
4. 公共函数必须声明参数和返回类型；简单组件内部函数可由 TS 推断。
5. DTO 类型优先来自 `src/api/generated`，不要重复手写。
6. 布尔变量使用 `is`、`has`、`can`、`should` 前缀。
7. 命名细则以 **`shared/02-naming.md`** 为准（本文件不重复列举）。

## Vue

1. 使用 `<script setup lang="ts">`。
2. Props / Emits 使用类型宏：`defineProps<Props>()`、`defineEmits<...>()`。
3. 需要 keep-alive 的页面必须 `defineOptions({ name: 'RouteName' })`。
4. 页面组件负责编排，不写大段公共逻辑。
5. 复用逻辑放到 `composables`，纯工具放到 `utils`。
6. 不在 store 中操作 DOM。
7. 不在 api 层直接调用 Element Plus message、dialog。

## Import

1. 优先使用 `@/` alias，禁止超过两级的 `../../../`。
2. 避免 barrel 导出造成循环依赖；公共包入口除外。
3. 业务页面禁止直接引入 `element-plus` 及 `element-plus/*`（见 `00-must-follow` §6）。
4. 类型导入使用 `import type`。

## AST: views 禁原生 Element Plus

目标：`src/views/**` 只使用 Base 封装组件（含禁止 `el-*` 与 denylist 内 `<ElButton>` 等，见 `00-must-follow` §5–7）。

禁止：

```vue
<el-button />
<el-table />
<ElButton />
<ElTable />
```

禁止：

```ts
import { ElMessage, ElTable } from 'element-plus'
import { ElButton } from 'element-plus/es/components/button'
```

允许：

```vue
<BaseButton />
<BaseTable />
<BaseDialog />
```

落地项目须组合 ESLint（import）与 `rules/examples/ci-scan-views-el-tags.mjs`（模板）；见 `examples/README.md`。

## 注释

1. 注释解释**为什么**，不要复述代码做了什么。
2. 复杂业务规则、权限判断、兼容逻辑、非显而易见的分支必须注释。
3. `TODO` / `FIXME` 必须包含负责人或任务 ID 与预期处理时间，不允许无跟进永久 TODO。
4. 公共组件、公共函数、复杂 composable 须在文件顶部或导出处说明**用法边界**（适用场景、必填上下文、副作用）。
5. 公共 API（utils、composable、Base 组件）的非 trivial 参数与返回值，使用 JSDoc `@param` / `@returns`（若项目已启用则遵循项目 ESLint 约定）。
6. 禁止大段注释掉的废弃代码；删除或用版本管理追溯，勿留「备用代码块」。
7. 中英文：团队主语言为中文时，业务注释用中文；类型名、API 名、协议字段保持英文原文。

## 日志

生产日志与错误上报见 **`shared/18-logging-observability.md`**（结构化 `event`、脱敏、traceId）。

要点：

1. 生产代码禁止散落 `console.log`。
2. 日志统一走 logger / monitor 封装。
3. 错误日志须含 `event`、`route`、`traceId`（或 `requestId`）等可定位字段。
4. 禁止记录密码、Token、完整证件号、未脱敏手机号、完整请求体。
