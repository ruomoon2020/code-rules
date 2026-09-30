# Gradle 后端接入测试夹具

本目录是 `scripts/check-project-adoption.py` 的最小化自动测试输入，用于证明后端 Gradle 项目的入口文件、规则路径和构建识别逻辑可被校验器识别。它不是业务脚手架，也不应作为新项目直接复制。

## 如何使用

在仓库根目录执行：

```bash
python scripts/check-project-adoption.py --repo examples/adoption-fixture/backend-gradle --stack backend
```

命令通过只表示“接入结构符合静态检查”，不表示业务代码、依赖、数据库迁移或权限流程正确。

## 修改约束

- 调整 `check-project-adoption.py` 的 Gradle 识别逻辑时，同步更新本夹具和对应单元测试。
- 夹具只保留触发检查所需的最小文件，不在这里堆放真实业务示例。
- 可复制的 Spring Boot Gradle 工程样板位于 `web-backend/rules/examples/gradle/`。
