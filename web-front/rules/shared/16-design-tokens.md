# 设计 Token 规则

业务代码的视觉约束以**项目 Token 文件**为准（如 `src/styles/tokens`、CSS 变量、Tailwind 主题配置）。无项目文件时，遵守下列执行规则。

## 必须使用 Token 的属性

- 颜色（含背景、边框、文字、状态色）
- 间距（padding、margin、gap）
- 圆角、阴影
- z-index（使用分层 Token，禁止随意 `9999`）
- 字体大小、行高（业务组件）

## 禁止

- 在业务组件写主题色十六进制（`#409EFF` 等）
- 用纯色块表达状态语义（须配合文案 / 图标 / 标签组件）
- 复制粘贴一套新的间距体系

## 状态色语义

- success / warning / danger / info 使用统一语义 Token
- 表格状态、标签、按钮 danger 与 `04-ui-patterns.md` 一致

## 主题与密度

- 明暗主题切换走项目主题插件，不在页面写死 `dark` 类名逻辑
- 表格、表单密度若项目支持 compact / default，须在模块内统一

## 响应式

- 筛选区、工具栏小屏可折行或折叠，禁止横向溢出
- 断点使用项目断点 Token，不写随意 `@media 768px` 除非项目约定

执行细节与页面布局见 `04-ui-patterns.md`；可访问性见 `07-security-performance.md`。
