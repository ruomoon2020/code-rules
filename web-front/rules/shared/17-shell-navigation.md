# 壳层与导航规则

## 应用壳层

1. 侧栏、顶栏、内容区、页签（若有）放在 `layouts` 或 `components/layout`。
2. 业务 `views` 只负责内容区，不重复实现全局导航。
3. 壳层组件不依赖具体业务 API；菜单数据通过配置或 store 注入。

## 路由与菜单

1. 路由 `name` 使用 PascalCase；启用 keep-alive 时，组件 `defineOptions({ name })` 必须与路由 `name` 一致，细则见 `02-naming.md`、`03-code-style.md`。
2. `meta` 至少包含项目约定字段：`title`、`permission`、`keepAlive`、`hidden`（按项目裁剪）。
3. 外链菜单必须明确 `target`、协议与来源白名单；新窗口使用 `noopener,noreferrer` 或等价隔离。禁止在业务页内嵌未知或未登记来源的 iframe。
4. iframe 只允许加载项目登记的 HTTPS 来源，并设置最小 `sandbox` / `allow` 权限；涉及登录态、跨窗通信或敏感数据时同时遵守 `07-security-performance.md`、`25-regulated-web-hardening.md`。

## 多页签与未保存状态

1. 关闭页签、切换租户、退出登录或批量关闭页签前，必须检查当前页未保存状态；确认策略复用 `04-ui-patterns.md`，禁止壳层直接销毁表单草稿。
2. 页签恢复只能恢复路由和允许持久化的筛选状态，禁止把密码、Token、完整表单或敏感详情写入本地缓存。

## 面包屑与页头

- 面包屑反映真实路由层级，不伪造路径。
- 页头主操作与 `04-ui-patterns.md` 一致：每区一个主按钮。

## 特殊页型

### 登录 / 注册 / 找回密码

- 独立 layout，不挂载后台侧栏。
- 表单校验、错误提示、提交 loading 完整。
- 不暴露内网地址、调试开关。

### Dashboard / 图表页

- 图表、地图等大型依赖懒加载。
- 卡片区块 loading / empty / error 分区处理，不整页空白。
- 时间范围筛选与接口参数一致。

## 禁止

- 在 `views` 内写全局 `position: fixed` 顶栏覆盖壳层
- 绕过统一菜单权限渲染「隐藏入口」
- 未确认即关闭含未保存修改的页签

详见 `06-state-route-permission.md`。
