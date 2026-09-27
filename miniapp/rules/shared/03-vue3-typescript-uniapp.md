# 03 Vue3 TypeScript uni-app

## 基础

1. Vue 文件必须使用 `<script setup lang="ts">`。
2. TypeScript 必须开启 strict；禁止显式 `any`。
3. props、emits、slots 必须显式类型。
4. computed 不得产生副作用；副作用放入事件或生命周期。
5. 禁止在模板中写复杂表达式；复杂逻辑放 computed 或函数。

## uni-app 约束

1. 使用 `uni-*` 能力前先确认平台兼容性。
2. 条件编译只允许出现在 adapter 或极少量入口文件；页面内不得密集出现。
3. 生命周期逻辑必须短小，复杂流程交给 composable / service。
4. 不直接操作 DOM；优先使用 uni-app 与小程序能力。
5. 不依赖浏览器专属 API，除非明确只在 H5 条件编译内使用。

## 类型与 generated

1. API request / response 类型来自 generated。
2. 外部参数、scene、二维码参数先用 `unknown` 接收，再校验为内部类型。
3. 支付、金额、时间、状态字段必须使用明确类型，禁止用宽泛 `string` 混过。

## 单文件组件组织顺序

1. SFC 使用 `<template>` → `<script setup lang="ts">` → `<style lang="scss" scoped>`；全局样式进入项目声明的全局样式目录。
2. script 内按：类型导入 → 值导入 → props/emits/slots/model → composables/store → state/computed → methods → watchers → lifecycle 组织。
3. 类型优先 `import type`；组件私有类型就近定义，公共类型进入 `types/`，API DTO 以 generated 为准。
4. props 视为只读，不复制为可漂移的第二份状态；草稿态必须定义同步、取消和提交语义。
5. 可增删或排序列表使用稳定业务 key，不使用数组下标。

## 组件通信决策

按最小作用域依次选择：

1. **Props / Emits**：父子组件默认方案，数据向下、事件向上。
2. **v-model**：用于具有可编辑值语义的受控组件；默认使用 `modelValue` / `update:modelValue`，多模型使用具名 model。
3. **Provide / Inject**：用于同一组件树内稳定上下文；使用 typed `InjectionKey`、只读状态和显式 actions，并定义缺少 provider 的行为。
4. **Pinia**：用于跨页面、跨分包或跨生命周期状态，不保存组件实例、节点引用、不可序列化对象或局部 UI 状态。
5. **EventBus**：仅用于一次性、低耦合的应用级通知；事件名和 payload 类型化，订阅方负责注销，不作为业务状态通道。

补充约束：

- `defineExpose` 只暴露明确的命令式能力，例如弹窗开关、表单校验或重置，并记录类型契约。
- 同一事实只由 props、Pinia、服务端缓存或组件局部状态中的一个来源维护。
- emits 表达已经发生的事实；组件不假定 emit 后父组件会同步更新 prop。

## Props、Emits、Slots 与 v-model 契约

1. 对外组件显式声明必填项、默认值、空值语义、允许范围和不可变约束。
2. Emits 声明 payload 类型，不使用宽泛 payload 逃避契约。
3. Slot 名使用 kebab-case，slot props 类型化，避免万能 default slot 承载多个隐式区域。
4. 表单组件定义输入合成、清空、校验失败和禁用时的 `modelValue` 行为。
