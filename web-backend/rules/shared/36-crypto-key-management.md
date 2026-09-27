# Crypto and Key Management

与 `21-configuration-secrets.md`、`29-data-privacy-lifecycle.md` 互补，约束密码、Token、签名、加密、随机数和密钥轮换。

## 基本原则

1. 禁止自研加密算法、编码代替加密、简单 hash 代替密码存储。
2. 密码只允许使用 BCrypt、Argon2、PBKDF2 等带盐慢哈希；禁止 MD5、SHA1、裸 SHA256 存密码。
3. 随机数、验证码、Token、nonce 必须使用 `SecureRandom` 或框架等价安全随机源。
4. 加密、签名、JWT、Webhook、API Key 的密钥必须来自环境变量、KMS、Vault 或配置中心；禁止硬编码。

## 密钥生命周期

1. 密钥须有 Owner、用途、创建时间、轮换周期、吊销方式。
2. 支持双密钥 / 多版本校验，便于平滑轮换；禁止只有一个不可替换的全局 secret。
3. 密钥泄露时须有应急流程：禁用、替换、影响范围、审计、通知。
4. 日志、异常、审计、错误响应中禁止输出密钥、Token、完整签名原文。

## Token 与签名

1. JWT 须校验签名、过期时间、issuer、audience（按项目）；禁止只解析不校验。
2. Refresh Token 须可撤销、可轮换；登出 / 改密 / 权限变更后按项目策略失效。
3. Webhook / 外部回调须校验签名、时间戳、nonce 或幂等键，防重放。
4. API Key 须分环境、分调用方、最小权限、可审计、可吊销。

## 数据加密

1. 需要可逆加密的敏感字段须说明算法、密钥来源、轮换方案、查询限制。
2. 不需要还原的敏感标识优先 hash + salt / pepper；禁止明文进入缓存 key。
3. 传输层默认 HTTPS / TLS；服务间 mTLS 见 `37-service-to-service-auth.md`。

## AI 生成约束

1. AI 不得生成 MD5/SHA1 密码存储、固定 secret、硬编码 token、弱随机验证码。
2. AI 生成签名 / Token 逻辑时，必须说明过期、轮换、吊销、重放防护。
