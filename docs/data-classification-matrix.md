# 跨端数据分类分级矩阵

> SSOT：新字段须在 OpenAPI / 数据字典标注级别。细则互补：`web-backend/rules/shared/29`、`web-front/rules/shared/18`、`miniapp/rules/shared/09`、`23`。

## 分级总表

| 级别 | 示例 | 后端 | 管理端 | 小程序 | 日志 / 埋点 | 缓存 / Storage | 导出 |
|---|---|---|---|---|---|---|---|
| **L0 公开** | 商品名、公告标题 | 可明文 | 可明文 | 可明文 | 可记录 | 可缓存 | 可导出 |
| **L1 内部** | 内部编码、非敏感配置 | 鉴权后返回 | 鉴权后展示 | 鉴权后展示 | 可记录 | 短 TTL | 鉴权导出 |
| **L2 敏感 PII** | 手机、邮箱、证件、地址 | 脱敏存储；展示脱敏 | 脱敏 + 权限码 | 最小采集；拒绝态 | **禁止明文**；hash/末四位 | **禁止未脱敏**；短 TTL | 权限 + 审计 + 条数上限 |
| **L3 凭证** | 密码、Token、密钥、支付凭证 | 禁止落库明文 | 禁止进 store 持久化 | 禁止进 storage | **绝对禁止** | **禁止** | **禁止** |
| **L4 财务** | 金额、账户、流水 | 审计 + 权限；金额类型规范 | 权限 + formatter | 支付以后端为准 | 脱敏 + 审计 | 不缓存明细 | 水印 / 有效期 |
| **L5 权限元数据** | 角色、数据范围、租户 | 变更审计 | 仅授权可见 | 按 scope | 记 operatorId | 会话级 | 管理员 + 审计 |

## 端侧要点

### 后端

- OpenAPI `description` 或扩展字段标注 `x-sensitive-level`（可选约定）。
- 错误响应、Swagger 示例、测试 fixture **禁止**真实生产 PII。
- 缓存 key 禁止明文手机号（见 `29`）。

### 管理端

- 日志 / RUM：**禁止** Token、完整手机号、证件号（`18-logging-observability`）。
- 导出 CSV：防公式注入 + L2+ 脱敏（E25）。
- 富文本 / UGC：sanitizer（E43）。

### 小程序

- 隐私弹窗与采集一致（`09-privacy-permission`）。
- `uni.setStorage` 不存 L3；L2 须加密或会话级（按项目）。
- UGC 先审后发或敏感词（`23-content-safety`）。

## 生命周期

| 阶段 | 要求 |
|---|---|
| 采集 | 最小必要；用途说明 |
| 使用 | 按级别脱敏展示 |
| 存储 | 保留周期 + 软删 + 物理清理策略 |
| 注销 | 匿名化或删除可识别 PII |
| 备份 | 加密 + 访问控制 + 销毁流程 |

## PR 自检

- [ ] 新字段已标级别
- [ ] 日志 / 缓存 / 导出 / 消息体已对照本表
- [ ] 测试数据无生产 PII

## 相关

- [`definition-of-done.md`](definition-of-done.md)
- [`codeowners-matrix.md`](codeowners-matrix.md)（PII 新字段行）
- `web-backend/rules/docs/compliance-cn-mapping.md`
