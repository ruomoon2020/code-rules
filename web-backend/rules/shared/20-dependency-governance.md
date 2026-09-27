# Dependency Governance

## 引入与评审

1. 新增依赖须说明：**用途**、**许可证**、**体积**、**安全影响**、**是否替代现有依赖**。
2. 须评估 **transitive dependency** 风险：传递依赖是否引入冲突许可证、重复实现或已知高危组件。
3. Spring Boot BOM 对齐；禁止随意升级 major 无回归。
4. MyBatis-Plus、驱动（mysql、postgresql）版本在父 POM 统一管理。
5. 公共 Starter / 拦截器类依赖变更须确认 Owner，必要时 ADR（见 `30-ownership-adr.md`）。
6. Spring Boot major 升级须单独评审：确认 Java 运行版本、Jakarta EE API、Servlet 容器、MyBatis-Plus、Springdoc/OpenAPI、Flyway、测试插件与 CI 均支持目标版本；迁移辅助依赖仅可临时加入，迁移完成后移除。

## 许可证

1. 维护许可证 **白名单**（如 Apache-2.0、MIT、BSD）与 **黑名单**（如 GPL 传染、未知许可证）。
2. PR 引入新许可证须在 Review 中说明合规结论。
3. 禁止引入 **abandoned**（长期无维护、官方归档）的包作为核心依赖；若无法替代须 ADR + 风险接受记录。

## 安全与 SBOM

1. 定期 **OWASP Dependency-Check**、GitHub Dependabot 或等价 SCA。
2. CI 生成或更新 **SBOM**（CycloneDX / SPDX，按项目工具）；发布分支保留 SBOM 产物或构建链接。
3. **高危 CVE**：按团队 SLA 修复（示例：Critical 7 天、High 30 天）；无法修复须风险登记与缓解措施。
4. 禁止在 `mvn verify` / `./gradlew check` 未跑依赖扫描时声称「无已知漏洞」。

## AI 生成

1. 不得随意添加未在 BOM 中管理的依赖。
2. 用户要求引入 GPL、来源不明或已废弃库时须拒绝并建议替代方案。
