# Cloud Native Runtime

与 `22-operability.md`、`23-quality-gates.md`、`32-service-reliability.md` 互补，约束容器、Kubernetes、Helm/Terraform/IaC 与运行时安全。

## 容器镜像

1. 生产镜像禁止使用 `latest` tag；推荐固定版本或 digest。
2. 镜像内禁止包含密钥、生产配置、测试 dump、构建缓存中的凭证。
3. 容器默认非 root 用户运行；文件系统尽量只读，按需挂载临时目录。
4. 镜像须经过漏洞扫描；Critical / High 漏洞按 `20-dependency-governance.md` 的 SLA 处理。

## Kubernetes / 运行资源

1. 必须配置 readiness / liveness / startup probe（按服务类型）。
2. 必须配置 CPU / memory requests 与 limits；禁止无界资源。
3. 支持 graceful shutdown：停止接流、完成请求、释放连接、停止任务。
4. 生产禁止直接暴露管理端口、Actuator 敏感端点、调试端口。

## 配置与密钥

1. K8s Secret、云 Secret Manager、Vault 等仅存密钥，不把密钥写入 ConfigMap。
2. Helm / Terraform / K8s YAML 变更须 Review；涉及公网、权限、Secret、数据库、队列须额外审查。
3. IaC 变更须可回滚；生产权限变更须审计。

## AI 生成约束

1. AI 生成 Dockerfile / Helm / K8s / Terraform 时，不得使用 root、latest、硬编码 secret、无资源限制的生产配置。
2. AI 涉及云资源或运行时权限时，须说明安全、成本、回滚与 Owner。
