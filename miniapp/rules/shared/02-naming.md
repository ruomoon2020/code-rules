# 02 Naming

## 文件与目录

1. 目录使用 kebab-case：`subpackages/order-detail/`。
2. 页面文件使用 `index.vue`，页面目录表达语义：`pages/home/index.vue`。
3. 组件文件使用 PascalCase：`BaseSafeArea.vue`、`OrderCard.vue`。
4. composable 使用 `useXxx.ts`：`useOrderList.ts`。
5. service 使用领域名：`order.service.ts`、`payment.service.ts`。
6. platform adapter 使用能力名：`payment.adapter.ts`、`share.adapter.ts`。
7. storage key 统一在 `stores/` 或 `auth/keys.ts` 管理，禁止散落字符串。
8. 测试文件与被测单元同名：`BaseButton.spec.ts`、`useOrderList.spec.ts`；辅助文件使用 `*.fixture.ts`、`*.factory.ts`。

## 变量与类型

1. 类型 / interface 使用 PascalCase：`OrderListItem`、`LoginSession`。
2. enum 或常量对象使用业务语义：`OrderStatus`、`PaymentChannel`。
3. API 方法使用动词开头：`fetchOrderPage`、`submitOrder`、`queryPaymentStatus`。
4. boolean 使用 `is/has/can/should` 前缀。
5. 普通自定义事件使用 kebab-case：`submit-success`；`v-model` 事件在 TypeScript 中使用 `update:modelValue`，模板监听写作 `@update:model-value`。
6. props 使用名词或状态语义；局部变量 camelCase，模块级常量 UPPER_SNAKE_CASE。
7. 泛型使用可读名称（`TItem`、`TValue`、`TResponse`），简单局部映射除外。

## CSS 与主题变量命名

1. 组件根类使用 kebab-case 与 BEM：`.base-button`、`.base-button__icon`、`.base-button--loading`。
2. 状态类使用 `.is-*` / `.has-*`；名称表达语义，不以颜色或位置命名。
3. 页面根类使用 `{domain}-{page}`，局部类避免 `.item`、`.title` 等过短通用名。
4. SCSS 与 CSS 自定义属性均采用语义化命名；业务主题变量必须带项目定义的前缀。
5. BEM 类是样式契约，不作为组件通信或节点查询接口。

## 小程序命名

1. 页面路由 path 必须稳定，不因标题变化而重命名。
2. 分包 root 使用业务域：`subpackages/order`、`subpackages/member`。
3. 订阅消息模板、支付场景、分享来源须有枚举或常量，不得使用魔法字符串。
